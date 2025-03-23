"""
This file is used to construct the Scans window in the GUI.
"""
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QLabel, QHBoxLayout, QGroupBox, QTableWidgetItem,
    QCheckBox
)
from PyQt5.QtCore import Qt
from gui.scans_window.dialogs_scans import (
    AddScanDialog, EditScanDialog
)
from gui.scans_window.backend_scans import (
    _add_scan, _edit_scan, _delete_scan,
    _get_all_scan_data, _get_scan_data,
    _update_scan_selected_status
)
from gui.scans_window.style_scans import (
    integrate_window_styling,
    integrate_summary_group_styling,
    integrate_scans_group_styling
)


class ScansWindow(QMainWindow):
    """Main window for Scans page."""
    def __init__(self):
        """
        This function initializes the scans page & features.

        This function should:
        1. create the vertical layout for all of the widgets.
        2. Establish the following widgets:
            a. An excerpt/summery on this page.
            b. A section for scans with the following:
                1. Table of scans.
                b. A list of buttons:
        3. Populate the scans table with the scan_data table.
        4. Initialize the styling for the following:
            a. Scans Window.
            b. Scans Summary Group.
            c. Scans Group.
        """
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_scans_summary()
        self.init_scans_section()

        integrate_window_styling(self)

        integrate_summary_group_styling(self)
        integrate_scans_group_styling(self)  # First call to color buttons.

        self.populate_scans_table()

        integrate_scans_group_styling(self)  # Second call to center text.

    def init_scans_summary(self):
        """
        Initializes the summary for the page.

        This function should:
        1. Creates a QGroupBox with the following:
            a. Title of "Scans Summary".
            b. The inclusion of the summary text.
        2. Displays the layout on the main layout.
        """
        self.scans_summary_group = QGroupBox("Scans Summary")
        group_layout = QVBoxLayout(self.scans_summary_group)

        summary_text = (
            "Step 1: Add your CSV scan exports to the table and "
            "select the checkbox for the scans you want in your report. "
        )

        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        group_layout.addWidget(summary_label)

        self.layout.addWidget(self.scans_summary_group)

    def init_scans_section(self):
        """
        Initializes the section for the scans data.

        This function should:
        1. Create a QGroupBox layout.
        2. Create a QVBoxLayout layout with the following:
            a. Horizontal button layout.
            b. Scans table.
        3. Add The QVBoxLayout to the QGroupBox.
        4. Add QGroupBox to the main layout for the page.
        """
        self.scans_group = QGroupBox("Scans")
        scans_section_layout = QVBoxLayout(self.scans_group)

        def init_button_layout():
            """
            Initilizes the button layout at the bottom of the window.

            The function should:
            1. Create a horizontal layout for the buttons.
            2. Create the following buttons:
                a. Add Scan.
            3. Ensure resizing of the buttons do the following:
                a. Add Scan -> Stretch.
            4. Add button layout to the main layout.
            """
            button_layout = QHBoxLayout()

            self.add_scan_button = QPushButton("Add Scan")
            self.add_scan_button.clicked.connect(self.open_add_scan_dialog)
            button_layout.addWidget(self.add_scan_button)

            scans_section_layout.addLayout(button_layout)

        def init_scans_table():
            """
            Initializes the table to display the scans.

            This function should:
            1. Setup a table widget with the following columns:
                a. Select.
                b. Scan Name.
                c. Total CVE IDs.
                d. Unique CVE IDs.
                e. Cache.
                f. Edit.
                g. Delete.
            2. Ensure the resising of the columns do the following:
                a. Select -> Resize to Contents.
                b. Scan name -> Stretch.
                c. Total CVE IDs -> Resize to Contents.
                d. Unique CVE IDs -> Resize to Contents.
                e. Cache -> Resize to Contents.
                f. Edit -> Resize to Contents.
                g. Delete -> Resize to Contents.
            3. Add the label and table widget to the layout.
            """
            self.scan_table = QTableWidget()
            self.scan_table.setColumnCount(8)

            self.scan_table.setHorizontalHeaderLabels([
                "Select", "Scan Name", "Total CVE IDs",
                "Unique CVE IDs", "Cache", "Cached %", "Edit", "Delete"
            ])

            self.scan_table.verticalHeader().setVisible(False)

            self.scan_table.setEditTriggers(QTableWidget.NoEditTriggers)

            header = self.scan_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

            self.scan_table.setColumnWidth(0, 70)

            scans_section_layout.addWidget(self.scan_table)

        init_button_layout()
        init_scans_table()

        self.layout.addWidget(self.scans_group)

    # FUNCTIONS FOR OPENING DIALOGS FROM DIALOGS_SCANS.PY #
    def open_add_scan_dialog(self):
        """
        Opens the Add Scan dialog when the user clicks the "Add Scan" button.

        This function should:
        1. Execute the AddScanDialog.
        2. If the dialog is accepted, retrieve the scan name
           and file path and call _add_scan.
        """
        dialog = AddScanDialog(self)
        if dialog.exec_():
            scan_name = dialog.scan_name_edit.text()
            file_path = dialog.file_path_edit.text()

            _add_scan(scan_name, file_path)
            self.populate_scans_table()

    def open_edit_scan_dialog(self, scan_id):
        """
        Opens the Edit Scan dialog for the selected scan.

        This function should:
        1. Get the scan details from the database.
        2. Create and display an EditScanDialog with the scan data.
        3. If the dialog is accepted, update the scan with the new values.
        """
        scan_details = _get_scan_data(scan_id)

        if scan_details:
            dialog = EditScanDialog(
                scan_id,
                scan_details["scan_name"],
                scan_details["file_path"],
                scan_details["cache_enabled"],
                self
            )

            if dialog.exec_():
                updated_scan_name = dialog.scan_name_edit.text()
                updated_file_path = dialog.file_path_edit.text()
                updated_cache_enabled = dialog.cache_enabled

                success, message = _edit_scan(
                    scan_id,
                    updated_scan_name,
                    updated_file_path,
                    updated_cache_enabled
                )

                if success:
                    self.populate_scans_table()

    # FUNCTIONS FOR DISPLAYING BACKEND DATA #
    def handle_checkbox_state_change(self, scan_id, state):
        """
        Updates the selected status in the database when a checkbox is toggled.

        This function should:
        1. Convert the checkbox state to a boolean.
        2. Call the backend function to update the scan's selected status.
        """
        selected = state == Qt.Checked
        _update_scan_selected_status(scan_id, selected)

    def populate_scans_table(self):
        """
        Loads scan data from the database and populates the scan table.

        This function should:
        1. Retrieve all scan data from the backend.
        2. Clear the GUI scans table.
        3. Repopulate the scans table with the updated data.
        4. Adds "Edit" and "Delete" buttons in their columns for scan entries.
        5. Recall integrate_scan_group_styling to prevent table changes.
        """
        all_scans = _get_all_scan_data()

        self.scan_table.setRowCount(0)
        self.scan_table.setRowCount(len(all_scans))

        for row, scan in enumerate(all_scans):
            checkbox = QCheckBox()
            checkbox.setChecked(scan.get("selected", False))

            scan_id = scan["id"]
            checkbox.stateChanged.connect(
                lambda state,
                s_id=scan_id: self.handle_checkbox_state_change(s_id, state)
            )

            checkbox_container = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_container)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)

            self.scan_table.setCellWidget(row, 0, checkbox_container)

            self.scan_table.setItem(
                row, 1, QTableWidgetItem(scan["scan_name"])
            )
            self.scan_table.setItem(
                row, 2, QTableWidgetItem(scan["total_cves"])
            )
            self.scan_table.setItem(
                row, 3, QTableWidgetItem(scan["unique_cves"])
            )
            self.scan_table.setItem(
                row, 4, QTableWidgetItem(scan["cache_enabled"])
            )
            self.scan_table.setItem(
                row, 5, QTableWidgetItem(scan["cached_percentage"])
            )

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(
                lambda checked, s_id=scan["id"]: self.edit_scan(s_id)
            )
            self.scan_table.setCellWidget(row, 6, edit_button)

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(
                lambda checked, s_id=scan["id"]: self.delete_scan(s_id)
            )
            self.scan_table.setCellWidget(row, 7, delete_button)

        integrate_scans_group_styling(self)

    # FUNCTIONS FOR ACTION BUTTONS IN SCAN TABLE #
    def edit_scan(self, scan_id):
        """
        Opens the Edit Scan dialog when the user clicks the "Edit"
        button for a scan.

        This function should:
        1. Call the open_edit_scan_dialog function with the scan_id.
        """
        self.open_edit_scan_dialog(scan_id)

    def delete_scan(self, scan_id):
        """
        Deletes a scan when the user clicks the "Delete" button for a scan.

        This function should:
        1. Call _delete_scan to remove the scan from the db.
        2. Refresh the scan table to show the updated data.
        """
        success, message = _delete_scan(scan_id)

        if success:
            self.populate_scans_table()
