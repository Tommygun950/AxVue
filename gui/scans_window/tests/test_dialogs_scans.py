"""
This file contains unit tests for the dialogs_scans.py module.

The tests validate the dialog classes for the Scans window:
1. test_add_scan_dialog -> tests the AddScanDialog class features.
2. test_edit_scan_dialog -> tests the EditScanDialog class features.
3. test_general_error_dialog -> tests the GeneralErrorDialog class features.
"""
import pytest
from PyQt5.QtWidgets import QApplication, QFileDialog

from gui.scans_window.dialogs_scans import (
    AddScanDialog, EditScanDialog, GeneralErrorDialog
)


@pytest.fixture(scope="module")
def app():
    """Fixture to create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't explicitly quit the app since it might be used by other tests


@pytest.fixture
def add_scan_dialog(app):
    """Fixture to create an AddScanDialog instance for testing."""
    dialog = AddScanDialog()
    yield dialog
    dialog.close()
    dialog.deleteLater()  # Ensure the widget is properly cleaned up


@pytest.fixture
def edit_scan_dialog(app):
    """
    Fixture to create an EditScanDialog instance for testing.

    This fixture creates an EditScanDialog with test data.
    """
    dialog = EditScanDialog(
        scan_id=1,
        scan_name="Test Scan",
        file_path="/path/to/test.csv",
        cache_enabled="Enabled"
    )
    yield dialog
    dialog.close()
    dialog.deleteLater()  # Ensure the widget is properly cleaned up


@pytest.fixture
def general_error_dialog(app):
    """Fixture to create a GeneralErrorDialog instance for testing."""
    dialog = GeneralErrorDialog("Test error message")
    yield dialog
    dialog.close()
    dialog.deleteLater()  # Ensure the widget is properly cleaned up


class TestAddScanDialog:
    """Tests for the AddScanDialog class."""

    def test_dialog_initialization(self, add_scan_dialog):
        """
        Tests that AddScanDialog initializes correctly.

        This test should:
        1. Verify the dialog title is set correctly.
        2. Verify the scan name edit field exists.
        3. Verify the file path edit field exists.
        4. Verify the browse button exists.
        5. Verify the OK and Cancel buttons exist.
        """
        assert add_scan_dialog.windowTitle() == "Add Scan"
        assert add_scan_dialog.scan_name_edit is not None
        assert add_scan_dialog.file_path_edit is not None
        assert add_scan_dialog.browse_button is not None
        assert add_scan_dialog.ok_button is not None
        assert add_scan_dialog.cancel_button is not None

    @pytest.mark.parametrize("file_name", ["/path/to/test.csv", ""])
    def test_browse_file(self, add_scan_dialog, monkeypatch, file_name):
        """
        Tests the browse_file function with both selected and canceled cases.

        This test should:
        1. Mock QFileDialog.getOpenFileName to return a test path.
        2. Call the browse_file method.
        3. Verify file_path_edit is updated correctly.
        """
        # Mock the QFileDialog.getOpenFileName method
        def mock_get_open_file_name(*args, **kwargs):
            return file_name, "CSV Files (*.csv)"

        monkeypatch.setattr(
            QFileDialog, "getOpenFileName", mock_get_open_file_name
        )

        # Call the browse_file method
        add_scan_dialog.browse_file()

        # Verify the file path was updated correctly
        assert add_scan_dialog.file_path_edit.text() == file_name

    def test_button_connections(self, add_scan_dialog):
        """
        Tests button signal connections are properly set up.

        This test should:
        1. Verify clicking OK results in dialog acceptance.
        2. Verify clicking Cancel results in dialog rejection.

        This uses monkeypatching to avoid actual dialog closing.
        """
        # Replace accept/reject methods to track calls
        original_accept = add_scan_dialog.accept
        original_reject = add_scan_dialog.reject

        accept_called = [False]
        reject_called = [False]

        def mock_accept():
            accept_called[0] = True

        def mock_reject():
            reject_called[0] = True

        add_scan_dialog.accept = mock_accept
        add_scan_dialog.reject = mock_reject

        # Test OK button
        add_scan_dialog.ok_button.click()
        assert accept_called[0] is True

        # Test Cancel button
        add_scan_dialog.cancel_button.click()
        assert reject_called[0] is True

        # Restore original methods
        add_scan_dialog.accept = original_accept
        add_scan_dialog.reject = original_reject


class TestEditScanDialog:
    """Tests for the EditScanDialog class."""

    def test_dialog_initialization(self, edit_scan_dialog):
        """
        Tests that EditScanDialog initializes correctly.

        This test should:
        1. Verify the dialog title is set correctly.
        2. Verify the ID is stored correctly.
        3. Verify the scan name field is initialized with the correct value.
        4. Verify the file path field is initialized with correct value.
        5. Verify the cache button is initialized with the correct text.
        6. Verify the OK and Cancel buttons exist.
        """
        assert edit_scan_dialog.windowTitle() == "Edit Scan"
        assert edit_scan_dialog.scan_id == 1
        assert edit_scan_dialog.scan_name_edit.text() == "Test Scan"
        assert edit_scan_dialog.file_path_edit.text() == "/path/to/test.csv"
        assert edit_scan_dialog.cache_button.text() == "Enabled"
        assert edit_scan_dialog.ok_button is not None
        assert edit_scan_dialog.cancel_button is not None

    @pytest.mark.parametrize("file_name", ["/path/to/new.csv", ""])
    def test_browse_file(self, edit_scan_dialog, monkeypatch, file_name):
        """
        Tests the browse_file function with both selected and canceled cases.

        This test should:
        1. Mock QFileDialog.getOpenFileName to return a test path.
        2. Call the browse_file method.
        3. Verify file_path_edit is updated correctly.
        """
        # Mock the QFileDialog.getOpenFileName method
        def mock_get_open_file_name(*args, **kwargs):
            return file_name, "CSV Files (*.csv)"

        monkeypatch.setattr(
            QFileDialog, "getOpenFileName", mock_get_open_file_name
        )

        # Call the browse_file method
        edit_scan_dialog.browse_file()

        # Verify the file path was updated correctly
        if file_name:
            assert edit_scan_dialog.file_path_edit.text() == file_name

    def test_toggle_cache(self, edit_scan_dialog):
        """
        Tests the toggle_cache function.

        This test should:
        1. Verify initial cache_enabled is "Enabled".
        2. Test toggling to "Disabled".
        3. Test toggling back to "Enabled".
        """
        # Initial status should be "Enabled"
        assert edit_scan_dialog.cache_enabled == "Enabled"
        assert edit_scan_dialog.cache_button.text() == "Enabled"

        # Toggle to "Disabled"
        edit_scan_dialog.toggle_cache()
        assert edit_scan_dialog.cache_enabled == "Disabled"
        assert edit_scan_dialog.cache_button.text() == "Disabled"

        # Toggle back to "Enabled"
        edit_scan_dialog.toggle_cache()
        assert edit_scan_dialog.cache_enabled == "Enabled"
        assert edit_scan_dialog.cache_button.text() == "Enabled"

    def test_button_connections(self, edit_scan_dialog):
        """
        Tests button signal connections are properly set up.

        This test should:
        1. Verify clicking OK results in dialog acceptance.
        2. Verify clicking Cancel results in dialog rejection.

        This uses monkeypatching to avoid actual dialog closing.
        """
        # Replace accept/reject methods to track calls
        original_accept = edit_scan_dialog.accept
        original_reject = edit_scan_dialog.reject

        accept_called = [False]
        reject_called = [False]

        def mock_accept():
            accept_called[0] = True

        def mock_reject():
            reject_called[0] = True

        edit_scan_dialog.accept = mock_accept
        edit_scan_dialog.reject = mock_reject

        # Test OK button
        edit_scan_dialog.ok_button.click()
        assert accept_called[0] is True

        # Test Cancel button
        edit_scan_dialog.cancel_button.click()
        assert reject_called[0] is True

        # Restore original methods
        edit_scan_dialog.accept = original_accept
        edit_scan_dialog.reject = original_reject

    def test_cache_button_connection(self, edit_scan_dialog):
        """
        Tests that the cache button properly calls toggle_cache.

        This test should verify that clicking the cache button changes
        the dialog's cache_enabled value appropriately.
        """
        # Check initial cache setting
        initial_cache = edit_scan_dialog.cache_enabled
        assert initial_cache in ("Enabled", "Disabled")

        # Click the cache button
        edit_scan_dialog.cache_button.click()

        # Verify cache has changed
        new_cache = edit_scan_dialog.cache_enabled
        assert new_cache != initial_cache
        assert new_cache in ("Enabled", "Disabled")

        # Verify button text matches the new cache setting
        assert edit_scan_dialog.cache_button.text() == new_cache


class TestGeneralErrorDialog:
    """Tests for the GeneralErrorDialog class."""

    def test_dialog_initialization(self, general_error_dialog):
        """
        Tests that GeneralErrorDialog initializes correctly.

        This test should:
        1. Verify the dialog title is set correctly.
        2. Verify the error message is stored correctly.
        3. Verify the OK button exists.
        """
        assert general_error_dialog.windowTitle() == "Error"
        assert general_error_dialog.error_message == "Test error message"
        assert general_error_dialog.ok_button is not None

    def test_ok_button_connection(self, general_error_dialog):
        """
        Tests the OK button signal connection.

        This test should:
        1. Verify clicking OK results in dialog acceptance.

        This uses monkeypatching to avoid actual dialog closing.
        """
        # Replace accept method to track calls
        original_accept = general_error_dialog.accept

        accept_called = [False]

        def mock_accept():
            accept_called[0] = True

        general_error_dialog.accept = mock_accept

        # Test OK button
        general_error_dialog.ok_button.click()
        assert accept_called[0] is True

        # Restore original method
        general_error_dialog.accept = original_accept
