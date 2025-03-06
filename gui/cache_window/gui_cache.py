"""This file is responsible for the layout of th Create Report window."""
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QToolBar, QAction, QLabel,
    QHBoxLayout, QGroupBox, QComboBox, QCheckBox
)
from PyQt5.QtCore import pyqtSignal

class CacheWindow(QMainWindow):
    """Main window for the cache page"""
    def __init__(self):
        """
        This function initializes the cache page & features.

        This function should:
        1. Initialize the toolbar.
        2. Create the vertical layout for all of the widgets.
        3. Establish the following widgets:
            a. Queried NVD Data Feed section.
            b. Stored NVD Data Feed section.
            c. A QHBoxLayout with the following:
                1. Pre-cache scan section.
                2. List of cached cves.
        """
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer")
        self.resize(1200, 800)

        self.nvd_api_key = ""

        self.init_toolbar()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_queried_data_feed_section()
        self.init_stored_data_feed_section()

        h_layout = QHBoxLayout()

        pre_cache_widget = self.init_pre_cache_scan_section()
        cached_cves_widget = self.init_cached_cves_section()

        h_layout.addWidget(pre_cache_widget)
        h_layout.addWidget(cached_cves_widget)

        self.layout.addLayout(h_layout)

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

    def init_queried_data_feed_section(self):
        """
        Initializes the section to display queried data feeds.

        This function should:
        1. Create a QGroupBox with the label "NVD Data Feed Selection".
        2. Add the following to a QVBoxLayout:
            a. Intitialize a horizontal button layout.
            b. Initialize a table for queried feed data.
        3. Add the QGroupBox to the main layout.
        """
        self.queried_nvd_data_group = QGroupBox("NVD Data Feed Selection")
        group_layout = QVBoxLayout(self.queried_nvd_data_group)

        def init_button_layout():
            """
            Initializes the button layout within the group box.
    
            This function should:
            1. Initialize a QHBoxLayout.
            2. Estbalish the following buttons:
                a. Query Data Feeds.
            3. Add the button to the QHBoxLayout.
            4. Add the QHBoxLayout to the QVBoxLayout.
            """
            button_layout = QHBoxLayout()

            self.refresh_button = QPushButton("Query Data Feeds")

            button_layout.addWidget(self.refresh_button)

            group_layout.addLayout(button_layout)

        def init_queried_feed_table():
            """
            Initializes the table to display the queried NVD data feeds.

            This function should:
            1. Setup a table widget wit the following columns:
                a. Year.
                b. File Size.
                c. Last Queried.
                d. Status.
            2. Ensure the resising of the columns do the following:
                a. Year -> Stretch.
                b. File Size -> Stretch.
                c. Last QUeried -> Stretch.
                d. Status -> Resize to Contents.
            3. Add the table to the QVBoxLayout.
            """
            self.queried_feed_table = QTableWidget()
            self.queried_feed_table.setColumnCount(4)
            self.queried_feed_table.setHorizontalHeaderLabels(["Year", "File Size", "Last Queried", "Status"])
            self.queried_feed_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            header = self.queried_feed_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            
            group_layout.addWidget(self.queried_feed_table)

        init_button_layout()
        init_queried_feed_table()

        self.layout.addWidget(self.queried_nvd_data_group)

    def init_stored_data_feed_section(self):
        """
        Initializes the section to display stored data feeds.

        This function should:
        1. Create a QGroupBox with the label "Stored NVD Data Feeds".
        2. Add the following to a QVBoxLayout:
            a. Intitialize a horizontal button layout.
            b. Initialize a table for stored feed data.
        3. Add the QGroupBox to the main layout.
        """
        self.stored_nvd_data_group = QGroupBox("Stored NVD Data Feeds")
        group_layout = QVBoxLayout(self.stored_nvd_data_group)

        def init_button_layout():
            """
            Initializes the button layout within the group box.
    
            This function should:
            1. Initialize a QHBoxLayout.
            2. Estbalish the following buttons:
                a. Check for Updates.
                a. Clear Data Feeds.
            3. Add the button to the QHBoxLayout.
            4. Add the QHBoxLayout to the QVBoxLayout.
            """
            button_layout = QHBoxLayout()

            self.check_for_updates_button = QPushButton("Check For Updates")
            self.clear_button = QPushButton("Clear Data Feeds")

            button_layout.addWidget(self.check_for_updates_button)
            button_layout.addWidget(self.clear_button)

            group_layout.addLayout(button_layout)

        def init_stored_feed_table():
            """
            Initializes the table to display the stored NVD data feeds.

            This function should:
            1. Setup a table widget wit the following columns:
                a. Year.
                b. File Size.
                c. CVE Count.
                d. Last Updated.
                e. Status.
                f. Cache.
            2. Ensure the resising of the columns do the following:
                a. Year -> Stretch.
                b. File Size -> Stretch.
                c. CVE Count -> Resize to Contents.
                d. Last Updated -> Resize to Contents.
                e. Status -> Resize to Contents.
                f. Cache -> Resize to Contetns.
            3. Add the table to the QVBoxLayout.
            """
            self.stored_feed_table = QTableWidget()
            self.stored_feed_table.setColumnCount(6)
            self.stored_feed_table.setHorizontalHeaderLabels([
                "Year", "File Size", "CVE Count", "Last Updated", "Status", "Cache"
            ])
            self.stored_feed_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            header = self.stored_feed_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

            group_layout.addWidget(self.stored_feed_table)

        init_button_layout()
        init_stored_feed_table()

        self.layout.addWidget(self.stored_nvd_data_group)

    def init_pre_cache_scan_section(self):
        """
        Initializes the section to display scans with cache enabled.
        """
        pre_cache_group = QGroupBox("Pre Cache Scans")
        group_layout = QVBoxLayout(pre_cache_group)

        def init_button_layout():
            button_layout = QHBoxLayout()
            self.clear_cve_cache_button = QPushButton("Clear Scan CVEs")
            button_layout.addWidget(self.clear_cve_cache_button)
            group_layout.addLayout(button_layout)

        def init_pre_cache_scan_table():
            self.pre_cache_scan_table = QTableWidget()
            self.pre_cache_scan_table.setColumnCount(4)
            self.pre_cache_scan_table.setHorizontalHeaderLabels([
                "Scan name", "Unique CVE IDs", "Cache %", "Cache"
            ])
            self.pre_cache_scan_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            header = self.pre_cache_scan_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

            group_layout.addWidget(self.pre_cache_scan_table)

        init_button_layout()
        init_pre_cache_scan_table()
        return pre_cache_group

    def init_cached_cves_section(self):
        """
        Initializes the section to display cached CVEs.
        """
        cached_cves_group = QGroupBox("Cached CVEs")
        group_layout = QVBoxLayout(cached_cves_group)

        def init_button_layout():
            button_layout = QHBoxLayout()
            self.clear_cve_cache_button = QPushButton("Clear Entire Cache")
            button_layout.addWidget(self.clear_cve_cache_button)
            group_layout.addLayout(button_layout)

        def init_cached_cves_table():
            self.cached_cves_table = QTableWidget()
            self.cached_cves_table.setColumnCount(2)
            self.cached_cves_table.setHorizontalHeaderLabels(["CVE ID", "Remove"])
            self.cached_cves_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            header = self.cached_cves_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

            group_layout.addWidget(self.cached_cves_table)

        init_button_layout()
        init_cached_cves_table()
        return cached_cves_group

if __name__ == "__main__":
    app = QApplication([])
    window = CacheWindow()
    window.show()
    app.exec_()