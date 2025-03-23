"""
This file contains unit tests for the backend_api_keys.py module.

The tests validate the backend API key functions:
1. test_add_api_key -> tests adding API keys to the database.
2. test_edit_api_key -> tests editing existing API keys.
3. test_delete_api_key -> tests deleting API keys from database.
4. test_update_api_key_selected_field -> tests updating the selected field.
5. test_get_all_api_key_data -> tests retrieving all API keys.
6. test_get_api_key_data -> tests retrieving a specific API key.
"""
import pytest
import sqlite3
from unittest.mock import patch, MagicMock

from gui.api_keys_window.backend_api_keys import (
    _add_api_key, _edit_api_key,
    _delete_api_key, _update_api_key_selected_field,
    _get_all_api_key_data, _get_api_key_data
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
    2. Create the necessary tables for API keys.
    3. Yield the connection for use in tests.
    4. Close the connection after tests are complete.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nvd_api_key (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_name TEXT,
            key_value TEXT,
            status TEXT,
            error_count INTEGER,
            selected INTEGER
        )
    """)

    # Insert some test data
    cursor.execute("""
        INSERT INTO nvd_api_key (
            key_name, key_value, status, error_count, selected
        ) VALUES (?, ?, ?, ?, ?)
    """, ("TestKey1", "value1", "Valid", 0, 0))

    cursor.execute("""
        INSERT INTO nvd_api_key (
            key_name, key_value, status, error_count, selected
        ) VALUES (?, ?, ?, ?, ?)
    """, ("TestKey2", "value2", "Invalid", 2, 1))

    conn.commit()

    yield conn

    conn.close()


@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_add_api_key_validation(mock_error_dialog, mock_db_connection):
    """
    Tests input validation in _add_api_key function.

    This test should:
    1. Test empty key_name scenario.
    2. Test empty key_value scenario.
    3. Verify error dialog is shown when validation fails.
    """
    mock_error_dialog.return_value = MagicMock()

    # Test empty key_name
    success, message = _add_api_key("", "test_value")
    assert success is False
    assert "Empty Field" in message
    mock_error_dialog.assert_called_once()
    mock_error_dialog.reset_mock()

    # Test empty key_value
    success, message = _add_api_key("test_name", "")
    assert success is False
    assert "Empty Field" in message
    mock_error_dialog.assert_called_once()


@patch("gui.api_keys_window.backend_api_keys.sqlite3")
@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_add_api_key_db_operation(
    mock_error_dialog, mock_sqlite, mock_db_connection
):
    """
    Tests database operations in _add_api_key function.

    This test should:
    1. Test successful DB insertion.
    2. Test DB error handling.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_sqlite.connect.return_value = mock_conn

    # Test successful insertion
    success, message = _add_api_key("NewKey", "NewValue")
    assert success is True
    assert "Successfully added key" in message

    # Verify correct SQL was executed
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "INSERT INTO nvd_api_key" in call_args[0]
    assert call_args[1][0] == "NewKey"
    assert call_args[1][1] == "NewValue"
    assert call_args[1][2] == "Valid"
    assert call_args[1][3] == 0
    assert call_args[1][4] == 0

    # Test DB error
    mock_sqlite.Error = sqlite3.Error
    mock_cursor.execute.side_effect = sqlite3.Error("DB Error")

    success, message = _add_api_key("ErrorKey", "ErrorValue")
    assert success is False
    assert "Database error" in message
    mock_error_dialog.assert_called_once()


@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_edit_api_key_validation(mock_error_dialog):
    """
    Tests input validation in _edit_api_key function.

    This test should:
    1. Test empty key_name scenario.
    2. Test empty key_value scenario.
    3. Verify error dialog is shown when validation fails.
    """
    mock_error_dialog.return_value = MagicMock()

    # Test empty key_name
    success, message = _edit_api_key(1, "", "test_value", "Valid")
    assert success is False
    assert "Empty" in message
    mock_error_dialog.assert_called_once()
    mock_error_dialog.reset_mock()

    # Test empty key_value
    success, message = _edit_api_key(1, "test_name", "", "Valid")
    assert success is False
    assert "Empty" in message
    mock_error_dialog.assert_called_once()


@patch("gui.api_keys_window.backend_api_keys.sqlite3")
@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_edit_api_key_db_operation(
    mock_error_dialog, mock_sqlite, mock_db_connection
):
    """
    Tests database operations in _edit_api_key function.

    This test should:
    1. Test successful DB update.
    2. Test DB error handling.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_sqlite.connect.return_value = mock_conn

    # Test successful update
    success, message = _edit_api_key(
        1, "UpdatedKey", "UpdatedValue", "Invalid"
    )
    assert success is True
    assert "Successfully updated Key" in message

    # Verify correct SQL was executed
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "UPDATE nvd_api_key" in call_args[0]
    assert call_args[1][0] == "UpdatedKey"
    assert call_args[1][1] == "UpdatedValue"
    assert call_args[1][2] == "Invalid"
    assert call_args[1][3] == 1

    # Test DB error
    mock_sqlite.Error = sqlite3.Error
    mock_cursor.execute.side_effect = sqlite3.Error("DB Error")

    success, message = _edit_api_key(1, "ErrorKey", "ErrorValue", "Valid")
    assert success is False
    assert "Database error" in message
    mock_error_dialog.assert_called_once()


@patch("gui.api_keys_window.backend_api_keys.sqlite3")
@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_delete_api_key(mock_error_dialog, mock_sqlite, mock_db_connection):
    """
    Tests the _delete_api_key function.

    This test should:
    1. Test successful deletion of an API key.
    2. Test error handling during deletion.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_sqlite.connect.return_value = mock_conn

    # Test successful deletion
    success, message = _delete_api_key(1)
    assert success is True
    assert "Successfully deleted API Key" in message

    # Verify correct SQL was executed
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "DELETE FROM nvd_api_key" in call_args[0]
    assert call_args[1] == (1,)

    # Test DB error
    mock_sqlite.Error = sqlite3.Error
    mock_cursor.execute.side_effect = sqlite3.Error("DB Error")

    success, message = _delete_api_key(1)
    assert success is False
    assert "Database error" in message
    mock_error_dialog.assert_called_once()


@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_update_api_key_selected_field_validation(mock_error_dialog):
    """
    Tests input validation in _update_api_key_selected_field function.

    This test should:
    1. Test invalid selected value scenario.
    2. Verify error dialog is shown when validation fails.
    """
    mock_error_dialog.return_value = MagicMock()

    # Test invalid selected value
    success, message = _update_api_key_selected_field(1, 2)
    assert success is False
    assert "Invalid input for selected field" in message
    mock_error_dialog.assert_called_once()

    # Test valid selected values
    for valid_value in [0, 1]:
        with patch(
            "gui.api_keys_window.backend_api_keys.sqlite3"
        ) as mock_sqlite:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_sqlite.connect.return_value = mock_conn

            success, message = _update_api_key_selected_field(1, valid_value)
            assert success is True


@patch("gui.api_keys_window.backend_api_keys.sqlite3")
@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_update_api_key_selected_field_db_operation(
        mock_error_dialog, mock_sqlite, mock_db_connection
):
    """
    Tests database operations in _update_api_key_selected_field function.

    This test should:
    1. Test successful DB update.
    2. Test DB error handling.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_sqlite.connect.return_value = mock_conn

    # Test successful update
    success, message = _update_api_key_selected_field(1, 1)
    assert success is True
    assert "Successfully updated selection status" in message

    # Verify correct SQL was executed
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "UPDATE nvd_api_key" in call_args[0]
    assert "SET selected = ?" in call_args[0]
    assert call_args[1] == (1, 1)

    # Test DB error
    mock_sqlite.Error = sqlite3.Error
    mock_cursor.execute.side_effect = sqlite3.Error("DB Error")

    success, message = _update_api_key_selected_field(1, 0)
    assert success is False
    assert "Database error" in message
    mock_error_dialog.assert_called_once()


def test_get_all_api_key_data(setup_test_db):
    """
    Tests the _get_all_api_key_data function using a test database.

    This test should:
    1. Use the setup_test_db fixture to create a test database.
    2. Call _get_all_api_key_data and verify it returns the correct data.
    """
    conn = setup_test_db

    with patch(
        "gui.api_keys_window.backend_api_keys.sqlite3.connect"
    ) as mock_connect:
        mock_connect.return_value = conn

        api_keys = _get_all_api_key_data()

        # Verify the returned data
        assert len(api_keys) == 2
        assert api_keys[0]["key_name"] == "TestKey1"
        assert api_keys[0]["key_value"] == "value1"
        assert api_keys[0]["status"] == "Valid"
        assert api_keys[0]["error_count"] == 0
        assert api_keys[0]["selected"] == 0

        assert api_keys[1]["key_name"] == "TestKey2"
        assert api_keys[1]["key_value"] == "value2"
        assert api_keys[1]["status"] == "Invalid"
        assert api_keys[1]["error_count"] == 2
        assert api_keys[1]["selected"] == 1


@patch("gui.api_keys_window.backend_api_keys.sqlite3")
@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_get_all_api_key_data_error(mock_error_dialog, mock_sqlite):
    """
    Tests error handling in _get_all_api_key_data function.

    This test should:
    1. Force a database error.
    2. Verify error dialog is shown.
    3. Verify an empty list is returned.
    """
    mock_sqlite.Error = sqlite3.Error
    mock_sqlite.connect.side_effect = sqlite3.Error("DB Error")

    result = _get_all_api_key_data()

    assert result == []
    mock_error_dialog.assert_called_once()


def test_get_api_key_data(setup_test_db):
    """
    Tests the _get_api_key_data function using a test database.

    This test should:
    1. Use the setup_test_db fixture to create a test database.
    2. Call _get_api_key_data and verify it returns the correct data.
    """
    conn = setup_test_db

    with patch(
        "gui.api_keys_window.backend_api_keys.sqlite3.connect"
    ) as mock_connect:
        mock_connect.return_value = conn

        # Get an existing API key
        api_key = _get_api_key_data(1)

        # Verify the returned data
        assert api_key["key_name"] == "TestKey1"
        assert api_key["key_value"] == "value1"
        assert api_key["status"] == "Valid"
        assert api_key["error_count"] == 0
        assert api_key["selected"] == 0


@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_get_api_key_data_not_found(mock_error_dialog, setup_test_db):
    """
    Tests the _get_api_key_data function when the key is not found.

    This test should:
    1. Request a non-existent key ID.
    2. Verify error dialog is shown.
    3. Verify None is returned.
    """
    conn = setup_test_db
    mock_error_dialog.return_value = MagicMock()

    with patch(
        "gui.api_keys_window.backend_api_keys.sqlite3.connect"
    ) as mock_connect:
        mock_connect.return_value = conn

        # Try to get a non-existent API key
        api_key = _get_api_key_data(999)

        # Verify the result and error dialog
        assert api_key is None
        mock_error_dialog.assert_called_once()


@patch("gui.api_keys_window.backend_api_keys.sqlite3")
@patch("gui.api_keys_window.backend_api_keys.GeneralErrorDialog")
def test_get_api_key_data_error(mock_error_dialog, mock_sqlite):
    """
    Tests error handling in _get_api_key_data function.

    This test should:
    1. Force a database error.
    2. Verify error dialog is shown.
    3. Verify None is returned.
    """
    mock_sqlite.Error = sqlite3.Error
    mock_sqlite.connect.side_effect = sqlite3.Error("DB Error")

    result = _get_api_key_data(1)

    assert result is None
    mock_error_dialog.assert_called_once()
