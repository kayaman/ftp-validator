import logging

from azure.storage.blob import BlobServiceClient

from .settings import settings


class BlobClient:
    def __init__(self):
        self.conn_str = settings.azure_storage_connection_string
        self.container_name = settings.blob_container_name
        self.blob_service = BlobServiceClient.from_connection_string(self.conn_str)
        self.base_path = settings.blob_base_path.strip("/")

    def get_files_with_size(self, date_str: str) -> dict:
        """Returns a dictionary of {filename: size} for blobs with the date prefix."""
        blob_files = {}

        target_prefix = (
            f"{self.base_path}/{date_str}/" if self.base_path else f"{date_str}/"
        )

        try:
            container_client = self.blob_service.get_container_client(
                self.container_name
            )

            if not container_client.exists():
                container_client.create_container()

            logging.info(f"Scanning Blob Storage with prefix: {target_prefix}")
            blobs = container_client.list_blobs(name_starts_with=target_prefix)

            for blob in blobs:
                filename = blob.name[len(target_prefix) :]
                blob_files[filename] = blob.size

        except Exception as e:
            logging.error(f"Azure Blob Storage error: {e}")
            raise

        return blob_files
