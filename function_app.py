import logging
import typing
from datetime import datetime, timedelta

import azure.functions as func

from ftp_validator.validator import run_validation

app = func.FunctionApp()


# --- 1. THE ORCHESTRATOR (Triggered manually via HTTP) ---
@app.route(route="start_retroactive_audit", auth_level=func.AuthLevel.FUNCTION)
@app.queue_output(
    arg_name="msg",
    queue_name="%QUEUE_NAME%",
    connection="AZURE_STORAGE_CONNECTION_STRING",
)
def start_audit(
    req: func.HttpRequest, msg: func.Out[typing.List[str]]
) -> func.HttpResponse:
    """
    Calculates the past 90 days and pushes each date into the Azure Queue.
    """
    # Get days from query param, default to 90
    days_to_check = req.params.get("days")
    days_to_check = int(days_to_check) if days_to_check else 90

    logging.info(f"Queueing retroactive audit for the last {days_to_check} days.")

    messages = []
    today = datetime.now()

    # Generate dates (e.g., from yesterday going backward)
    for i in range(1, days_to_check + 1):
        target_date = today - timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        messages.append(date_str)

    # Push all 90 dates to the queue at once
    msg.set(messages)

    return func.HttpResponse(
        f"Successfully queued {days_to_check} days for validation. Check Azure Tables for results shortly.",
        status_code=200,
    )


# --- 2. THE WORKER (Triggered automatically by the Queue) ---
@app.queue_trigger(
    arg_name="azqueue",
    queue_name="%QUEUE_NAME%",
    connection="AZURE_STORAGE_CONNECTION_STRING",
)
def process_daily_validation(azqueue: func.QueueMessage):
    """
    Picks up a single date from the queue and runs the validation logic.
    """
    date_str = azqueue.get_body().decode("utf-8")
    logging.info(f"Queue Worker picked up date: {date_str}")

    try:
        # Convert string back to datetime object for our validator
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        run_validation(target_date)
        logging.info(f"Successfully processed {date_str}")
    except Exception as e:
        logging.error(f"Failed to process date {date_str}: {e}")
        raise e
