"""
Unit tests for backend_scans.py and its functionality.
"""
import os
import sqlite3
import pytest
from gui.scans_window.dialogs_scans import GeneralErrorDialog
from gui.scans_window.backend_scans import (
    _add_scan,
)


@pytest.fixture
def test_db_path():
    """
    Returns a temp db path for testing.
    """
    return "temp_vuln_data.db"


@pytest.fixture
def empty_test_db(test_db_path):
    """
    Creates an empty temp-db for testing.
    """
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    create_empty_db_query = """
    CREATE TABLE IF NOT EXISTS scan_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        total_vulnerabilities INTEGER,
        unique_cve_list TEXT,
        cache_enabled INTEGER NOT NULL DEFAULT 1,
        cached_percentage FLOAT NOT NULL DEFAULT 0.0,
        selected INTEGER NOT NULL DEFAULT 0
    )
    """
    cursor.execute(create_empty_db_query)

    conn.commit()
    conn.close()

    yield test_db_path

    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def populated_test_db(empty_test_db):
    """
    Populates an empty temp db for testing.
    """
    def return_sample_scans() -> list[dict]:
        """
        Returns a list of predefined sample scan data.

        Happy path test scans:
        1. happy_path_scan_1 -> happy path test.
        2. happy_path_scan_2 -> happy path test.
        3. happy_path_scan_3 -> happy path test.
        """
        happy_path_scan_1 = {
            "scan_name": "Test Scan 1",
            "file_path": r"C:\Users\dan\Downloads\test_scan_1.csv",
            "total_vulnerabilities": 3400,
            "unique_cve_list": "CVE-2001-12345",
            "cache_enabled": 1,
            "cached_percentage": 91.2,
            "selected": 0
        }
        happy_path_scan_2 = {
            "scan_name": "Test Scan 2",
            "file_path": "/home/brian/Downloads/test_scan_2.csv",
            "total_vulnerabilities": 1280,
            "unique_cve_list": "CVE-2001-12345, CVE-2002-54321",
            "cache_enabled": 1,
            "cached_percentage": 32.1,  # Corrected field name
            "selected": 0
        }
        happy_path_scan_3 = {
            "scan_name": "Test Scan 3",
            "file_path": r"C:\Users\chris\Desktop\test_scan_3.csv",
            "total_vulnerabilities": 56,
            "unique_cve_list": """
                CVE-2001-12345, CVE-2002-54321, CVE-2003-12345
            """,
            "cache_enabled": 1,
            "cached_percentage": 23.0,  # Corrected field name
            "selected": 0
        }
        return [
            happy_path_scan_1,
            happy_path_scan_2,
            happy_path_scan_3,
        ]

    sample_scans = return_sample_scans()

    conn = sqlite3.connect(empty_test_db)
    cursor = conn.cursor()

    for scan in sample_scans:
        cursor.execute('''
        INSERT INTO scan_data (
            scan_name, file_path, total_vulnerabilities,
            unique_cve_list, cache_enabled, cached_percentage, selected
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan["scan_name"],
            scan["file_path"],
            scan["total_vulnerabilities"],
            scan["unique_cve_list"],
            scan["cache_enabled"],
            scan.get("cached_percentage", scan.get("cache_percentage", 0.0)),  # Handling both field names
            scan["selected"]
        ))

    conn.commit()
    conn.close()

    return empty_test_db


@pytest.fixture
def mock_cve_functions(monkeypatch):
    """
    Fixture that mocks the functions from processing.scans_processing.
    """
    def mock_return_cve_ids_from_csv(*args, **kwargs):
        return (
            ["CVE-2023-1111", "CVE-2023-2222", "CVE-2023-1111"],
            {"CVE-2023-1111", "CVE-2023-2222"}
        )

    def mock_return_cached_percentage(*args, **kwargs):
        return 85.0

    monkeypatch.setattr(
        'gui.scans_window.backend_scans.return_cve_ids_from_csv',
        mock_return_cve_ids_from_csv
    )
    monkeypatch.setattr(
        'gui.scans_window.backend_scans.return_cached_percentage',
        mock_return_cached_percentage
    )

    yield {
        'return_cve_ids_from_csv': mock_return_cve_ids_from_csv,
        'return_cached_percentage': mock_return_cached_percentage
    }


@pytest.fixture
def mock_general_error_dialog(monkeypatch):
    """
    Fixture that tracks GeneralErrorDialog instances created during tests
    without actually displaying dialogs.
    """
    dialog_instances = []

    original_init = GeneralErrorDialog.__init__

    def tracked_init(self, error_message, parent=None):
        original_init(self, error_message, parent)
        dialog_instances.append(self)

    def silent_exec(self):
        return True

    monkeypatch.setattr(GeneralErrorDialog, '__init__', tracked_init)
    monkeypatch.setattr(GeneralErrorDialog, 'exec_', silent_exec)

    # Clear dialog instances before each test
    yield dialog_instances
    dialog_instances.clear()


# TEST FUNCTIONS FOR _add_scan #


def test_add_scan_empty_value_error(empty_test_db, mock_general_error_dialog):
    """
    Tests if an error with an empty scan_name or file_path
    is handled correctly.

    This function tests:
    1. User entered data with an empty scan_name.
        a. The return tuple...
            1. Returns a False bool value.
            2. Returns the correct error_msg.
        b. The GeneralErrorDialog...
            1. Pops up.
            2. Pops up with the correct message.
    2. User entered data with an empty file_path.
        a. The return tuple...
            1. Returns a False bool value.
            2. Returns the correct error_msg.
        b. The GeneralErrorDialog...
            1. Pops up.
            2. Pops up with the correct message.
    """
    # Test empty scan name
    success, message = _add_scan("", "/path/to/scan.csv", empty_test_db)

    assert success is False  # Test 1a1.
    assert "Empty Field" in message  # Test 1a2.
    assert len(mock_general_error_dialog) == 1  # Test 1b1.
    error_msg = mock_general_error_dialog[0].error_message
    assert "cannot be empty" in error_msg  # Test 1b2.
    
    # Clear dialog instances for the next test
    mock_general_error_dialog.clear()
    
    # Test empty file path
    success, message = _add_scan("Test Scan", "", empty_test_db)

    assert success is False  # Test 2a1.
    assert "Empty Field" in message  # Test 2a2.
    assert len(mock_general_error_dialog) == 1  # Test 2b1.
    error_msg = mock_general_error_dialog[0].error_message
    assert "cannot be empty" in error_msg  # Test 2b2.


def test_add_scan_file_type_error(empty_test_db, mock_general_error_dialog):
    """
    Tests if an error with an invalid file type
    is handled correctly.

    This function tests:
    1. User entered file that's not a csv file.
        a. The return tuple...
            1. Returns a False bool value.
            2. Returns the correct error_msg.
        b. The GeneralErrorDialog...
            1. Pops up.
            2. Pops up with the correct message.
    """
    def return_test_user_input() -> list[dict]:
        """
        Gives a list of user cases to test.

        This function should return:
        1. edge_case1 -> .txt file.
        2. edge_case2 -> .pdf file.
        3. edge_case3 -> gibberish.
        4. edge_case4 -> gibberish w/ "csv" at end.
        """
        edge_case1 = {
            "scan_name": "Test Scan 1",
            "file_path": "/path/to/scan.txt",
        }
        edge_case2 = {
            "scan_name": "Test Scan 2",
            "file_path": "/path/to/scan.pdf",
        }
        edge_case3 = {
            "scan_name": "Test Scan 3",
            "file_path": "sffdgbdsf",
        }
        edge_case4 = {
            "scan_name": "Test Scan 4",
            "file_path": "23*@)!)*!?csv",
        }

        return [
            edge_case1,
            edge_case2,
            edge_case3,
            edge_case4
        ]

    sample_scans = return_test_user_input()

    for i, scan in enumerate(sample_scans):
        # Clear the dialog list before each test
        mock_general_error_dialog.clear()
        
        success, message = _add_scan(
            scan["scan_name"], scan["file_path"], empty_test_db
        )
        assert success is False, f"Test case {i+1} should return False"  # Test 1a1.
        assert "Invalid File Format" in message, f"Test case {i+1} should return 'Invalid File Format' message"  # Test 1a2.

        assert len(mock_general_error_dialog) == 1, f"Test case {i+1} should create exactly one dialog"  # Test 1b1.
        error_msg = mock_general_error_dialog[0].error_message
        assert "Invalid File Format" in error_msg, f"Test case {i+1} should show 'Invalid File Format' error"  # Test 1b2.


# Add additional test functions for _add_scan, such as:
def test_add_scan_success(empty_test_db, mock_cve_functions, mock_general_error_dialog):
    """
    Tests successful scan addition.
    """
    success, message = _add_scan(
        "New Test Scan", 
        "/path/to/valid_scan.csv", 
        empty_test_db
    )
    
    assert success is True
    assert "success" in message.lower()
    assert len(mock_general_error_dialog) == 0  # No error dialogs should be shown
    
    # Verify data was added to database
    conn = sqlite3.connect(empty_test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_data WHERE scan_name = 'New Test Scan'")
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    assert result[1] == "New Test Scan"  # scan_name
    assert result[2] == "/path/to/valid_scan.csv"  # file_path


def test_add_scan_duplicate(populated_test_db, mock_general_error_dialog):
    """
    Tests handling of duplicate scan names.
    """
    # Try to add a scan with a name that already exists
    success, message = _add_scan(
        "Test Scan 1",  # This name already exists in populated_test_db
        "/path/to/another_scan.csv", 
        populated_test_db
    )
    
    assert success is False
    assert "already exists" in message.lower() or "duplicate" in message.lower()
    assert len(mock_general_error_dialog) == 1
    assert "already exists" in mock_general_error_dialog[0].error_message.lower() or "duplicate" in mock_general_error_dialog[0].error_message.lower()