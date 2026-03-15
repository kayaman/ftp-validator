import os
import csv
from azure.data.tables import TableServiceClient

CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
TABLE_NAME = os.environ.get("TABLE_NAME", "ValidationAudit")


def generate_csv_report(output_filename="missing_files_report.csv"):
    if not CONNECTION_STRING:
        print("Error: AZURE_STORAGE_CONNECTION_STRING environment variable is not set.")
        return

    print(f"Connecting to Azure Table: {TABLE_NAME}...")
    try:
        table_service = TableServiceClient.from_connection_string(CONNECTION_STRING)
        table_client = table_service.get_table_client(TABLE_NAME)

        # We query all records. Since we only log discrepancies (Missing/Mismatch),
        # every row in this table is an actionable item for management.
        print("Fetching discrepancy records from Azure...")
        entities = table_client.list_entities()

        # Extract the generator into a list so we can count it
        records = list(entities)

        if not records:
            print("Great news! No discrepancies found. The table is empty.")
            return

        print(f"Found {len(records)} discrepancies. Writing to {output_filename}...")

        # Define headers mapping to the fields we created in table_logger.py
        headers = [
            "Target Date",
            "File Name",
            "Issue Status",
            "FTP Size (Bytes)",
            "Blob Size (Bytes)",
            "Audit Timestamp",
        ]

        with open(output_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for entity in records:
                writer.writerow(
                    [
                        entity.get("PartitionKey"),  # Target Date
                        entity.get("RowKey"),  # File Name
                        entity.get("Status"),
                        entity.get("FtpSize"),
                        entity.get("BlobSize"),
                        entity.get("CheckedAt"),
                    ]
                )

        print(f"Success! Report saved to {output_filename}")

    except Exception as e:
        print(f"Failed to generate report: {e}")


if __name__ == "__main__":
    generate_csv_report()
