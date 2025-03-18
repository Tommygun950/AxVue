"""
This file is used to construct the API Keys window in the GUI.
"""

from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QLabel, QHBoxLayout, QGroupBox
)
from gui.api_keys_window.dialogs_api_keys import (
    AddAPIKeyDialog, EditAPIKeyDialog
)

class ApiKeysWindow(QMainWindow):
    """Main window for API Keys page."""
    def __init__(self):
        """
        This function initializes the api keys page & features.

        This function should:
        1. create the vertical layout for all of the widgets.
        2. Establish the following widgets:
            a. An excerpt/summery on this page.
            b. Table of scans.
            c. A list of buttons:
                1. Add API Key.
        """
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_scans_summary()
        self.init_api_keys_section()

    def init_scans_summary(self):
        """
        Initializes the summary for the page.

        this function should:
        1. Creates a QGroupBox with the following:
            a. Title of "API Keys Summary".
            b. The inclusion of the summary text.
        2. Displays the layout on the main layout.
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
        Initializes the section for the api keys.

        This function should:
        1. Create a QGroupBox layout.
        2. Create a QVBoxLayout layout with the following:
            a. Horizontal button layout.
            b. API Keys table.
        3. Add The QVBoxLayout to the QGroupBox.
        4. Add QGroupBox to the main layout for the page.
        """
        api_keys_group = QGroupBox("API Keys")
        api_keys_layout = QVBoxLayout(api_keys_group)

        def init_button_layout(self):
            """
            Initilizes the button layout at the bottom of the window.

            The function should:
            1. Create a horizontal layout for the buttons.
            2. Create the following buttons:
                a. Add API Key.
            3. Ensure resizing of the buttons do the following:
                a. Add API Key -> Stretch.
            4. Add button layout to the main layout.
            """
            button_layout = QHBoxLayout()

            self.add_api_key_button = QPushButton("Add API Key")
            button_layout.addWidget(self.add_api_key_button)

            api_keys_layout.addLayout(button_layout)

        def init_api_keys_table(self):
            """
            Initializes the table to display the api keys.

            This function should:
            1. Setup a table widget with the following columns:
                a. Key Name.
                b. Key Value.
                c. Status.
            2. Ensure the resising of the columns do the following:
                a. Key Name -> Stretch.
                b. Key Value -> Stretch.
                c. Status -> Resize to Contents.
            3. Add the label and table widget to the layout.
            """
            self.api_keys_table = QTableWidget()
            self.api_keys_table.setColumnCount(3)

            self.api_keys_table.setHorizontalHeaderLabels([
                "Key Name", "Key Value", "Status"
            ])

            self.api_keys_table.setEditTriggers(QTableWidget.NoEditTriggers)

            header = self.api_keys_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

            api_keys_layout.addWidget(self.api_keys_table)

        init_button_layout(self)
        init_api_keys_table(self)
        self.layout.addWidget(api_keys_group)

    # FUNCTIONS FOR OPENING DIALOGS FROM DIALOGS_API_KEYS.PY #
    def open_add_api_key_dialog(self):
        """
        Opens the Add API Key Dialog when user clicks the "Add API Key" button.

        This function should:
        1. Execute the AddAPIKeyDialog.
        2. If the dialog is accepted, retrieve the API Key Name & value
        & call _add_api_key.
        """
        dialog = AddAPIKeyDialog(self)
        if dialog.exec_():
            key_name = dialog.api_key_name_edit.text()
            key_value = dialog.api_key_value_edit.text()

            _add_api_key(key_name, key_value)
            self.populate_api_keys_table()