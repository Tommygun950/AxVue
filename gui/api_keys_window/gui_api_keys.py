"""
This file is used to construct the API Keys window in the GUI.
"""

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton,
    QToolBar, QAction, QLabel, QHBoxLayout,
    QGroupBox
)

class ApiKeysWindow(QMainWindow):
    """Main window for API Keys page."""
    def __init__(self):
        """
        This function initializes the api keys page & features.

        This function should:
        1. Initialize the toolbar.
        2. create the vertical layout for all of the widgets.
        3. Establish the following widgets:
            a. An excerpt/summery on this page.
            b. Table of scans.
            c. A list of buttons:
                1. Add API Key.
        """
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer - Scans")
        self.resize(1200, 800)

        self.init_toolbar()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_scans_summary()
        self.init_api_keys_section()

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

    def init_scans_summary(self):
        """
        Initializes the summary for the page.

        this function should:
        1. Creates a QGroupBox with the following:
            a. Title of "API Keys Summary".
            b. The inclusion of the summary text.
        2. Displays the layout on the main layout.
        """
        self.api_keys_summary_group = QGroupBox("API Keys Summary")
        group_layout = QVBoxLayout(self.api_keys_summary_group)

        summary_text = (
            "On this page, you can add and manage your NVD API Keys. To add an API key, click the 'Add API Key' "
            "button at the bottom of this page. You'll need to provide a name for your key and the actual API key value. "
            "Important features:\n"
            " 1. The program automatically validates your API keys by checking for 404 errors when connecting to the NVD API.\n"
            " 2. You can add multiple API keys to ensure report generation continues even if one key becomes invalid.\n"
            " 3. To use an API key, select the checkbox to the left of the key entry in the table.\n"
            " 4. Using multiple API keys will not speed up report generation, but provides redundancy in case a key fails.\n"
            " 5. After adding an API key to the table, you can edit or delete it using the corresponding buttons in its row.\n"
            "Selected API keys will be used when generating vulnerability reports from your scan data."
        )

        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        group_layout.addWidget(summary_label)
        
        self.layout.addWidget(self.api_keys_summary_group)

    def init_api_keys_section(self):
        """
        Initializes the section for the api keys.

        This function should:
        1. Create a QGroupBox layout.
        2. Create a QVBoxLayout layout with the following:
            a. Horizontal button layout.
            b. API Keys table.
        3. Add The QVBoxLayout to the QGroupBox.
        4. Add QGroupBox to the main layout for the page.
        """
        api_keys_group = QGroupBox("API Keys")
        api_keys_layout = QVBoxLayout(api_keys_group)

        def init_button_layout(self):
            """
            Initilizes the button layout at the bottom of the window.

            The function should:
            1. Create a horizontal layout for the buttons.
            2. Create the following buttons:
                a. Add API Key.
            3. Ensure resizing of the buttons do the following:
                a. Add API Key -> Stretch.
            4. Add button layout to the main layout.
            """
            button_layout = QHBoxLayout()

            self.add_scan_button = QPushButton("Add API Key")
            button_layout.addWidget(self.add_scan_button)

            api_keys_layout.addLayout(button_layout)

        def init_api_keys_table(self):
            """
            Initializes the table to display the api keys.

            This function should:
            1. Setup a table widget with the following columns:
                a. Key Name.
                b. Key Value.
                c. Status.
            2. Ensure the resising of the columns do the following:
                a. Key Name -> Stretch.
                b. Key Value -> Stretch.
                c. Status -> Resize to Contents.
            3. Add the label and table widget to the layout.
            """
            self.scan_table = QTableWidget()
            self.scan_table.setColumnCount(3)

            self.scan_table.setHorizontalHeaderLabels([
                "Key Name", "Key Value", "Status"
            ])

            self.scan_table.setEditTriggers(QTableWidget.NoEditTriggers)

            header = self.scan_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

            api_keys_layout.addWidget(self.scan_table)

        init_button_layout(self)
        init_api_keys_table(self)
        self.layout.addWidget(api_keys_group)

if __name__ == "__main__":
    app = QApplication([])
    window = ApiKeysWindow()
    window.show()
    app.exec_()