"""
This file is responsible for the layout of th Create Report window.
"""
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QLabel, QTableWidgetItem, QHBoxLayout,
    QGroupBox, QComboBox, QCheckBox
)
from gui.create_report_window.backend_create_report import (
    _get_selected_api_keys, _get_selected_scans,
    _remove_api_key, _remove_scan
)
from gui.create_report_window.style_create_report import (
    integrate_window_styling,
    integrate_api_keys_group_styling,
    integrate_scans_group_styling,
    integrate_export_config_styling
)


class CreateReportWindow(QMainWindow):
    """Main window for the create report page"""
    # FUNCTIONS FOR INITIALIZING GUI ELEMENTS/LAYOUTS/WIDGETS #
    def __init__(self):
        """
        This function initializes the create report page & features.

        This function should:
        2. Creates a central widget/layout with the following:
            a. List of selected NVD API keys.
            b. List of selected Scans.
            c. Export configuration box.
        3. Initialize the styling for the following:
            a. Create Report Window.
            b. API Keys Section.
            c. Scans Section.
            d. Export Config Section.
        3. Populates the selected API Keys table.
        4. Populates the selected Scans table.
        """
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_api_key_section()
        self.init_scans_section()
        self.init_export_config()

        integrate_window_styling(self)
        integrate_api_keys_group_styling(self)
        integrate_scans_group_styling(self)
        integrate_export_config_styling(self)

        self.populate_selected_api_keys_table()
        self.populate_selected_scans_table()

    def init_api_key_section(self):
        """
        Creates the selected api keys section.

        This function should:
        1. Create the label "Selected API Keys: ".
        2. Setup a table widget with the following columns:
            a. Key Name.
            b. Key Value.
            c. Status.
            d. Remove.
        3. Ensure the resizing of the columns do the following:
            a. Key Name -> Stretch.
            b. Key Value -> Stretch.
            c. Status -> Resize to Contents.
            d. Remove -> Resize to Contents.
        4. Add the labl and the table widget to the layout.
        """
        self.api_key_group = QGroupBox("Selected API Keys")
        group_layout = QVBoxLayout(self.api_key_group)

        self.api_keys_table = QTableWidget()
        self.api_keys_table.setColumnCount(4)

        self.api_keys_table.setHorizontalHeaderLabels([
            "Key Name",
            "Key Value",
            "Status",
            "Remove"
        ])

        self.api_keys_table.verticalHeader().setVisible(False)
        self.api_keys_table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.api_keys_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        group_layout.addWidget(self.api_keys_table)
        self.layout.addWidget(self.api_key_group)

    def init_scans_section(self):
        """
        Creates the selected scans section.

        This function should:
        1. Create the label "Selected Scans: ".
        2. Setup a table widget with the following columns:
            a. Scan Name.
            b. Total CVE IDs.
            c. Unique CVE IDs.
            d. Cache.
            e. Cached %.
            f. Remove.
        3. Ensure the resizing of the columns do the following:
            a. Scan Name -> Stretch.
            b. Total CVE IDS -> Resize to Contents.
            c. Unique CVE IDs -> Resize to Contents.
            d. Cache -> Resize to Contents.
            e. Cached % -> Resize to Contents.
            f. Remove -> Resize to Contents.
        4. Add the label and the table widget to the layout.
        """
        self.scans_group = QGroupBox("Selected Scans")
        group_layout = QVBoxLayout(self.scans_group)

        self.scans_table = QTableWidget()
        self.scans_table.setColumnCount(6)

        self.scans_table.setHorizontalHeaderLabels([
            "Scan Name",
            "Total CVE IDs",
            "Unique CVE IDs",
            "Cache",
            "Cached %",
            "Remove"
        ])

        self.scans_table.verticalHeader().setVisible(False)
        self.scans_table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.scans_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        group_layout.addWidget(self.scans_table)
        self.layout.addWidget(self.scans_group)

    def init_export_config(self):
        """
        Creates the export configuration section.

        This function should:
        1. Creat the groupbox for Export Configuration
        2. Add the combo box for Export Type selection.
        3. Add the checkbox for the Pages to Export section.
        4. Add the Create Report button.
        5. Add layout to the main window.
        """
        self.export_config_group = QGroupBox("Export Configuration")
        group_layout = QVBoxLayout(self.export_config_group)

        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Export Type:"))
        self.export_type_combo = QComboBox()
        self.export_type_combo.addItems(["PDF", "Excel"])
        type_layout.addWidget(self.export_type_combo)
        group_layout.addLayout(type_layout)

        group_layout.addWidget(QLabel("Pages to Export:"))
        self.page_checkboxes = {}
        for page in [
            "KEV Catalog Comparison",
            "Base Metrics",
            "Temporal Metrics"
        ]:
            checkbox = QCheckBox(page)
            checkbox.setChecked(True)
            self.page_checkboxes[page] = checkbox
            group_layout.addWidget(checkbox)

        self.export_button = QPushButton("Create Report")
        self.export_button.setObjectName("export_button")
        group_layout.addWidget(self.export_button)

        self.layout.addWidget(self.export_config_group)

    # FUNCTIONS FOR DIAPLAYING BACKEND DATA #
    def populate_selected_api_keys_table(self):
        """
        Loads the selected API key data from the
        db & populates the API key table.

        This function should:
        1. Call _get_selected_api_keys to store all API key data.
        2. Create as many rows as there are selected API key entries in the db.
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

        def add_api_key_row_to_table(row: int, api_key: dict):
            """
            Adds a singular API key into a specific row in the
            API key table.

            This function should:
            1. Populate a table row with the following data:
                a. Column1: key_name.
                b. Column2: the masked key_value for security.
                c. Column3: status (a non-pushable button for styling).
                d. Column4: a remove button.
            """
            self.api_keys_table.setItem(
                row, 0, QTableWidgetItem(api_key["key_name"])
            )

            plaintext_api_key = api_key["key_value"]
            self.api_keys_table.setItem(
                row, 1, QTableWidgetItem(mask_key_value(plaintext_api_key))
            )

            status_button = QPushButton(api_key["status"])
            status_button.setEnabled(False)
            self.api_keys_table.setCellWidget(row, 2, status_button)

            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(
                lambda checked, k_id=api_key["id"]: self.remove_api_key(k_id)
            )
            self.api_keys_table.setCellWidget(row, 3, remove_button)

        selected_api_keys = _get_selected_api_keys()

        self.api_keys_table.setRowCount(0)
        self.api_keys_table.setRowCount(len(selected_api_keys))

        for row, api_key in enumerate(selected_api_keys):
            add_api_key_row_to_table(row, api_key)

        integrate_api_keys_group_styling(self)

    def populate_selected_scans_table(self):
        """
        Loads the selected scan data from the db
        and populates the scans table.

        This funciton should:
        1. Call _get_selected_scans to store all scan data.
        2. create as many rows as there are selected scan entries in the db.
        3. Re-initialize the styling for the table to style new entry.
        """
        def return_unique_cve_list_ct(unique_cve_list: str) -> int:
            """
            Given the string of unique cves, return the count of
            cves in the string.

            This function should:
            1. Split the string by every ", ".
            2. Return the count of splits.
            """
            return (len(unique_cve_list.split(", ")))

        def add_scan_row_to_table(row: int, scan: dict):
            """
            Adds a singular scan into a specific row in the scan table.

            This function should:
            1. Populate a table row with the following data:
                a. Column1: scan_name.
                b. Column2: total_vulnerabilities.
                c. Column3: unique_cve_list count.
                d. Column4: cache_enabled (a non-pushable button for styling)
                e. Column5: cached_percentage.
                f. Column6: a remove button.
            """
            self.scans_table.setItem(
                row, 0, QTableWidgetItem(scan["scan_name"])
            )

            total_vulns_str = str(scan["total_vulnerabilities"])
            self.scans_table.setItem(
                row, 1, QTableWidgetItem(total_vulns_str)
            )

            unique_cves_ct = return_unique_cve_list_ct(scan["unique_cve_list"])
            unique_cves_ct_str = str(unique_cves_ct)
            self.scans_table.setItem(
                row, 2, QTableWidgetItem(unique_cves_ct_str)
            )

            cache_button = QPushButton(scan["cache_enabled"])
            cache_button.setEnabled(False)
            self.scans_table.setCellWidget(row, 3, cache_button)

            cached_perc_str = f"{scan["cached_percentage"]}%"
            cached_perc_button = QPushButton(cached_perc_str)
            cached_perc_button.setEnabled(False)
            self.scans_table.setCellWidget(row, 4, cached_perc_button)

            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(
                lambda checked, s_id=scan["id"]: self.remove_scan(s_id)
            )
            self.scans_table.setCellWidget(row, 5, remove_button)

        selected_scans = _get_selected_scans()

        self.scans_table.setRowCount(0)
        self.scans_table.setRowCount(len(selected_scans))

        for row, scan in enumerate(selected_scans):
            add_scan_row_to_table(row, scan)

        integrate_scans_group_styling(self)

    # FUNCTIONS FOR ACTION BUTTONS ON WINDOW #
    def remove_api_key(self, id):
        """
        Removes an API key when the user clicks the "Remove" button
        for an API key by changing the selected field to "0" and refreshing
        the table.

        This function should:
        1. Call _remove_api_key to remove the API key from the table.
        2. Refresh the API keys table to show the updated data.
        """
        success, message = _remove_api_key(id)

        if success:
            self.populate_selected_api_keys_table()

    def remove_scan(self, id):
        """
        Removes a scan when the user clicks the "Remove" button for the scan
        by changing the selected field to "0" and refreshing the table.

        This function should:
        1. Call _remove_scan to remove the scan from the table.
        2. Refresh the scans table to show the updated data.
        """
        success, message = _remove_scan(id)

        if success:
            self.populate_selected_scans_table()
