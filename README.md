# ftp-validator

## project structure

```text
ftp-validator/
├── docker-compose.yml        # Local infrastructure (Azurite & FTP)
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Testing and linting tools (pytest, etc.)
├── host.json                 # Azure Functions global config
├── local.settings.json       # Local environment variables
├── function_app.py           # Azure Function v2 entry point
├── src/                      # Business Logic
│   ├── __init__.py
│   ├── ftp_client.py         # Handles FTP connection and listing
│   ├── blob_client.py        # Handles Azure Blob operations
│   ├── table_logger.py       # Handles writing audit logs to Azure Tables
│   └── validator.py          # Orchestrates the comparison logic
└── tests/                    # Unit & Integration Tests
    ├── __init__.py
    ├── conftest.py           # Pytest fixtures (mocks)
    └── test_validator.py
```

## references

### deploying

1. Export your production dependencies

```bash
uv export --format requirements-txt --no-dev --no-hashes > requirements.txt
```

2. Log into Azure

```bash
az login
```

3. Publish the code

```bash
func azure functionapp publish <YourFunctionAppName> --build remote
```

4. Configure the environment variables

```bash
az functionapp config appsettings set \
  --name <YourFunctionAppName> \
  --resource-group <YourResourceGroupName> \
  --settings \
    "FTP_HOST=your_vendor_host" \
    "FTP_USER=your_vendor_user" \
    "FTP_PASS=your_vendor_pass" \
    "AZURE_STORAGE_CONNECTION_STRING=your_real_conn_string" \
    "BLOB_CONTAINER=vendor-data" \
    "QUEUE_NAME=your_queue_name" \
    "TABLE_NAME=ValidationAudit"
```

### execute

```bash
curl -X GET "https://<YourFunctionAppName>.azurewebsites.net/api/start_retroactive_audit?days=90" \
     -H "x-functions-key: <YourFunctionKey>"
```

### generate report

```bash
uv run python generate_report.py
```

