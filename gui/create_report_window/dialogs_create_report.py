"""
This file contains all of the code for dialogs within Create Report Window.

This file contains the following Dialogs:
1. GeneralErrorDialog -> generates an error with a custom error message.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)


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
