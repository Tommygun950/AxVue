"""
This file contains all of the code for popup dialogs within the ScansWindow.

This file contains the following Dialogs:
1. AddScanDialog -> allows user to add scans to the db and table.
2. EditScanDialog -> allows user to edit a particular scan in the table/db.
3. GeneralErrorDialog -> generates an error with a custom error message.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog
)


class AddScanDialog(QDialog):
    """
    Dialog for adding a new scan with a name and file path.
    """
    def __init__(self, parent=None):
        """Initializes the QDialog popup."""
        super().__init__(parent)
        self.setWindowTitle("Add Scan")
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the layout for the QDialog.

        This function should:
        1. Establish a QVBoxLayout with the following:
            a. Establish a QHBoxLayout for the scan name
            seciton with the following:
                1. A QLabel with the text "Scan Name:".
                2. A QLineEdit where the user can add the scan name.
                3. Add the label and line edit to the QHBoxLayout.
                4. Add QHBoxLayout to the QVBoxLayout.
            b. Establish a QHBoxLayout for the filepath section
            with the following:
                1. A QLabel with the text "File Path: ".
                2. An optional QLineEdit if users want to type in the
                file path.
                3. A QPushButton called "Browse" so the user can
                select the file.
                4. Call the browse_file function when the user clicks
                the "Browse" button.
                5. Add the label, line edit, and button to the QHBoxLayout.
                6. Add QHBoxLayout to the QVBoxLayout.
            c. Establish a QHBoxLayout for the buttons with the following:
                1. A QPushButton for "OK".
                2. A QPushButton for "Cancel".
                3. If OK is clicked, close dialog and return accepted status.
                4. If Cancel is clicked, close dialog & return rejected status.
                5. Add the buttons to the QHBoxLayout.
                6. Add the QHBoxLayout to the QVBoxLayout.
        """
        layout = QVBoxLayout(self)  # 1.

        def scan_name_section():
            """Creates the Scan Name Section of the Dialog."""
            name_layout = QHBoxLayout()  # 1a.
            name_label = QLabel("Scan Name:")  # 1a1.
            self.scan_name_edit = QLineEdit()  # 1a2.
            name_layout.addWidget(name_label)  # 1a3.
            name_layout.addWidget(self.scan_name_edit)  # 1a3.
            layout.addLayout(name_layout)  # 1a4.

        def file_path_section():
            path_layout = QHBoxLayout()  # 1b.
            path_label = QLabel("File Path:")  # 1b1.
            self.file_path_edit = QLineEdit()  # 1b2.
            self.browse_button = QPushButton("Browse")  # 1b3.
            self.browse_button.clicked.connect(self.browse_file)  # 1b4.
            path_layout.addWidget(path_label)  # 1b5.
            path_layout.addWidget(self.file_path_edit)  # 1b5.
            path_layout.addWidget(self.browse_button)  # 1b5.
            layout.addLayout(path_layout)  # 1b6.

        def buttons_section():
            button_layout = QHBoxLayout()  # 1c.
            self.ok_button = QPushButton("OK")  # 1c1.
            self.cancel_button = QPushButton("Cancel")  # 1c2.
            self.ok_button.clicked.connect(self.accept)  # 1c3.
            self.cancel_button.clicked.connect(self.reject)  # 1c4.
            button_layout.addWidget(self.ok_button)  # 1c5.
            button_layout.addWidget(self.cancel_button)  # 1c5.
            layout.addLayout(button_layout)  # 1c6.

        scan_name_section()
        file_path_section()
        buttons_section()

    def browse_file(self):
        """
        Opens a file dialog to select a CSV file.

        This function should:
        1. Open a modal file dialog titled "Select File" that filters
        for CSV files (*.csv) and all files.
        2. Retrieve the selected file's path from the dialog.
        3. If a file is selected, update the file path QLineEdit
        (self.file_path_edit) with the selected file path.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            self.file_path_edit.setText(file_name)


class EditScanDialog(QDialog):
    """
    Dialog for editing a scan with a name, file path, & cache setting.
    """
    def __init__(
            self, scan_id,
            scan_name, file_path,
            cache_enabled, parent=None
    ):
        """
        Initializes the QDialog popup with existing scan data.

        Parameters for a specific scan:
        1. scan_id.
        2. scan_name.
        3. file_path.
        4. cache_enabled.
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Scan")
        self.scan_id = scan_id
        self.scan_name = scan_name
        self.file_path = file_path
        self.cache_enabled = cache_enabled
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the layout for the QDialog.

        This function should:
        1. Establish a QVBoxLayout with the following:
            a. Establish a QHBoxLayout for the scan name
            section with the following:
                1. A QLabel with the text "Scan Name:".
                2. A QLineEdit where the user can edit the scan name.
                3. Prefil the QLineEdit with the previous scan name.
                4. Add the label and line edit to the QHBoxLayout.
                5. Add QHBoxLayout to the QVBoxLayout.
            b. Establish a QHBoxLayout for the filepath section
            with the following:
                1. A QLabel with the text "File Path: ".
                2. An QLineEdit pre-filled with the current file path.
                3. A QPushButton called "Browse" so the user can
                select a new file.
                4. Call the browse_file function when the user clicks
                the "Browse" button.
                5. Add the label, line edit, and button to the QHBoxLayout.
                6. Add QHBoxLayout to the QVBoxLayout.
            c. Establish a QHBoxLayout for the cache section
            with the following:
                1. A QLabel with the text "Caching:".
                2. A QPushButton that toggles between "Enabled" and "Disabled".
                3. Have the setting default to the existing value in the db.
                4. Call the toggle_cache function when the user clicks  button.
                5. Add the label and button to the QHBoxLayout.
                6. Add QHBoxLayout to the QVBoxLayout.
            d. Establish a QHBoxLayout for the buttons with the following:
                1. A QPushButton for "OK".
                2. A QPushButton for "Cancel".
                3. If OK is clicked, close dialog and return accepted status.
                4. If Cancel is clicked, close dialog & return rejected status.
                5. Add the buttons to the QHBoxLayout.
                6. Add the QHBoxLayout to the QVBoxLayout.
        """
        layout = QVBoxLayout(self)  # 1.

        def scan_name_section():
            name_layout = QHBoxLayout()  # 1a.
            name_label = QLabel("Scan Name:")  # 1a1.
            self.scan_name_edit = QLineEdit()  # 1a2.
            self.scan_name_edit.setText(self.scan_name)  # 1a3.
            name_layout.addWidget(name_label)  # 1a4.
            name_layout.addWidget(self.scan_name_edit)  # 1a4.
            layout.addLayout(name_layout)  # 1a5.

        def file_path_section():
            path_layout = QHBoxLayout()  # 1b.
            path_label = QLabel("File Path:")  # 1b1.
            self.file_path_edit = QLineEdit()  # 1b2.
            self.file_path_edit.setText(self.file_path)   # 1b2.
            self.browse_button = QPushButton("Browse")  # 1b3.
            self.browse_button.clicked.connect(self.browse_file)  # 1b4.
            path_layout.addWidget(path_label)  # 1b5.
            path_layout.addWidget(self.file_path_edit)  # 1b5.
            path_layout.addWidget(self.browse_button)  # 1b5.
            layout.addLayout(path_layout)  # 1b6.

        def cache_section():
            cache_layout = QHBoxLayout()  # 1c.
            cache_label = QLabel("Cache Setting:")  # 1c1.
            self.cache_button = QPushButton()  # 1c2.
            self.update_cache_button_text()   # 1c3.
            self.cache_button.clicked.connect(self.toggle_cache)  # 1c4.
            cache_layout.addWidget(cache_label)  # 1c5.
            cache_layout.addWidget(self.cache_button)  # 1c5.
            layout.addLayout(cache_layout)  # 1c6.

        def buttons_section():
            button_layout = QHBoxLayout()  # 1d.
            self.ok_button = QPushButton("OK")  # 1d1.
            self.cancel_button = QPushButton("Cancel")  # 1d2.
            self.ok_button.clicked.connect(self.accept)  # 1d3.
            self.cancel_button.clicked.connect(self.reject)  # 1d4.
            button_layout.addWidget(self.ok_button)  # 1d5.
            button_layout.addWidget(self.cancel_button)  # 1d5.
            layout.addLayout(button_layout)  # 1d6.

        scan_name_section()
        file_path_section()
        cache_section()
        buttons_section()

    def update_cache_button_text(self):
        """
        Updates the cache button text based on the current cache setting.

        This function should:
        1. Change the text on the gui dialog depending on the value.
        """
        if self.cache_enabled:
            self.cache_button.setText("Enabled")
        else:
            self.cache_button.setText("Disabled")

    def toggle_cache(self):
        """
        Toggles the cache setting between enabled and disabled.

        This funciton should:
        1. If the cache button is toggled, switch it to the opposite value.
        """
        self.cache_enabled = not self.cache_enabled
        self.update_cache_button_text()

    def browse_file(self):
        """
        Opens a file dialog to select a CSV file.

        This function should:
        1. Open a modal file dialog titled "Select File" that filters
        for CSV files (*.csv) and all files.
        2. Retrieve the selected file's path from the dialog.
        3. If a file is selected, update the file path QLineEdit
        (self.file_path_edit) with the selected file path.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            self.file_path_edit.setText(file_name)


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
