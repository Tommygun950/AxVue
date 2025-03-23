"""
This file is used to construct the Scans window in the GUI.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QLabel, QHBoxLayout, QGroupBox, QTableWidgetItem,
    QCheckBox
)
from gui.scans_window.dialogs_scans import (
    AddScanDialog, EditScanDialog
)
from gui.scans_window.backend_scans import (
    _add_scan, _edit_scan, _delete_scan,
    _get_all_scan_data, _get_scan_data,
    _update_scan_selected_field
)
from gui.scans_window.style_scans import (
    integrate_window_styling,
    integrate_summary_group_styling,
    integrate_scans_group_styling
)


class ScansWindow(QMainWindow):
    """Main window for Scans page."""
    # FUNCTIONS FOR INITIALIZING GUI ELEMENTS/LAYOUTS/WIDGETS #
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
        integrate_scans_group_styling(self)

        self.populate_scans_table()

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
                a. Select -> checkbox for selecting scans in the report.
                b. Scan Name -> text for the scan name.
                c. Total CVE IDs -> count of total cves in scan.
                d. Unique CVE IDs -> list of total unique cves in scan.
                e. Cache -> whether caching is "Enabled" or "Disabled".
                f. Edit -> button for editing a specific scan.
                g. Delete -> button for deleting a specific scan.
            """
            self.scan_table = QTableWidget()
            self.scan_table.setColumnCount(8)

            self.scan_table.setHorizontalHeaderLabels([
                "Select",
                "Scan Name",
                "Total CVE IDs",
                "Unique CVE IDs",
                "Cache",
                "Cached %",
                "Edit",
                "Delete"
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

    def open_edit_scan_dialog(self, id):
        """
        Opens the Edit Scan dialog for the selected scan.

        This function should:
        1. Get the scan details from the database.
        2. Create and display an EditScanDialog with the scan data.
        3. If the dialog is accepted, update the scan with the new values.
        """
        scan_details = _get_scan_data(id)

        if scan_details:
            dialog = EditScanDialog(
                id,
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
                    id,
                    updated_scan_name,
                    updated_file_path,
                    updated_cache_enabled
                )

                if success:
                    self.populate_scans_table()

    # FUNCTIONS FOR DISPLAYING BACKEND DATA #
    def handle_checkbox_state_change(self, id, state):
        """
        Updates the selected status in the db when the checkbox is toggled.

        This function should:
        1. Update the selected variable based on if the checkbox is checked.
        2. Call the backend function to update the API key's selected field.
        """
        selected = 1 if state == Qt.Checked else 0
        _update_scan_selected_field(id, selected)

    def populate_scans_table(self):
        """
        Loads the scan data from the db & populates the scan table.

        This function should:
        1. Call _get_all_scan_data to stor all scan data.
        2. Create as many rows as there are scan entries in the db.
        3. Re-initialize the styling for the table to style new entry.
        """
        def create_checkbox_container(id: int):
            """
            Creates a container for the QCheckBox for a specific scan
            in the scans table.

            This function should:
            1. Create a QCheckBox.
            2. Set the QCheckBox's selected to 0/not-selected.
            3. If the checkbox is selected, call handle_checkbox_stat_change to
            update the selection field for that scan.
            4. Create the following QHBoxLayout to contain the QCheckBox:
                a. Add the QCheckBox.
                b. Align the checkbox to the center.
                c. Remove margins.
            5. Return the checkbox container.
            """
            checkbox = QCheckBox()
            checkbox.setChecked(scan.get("selected", 0))

            checkbox.stateChanged.connect(
                lambda state,
                s_id=id: self.handle_checkbox_state_change(s_id, state)
            )

            checkbox_container = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_container)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)

            return checkbox_container

        def return_unique_cve_list_ct(unique_cve_list: str) -> int:
            """
            Given the string of unique cves, return the count
            of cves in the string.

            This function should:
            1. Split the string by every ", ".
            2. The return the count of splits.
            """
            return (len(unique_cve_list.split(", ")))

        def add_scan_row_to_table(row: int, scan: dict):
            """
            Adds a singular scan into a specific row in the
            scan table.

            This function should:
            1. Populate a table row with the following data:
                a. Column1: a QCheckBox for toggling the selected field.
                b. Column2: scan_name.
                c. Column3: total_vulnerabilities (int).
                d. Column4: unique_cves count (int).
                e. Column5: cache_enabled (a non-pushable button for styling).
                f. Column6: cached_percentage (a non-pushable button to style).
                g. Column7: an edit button.
                h. Column8: a delete button.
            """
            checkbox_container = create_checkbox_container(scan["id"])
            self.scan_table.setCellWidget(row, 0, checkbox_container)

            self.scan_table.setItem(
                row, 1, QTableWidgetItem(scan["scan_name"])
            )

            total_vulns_str = str(scan["total_vulnerabilities"])
            self.scan_table.setItem(
                row, 2, QTableWidgetItem(total_vulns_str)
            )

            unique_cves_ct = return_unique_cve_list_ct(scan["unique_cve_list"])
            unique_cves_ct_str = str(unique_cves_ct)
            self.scan_table.setItem(
                row, 3, QTableWidgetItem(unique_cves_ct_str)
            )

            cache_button = QPushButton(scan["cache_enabled"])
            cache_button.setEnabled(False)
            self.scan_table.setCellWidget(row, 4, cache_button)

            cached_perc_str = f"{scan["cached_percentage"]}%"
            cached_perc_button = QPushButton(cached_perc_str)
            cached_perc_button.setEnabled(False)
            self.scan_table.setCellWidget(row, 5, cached_perc_button)

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

        all_scans = _get_all_scan_data()

        self.scan_table.setRowCount(0)
        self.scan_table.setRowCount(len(all_scans))

        for row, scan in enumerate(all_scans):
            add_scan_row_to_table(row, scan)

        integrate_scans_group_styling(self)

    # FUNCTIONS FOR ACTION BUTTONS IN SCAN TABLE #
    def edit_scan(self, id):
        """
        Opens the Edit Scan dialog when the user clicks the "Edit"
        button for a scan.

        This function should:
        1. Call the open_edit_scan_dialog function with the id.
        """
        self.open_edit_scan_dialog(id)

    def delete_scan(self, id):
        """
        Deletes a scan when the user clicks the "Delete" button for a scan.

        This function should:
        1. Call _delete_scan to remove the scan from the db.
        2. Refresh the scan table to show the updated data.
        """
        success, message = _delete_scan(id)

        if success:
            self.populate_scans_table()
