import pytest


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """
    Automatically injects mock environment variables for all tests.
    This prevents the clients from failing during instantiation.
    """
    monkeypatch.setenv("FTP_HOST", "mock_host")
    monkeypatch.setenv("FTP_PORT", "21")
    monkeypatch.setenv("FTP_USER", "mock_user")
    monkeypatch.setenv("FTP_PASS", "mock_pass")
    monkeypatch.setenv("FTP_BASE_PATH", "mock/ftp/path")
    monkeypatch.setenv("BLOB_BASE_PATH", "mock/blob/path")
    monkeypatch.setenv(
        "AZURE_STORAGE_CONNECTION_STRING",
        "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=mock_key;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;",
    )
    monkeypatch.setenv("BLOB_CONTAINER", "mock_container")
    monkeypatch.setenv("TABLE_NAME", "mock_table")
    monkeypatch.setenv("QUEUE_NAME", "mock_queue")
    monkeypatch.setenv("AZURE_FUNCTION_APP_NAME", "mock_function_app")
    monkeypatch.setenv("AZURE_FUNCTION_APP_KEY", "mock_function_key")
