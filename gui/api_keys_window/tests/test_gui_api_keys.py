"""
This file contains unit tests for the gui_api_keys.py module.

The tests validate the API Keys window functionality:
1. test_api_keys_window_initialization -> tests window init and layout setup.
2. test_init_api_keys_summary -> tests the summary section initialization.
3. test_init_api_keys_section -> tests the API Keys section initialization.
4. test_open_add_api_key_dialog -> tests the add API key dialog functionality.
5. test_open_edit_api_key_dialog -> tests edit API key dialog functionality.
6. test_handle_checkbox_state_change -> tests checkbox state handling.
7. test_populate_api_keys_table -> tests table population with API key data.
8. test_edit_api_key -> tests the edit API key button functionality.
9. test_delete_api_key -> tests the delete API key button functionality.
"""
import pytest
from PyQt5.QtWidgets import (
    QApplication, QWidget,
    QVBoxLayout, QGroupBox, QTableWidget,
    QPushButton, QCheckBox
)
from PyQt5.QtCore import Qt
from unittest.mock import patch, MagicMock

from gui.api_keys_window.gui_api_keys import APIKeysWindow


@pytest.fixture(scope="session")
def app():
    """Fixture to create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # No explicit app.quit() here as it might affect other tests


@pytest.fixture
def mock_api_keys():
    """Fixture to provide mock API key data for testing."""
    return [
        {
            "id": 1,
            "key_name": "Test Key 1",
            "key_value": "test_value_123",
            "status": "Valid",
            "error_count": 0,
            "selected": 0
        },
        {
            "id": 2,
            "key_name": "Test Key 2",
            "key_value": "test_value_456",
            "status": "Invalid",
            "error_count": 2,
            "selected": 1
        }
    ]


@pytest.fixture
def api_keys_window(app, monkeypatch):
    """
    Fixture to create a mock APIKeysWindow with patched backend functions.

    This fixture:
    1. Patches all the backend functions to avoid database operations.
    2. Returns a usable APIKeysWindow instance for testing.
    """
    with patch(
        "gui.api_keys_window.gui_api_keys._get_all_api_key_data"
    ) as mock_all:
        with patch(
            "gui.api_keys_window.gui_api_keys."
            "integrate_window_styling"
        ) as _:
            with patch(
                "gui.api_keys_window.gui_api_keys."
                "integrate_summary_group_styling"
            ) as _:
                with patch(
                    "gui.api_keys_window.gui_api_keys."
                    "integrate_api_keys_group_styling"
                ) as _:
                    mock_all.return_value = []
                    window = APIKeysWindow()

                    # Ensure window doesn't actually show during tests
                    window.show = MagicMock()

                    try:
                        yield window
                    finally:
                        # More thorough cleanup
                        app.processEvents()  # Process any pending events
                        window.close()
                        window.deleteLater()  # Mark for deletion
                        app.processEvents()  # Process the deleteLater event


class TestAPIKeysWindow:
    """Tests for the APIKeysWindow class."""

    def test_api_keys_window_initialization(self, api_keys_window):
        """
        Tests that APIKeysWindow initializes correctly.

        This test should:
        1. Verify central widget is set.
        2. Verify main layout is a QVBoxLayout.
        3. Verify API Keys Summary group exists.
        4. Verify API Keys table group exists.
        5. Verify styles are applied.
        """
        assert isinstance(api_keys_window.central_widget, QWidget)
        assert isinstance(api_keys_window.layout, QVBoxLayout)
        assert isinstance(api_keys_window.api_keys_summary_group, QGroupBox)
        assert isinstance(api_keys_window.api_keys_group, QGroupBox)
        assert isinstance(api_keys_window.api_keys_table, QTableWidget)

    def test_init_api_keys_summary(self, api_keys_window):
        """
        Tests that the API Keys summary section initializes correctly.

        This test should:
        1. Verify the group box title is correct.
        2. Verify the group contains a summary label.
        3. Verify the summary text contains expected content.
        """
        group_box = api_keys_window.api_keys_summary_group
        assert group_box.title() == "API Keys Summary"

        # Find the summary label
        children = group_box.findChildren(QWidget)
        summary_labels = [
            c for c in children
            if hasattr(c, 'text') and 'API keys' in c.text()
        ]

        assert len(summary_labels) > 0
        summary_text = summary_labels[0].text()
        assert "API keys" in summary_text
        assert "select" in summary_text.lower()

    def test_init_api_keys_section(self, api_keys_window):
        """
        Tests that the API Keys section initializes correctly.

        This test should:
        1. Verify the group box title is correct.
        2. Verify the Add API Key button exists.
        3. Verify the API keys table exists with correct columns.
        """
        group_box = api_keys_window.api_keys_group
        assert group_box.title() == "API Keys"

        # Check Add API Key button
        assert isinstance(api_keys_window.add_api_key_button, QPushButton)
        assert api_keys_window.add_api_key_button.text() == "Add API Key"

        # Check table
        table = api_keys_window.api_keys_table
        assert isinstance(table, QTableWidget)
        assert table.columnCount() == 6

        # Check table headers
        headers = [
            table.horizontalHeaderItem(i).text()
            for i in range(table.columnCount())
        ]
        expected_headers = [
            "Select",
            "Key Name",
            "Key Value",
            "Status",
            "Edit",
            "Delete"
         ]
        assert headers == expected_headers

        # Verify edit triggers
        assert table.editTriggers() == QTableWidget.NoEditTriggers

    @patch("gui.api_keys_window.gui_api_keys.AddAPIKeyDialog")
    @patch("gui.api_keys_window.gui_api_keys._add_api_key")
    def test_open_add_api_key_dialog(
        self, mock_add_api_key, mock_dialog_class, api_keys_window
    ):
        """
        Tests opening the AddAPIKeyDialog and processing its result.

        This test should:
        1. Set up a mock dialog return object.
        2. Verify dialog execution & calling _add_api_key with correct params.
        3. Verify table population is called afterwards.
        """
        # Set up mock dialog and execution
        mock_dialog = MagicMock()
        mock_dialog.exec_.return_value = True
        mock_dialog.api_key_name_edit.text.return_value = "New Key"
        mock_dialog.api_key_value_edit.text.return_value = "new_value_123"
        mock_dialog_class.return_value = mock_dialog

        # Replace populate method to check it's called
        original_populate = api_keys_window.populate_api_keys_table
        populate_called = [False]

        def mock_populate():
            populate_called[0] = True

        api_keys_window.populate_api_keys_table = mock_populate

        # Call the tested method
        api_keys_window.open_add_api_key_dialog()

        # Verify dialog was created and executed
        mock_dialog_class.assert_called_once_with(api_keys_window)
        mock_dialog.exec_.assert_called_once()

        # Verify _add_api_key called with correct params
        mock_add_api_key.assert_called_once_with("New Key", "new_value_123")

        # Verify table was populated
        assert populate_called[0] is True

        # Restore original method
        api_keys_window.populate_api_keys_table = original_populate

    @patch("gui.api_keys_window.gui_api_keys._get_api_key_data")
    @patch("gui.api_keys_window.gui_api_keys.EditAPIKeyDialog")
    @patch("gui.api_keys_window.gui_api_keys._edit_api_key")
    def test_open_edit_api_key_dialog(
        self, mock_edit_api_key, mock_dialog_class, mock_get_api_key_data,
        api_keys_window
    ):
        """
        Tests opening the EditAPIKeyDialog and processing its result.

        This test should:
        1. Set up mock data returns and dialog behavior.
        2. Verify dialog creation with correct initial values.
        3. Verify _edit_api_key is called with the updated values.
        4. Verify table population is called on success.
        """
        # Set up mock API key data
        mock_key_data = {
            "key_name": "Test Key",
            "key_value": "test_value_123",
            "status": "Valid"
        }
        mock_get_api_key_data.return_value = mock_key_data

        # Set up mock dialog and execution
        mock_dialog = MagicMock()
        mock_dialog.exec_.return_value = True
        mock_dialog.key_name_edit.text.return_value = "Updated Key"
        mock_dialog.key_value_edit.text.return_value = "updated_value_123"
        mock_dialog.status = "Invalid"
        mock_dialog_class.return_value = mock_dialog

        # Set up mock _edit_api_key response
        mock_edit_api_key.return_value = (True, "Success")

        # Replace populate method to check it's called
        original_populate = api_keys_window.populate_api_keys_table
        populate_called = [False]

        def mock_populate():
            populate_called[0] = True

        api_keys_window.populate_api_keys_table = mock_populate

        # Call the tested method
        api_keys_window.open_edit_api_key_dialog(1)

        # Verify _get_api_key_data called correctly
        mock_get_api_key_data.assert_called_once_with(1)

        # Verify dialog was created with correct parameters
        mock_dialog_class.assert_called_once_with(
            1,
            "Test Key",
            "test_value_123",
            "Valid",
            api_keys_window
        )

        # Verify _edit_api_key called with updated values
        mock_edit_api_key.assert_called_once_with(
            1,
            "Updated Key",
            "updated_value_123",
            "Invalid"
        )

        # Verify table was populated
        assert populate_called[0] is True

        # Restore original method
        api_keys_window.populate_api_keys_table = original_populate

        # Test case where _edit_api_key fails
        mock_edit_api_key.return_value = (False, "Failed")
        populate_called[0] = False

        api_keys_window.open_edit_api_key_dialog(1)

        # Table should not be populated on failure
        assert populate_called[0] is False

    @patch("gui.api_keys_window.gui_api_keys._update_api_key_selected_field")
    def test_handle_checkbox_state_change(
        self, mock_update_field, api_keys_window
    ):
        """
        Tests the checkbox state change handler.

        This test should:
        1. Test checked state conversion to selected=1.
        2. Test unchecked state conversion to selected=0.
        """
        # Test checked state
        api_keys_window.handle_checkbox_state_change(1, Qt.Checked)
        mock_update_field.assert_called_once_with(1, 1)
        mock_update_field.reset_mock()

        # Test unchecked state
        api_keys_window.handle_checkbox_state_change(1, Qt.Unchecked)
        mock_update_field.assert_called_once_with(1, 0)

    @patch("gui.api_keys_window.gui_api_keys._get_all_api_key_data")
    @patch("gui.api_keys_window.gui_api_keys.integrate_api_keys_group_styling")
    def test_populate_api_keys_table(
        self, mock_styling, mock_get_all_api_key_data, api_keys_window,
        mock_api_keys
    ):
        """
        Tests the populate_api_keys_table method.

        This test should:
        1. Verify table rows are created for each API key.
        2. Verify CheckBox widgets are created in the first column.
        3. Verify text values are set correctly in key name and value cols.
        4. Verify button widgets are created for status, edit, and delete cols.
        5. Verify styling is applied to the table.
        """
        mock_get_all_api_key_data.return_value = mock_api_keys

        # Call the tested method
        api_keys_window.populate_api_keys_table()

        # Verify table was populated with correct number of rows
        assert api_keys_window.api_keys_table.rowCount() == 2

        # Get table widgets for each cell
        table = api_keys_window.api_keys_table

        # Verify checkbox containers in column 0
        for row in range(2):
            cell_widget = table.cellWidget(row, 0)
            assert cell_widget is not None
            checkbox = cell_widget.findChild(QCheckBox)
            assert checkbox is not None
            # Verify checkbox state matches 'selected' value
            expected = bool(mock_api_keys[row]["selected"])
            assert checkbox.isChecked() == expected

        # Verify text values in columns 1-2
        assert table.item(0, 1).text() == "Test Key 1"
        assert table.item(1, 1).text() == "Test Key 2"

        # Check key values are masked
        assert table.item(0, 2).text().startswith("********")
        assert table.item(1, 2).text().startswith("********")

        # Verify status buttons in column 3
        status_btn_0 = table.cellWidget(0, 3)
        status_btn_1 = table.cellWidget(1, 3)
        assert isinstance(status_btn_0, QPushButton)
        assert isinstance(status_btn_1, QPushButton)
        assert status_btn_0.text() == "Valid"
        assert status_btn_1.text() == "Invalid"
        assert not status_btn_0.isEnabled()
        assert not status_btn_1.isEnabled()

        # Verify edit buttons in column 4
        edit_btn_0 = table.cellWidget(0, 4)
        edit_btn_1 = table.cellWidget(1, 4)
        assert isinstance(edit_btn_0, QPushButton)
        assert isinstance(edit_btn_1, QPushButton)
        assert edit_btn_0.text() == "Edit"
        assert edit_btn_1.text() == "Edit"

        # Verify delete buttons in column 5
        delete_btn_0 = table.cellWidget(0, 5)
        delete_btn_1 = table.cellWidget(1, 5)
        assert isinstance(delete_btn_0, QPushButton)
        assert isinstance(delete_btn_1, QPushButton)
        assert delete_btn_0.text() == "Delete"
        assert delete_btn_1.text() == "Delete"

        # Verify styling was applied
        mock_styling.assert_called_once_with(api_keys_window)

    @patch(
     "gui.api_keys_window.gui_api_keys.APIKeysWindow.open_edit_api_key_dialog"
    )
    def test_edit_api_key(self, mock_open_dialog, api_keys_window):
        """
        Tests the edit_api_key method.

        This test should:
        1. Verify open_edit_api_key_dialog is called with the correct ID.
        """
        api_keys_window.edit_api_key(1)
        mock_open_dialog.assert_called_once_with(1)

    @patch("gui.api_keys_window.gui_api_keys._delete_api_key")
    def test_delete_api_key(self, mock_delete_api_key, api_keys_window):
        """
        Tests the delete_api_key method.

        This test should:
        1. Verify _delete_api_key is called with the correct ID.
        2. Verify table is repopulated on success.
        3. Verify table is not repopulated on failure.
        """
        # Set up mock return values
        mock_delete_api_key.return_value = (True, "Success")

        # Replace populate method to check it's called
        original_populate = api_keys_window.populate_api_keys_table
        populate_called = [False]

        def mock_populate():
            populate_called[0] = True

        api_keys_window.populate_api_keys_table = mock_populate

        # Call the tested method
        api_keys_window.delete_api_key(1)

        # Verify _delete_api_key called with correct ID
        mock_delete_api_key.assert_called_once_with(1)

        # Verify table was populated on success
        assert populate_called[0] is True

        # Test failure case
        mock_delete_api_key.reset_mock()
        mock_delete_api_key.return_value = (False, "Failed")
        populate_called[0] = False

        api_keys_window.delete_api_key(2)

        # Verify _delete_api_key called with correct ID
        mock_delete_api_key.assert_called_once_with(2)

        # Verify table was not populated on failure
        assert populate_called[0] is False

        # Restore original method
        api_keys_window.populate_api_keys_table = original_populate


def test_button_click_handlers(api_keys_window):
    """
    Tests the button click handlers in the table.

    This test should:
    1. Mock the edit_api_key and delete_api_key methods.
    2. Trigger button clicks and verify handlers are called with correct IDs.
    """
    # Replace handler methods with mocks
    original_edit = api_keys_window.edit_api_key
    original_delete = api_keys_window.delete_api_key

    edit_calls = []
    delete_calls = []

    api_keys_window.edit_api_key = lambda id: edit_calls.append(id)
    api_keys_window.delete_api_key = lambda id: delete_calls.append(id)

    # Need to populate the table with some data
    with patch(
        "gui.api_keys_window.gui_api_keys._get_all_api_key_data"
    ) as mock_get_all:
        with patch(
            "gui.api_keys_window.gui_api_keys.integrate_api_keys_group_styling"
        ):
            # Set up mock API key data
            mock_get_all.return_value = [
                {
                    "id": 1,
                    "key_name": "Test Key 1",
                    "key_value": "test_value_123",
                    "status": "Valid",
                    "error_count": 0,
                    "selected": 0
                },
                {
                    "id": 2,
                    "key_name": "Test Key 2",
                    "key_value": "test_value_456",
                    "status": "Invalid",
                    "error_count": 2,
                    "selected": 1
                }
            ]

            # Populate the table
            api_keys_window.populate_api_keys_table()

            # Test edit button clicks
            table = api_keys_window.api_keys_table
            edit_btn_0 = table.cellWidget(0, 4)
            edit_btn_1 = table.cellWidget(1, 4)

            edit_btn_0.click()
            edit_btn_1.click()

            assert edit_calls == [1, 2]

            # Test delete button clicks
            delete_btn_0 = table.cellWidget(0, 5)
            delete_btn_1 = table.cellWidget(1, 5)

            delete_btn_0.click()
            delete_btn_1.click()

            assert delete_calls == [1, 2]

    # Restore original methods
    api_keys_window.edit_api_key = original_edit
    api_keys_window.delete_api_key = original_delete


@patch("gui.api_keys_window.gui_api_keys._update_api_key_selected_field")
def test_checkbox_handler(mock_update_field, api_keys_window):
    """
    Tests the checkbox state change handler through direct interaction.

    This test should:
    1. Populate the table with mock data.
    2. Find the checkbox widgets and trigger state changes.
    3. Verify _update_api_key_selected_field is called with correct values.
    """
    # Need to populate the table with some data
    with patch(
        "gui.api_keys_window.gui_api_keys._get_all_api_key_data"
    ) as mock_get_all:
        with patch(
            "gui.api_keys_window.gui_api_keys.integrate_api_keys_group_styling"
        ):
            # Set up mock API key data
            mock_get_all.return_value = [
                {
                    "id": 1,
                    "key_name": "Test Key 1",
                    "key_value": "test_value_123",
                    "status": "Valid",
                    "error_count": 0,
                    "selected": 0
                }
            ]

            # Populate the table
            api_keys_window.populate_api_keys_table()

            # Find the checkbox widget
            table = api_keys_window.api_keys_table
            cell_widget = table.cellWidget(0, 0)
            checkbox = cell_widget.findChild(QCheckBox)

            # Test checking the checkbox
            checkbox.setChecked(True)
            mock_update_field.assert_called_once_with(1, 1)
            mock_update_field.reset_mock()

            # Test unchecking the checkbox
            checkbox.setChecked(False)
            mock_update_field.assert_called_once_with(1, 0)
