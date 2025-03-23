"""
This file contains unit tests for the dialogs_api_keys.py module.

The tests validate the dialog classes for the API Keys window:
1. test_add_api_key_dialog -> tests the AddAPIKeyDialog class features.
2. test_edit_api_key_dialog -> tests the EditAPIKeyDialog class features.
3. test_general_error_dialog -> tests the GeneralErrorDialog class features.
"""
import pytest
from PyQt5.QtWidgets import QApplication, QLineEdit

from gui.api_keys_window.dialogs_api_keys import (
    AddAPIKeyDialog, EditAPIKeyDialog, GeneralErrorDialog
)


@pytest.fixture(scope="session")
def app():
    """Fixture to create QApplication instance for tests."""
    app = QApplication([])
    yield app


@pytest.fixture
def add_api_key_dialog(app):
    """Fixture to create an AddAPIKeyDialog instance for testing."""
    dialog = AddAPIKeyDialog()
    yield dialog
    dialog.close()


@pytest.fixture
def edit_api_key_dialog(app):
    """
    Fixture to create an EditAPIKeyDialog instance for testing.

    This fixture creates an EditAPIKeyDialog with test data.
    """
    dialog = EditAPIKeyDialog(
        id=1,
        key_name="Test Key",
        key_value="test_value_123",
        status="Valid"
    )
    yield dialog
    dialog.close()


@pytest.fixture
def general_error_dialog(app):
    """Fixture to create a GeneralErrorDialog instance for testing."""
    dialog = GeneralErrorDialog("Test error message")
    yield dialog
    dialog.close()


class TestAddAPIKeyDialog:
    """Tests for the AddAPIKeyDialog class."""

    def test_dialog_initialization(self, add_api_key_dialog):
        """
        Tests that AddAPIKeyDialog initializes correctly.

        This test should:
        1. Verify the dialog title is set correctly.
        2. Verify the API key name edit field exists.
        3. Verify the API key value edit field exists.
        4. Verify the OK and Cancel buttons exist.
        """
        assert add_api_key_dialog.windowTitle() == "Add API Key"
        assert add_api_key_dialog.api_key_name_edit is not None
        assert add_api_key_dialog.api_key_value_edit is not None
        assert add_api_key_dialog.ok_button is not None
        assert add_api_key_dialog.cancel_button is not None

    def test_key_value_field_obscured(self, add_api_key_dialog):
        """
        Tests that the key value field has obscured text.

        This test should:
        1. Verify the key value QLineEdit has its echo mode set to Password.
        """
        assert (
            add_api_key_dialog.api_key_value_edit.echoMode() ==
            QLineEdit.Password
        )

    def test_button_connections(self, add_api_key_dialog):
        """
        Tests button signal connections are properly set up.

        This test should:
        1. Verify clicking OK results in dialog acceptance.
        2. Verify clicking Cancel results in dialog rejection.

        This uses monkeypatching to avoid actual dialog closing.
        """
        # Replace accept/reject methods to track calls
        original_accept = add_api_key_dialog.accept
        original_reject = add_api_key_dialog.reject

        accept_called = [False]
        reject_called = [False]

        def mock_accept():
            accept_called[0] = True

        def mock_reject():
            reject_called[0] = True

        add_api_key_dialog.accept = mock_accept
        add_api_key_dialog.reject = mock_reject

        # Test OK button
        add_api_key_dialog.ok_button.click()
        assert accept_called[0] is True

        # Test Cancel button
        add_api_key_dialog.cancel_button.click()
        assert reject_called[0] is True

        # Restore original methods
        add_api_key_dialog.accept = original_accept
        add_api_key_dialog.reject = original_reject


class TestEditAPIKeyDialog:
    """Tests for the EditAPIKeyDialog class."""

    def test_dialog_initialization(self, edit_api_key_dialog):
        """
        Tests that EditAPIKeyDialog initializes correctly.

        This test should:
        1. Verify the dialog title is set correctly.
        2. Verify the ID is stored correctly.
        3. Verify the API key name field is initialized with the correct value.
        4. Verify the API key value field is initialized with correct value.
        5. Verify the status button is initialized with the correct text.
        6. Verify the OK and Cancel buttons exist.
        """
        assert edit_api_key_dialog.windowTitle() == "Edit API Key"
        assert edit_api_key_dialog.id == 1
        assert edit_api_key_dialog.key_name_edit.text() == "Test Key"
        assert edit_api_key_dialog.key_value_edit.text() == "test_value_123"
        assert edit_api_key_dialog.status_button.text() == "Valid"
        assert edit_api_key_dialog.ok_button is not None
        assert edit_api_key_dialog.cancel_button is not None

    def test_key_value_field_obscured(self, edit_api_key_dialog):
        """
        Tests that the key value field has obscured text.

        This test should:
        1. Verify the key value QLineEdit has its echo mode set to Password.
        """
        assert (
            edit_api_key_dialog.key_value_edit.echoMode() ==
            QLineEdit.Password
        )

    def test_toggle_status(self, edit_api_key_dialog):
        """
        Tests the toggle_status function.

        This test should:
        1. Verify initial status is "Valid".
        2. Test toggling to "Invalid".
        3. Test toggling back to "Valid".
        """
        # Initial status should be "Valid"
        assert edit_api_key_dialog.status == "Valid"
        assert edit_api_key_dialog.status_button.text() == "Valid"

        # Toggle to "Invalid"
        edit_api_key_dialog.toggle_status()
        assert edit_api_key_dialog.status == "Invalid"
        assert edit_api_key_dialog.status_button.text() == "Invalid"

        # Toggle back to "Valid"
        edit_api_key_dialog.toggle_status()
        assert edit_api_key_dialog.status == "Valid"
        assert edit_api_key_dialog.status_button.text() == "Valid"

    def test_button_connections(self, edit_api_key_dialog):
        """
        Tests button signal connections are properly set up.

        This test should:
        1. Verify clicking OK results in dialog acceptance.
        2. Verify clicking Cancel results in dialog rejection.

        This uses monkeypatching to avoid actual dialog closing.
        """
        # Replace accept/reject methods to track calls
        original_accept = edit_api_key_dialog.accept
        original_reject = edit_api_key_dialog.reject

        accept_called = [False]
        reject_called = [False]

        def mock_accept():
            accept_called[0] = True

        def mock_reject():
            reject_called[0] = True

        edit_api_key_dialog.accept = mock_accept
        edit_api_key_dialog.reject = mock_reject

        # Test OK button
        edit_api_key_dialog.ok_button.click()
        assert accept_called[0] is True

        # Test Cancel button
        edit_api_key_dialog.cancel_button.click()
        assert reject_called[0] is True

        # Restore original methods
        edit_api_key_dialog.accept = original_accept
        edit_api_key_dialog.reject = original_reject

    def test_status_button_connection(self, edit_api_key_dialog):
        """
        Tests that the status button properly calls toggle_status.

        This test should verify that clicking the status button changes
        the dialog's status value appropriately.
        """
        # Check initial status
        initial_status = edit_api_key_dialog.status
        assert initial_status in ("Valid", "Invalid")

        # Click the status button
        edit_api_key_dialog.status_button.click()

        # Verify status has changed
        new_status = edit_api_key_dialog.status
        assert new_status != initial_status
        assert new_status in ("Valid", "Invalid")

        # Verify button text matches the new status
        assert edit_api_key_dialog.status_button.text() == new_status


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
