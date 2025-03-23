"""
This file contains unit tests for the backend_scans.py module.

The tests validate the backend scan functions:
1. test_add_scan -> tests adding scans to the database.
2. test_edit_scan -> tests editing existing scans.
3. test_delete_scan -> tests deleting scans from database.
4. test_update_scan_selected_field -> tests updating the selected field.
5. test_get_all_scan_data -> tests retrieving all scans.
6. test_get_scan_data -> tests retrieving a specific scan.
"""
import pytest
import sqlite3
from unittest.mock import patch, MagicMock

from gui.scans_window.backend_scans import (
    _add_scan, _edit_scan, _delete_scan, _update_scan_selected_field,
    _get_all_scan_data, _get_scan_data
)


@pytest.fixture
def mock_db_connection():
    """
    Fixture that provides a mock SQLite connection and cursor.

    This fixture should:
    1. Create mock objects for the SQLite connection and cursor.
    2. Configure the mock cursor to return appropriate values.
    3. Return the configured mocks for testing.
    """
    mock_conn = MagicMock(spec=sqlite3.Connection)
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    mock_conn.cursor.return_value = mock_cursor

    return mock_conn, mock_cursor


@pytest.fixture
def setup_test_db():
    """
    Fixture that creates a temporary SQLite database for testing.

    This fixture should:
    1. Create an in-memory SQLite database.
    2. Create the necessary tables for scans.
    3. Yield the connection for use in tests.
    4. Close the connection after tests are complete.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_name TEXT,
            file_path TEXT,
            total_vulnerabilities INTEGER,
            unique_cve_list TEXT,
            cache_enabled TEXT,
            cached_percentage REAL,
            selected INTEGER
        )
    """)

    # Insert some test data
    cursor.execute("""
        INSERT INTO scan_data (
            scan_name, file_path, total_vulnerabilities,
            unique_cve_list, cache_enabled, cached_percentage, selected
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "TestScan1", "/path/test1.csv", 100,
        "CVE-2021-1, CVE-2021-2", "Enabled", 75.5, 0
        )
    )

    cursor.execute("""
        INSERT INTO scan_data (
            scan_name, file_path, total_vulnerabilities,
            unique_cve_list, cache_enabled, cached_percentage, selected
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "TestScan2", "/path/test2.csv", 50,
        "CVE-2021-3, CVE-2021-4", "Disabled", 45.2, 1
        )
    )

    conn.commit()

    yield conn

    conn.close()


@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_add_scan_validation(mock_error_dialog):
    """
    Tests input validation in _add_scan function.

    This test should:
    1. Test empty scan_name scenario.
    2. Test empty file_path scenario.
    3. Test invalid file extension scenario.
    4. Verify error dialog is shown when validation fails.
    """
    mock_error_dialog.return_value = MagicMock()

    # Test empty scan_name
    success, message = _add_scan("", "/path/test.csv")
    assert success is False
    assert "Empty Field" in message
    mock_error_dialog.assert_called_once()
    mock_error_dialog.reset_mock()

    # Test empty file_path
    success, message = _add_scan("Test Scan", "")
    assert success is False
    assert "Empty Field" in message
    mock_error_dialog.assert_called_once()
    mock_error_dialog.reset_mock()

    # Test invalid file extension
    success, message = _add_scan("Test Scan", "/path/test.txt")
    assert success is False
    assert "Invalid File Format" in message
    mock_error_dialog.assert_called_once()


