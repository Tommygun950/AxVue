"""
This file is used to construct the API Keys window in the GUI.

The APIKeysWindow seperates functions by the following:
1. Initializing GUI elements, layouts, & widgets:
    a. __init__ -> initializes the API keys window.
    b. init_api_keys_summary -> inits layout for summary group.
    c. init_api_keys_section -> inits layout for table & buttons.
2. Opening dialogs:
    a. open_add_api_key_dialog -> opens AddAPIKeyDialog & calls _add_api_key
    & repopulates the GUI table.
    b. open_edit_api_key_dialog -> opens EditAPIKeyDialog & calls _edit_api_key
    & repopulates the GUI table.
3. Displaying backend data:
    a. handle_checkbox_state_change -> toggles selected status in the db & GUI.
    b. populate_api_keys_table -> adds nvd_api_key data to GUI table.
4. Using buttons:
    a. edit_api_key -> opens EditAPIKeyDialog when Edit button is pressed.
    b. delete_api_key ->  calls _delete_api_key when Delete button is pressed.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QLabel, QHBoxLayout, QGroupBox,
    QCheckBox, QTableWidgetItem,
)
from gui.api_keys_window.dialogs_api_keys import (
    AddAPIKeyDialog, EditAPIKeyDialog
)
from gui.api_keys_window.backend_api_keys import (
    _add_api_key, _edit_api_key,
    _delete_api_key, _update_api_key_selected_status,
    _get_all_api_key_data, _get_api_key_data
)
from gui.api_keys_window.style_api_keys import (
    integrate_window_styling,
    integrate_summary_group_styling,
    integrate_api_keys_group_styling
)


class APIKeysWindow(QMainWindow):
    """Window for API Keys page."""
    # FUNCTIONS FOR INITIALIZING GUI ELEMENTS/LAYOUTS/WIDGETS #
    def __init__(self):
        """
        This function initializes the api keys window & features.

        This function should:
        1. Creates a central widget/layout with the following:
            a. A QVBoxLayout wiht the following:
                1. The API Keys Summary.
                2. The API Keys buttons & table section.
        2. Integrates the styling for the following:
            a. The entire window.
            b. The Summary QGroupBox.
            c. The API Keys Section.
        3. Populates the API Keys table with db data.
        """
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_api_keys_summary()
        self.init_api_keys_section()

        integrate_window_styling(self)

        integrate_summary_group_styling(self)
        integrate_api_keys_group_styling(self)  # First call to color buttons.

        self.populate_api_keys_table()

        integrate_api_keys_group_styling(self)  # Second call to center text.

    def init_api_keys_summary(self):
        """
        Initializes the contents of the API Keys summary page.

        This function should:
        1. Create a QVBoxLayout with the following:
            a. QGroupBox for the title called "API Keys Summary".
            b. QLabel containing the summary text/instructions.
        2. Add the QVBoxLayout to the main layout.
        """
        self.api_keys_summary_group = QGroupBox("API Keys Summary")
        group_layout = QVBoxLayout(self.api_keys_summary_group)

        summary_text = (
            "Step 2: Add your NVD API keys to the table and select the "
            "checkbox for the keys you want to include in your report. "
        )

        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        group_layout.addWidget(summary_label)

        self.layout.addWidget(self.api_keys_summary_group)

    def init_api_keys_section(self):
        """
        Initializes the API keys section which contains the buttons
        and the API Keys table.

        This function should:
        1. Create a QVBoxLayout with the following:
            a. QGroupBox for the section title labeled "API Keys".
            b. Initialize the button layout.
            c. initialize the API Keys table.
        2. Add the QVBoxLayout to the main layout.
        """
        self.api_keys_group = QGroupBox("API Keys")
        api_keys_layout = QVBoxLayout(self.api_keys_group)

        def init_button_layout(self):
            """
            Initializes the button layout above the API Key table.

            This function should:
            1. Create a QHBoxLayout containing:
                a. "Add API Key" QPushbutton that opens Add API Key dialog.
            2. Add the QHBoxLayout to the API Keys section layout.
            """
            button_layout = QHBoxLayout()

            self.add_api_key_button = QPushButton("Add API Key")
            self.add_api_key_button.clicked.connect(
                self.open_add_api_key_dialog
            )
            button_layout.addWidget(self.add_api_key_button)

            api_keys_layout.addLayout(button_layout)

        def init_api_keys_table(self):
            """
            Initializes the table for the API keys.

            This function should:
            1. Create a QTableWidget with the following attributes:
                a. The following columns/headers:
                    1. Select -> checkbox for selecting API keys in the report.
                    2. Key Name -> text for the key name.
                    3. Key Value -> masked text for the key value.
                    4. Status -> "Valid" or "Invalid" base on the key's status.
                    5. Edit -> button for editing a particular API key.
                    6. Delete -> button for deleting a particular API key.
            """
            self.api_keys_table = QTableWidget()
            self.api_keys_table.setColumnCount(6)

            self.api_keys_table.setHorizontalHeaderLabels([
                "Select",
                "Key Name",
                "Key Value",
                "Status",
                "Edit",
                "Delete"
            ])

            self.api_keys_table.verticalHeader().setVisible(False)
            self.api_keys_table.setEditTriggers(QTableWidget.NoEditTriggers)

            header = self.api_keys_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

            self.api_keys_table.setColumnWidth(0, 70)

            api_keys_layout.addWidget(self.api_keys_table)

        init_button_layout(self)
        init_api_keys_table(self)

        self.layout.addWidget(self.api_keys_group)

    # FUNCTIONS FOR OPENING DIALOGS FROM DIALOGS_API_KEYS.PY #
    def open_add_api_key_dialog(self):
        """
        Opens the AddAPIKeyDialog & processes user-entered data.

        This function should:
        1. Create the AddAPIKeyDialog.
        2. Execute the dialog & store the following user-entered data:
            a. key_name.
            b. key_value.
        3. Call _add_api_key to add API Key to the db.
        4. Repopulate the API Keys table to show most current API keys.
        """
        dialog = AddAPIKeyDialog(self)
        if dialog.exec_():
            key_name = dialog.api_key_name_edit.text()
            key_value = dialog.api_key_value_edit.text()

            _add_api_key(key_name, key_value)
            self.populate_api_keys_table()

    def open_edit_api_key_dialog(self, id):
        """
        Opens the EditAPIKeyDialog & and updates the specific API Key
        with the new user-entered data.

        This function should:
        1. Retrieve all data for the specifiec API key.
        2. If the specific API Key exists, open & populate the
        dialog with previous API key data.
        3. Once the dialog is successfully closed...
            a. Collect the updated variables.
            b. Call _edit_api_key to update API key entry
            with new values.
        """
        api_key_details = _get_api_key_data(id)

        if api_key_details:
            dialog = EditAPIKeyDialog(
                id,
                api_key_details["key_name"],
                api_key_details["key_value"],
                api_key_details["status"],
                self
            )

            if dialog.exec_():
                updated_api_key_name = dialog.key_name_edit.text()
                updated_api_key_value = dialog.key_value_edit.text()
                updated_status = dialog.status_validity
                print(updated_status)

                success, message = _edit_api_key(
                    id,
                    updated_api_key_name,
                    updated_api_key_value,
                    updated_status
                )

                if success:
                    self.populate_api_keys_table()

    # FUNCTIONS FOR DISPLAYING BACKEND DATA #
    def handle_checkbox_state_change(self, id, state):
        """
        Updates the selected status in the db when the checkbox is toggled.

        This function should:
        1. Convert the checkbox state to a bool.
        2. Call the backend function to update the API key's selected status.
        """
        selected = state == Qt.Checked
        _update_api_key_selected_status(id, selected)

    def populate_api_keys_table(self):
        """
        Loads the API key data from the db & populates the API key table.

        This function should:
        1. Call _get_all_api_key_data to store all API key data.
        2. Create as many rows as there are API key entries in the db.
        3. Re-initialize the styling for the table to style new entry.
        """
        def mask_key_value(api_key: str):
            """
            Conceals the first 8 chars of a given key_value.

            This function should:
            1. If the len fo the API key is greater than 8, mask
            the first 8 chars.
            2. Else, mask the entire API key.
            3. Returned the masked API key.
            """
            if len(api_key) > 8:
                masked_api_key = "*" * 8 + api_key[8:]
            else:
                masked_api_key = "*" * len(api_key)

            return masked_api_key

        def create_checkbox_container(id: int):
            """
            Creates a container for the QCheckBox for a specific API key in
            the API Keys table.

            This function should:
            1. Create a QCheckBox.
            2. Set the QCheckBox's selection to false/not-selected.
            3. If the checkbox is selected, call hande_checkbox_state_change
            to update the selection status for that API key.
            4. Create the following QHBoxLayout to contain the QCheckBox:
                a. Add the QCheckBox.
                b. Align the checkbox to the center.
                c. Remove margins.
            5. Return the checkbox container.
            """
            checkbox = QCheckBox()
            checkbox.setChecked(api_key.get("selected", False))

            checkbox.stateChanged.connect(
                lambda state,
                k_id=id: self.handle_checkbox_state_change(k_id, state)
            )

            checkbox_container = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_container)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)

            return checkbox_container

        def add_api_key_row_to_table(row: int, api_key: dict):
            """
            Adds a singular API key into a specific row in the
            API Key table.

            This function should:
            1. Populate a table row with the following data:
                a. Column1: a QCheckBox for toggling the selected status.
                b. Column2: key_name.
                c. Column3: the masked key_value for security.
                d. Column4: status.
                e. Column5: an edit button.
                f. Column6: a delete button.
            """
            checkbox_container = create_checkbox_container(api_key["id"])
            self.api_keys_table.setCellWidget(row, 0, checkbox_container)

            self.api_keys_table.setItem(
                row, 1, QTableWidgetItem(api_key["key_name"])
            )

            plaintext_api_key = api_key["key_value"]
            self.api_keys_table.setItem(
                row, 2, QTableWidgetItem(mask_key_value(plaintext_api_key))
            )
            self.api_keys_table.setItem(
                row, 3, QTableWidgetItem(api_key["status"])
            )

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(
                lambda checked, k_id=api_key["id"]: self.edit_api_key(k_id)
            )
            self.api_keys_table.setCellWidget(row, 4, edit_button)

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(
                lambda checked, k_id=api_key["id"]: self.delete_api_key(k_id)
            )
            self.api_keys_table.setCellWidget(row, 5, delete_button)

        all_api_keys = _get_all_api_key_data()

        self.api_keys_table.setRowCount(0)
        self.api_keys_table.setRowCount(len(all_api_keys))

        for row, api_key in enumerate(all_api_keys):
            add_api_key_row_to_table(row, api_key)

        integrate_api_keys_group_styling(self)

    # FUNCTIONS FOR ACTION BUTTONS IN API KEYS TABLE #
    def edit_api_key(self, id):
        """
        Opens the Edit API Key dialog when the user clicks the "Edit"
        button for a particular API Key.

        This function should:
        1. Call the open_edit_api_key_dialog function with the id.
        """
        self.open_edit_api_key_dialog(id)

    def delete_api_key(self, id):
        """
        Deletes an API key when the user clicks the "Delete" button for
        an API key.

        This function should:
        1. Call _delete_api_key to remove the API key from the db.
        2. Refresh the API keys table to show the updated data.
        """
        success, message = _delete_api_key(id)

        if success:
            self.populate_api_keys_table()
