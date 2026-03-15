from datetime import datetime

from ftp_validator.validator import run_validation


def test_run_validation_all_match(mocker):
    # 1. ARRANGE
    # Mock the three client classes so they don't make real network calls
    mock_ftp = mocker.patch("ftp_validator.validator.FtpClient")
    mock_blob = mocker.patch("ftp_validator.validator.BlobClient")
    mock_table = mocker.patch("ftp_validator.validator.TableLogger")

    # Configure what the mocked clients should return
    mock_ftp.return_value.get_files_with_size.return_value = {
        "file1.txt": 100,
        "file2.txt": 200,
    }
    mock_blob.return_value.get_files_with_size.return_value = {
        "file1.txt": 100,
        "file2.txt": 200,
    }

    test_date = datetime(2026, 3, 13)

    # 2. ACT
    run_validation(target_date=test_date)

    # 3. ASSERT
    # Verify the clients were called with the correctly formatted date string
    mock_ftp.return_value.get_files_with_size.assert_called_once_with("2026-03-13")
    mock_blob.return_value.get_files_with_size.assert_called_once_with("2026-03-13")

    # Verify that no discrepancies were logged
    mock_table.return_value.log_discrepancy.assert_not_called()


def test_run_validation_missing_file(mocker):
    # ARRANGE
    mock_ftp = mocker.patch("ftp_validator.validator.FtpClient")
    mock_blob = mocker.patch("ftp_validator.validator.BlobClient")
    mock_table = mocker.patch("ftp_validator.validator.TableLogger")

    # file2.txt is on the FTP, but missing from Blob
    mock_ftp.return_value.get_files_with_size.return_value = {
        "file1.txt": 100,
        "file2.txt": 200,
    }
    mock_blob.return_value.get_files_with_size.return_value = {"file1.txt": 100}

    test_date = datetime(2026, 3, 13)

    # ACT
    run_validation(target_date=test_date)

    # ASSERT
    # Verify the logger was called exactly once with the correct "Missing" parameters
    mock_table.return_value.log_discrepancy.assert_called_once_with(
        "2026-03-13", "file2.txt", 200, 0, "Missing from Blob"
    )


def test_run_validation_size_mismatch(mocker):
    # ARRANGE
    mock_ftp = mocker.patch("ftp_validator.validator.FtpClient")
    mock_blob = mocker.patch("ftp_validator.validator.BlobClient")
    mock_table = mocker.patch("ftp_validator.validator.TableLogger")

    # file1.txt exists in both, but the blob size is smaller (e.g., incomplete download)
    mock_ftp.return_value.get_files_with_size.return_value = {"file1.txt": 100}
    mock_blob.return_value.get_files_with_size.return_value = {"file1.txt": 99}

    test_date = datetime(2026, 3, 13)

    # ACT
    run_validation(target_date=test_date)

    # ASSERT
    # Verify the logger was called exactly once with the "Size Mismatch" parameters
    mock_table.return_value.log_discrepancy.assert_called_once_with(
        "2026-03-13", "file1.txt", 100, 99, "Size Mismatch"
    )
