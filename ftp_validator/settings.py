from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ftp_host: str = Field(description="FTP host address")
    ftp_user: str = Field(description="FTP username")
    ftp_pass: str = Field(description="FTP password")
    ftp_port: int = Field(description="FTP port")
    ftp_base_path: str = Field(description="FTP base path")

    azure_storage_connection_string: str = Field(
        description="Azure storage connection string"
    )
    blob_container_name: str = Field(description="Azure blob container name")
    blob_base_path: str = Field(description="Blob base path")
    table_name: str = Field(description="Table name")
    queue_name: str = Field(description="Queue name")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
