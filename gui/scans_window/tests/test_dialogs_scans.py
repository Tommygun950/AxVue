"""
File for testing the functionality of dialogs_scans.py.
"""
import sys
import pytest
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QLabel
)
from gui.scans_window.dialogs_scans import (
    AddScanDialog, EditScanDialog, GeneralErrorDialog
)

# FIXTURES FOR TESTING #


@pytest.fixture
def app():
    """Create a QApplication instance for the tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_file_dialog(monkeypatch):
    """Mock QFileDialog.getOpenFileName to return a specific file path."""
    def _mock_get_open_file_name(parent, title, directory, filter):
        return "/path/to/test/file.csv", filter

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        _mock_get_open_file_name
    )


@pytest.fixture
def mock_file_dialog_cancel(monkeypatch):
    """Mock QFileDialog.getOpenFileName to simulate cancellation."""
    def _mock_get_open_file_name_cancel(parent, title, directory, filter):
        return "", filter

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        _mock_get_open_file_name_cancel
    )


# TESTS FOR TestAddScanDialog #


class TestAddScanDialog:
    def test_initialization(self, app):
        """
        Test that the AddScanDialog initializes correctly.

        This function tests:
        1. The window title is "Add Scan".
        2. QLineEdit (scan_name_edit) exists.
        3. QLineEdit(file_path_edit) exists.
        4. QPushButton (browse_button) exists.
        5. QPushButton (ok_button) exists.
        6. QPushButton (cancel_button) exists.
        """
        dialog = AddScanDialog()
        assert [  # Test 1.
            dialog.windowTitle() == "Add Scan",
            f"Dialog title isn't 'Add Scan', got {dialog.windowTitle} instead."
        ]
        assert [  # Test 2.
            hasattr(dialog, "scan_name_edit"),
            "Scan Name QLineEdit widget wasn't found."
        ]
        assert [  # Test 3.
            hasattr(dialog, "file_path_edit"),
            "File Path QLineEdit widget wasn't found."
        ]
        assert [  # Test 4.
            hasattr(dialog, "browse_button"),
            "Browse QPushButton widget wasn't found."
        ]
        assert [  # Test 5.
            hasattr(dialog, "ok_button"),
            "OK QPushButton widget wasn't found."
        ]
        assert [  # Test 6.
            hasattr(dialog, "cancel_button"),
            "Cacnel QPushButton widget wasn't found."
            ]

    def test_accept(self, app, monkeypatch):
        """
        Test that the OK button works correctly.

        This function should:
        1. Create an AddScanDialog dialog.
        2. Define a bool variable for the accept method being called.
        3. Create a mock acception.
        4. Patch the accept method.
        5. Pseudo-click ok in the dialog.

        This function tests:
        1. The PyQt accept method was called.
        """
        dialog = AddScanDialog()  # 1.

        accept_called = False  # 2.

        def mock_accept():  # 3.
            nonlocal accept_called
            accept_called = True

        monkeypatch.setattr(dialog, "accept", mock_accept)  # 4.

        dialog.ok_button.click()  # 5.

        assert accept_called is True  # Test 1.

    def test_reject(self, app, monkeypatch):
        """
        Test that the Cancel button works correctly.

        This function should:
        1. Create an AddScanDialog dialog.
        2. Define a bool varaible for the reject method being called.
        3. Create a mock rejection.
        4. Patch the reject method.
        5. Pseudo click the cancel button.

        This function tests:
        1. The PyQt reject method was called.
        """
        dialog = AddScanDialog()  # 1.

        reject_called = False  # 2.

        def mock_reject():  # 3.
            nonlocal reject_called
            reject_called = True

        monkeypatch.setattr(dialog, "reject", mock_reject)  # 4.

        dialog.cancel_button.click()  # 5.

        assert reject_called is True  # Test 1.

    def test_browse_file(self, app, mock_file_dialog):
        """
        Test that the file browser works correctly.

        This function should:
        1. Create an AddScanDialog dialog.
        2. Pseudo-click the browse button.

        This function tests:
        1. The file_path QLineEdit text was updated correctly.
        """
        dialog = AddScanDialog()  # 1.

        dialog.browse_button.click()  # 2.

        assert [  # Test 1.
            dialog.file_path_edit.text() == "/path/to/test/file.csv",
            """
                File Path QLineEdit was not updated properly after
                accessing the Browse QPushButton.
            """
        ]

    def test_browse_file_cancelled(self, app, mock_file_dialog_cancel):
        """
        Test that nothing happens when file dialog is cancelled.

        This function should:
        1. Create an AddScanDialog.
        2. Set an initial path.
        3. Set the path text to the File Path QLineEdit.
        4. Pseudo-click the Browse QPushButton.

        This function tests:
        1. File Path QLineEdit text isn't changed after cancelling
        browsing for a file.
        """
        dialog = AddScanDialog()  # 1.

        initial_path = "initial/path.csv"  # 2.
        dialog.file_path_edit.setText(initial_path)  # 3.

        dialog.browse_button.click()  # 4.

        assert [  # Test 1.
            dialog.file_path_edit.text() == initial_path,
            """
                File Path QLineEdit text was incorrectly altered
                after cancelling the browse_file functionality.
            """
        ]


# TESTS FOR TestEditScanDialog #


class TestEditScanDialog:
    @pytest.fixture(params=[
        {  # Happy path case 1.
            'case': "standard_scan",
            'scan_id': 123,
            'scan_name': "Regular Scan",
            'file_path': "/path/to/test/scan.csv",
            'cache_enabled': True
        },
        {  # Happy path case 2.
            'case': "long_name",
            'scan_id': 456,
            'scan_name': """
                This is a scan with a very long name that might
                test boundary conditions of the UI layout
            """,
            'file_path': "/path/to/documents/results/data.csv",
            'cache_enabled': True
        },
        {  # Happy path case 3.
            'case': "custom_extension",
            'scan_id': 789,
            'scan_name': "Custom Extension Scan",
            'file_path': "/data/exports/scan_results.data",
            'cache_enabled': False
        },
        {  # Edge case 1 -> empty scan name.
            'case': "empty_name",
            'scan_id': 321,
            'scan_name': "",
            'file_path': "/tmp/scan.csv",
            'cache_enabled': True
        },
        {  # Edge case 2 -> scan name with special chars.
            'case': "special_chars",
            'scan_id': 654,
            'scan_name': "Scan_With!@#$%^&*()_+{}|:<>?~`-=[]\\;',./",
            'file_path': "/home/user/Documents/Scans/special_file!@#.csv",
            'cache_enabled': False
        },
        {  # Edge case 3 -> really larger scan_id.
            'case': "very_large_id",
            'scan_id': 9999999999,
            'scan_name': "Large ID Test",
            'file_path': "/scans/test.csv",
            'cache_enabled': True
        }
    ])
    def sample_scan_data(self, request):
        """
        Fixture providing various sample scan data for
        both happy paths and edge cases.

        Happy path cases:
        - standard_scan: A typical scan with normal values
        - long_name: Tests UI with a very long scan name
        - custom_extension: Uses a non-standard file extension

        Edge cases:
        - empty_name: Tests handling of empty scan names
        - special_chars: Tests handling of special characters in name and path
        - very_large_id: Tests handling of extremely large ID values
        """
        return request.param

    def test_initialization(self, app, sample_scan_data):
        """
        Test that the EditScanDialog initializes correctly with provided data.

        This function tests (for each test case):
        1. The dialog's title is "Edit Scan".
        2. The following internal properties match the input data.
            a. scan_id.
            b. scan_name.
            c. file_path.
            d. cache_enabled.
        3. All UI elements display the correct initial values:
            a. scan_name_edit text matches the provided scan_name
            b. file_path_edit text matches the provided file_path
            c. cache_button text shows "Enabled" or "Disabled"
            based on cache_enabled value.
        """
        dialog = EditScanDialog(
            sample_scan_data['scan_id'],
            sample_scan_data['scan_name'],
            sample_scan_data['file_path'],
            sample_scan_data['cache_enabled']
        )

        test_case = sample_scan_data['case']

        assert [  # Test 1.
            dialog.windowTitle() == "Edit Scan",
            "Window title incorrect for case: {test_case}"
        ]
        assert [  # Test 2a.
            dialog.scan_id == sample_scan_data['scan_id'],
            f"scan_id mismatch for case: {test_case}"
        ]
        assert [  # Test 2b.
            dialog.scan_name == sample_scan_data['scan_name'],
            f"scan_name mismatch for case: {test_case}"
        ]
        assert [  # Test 2c.
            dialog.file_path == sample_scan_data['file_path'],
            f"file_path mismatch for case: {test_case}"
        ]
        assert [  # Test 2d.
            dialog.cache_enabled == sample_scan_data['cache_enabled'],
            f"cache_enabled mismatch for case: {test_case}"
        ]

        assert [  # Test 3a.
            dialog.scan_name_edit.text() == sample_scan_data['scan_name'],
            f"scan_name_edit text mismatch for case: {test_case}"
        ]
        assert [  # Test 3b.
            dialog.file_path_edit.text() == sample_scan_data['file_path'],
            f"file_path_edit text mismatch for case: {test_case}"
        ]

        cache_enabled = sample_scan_data['cache_enabled']
        expected_button_text = "Enabled" if cache_enabled else "Disabled"

        assert [  # Test 3c.
            dialog.cache_button.text() == expected_button_text,
            f"cache_button text mismatch for case: {test_case}"
        ]

    def test_toggle_cache(self, app, sample_scan_data):
        """
        Test that the cache toggle works correctly.

        This function tests (for each test case):
        1. The initial cache state matches the input data.
            a. The cache_enabled property matches the sample data.
            b. The cache_button text shows "Enabled" or "Disabled" accordingly.
        2. After first toggle:
            a. The cache_enabled property flips to the opposite state.
            b. The cache_button text updates to reflect the new state.
        3. After second toggle:
            a. The cache_enabled property returns to its original state.
            b. The cache_button text returns to its original value.
        """
        dialog = EditScanDialog(
            sample_scan_data['scan_id'],
            sample_scan_data['scan_name'],
            sample_scan_data['file_path'],
            sample_scan_data['cache_enabled']
        )

        test_case = sample_scan_data['case']

        initial_state = sample_scan_data['cache_enabled']
        expected_initial_text = "Enabled" if initial_state else "Disabled"

        assert [  # Test 1a.
            dialog.cache_enabled is initial_state,
            f"Initial cache state incorrect for case: {test_case}"
        ]
        assert [  # Test 1b.
            dialog.cache_button.text() == expected_initial_text,
            f"Initial button text incorrect for case: {test_case}"
        ]

        dialog.cache_button.click()
        new_state = not initial_state
        expected_new_text = "Enabled" if new_state else "Disabled"

        assert [  # Test 2a.
            dialog.cache_enabled is new_state,
            f"First toggle failed for case: {test_case}"
        ]
        assert [  # Test 2b.
            dialog.cache_button.text() == expected_new_text,
            f"Button text after first toggle incorrect for case: {test_case}"
        ]

        dialog.cache_button.click()

        assert [  # Test 3a.
            dialog.cache_enabled is initial_state,
            f"Second toggle failed for case: {test_case}"
        ]
        assert [  # Test 3b.
            dialog.cache_button.text() == expected_initial_text,
            f"Button text after second toggle incorrect for case: {test_case}"
        ]

    @pytest.fixture
    def fixed_scan_data(self):
        """A fixture for tests where only 1 sample is needed."""
        return {
            'scan_id': 123,
            'scan_name': "Test Scan",
            'file_path': "/path/to/test/scan.csv",
            'cache_enabled': True
        }

    def test_accept(self, app, fixed_scan_data, monkeypatch):
        """
        Test that the OK button works correctly.

        This function tests:
        1.The accept method of the dialog is called when OK button is clicked.
        """
        dialog = EditScanDialog(
            fixed_scan_data['scan_id'],
            fixed_scan_data['scan_name'],
            fixed_scan_data['file_path'],
            fixed_scan_data['cache_enabled']
        )

        accept_called = False

        def mock_accept():
            nonlocal accept_called
            accept_called = True

        monkeypatch.setattr(dialog, "accept", mock_accept)

        dialog.ok_button.click()

        assert [  # Test 1.
            accept_called is True,
            "Dialog accept method was not called when OK button was clicked"
        ]

    def test_reject(self, app, fixed_scan_data, monkeypatch):
        """
        Test that the Cancel button works correctly.

        This function tests:
        1. Reject method of the dialog is called when cancel button is clicked.
        """
        dialog = EditScanDialog(
            fixed_scan_data['scan_id'],
            fixed_scan_data['scan_name'],
            fixed_scan_data['file_path'],
            fixed_scan_data['cache_enabled']
        )

        reject_called = False

        def mock_reject():
            nonlocal reject_called
            reject_called = True

        monkeypatch.setattr(dialog, "reject", mock_reject)

        dialog.cancel_button.click()

        assert [  # Test 1.
            reject_called is True,
            "Dialog reject method wasn't called when Cancel button was clicked"
        ]

    def test_browse_file(self, app, fixed_scan_data, mock_file_dialog):
        """
        Test that the file browser works correctly.

        This function tests:
        1. When Browse button is clicked:
            a. The QFileDialog is opened and a new path is selected.
            b. The file_path_edit QLineEdit is updated with the new path.
            c. The new path is different from the original path.
        """
        dialog = EditScanDialog(
            fixed_scan_data['scan_id'],
            fixed_scan_data['scan_name'],
            fixed_scan_data['file_path'],
            fixed_scan_data['cache_enabled']
        )

        original_path = dialog.file_path_edit.text()

        dialog.browse_button.click()

        new_path = "/path/to/test/file.csv"

        assert [  # Test 1a & 1b.
            dialog.file_path_edit.text() == new_path,
            "File path was not updated to the new path from file dialog"
        ]
        assert [  # Test 1c.
            dialog.file_path_edit.text() != original_path,
            "File path was not changed from original path"
        ]


# TESTS FOR GeneralErrorDialog #


class TestGeneralErrorDialog:
    def test_initialization(self, app):
        """
        Tests the GeneralErrorDialog initializes correctly with the error msg.

        This function tests:
        1. The window title is "Error".
        2. The error_message property matches the input message.
        3. The error message is displayed in a QLabel within the dialog.
        4. QPushButton (ok_button) exists.
        """
        error_message = "This is a test error message."
        dialog = GeneralErrorDialog(error_message)

        assert [  # Test 1.
            dialog.windowTitle() == "Error",
            f"Dialog title isn't 'Error', got {dialog.windowTitle()} instead."
        ]
        assert [  # Test 2.
            dialog.error_message == error_message,
            "Error message property doesn't match the provided message."
        ]

        labels = dialog.findChildren(QLabel)
        label_texts = [label.text() for label in labels]

        assert [  # Test 3.
            error_message in label_texts,
            "Error message not found in any QLabel within the dialog."
        ]

        assert [  # Test 4.
            hasattr(dialog, "ok_button"),
            "OK QPushButton widget wasn't found."
        ]

    def test_accept(self, app, monkeypatch):
        """
        Test that the OK button correctly closes the dialog.

        This function tests:
        1. The accept method of the dialog is called when OK button is clicked.
        """
        dialog = GeneralErrorDialog("Test error")

        accept_called = False

        def mock_accept():
            nonlocal accept_called
            accept_called = True

        monkeypatch.setattr(dialog, "accept", mock_accept)

        dialog.ok_button.click()

        assert [  # Test 1.
            accept_called is True,
            "Dialog accept method wasn't called when OK button was clicked."
        ]
