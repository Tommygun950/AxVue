"""This file is responsible for the layout of th Create Report window."""
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QToolBar, QAction, QLabel,
    QHBoxLayout, QGroupBox, QComboBox, QCheckBox
)

class MainWindow(QMainWindow):
    """Main window for the create report page"""
    def __init__(self):
        """
        This function initializes the create report page & features.

        This function should:
        1. Create the vertical layout for all of the widgets.
        2. Establish the following widgets:
            a. List of selected NVD API keys.
            b. List of selected Scans.
            c. Export configuration box.
        """
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_api_key_section()
        self.init_scans_section()
        self.init_export_config()

    def init_toolbar(self):
        """
        Creates a toolbar with actions to switch between pages.

        This function should:
        1. Create the main toolbar.
        2. Create the following buttons:
            a. 1. Scans -> opens ScansWindow.
            b. 2. API Keys -> opens ApiKeysWindow.
            c. 3. Cache -> opens CacheWindow.
            d. 4. Create report -> opens CreateReportWindow.
            e. 5. Exports -> opens ExportsWindow.
        3. Add the buttons to the toolbar.
        """
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        scans_action = QAction("1. Scans", self)
        api_keys_action = QAction("2. API Keys", self)
        cache_action = QAction("3. Cache", self)   
        create_report_action = QAction("4. Create Report", self)        
        exports_action = QAction("5. Exports", self)
        
        toolbar.addAction(scans_action)
        toolbar.addAction(api_keys_action)
        toolbar.addAction(cache_action)
        toolbar.addAction(create_report_action)
        toolbar.addAction(exports_action)

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
        api_key_group = QGroupBox("Selected API Keys:")
        group_layout = QVBoxLayout(api_key_group)

        self.api_key_table = QTableWidget()
        self.api_key_table.setColumnCount(4)
        self.api_key_table.setHorizontalHeaderLabels([
            "Key Name", "Value", "Status", "Remove"
        ])
        self.api_key_table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.api_key_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        group_layout.addWidget(self.api_key_table)
        self.layout.addWidget(api_key_group)

    def init_scans_section(self):
        """
        Creates the selected scans section.

        This function should:
        1. Create the label "Selected Scans: ".
        2. Setup a table widget with the following columns:
            a. Scan Name.
            b. File Path.
            c. Total CVE IDs.
            d. Unique CVE IDs.
            e. Cache.
            f. Cached %.
            g. Remove.
        3. Ensure the resizing of the columns do the following:
            a. Scan Name -> Stretch.
            b. File Path -> Stretch.
            c. Total CVE IDS -> Resize to Contents.
            d. Unique CVE IDs -> Resize to Contents.
            e. Cache -> Resize to Contents.
            f. Cached % -> Resize to Contents.
            g. Remove -> Resize to Contents.
        4. Add the label and the table widget to the layout.
        """
        scans_group = QGroupBox("Selected Scans:")
        group_layout = QVBoxLayout(scans_group)

        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(7)
        self.scan_table.setHorizontalHeaderLabels([
            "Scan Name", "File Path", "Total CVE IDs",
            "Unique CVE IDs", "Cache", "Cached %", "Remove"
        ])

        self.scan_table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.scan_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        group_layout.addWidget(self.scan_table)
        self.layout.addWidget(scans_group)

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
        for page in ["KEV Catalog Comparison", "Base Metrics", "Temporal Metrics"]:
            checkbox = QCheckBox(page)
            checkbox.setChecked(True)
            self.page_checkboxes[page] = checkbox
            group_layout.addWidget(checkbox)

        self.export_button = QPushButton("Create Report")
        group_layout.addWidget(self.export_button)

        self.layout.addWidget(self.export_config_group)
