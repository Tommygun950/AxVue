"""
This file contains all of the code for dialogs within the API Keys Window.

This file contains the following Dialogs:
1. AddAPIKeyDialog -> allows user to add API keys to the db and table.
2. EditAPIKeyDialog -> allows user to edit a particular key in the table/db.
3. GeneralErrorDialog -> generates an error with a custom error message.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton
)


class AddAPIKeyDialog(QDialog):
    """
    Dialog for adding a new API Key with a name & a key value.
    """
    def __init__(self, parent=None):
        """Initializes the QDialog popup."""
        super().__init__(parent)
        self.setWindowTitle("Add API Key")
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the layout for the QDialog.

        This function should:
        1. Establish a QVBoxLayout with the following:
            a. Establish a QHBoxLayout for the API Key name section
            with the following:
                1. A QLabel with the text "Key Name:".
                2. A QLineEdit where the user can add the key name.
                3. Add the QLabel & QLineEdit to the QHBoxLayout.
                4. Add the QHBoxLayout to the QVBoxLayout.
            b. Establish a QHBoxLayout for the API Key Value section
            with the following:
                1. A QLabel with the text "Key Value:".
                2. A QLineEdit where the user can add the key value
                where the text is obscured.
                3. Add the QLabel & QLineEdit to the QHBoxLayout.
                4. Add the QHBoxLayout to the QVBoxLayout.
            c. Establish a QHBoxLayout for the buttons with the following:
                1. A QPushButton for "OK".
                2. A QPushButton for "Cancel".
                3. If OK is clicked, close dialog & return accepted status.
                4. If Cancel is clicked, close dialog & return rejected status.
                5. Add the buttons to the QHBoxLayout.
                6. Add the QHBoxLayout to the QVBoxLayout.
        """
        layout = QVBoxLayout(self)

        def api_key_name_section():
            """Creates the API Key Name Section of the Dialog."""
            name_layout = QHBoxLayout()
            name_label = QLabel("Key Name:")
            self.api_key_name_edit = QLineEdit()
            name_layout.addWidget(name_label)
            name_layout.addWidget(self.api_key_name_edit)
            layout.addLayout(name_layout)

        def api_key_value_section():
            """Creates the API Key Value Section of the Dialog."""
            value_layout = QHBoxLayout()
            value_label = QLabel("Key Value:")
            self.api_key_value_edit = QLineEdit()
            self.api_key_value_edit.setEchoMode(QLineEdit.Password)
            value_layout.addWidget(value_label)
            value_layout.addWidget(self.api_key_value_edit)
            layout.addLayout(value_layout)

        def buttons_section():
            """Creates the Buttons Section of the Dialog."""
            button_layout = QHBoxLayout()
            self.ok_button = QPushButton("OK")
            self.cancel_button = QPushButton("Cancel")
            self.ok_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(self.ok_button)
            button_layout.addWidget(self.cancel_button)
            layout.addLayout(button_layout)

        api_key_name_section()
        api_key_value_section()
        buttons_section()


