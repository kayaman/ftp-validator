import os
import pandas as pd
import matplotlib.pyplot as plt
from azure.data.tables import TableServiceClient

# Pull connection string from environment
CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
TABLE_NAME = os.environ.get("TABLE_NAME", "ValidationAudit")


def generate_visual_report():
    if not CONNECTION_STRING:
        print("Error: AZURE_STORAGE_CONNECTION_STRING is not set.")
        return

    print("Fetching data from Azure Table...")
    table_service = TableServiceClient.from_connection_string(CONNECTION_STRING)
    table_client = table_service.get_table_client(TABLE_NAME)

    # Fetch all records
    records = list(table_client.list_entities())

    if not records:
        print("No data to chart! The validation found zero discrepancies.")
        return

    # Load data into a Pandas DataFrame for easy manipulation
    df = pd.DataFrame(records)

    # Rename columns for cleaner chart labels
    df = df.rename(columns={"PartitionKey": "Date", "RowKey": "File Name"})

    # Set up the visual style
    plt.style.use("ggplot")

    # --- CHART 1: Discrepancies by Type (Pie Chart) ---
    print("Generating 'Discrepancies by Type' chart...")
    plt.figure(figsize=(8, 6))
    status_counts = df["Status"].value_counts()
    status_counts.plot(
        kind="pie", autopct="%1.1f%%", startangle=140, colors=["#e74c3c", "#f39c12"]
    )
    plt.title("Validation Issues by Type", pad=20)
    plt.ylabel("")  # Hide the y-label for pie charts
    plt.savefig("issues_by_type.png", bbox_inches="tight")
    plt.close()

    # --- CHART 2: Discrepancies by Date (Bar Chart) ---
    print("Generating 'Discrepancies by Date' chart...")
    plt.figure(figsize=(12, 6))
    date_counts = df.groupby("Date").size()

    # Create a bar chart, coloring bars based on volume
    date_counts.plot(kind="bar", color="#3498db")
    plt.title("Daily File Discrepancies (Last 90 Days)", pad=20)
    plt.xlabel("Date")
    plt.ylabel("Number of Missing/Mismatched Files")

    # Rotate date labels so they are readable
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()  # Ensures labels don't get cut off
    plt.savefig("issues_by_date.png")
    plt.close()

    print("Success! Generated 'issues_by_type.png' and 'issues_by_date.png'.")

    # Also save a quick summary text file
    total_missing = len(df[df["Status"] == "Missing from Blob"])
    total_mismatch = len(df[df["Status"] == "Size Mismatch"])

    with open("executive_summary.txt", "w") as f:
        f.write("--- RETROACTIVE AUDIT SUMMARY ---\n")
        f.write(f"Total Discrepancies Found: {len(df)}\n")
        f.write(f"Totally Missing Files: {total_missing}\n")
        f.write(f"Corrupted/Incomplete Files (Size Mismatch): {total_mismatch}\n")
        f.write(
            f"Most problematic date: {date_counts.idxmax()} ({date_counts.max()} issues)\n"
        )

    print("Created 'executive_summary.txt'.")


if __name__ == "__main__":
    generate_visual_report()
