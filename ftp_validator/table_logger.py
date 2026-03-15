import os
import logging
import re
from datetime import datetime, timezone
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError


class TableLogger:
    def __init__(self):
        self.conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        self.table_name = os.environ.get("TABLE_NAME", "ValidationAudit")
        self.table_service = TableServiceClient.from_connection_string(self.conn_str)
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Creates the table if it doesn't already exist."""
        try:
            self.table_service.create_table(self.table_name)
        except ResourceExistsError:
            pass

    def log_discrepancy(
        self, date_str: str, filename: str, ftp_size: int, blob_size: int, status: str
    ):
        """Upserts an audit record into the Azure Table."""
        table_client = self.table_service.get_table_client(self.table_name)

        # Azure Table RowKeys cannot contain certain characters like '/', '\', '#', '?'
        safe_filename = re.sub(r"[\\/#\?]", "_", filename)

        entity = {
            "PartitionKey": date_str,
            "RowKey": safe_filename,
            "Status": status,
            "FtpSize": ftp_size,
            "BlobSize": blob_size,
            "CheckedAt": datetime.now(timezone.utc).isoformat(),
        }

        try:
            table_client.upsert_entity(entity)
            logging.info(f"Logged discrepancy: [{status}] for {filename}")
        except Exception as e:
            logging.error(f"Failed to write to Table Storage for {filename}: {e}")