class EditAPIKeyDialog(QDialog):
    """
    Dialog for editing an API Key with a name, value, and status
    """
    def __init__(
        self, id,
        key_name, key_value,
        status_validity, parent=None
    ):
        """
        Initializes the QDialog popup with existing API Key Data.

        Parameters for a specific scan:
        1. id.
        2. key_name.
        3. key_value.
        4. status_validity.
        """
        super().__init__(parent)
        self.setWindowTitle("Edit API Key")
        self.id = id
        self.key_name = key_name
        self.key_value = key_value
        self.status_validity = status_validity
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the layout for the QDialog.

        This function should:
        1. Establish a QVBoxLayout with the following:
            a. Establish a QHBoxLayout for the key name
            section with the following:
                1. A QLabel with the text "Key Name:".
                2. A QLineEdit where the user can edit the key name.
                3. Prefil the QLineEdit with the previous api key name.
                4. Add the QLabel & QLineEdit to the QHBoxLayout.
                5. Add QHBoxLayout to the QVBoxLayout.
            b. Establish a QHBoxLayout for the key value section
            with the following:
                1. A QLabel with the text "Key Value:".
                3. A QLineEdit where the user can edit the key value.
                3. Prefile the QLineEdit with the previous api key value.
                4. Obscure the contents of the QLineEdit.
                5. Add the QLabel & QLineEdit to the QHBoxLayout.
                6. Add the QHBoxLayout to the QVBoxLayout.
            c. Establish a QHBoxLayout for the status section
            with the following:
                1. A QLabel with the text "Status:".
                2. A QPushButton that toggles between "Valid" & "Invalid".
                3. Have the setting default ot the existing value in the db.
                4. Call the toggle_status function when the user clicks button.
                5. Add the QLabel & QPushButton to the QHBoxLayout.
                6. Add the QHBoxLayout to the QVBoxLayout.
            d. Establish a QHBoxLayout for the buttons with the following:
                1. A QPushButton for "OK".
                2. A QPushButton for "Cancel".
                3. If OK is clicked, close dialog and return accepted status.
                4. If Cancel is clicked, close dialog & return rejected status.
                5. Add the buttons to the QHBoxLayout.
                6. Add the QHBoxLayout to the QVBoxLayout.
        """
        layout = QVBoxLayout(self)

        def api_key_name_section():
            """Creates the API Key Name section."""
            name_layout = QHBoxLayout()
            name_label = QLabel("Key Name:")
            self.key_name_edit = QLineEdit()
            self.key_name_edit.setText(self.key_name)
            name_layout.addWidget(name_label)
            name_layout.addWidget(self.key_name_edit)
            layout.addLayout(name_layout)

        def api_key_value_section():
            """Creates the API Key Value section."""
            value_layout = QHBoxLayout()
            value_label = QLabel("Key Value:")
            self.key_value_edit = QLineEdit()
            self.key_value_edit.setText(self.key_value)
            self.key_value_edit.setEchoMode(QLineEdit.Password)
            value_layout.addWidget(value_label)
            value_layout.addWidget(self.key_value_edit)
            layout.addLayout(value_layout)

        def status_section():
            """Creates the API Key Status section."""
            status_layout = QHBoxLayout()
            status_label = QLabel("Status:")
            self.status_button = QPushButton()
            self.update_status_button_text()
            self.status_button.clicked.connect(self.toggle_status)
            status_layout.addWidget(status_label)
            status_layout.addWidget(self.status_button)
            layout.addLayout(status_layout)

        def buttons_section():
            """Creates the buttons section."""
            button_layout = QHBoxLayout()
            self.ok_button = QPushButton("OK")
            self.cancel_button = QPushButton("Cancel")
            self.ok_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(self.ok_button)
            button_layout.addWidget(self.cancel_button)
            layout.addLayout(button_layout)

        api_key_name_section()
        api_key_value_section()
        status_section()
        buttons_section()

    def update_status_button_text(self):
        """
        Updates the status button text based on the current status.

        This function should:
        1. change the text on the gui dialog depending on the value.
        """
        print(self.status_validity)
        if self.status_validity:
            self.status_button.setText("Valid")
        else:
            self.status_button.setText("Invalid")

    def toggle_status(self):
        """
        Toggles the status between valid & invalid.

        this function should:
        1. If the status button is toggled, switch it to the opposite value.
        """
        self.status_validity = not self.status_validity
        self.update_status_button_text()


class GeneralErrorDialog(QDialog):
    """
    Dialog for displaying a general error message.
    """
    def __init__(self, error_message: str, parent=None):
        """
        Initializes the QDialog popup with a specified error message.
        """
        super().__init__(parent)
        self.setWindowTitle("Error")
        self.error_message = error_message
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the layout for the QDialog.

        This function should:
        1. Establish a QVBoxLayout for the dialog.
        2. Add a QLabel that displays the error message (self.error_message).
        3. Establish a QHBoxLayout for the button(s).
        4. Create a QPushButton, "OK" that closes the dialog when clicked.
        """
        layout = QVBoxLayout(self)

        error_label = QLabel(self.error_message)
        error_label.setWordWrap(True)
        layout.addWidget(error_label)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)
