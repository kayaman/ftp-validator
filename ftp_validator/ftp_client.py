import logging
from ftplib import FTP

from .settings import settings


class FtpClient:
    def __init__(self):
        self.host = settings.ftp_host
        self.port = int(settings.ftp_port)
        self.user = settings.ftp_user
        self.password = settings.ftp_pass
        self.base_path = settings.ftp_base_path.strip("/")

    def get_files_with_size(self, date_str: str) -> dict:
        """Returns a dictionary of {filename: size} for a specific date directory."""
        ftp_files: dict = {}

        target_path = (
            f"/{self.base_path}/{date_str}" if self.base_path else f"/{date_str}"
        )

        try:
            ftp = FTP()
            ftp.connect(self.host, self.port)
            ftp.login(self.user, self.password)

            try:
                logging.info(f"Navigating to FTP path: {target_path}")
                ftp.cwd(target_path)
            except Exception as e:
                logging.warning(
                    f"FTP directory '{target_path}' not found or inaccessible: {e}"
                )
                ftp.quit()
                return ftp_files

            for name, meta in ftp.mlsd():
                if meta.get("type") == "file":
                    ftp_files[name] = int(meta.get("size", 0))

            ftp.quit()
        except Exception as e:
            logging.error(f"Critical FTP connection error: {e}")
            raise

        return ftp_files