@patch("gui.scans_window.backend_scans.return_cve_ids_from_csv")
@patch("gui.scans_window.backend_scans.return_cached_percentage")
@patch("gui.scans_window.backend_scans.sqlite3")
@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_add_scan_db_operation(
    mock_error_dialog, mock_sqlite, mock_cached_percentage,
    mock_return_cve_ids, mock_db_connection
):
    """
    Tests database operations in _add_scan function.

    This test should:
    1. Test successful DB insertion.
    2. Test DB error handling.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_sqlite.connect.return_value = mock_conn

    # Mock processing functions
    mock_return_cve_ids.return_value = (
        ["CVE-2021-1", "CVE-2021-2"], {"CVE-2021-1", "CVE-2021-2"}
    )
    mock_cached_percentage.return_value = 75.5

    # Test successful insertion
    success, message = _add_scan("NewScan", "/path/test.csv")
    assert success is True
    assert "Successfully added scan" in message

    # Verify correct SQL was executed
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "INSERT INTO scan_data" in call_args[0]
    assert call_args[1][0] == "NewScan"
    assert call_args[1][1] == "/path/test.csv"
    assert call_args[1][2] == 2  # total_vulnerabilities
    assert call_args[1][3] == "CVE-2021-1, CVE-2021-2"  # unique_cve_list
    assert call_args[1][4] == "Enabled"  # cache_enabled
    assert call_args[1][5] == 75.5  # cached_percentage

    # Test DB error
    mock_sqlite.Error = sqlite3.Error
    mock_cursor.execute.side_effect = sqlite3.Error("DB Error")

    success, message = _add_scan("ErrorScan", "/path/test.csv")
    assert success is False
    assert "Database error" in message
    mock_error_dialog.assert_called_once()


@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_edit_scan_validation(mock_error_dialog):
    """
    Tests input validation in _edit_scan function.

    This test should:
    1. Test empty scan_name scenario.
    2. Test empty file_path scenario.
    3. Test invalid file extension scenario.
    4. Verify error dialog is shown when validation fails.
    """
    mock_error_dialog.return_value = MagicMock()

    # Test empty scan_name
    success, message = _edit_scan(1, "", "/path/test.csv", "Enabled")
    assert success is False
    assert "Empty" in message
    mock_error_dialog.assert_called_once()
    mock_error_dialog.reset_mock()

    # Test empty file_path
    success, message = _edit_scan(1, "Test Scan", "", "Enabled")
    assert success is False
    assert "Empty" in message
    mock_error_dialog.assert_called_once()
    mock_error_dialog.reset_mock()

    # Test invalid file extension
    success, message = _edit_scan(1, "Test Scan", "/path/test.txt", "Enabled")
    assert success is False
    assert "Invalid File Format" in message
    mock_error_dialog.assert_called_once()


@patch("gui.scans_window.backend_scans.return_cve_ids_from_csv")
@patch("gui.scans_window.backend_scans.return_cached_percentage")
@patch("gui.scans_window.backend_scans.sqlite3")
@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_edit_scan_db_operation(
    mock_error_dialog, mock_sqlite, mock_cached_percentage,
    mock_return_cve_ids, mock_db_connection
):
    """
    Tests database operations in _edit_scan function.

    This test should:
    1. Test successful DB update.
    2. Test DB error handling.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_sqlite.connect.return_value = mock_conn

    # Mock processing functions
    mock_return_cve_ids.return_value = (
        ["CVE-2021-5", "CVE-2021-6"], {"CVE-2021-5", "CVE-2021-6"}
    )
    mock_cached_percentage.return_value = 80.0

    # Test successful update
    success, message = _edit_scan(
        1, "UpdatedScan", "/path/updated.csv", "Disabled"
    )
    assert success is True
    assert "Successfully updated scan" in message

    # Verify correct SQL was executed
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "UPDATE scan_data" in call_args[0]
    assert call_args[1][0] == "UpdatedScan"
    assert call_args[1][1] == "/path/updated.csv"
    assert call_args[1][2] == 2  # total_vulnerabilities

    # For unique_cve_list, check the contents rather than the exact string,
    # since set ordering is not guaranteed
    unique_cve_list = call_args[1][3]
    assert "CVE-2021-5" in unique_cve_list
    assert "CVE-2021-6" in unique_cve_list

    assert call_args[1][4] == "Disabled"  # cache_enabled
    assert call_args[1][5] == 80.0  # cached_percentage
    assert call_args[1][6] == 1  # id

    # Test DB error
    mock_sqlite.Error = sqlite3.Error
    mock_cursor.execute.side_effect = sqlite3.Error("DB Error")

    success, message = _edit_scan(
        1, "ErrorScan", "/path/updated.csv", "Enabled"
    )
    assert success is False
    assert "Database error" in message
    mock_error_dialog.assert_called_once()


@patch("gui.scans_window.backend_scans.sqlite3")
@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_delete_scan(mock_error_dialog, mock_sqlite, mock_db_connection):
    """
    Tests the _delete_scan function.

    This test should:
    1. Test successful deletion of a scan.
    2. Test error handling during deletion.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_sqlite.connect.return_value = mock_conn

    # Test successful deletion
    success, message = _delete_scan(1)
    assert success is True
    assert "Successfully deleted scan" in message

    # Verify correct SQL was executed
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "DELETE FROM scan_data" in call_args[0]
    assert call_args[1] == (1,)

    # Test DB error
    mock_sqlite.Error = sqlite3.Error
    mock_cursor.execute.side_effect = sqlite3.Error("DB Error")

    success, message = _delete_scan(1)
    assert success is False
    assert "Database error" in message
    mock_error_dialog.assert_called_once()


@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_update_scan_selected_field_validation(mock_error_dialog):
    """
    Tests input validation in _update_scan_selected_field function.

    This test should:
    1. Test invalid selected value scenario.
    2. Verify error dialog is shown when validation fails.
    """
    mock_error_dialog.return_value = MagicMock()

    # Test invalid selected value
    success, message = _update_scan_selected_field(1, 2)
    assert success is False
    assert "Invalid input for selected field" in message
    mock_error_dialog.assert_called_once()

    # Test valid selected values
    for valid_value in [0, 1]:
        with patch(
            "gui.scans_window.backend_scans.sqlite3"
        ) as mock_sqlite:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_sqlite.connect.return_value = mock_conn

            success, message = _update_scan_selected_field(1, valid_value)
            assert success is True


@patch("gui.scans_window.backend_scans.sqlite3")
@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_update_scan_selected_field_db_operation(
        mock_error_dialog, mock_sqlite, mock_db_connection
):
    """
    Tests database operations in _update_scan_selected_field function.

    This test should:
    1. Test successful DB update.
    2. Test DB error handling.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_sqlite.connect.return_value = mock_conn

    # Test successful update
    success, message = _update_scan_selected_field(1, 1)
    assert success is True
    assert "Successfully updated selection status" in message

    # Verify correct SQL was executed
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "UPDATE scan_data" in call_args[0]
    assert "SET selected = ?" in call_args[0]
    assert call_args[1] == (1, 1)

    # Test DB error
    mock_sqlite.Error = sqlite3.Error
    mock_cursor.execute.side_effect = sqlite3.Error("DB Error")

    success, message = _update_scan_selected_field(1, 0)
    assert success is False
    assert "Database error" in message
    mock_error_dialog.assert_called_once()


