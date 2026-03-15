import logging
from datetime import datetime, timedelta

from ftp_validator.blob_client import BlobClient
from ftp_validator.ftp_client import FtpClient
from ftp_validator.table_logger import TableLogger


def run_validation(target_date: datetime | None = None):
    """
    Main orchestration logic. Compares FTP files against Blob storage.
    If no target_date is provided, it defaults to yesterday.
    """
    if not target_date:
        # Default run processes the previous day's files
        target_date = datetime.now() - timedelta(days=1)

    date_str = target_date.strftime("%Y-%m-%d")
    logging.info(f"Starting file validation for date: {date_str}")

    # Initialize clients
    ftp_client = FtpClient()
    blob_client = BlobClient()
    audit_logger = TableLogger()

    # 1. Get FTP Data
    logging.info("Scanning FTP server...")
    ftp_files = ftp_client.get_files_with_size(date_str)
    logging.info(f"Found {len(ftp_files)} files on FTP.")

    if not ftp_files:
        logging.info("No files found on FTP. Exiting validation early.")
        return

    # 2. Get Blob Data
    logging.info("Scanning Azure Blob Storage...")
    blob_files = blob_client.get_files_with_size(date_str)
    logging.info(f"Found {len(blob_files)} files in Blob Storage.")

    # 3. Compare and Log Discrepancies
    discrepancies = 0
    for filename, ftp_size in ftp_files.items():
        if filename not in blob_files:
            audit_logger.log_discrepancy(
                date_str, filename, ftp_size, 0, "Missing from Blob"
            )
            discrepancies += 1
        elif blob_files[filename] != ftp_size:
            audit_logger.log_discrepancy(
                date_str, filename, ftp_size, blob_files[filename], "Size Mismatch"
            )
            discrepancies += 1

    # 4. Final summary
    if discrepancies == 0:
        logging.info(
            f"Validation successful. All {len(ftp_files)} files match perfectly."
        )
    else:
        logging.warning(
            f"Validation finished. Found {discrepancies} discrepancies out of {len(ftp_files)} files."
        )
