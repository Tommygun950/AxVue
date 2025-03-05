"""This file is responsible for the layout of th Create Report window."""
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QToolBar, QAction, QLabel,
    QHBoxLayout, QGroupBox, QComboBox, QCheckBox
)
from PyQt5.QtCore import pyqtSignal

class MainWindow(QMainWindow):
    """Main window for the create report page"""
    exportTriggered = pyqtSignal(str, list, str, list)

    def __init__(self):
        """
        This function initializes the create report page & features.

        This function should:
        1. Initialize the toolbar.
        2. Create the vertical layout for all of the widgets.
        3. Establish the following widgets:
            a. List of selected NVD API keys.
            b. List of selected Scans.
            c. Export configuration box.
        """
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer")
        self.resize(1200, 800)

        self.nvd_api_key = ""

        self.init_toolbar()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_api_key_table()
        self.init_scans_table()
        self.init_export_config()

    def init_toolbar(self):
        """
        Creates a toolbar with actions.

        This function should:
        1. Create the main toolbar.
        2. Create the following buttons:
            a. Create Report.
            b. Exports.
            c. Scans.
            d. API Keys.
            e. Cache.
        3. Add the buttons to the toolbar.
        """
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        create_report_action = QAction("Create Report", self)
        exports_action = QAction("Exports", self)
        scans_action = QAction("Scans", self)
        api_keys_action = QAction("API Keys", self)
        cache_action = QAction("Cache", self)
        
        toolbar.addAction(create_report_action)
        toolbar.addAction(exports_action)
        toolbar.addAction(scans_action)
        toolbar.addAction(api_keys_action)
        toolbar.addAction(cache_action)

    def init_api_key_table(self):
        """
        Creates the selected api keys table.

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
        self.api_key_label = QLabel("Selected API Keys:")

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

        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_table)

    def init_scans_table(self):
        """
        Creates the selected scans table.

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
        self.scan_label = QLabel("Selected Scans:")

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

        self.layout.addWidget(self.scan_label)
        self.layout.addWidget(self.scan_table)

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

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()