"""
This file is used to construct the Scans window in the GUI.
"""

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QToolBar, QAction, QLabel, QHBoxLayout,
    QGroupBox
)

class ScansWindow(QMainWindow):
    """Main window for Scans page."""
    def __init__(self):
        """
        This function initializes the scans page & features.

        This function should:
        1. Initialize the toolbar.
        2. create the vertical layout for all of the widgets.
        3. Establish the following widgets:
            a. An excerpt/summery on this page.
            b. Table of scans.
            c. A list of buttons:
                1. Add Scan.
        """
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer - Scans")
        self.resize(1200, 800)

        self.init_toolbar()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_scans_summary()
        self.init_scans_table()
        self.init_button_layout()

    def init_toolbar(self):
        """Creates a toolbar with actions."""
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

    def init_scans_summary(self):
        """
        Initializes the summary for the page.

        this function should:
        1. Creates a QGroupBox with the following:
            a. Title of "Scans Summary".
            b. The inclusion of the summary text.
        2. Displays the layout on the main layout.
        """
        self.exports_summary_group = QGroupBox("Exports Summary")
        group_layout = QVBoxLayout(self.exports_summary_group)

        summary_text = (
            "On this page, you have the ability to add and manage your csv scan "
            "exports. To add a scan to this list, select the 'Add Scan' button "
            "at the bottom of this page. The only information you need to enter is "
            "your desired name for the scan data and the filepath to your csv export. "
            "Important features:\n"
            " 1. This program will automatically calculate the number of total and "
            "unique cve ids.\n"
            " 2. The cached percentage is how much of your scan data is already stored "
            " within the cve CVSS metric database, which saves time when creating a report.\n"
            " 3. If you're concerned with caching critical vulnerability data to your system, "
            "You can either enable or disable caching for any new vulnerabilities within your "
            "csv scan file.\n"
            " 4. After adding a scan to the table, you may delete or edit any of the informaiton "
            "by selecting the desired row's 'Edit' or 'Delete' button.\n"
            "To create a report with your desired scans, click the checkmark to the left of the "
            "scan(s) and they will popup within the 'Create Report' window ready for export. "
        )

        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        group_layout.addWidget(summary_label)
        
        self.layout.addWidget(self.exports_summary_group)

    def init_scans_table(self):
        """
        Initializes the table to display the scans.

        This function should:
        1. Create the label "Scans: ".
        2. Setup a table widget with the following columns:
            a. Scan Name.
            b. File Path.
            c. Total CVE IDs.
            d. Unique CVE IDs.
            e. Cache.
            f. Edit.
            g. Delete.
        3. Ensure the resising of the columns do the following:
            a. Scan name -> Stretch.
            b. File Path -> Stretch.
            c. Total CVE IDs -> Resize to Contents.
            d. Unique CVE IDs -> Resize to Contents.
            e. Cache -> Resize to Contents.
            f. Edit -> Resize to Contents.
            g. Delete -> Resize to Contents.
        4. Add the label and table widget to the layout.
        """
        scans_label = QLabel("Scans:")

        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(8)

        self.scan_table.setHorizontalHeaderLabels([
            "Scan Name", "File Path", "Total CVE IDs",
            "Unique CVE IDs", "Cache", "Cached %", "Edit", "Delete"
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
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

        self.layout.addWidget(scans_label)
        self.layout.addWidget(self.scan_table)
    
    def init_button_layout(self):
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
        self.layout.addWidget(self.add_scan_button)

        self.layout.addLayout(button_layout)

if __name__ == "__main__":
    app = QApplication([])
    window = ScansWindow()
    window.show()
    app.exec_()