def test_get_all_scan_data(setup_test_db):
    """
    Tests the _get_all_scan_data function using a test database.

    This test should:
    1. Use the setup_test_db fixture to create a test database.
    2. Call _get_all_scan_data and verify it returns the correct data.
    """
    conn = setup_test_db

    with patch(
        "gui.scans_window.backend_scans.sqlite3.connect"
    ) as mock_connect:
        mock_connect.return_value = conn

        scans = _get_all_scan_data()

        # Verify the returned data
        assert len(scans) == 2
        assert scans[0]["scan_name"] == "TestScan1"
        assert scans[0]["total_vulnerabilities"] == 100
        assert scans[0]["unique_cve_list"] == "CVE-2021-1, CVE-2021-2"
        assert scans[0]["cache_enabled"] == "Enabled"
        assert scans[0]["cached_percentage"] == 75.5
        assert scans[0]["selected"] == 0

        assert scans[1]["scan_name"] == "TestScan2"
        assert scans[1]["total_vulnerabilities"] == 50
        assert scans[1]["unique_cve_list"] == "CVE-2021-3, CVE-2021-4"
        assert scans[1]["cache_enabled"] == "Disabled"
        assert scans[1]["cached_percentage"] == 45.2
        assert scans[1]["selected"] == 1


@patch("gui.scans_window.backend_scans.sqlite3")
@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_get_all_scan_data_error(mock_error_dialog, mock_sqlite):
    """
    Tests error handling in _get_all_scan_data function.

    This test should:
    1. Force a database error.
    2. Verify error dialog is shown.
    3. Verify an empty list is returned.
    """
    mock_sqlite.Error = sqlite3.Error
    mock_sqlite.connect.side_effect = sqlite3.Error("DB Error")

    result = _get_all_scan_data()

    assert result == []
    mock_error_dialog.assert_called_once()


def test_get_scan_data(setup_test_db):
    """
    Tests the _get_scan_data function using a test database.

    This test should:
    1. Use the setup_test_db fixture to create a test database.
    2. Call _get_scan_data and verify it returns the correct data.
    """
    conn = setup_test_db

    with patch(
        "gui.scans_window.backend_scans.sqlite3.connect"
    ) as mock_connect:
        mock_connect.return_value = conn

        # Get an existing scan
        scan = _get_scan_data(1)

        # Verify the returned data
        assert scan["scan_name"] == "TestScan1"
        assert scan["file_path"] == "/path/test1.csv"
        assert scan["total_vulnerabilities"] == 100
        assert scan["unique_cve_list"] == "CVE-2021-1, CVE-2021-2"
        assert scan["cache_enabled"] == "Enabled"
        assert scan["cached_percentage"] == 75.5
        assert scan["selected"] == 0


@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_get_scan_data_not_found(mock_error_dialog, setup_test_db):
    """
    Tests the _get_scan_data function when the scan is not found.

    This test should:
    1. Request a non-existent scan ID.
    2. Verify error dialog is shown.
    3. Verify None is returned.
    """
    conn = setup_test_db
    mock_error_dialog.return_value = MagicMock()

    with patch(
        "gui.scans_window.backend_scans.sqlite3.connect"
    ) as mock_connect:
        mock_connect.return_value = conn

        # Try to get a non-existent scan
        scan = _get_scan_data(999)

        # Verify the result and error dialog
        assert scan is None
        mock_error_dialog.assert_called_once()


@patch("gui.scans_window.backend_scans.sqlite3")
@patch("gui.scans_window.backend_scans.GeneralErrorDialog")
def test_get_scan_data_error(mock_error_dialog, mock_sqlite):
    """
    Tests error handling in _get_scan_data function.

    This test should:
    1. Force a database error.
    2. Verify error dialog is shown.
    3. Verify None is returned.
    """
    mock_sqlite.Error = sqlite3.Error
    mock_sqlite.connect.side_effect = sqlite3.Error("DB Error")

    result = _get_scan_data(1)

    assert result is None
    mock_error_dialog.assert_called_once()
