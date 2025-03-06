"""This code is the main file for the gui feature."""
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QToolBar, QAction
)

from .create_report_window.gui_create_report import MainWindow as CreateReportWindow
from .exports_window.gui_exports import ExportsWindow
from .scans_window.gui_scans import ScansWindow
from .api_keys_window.gui_api_keys import ApiKeysWindow
from .cache_window.gui_cache import CacheWindow

class MainAppWindow(QMainWindow):
    """
    Main application window that contains all pages in a stacked widget.

    This function should:
    1. Establish the name & window size of the gui.
    2. Create a stacked widget to allow for multiple pages.
    3. Initialize the page instances for the following:
        a. 1. Scans.
        b. 2. API Keys.
        c. 3. Cache.
        d. 4. Create Report
        e. 5. Exports
    4. Add those pages to the stacked widget.
    5. Initialize the toolbar with the buttons to access thos pages.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer")
        self.resize(1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.scans_page = ScansWindow()
        self.api_keys_page = ApiKeysWindow()
        self.cache_page = CacheWindow()
        self.create_report_page = CreateReportWindow()
        self.exports_page = ExportsWindow()

        self.stacked_widget.addWidget(self.scans_page.central_widget)
        self.stacked_widget.addWidget(self.api_keys_page.central_widget)
        self.stacked_widget.addWidget(self.cache_page.central_widget)
        self.stacked_widget.addWidget(self.create_report_page.central_widget)
        self.stacked_widget.addWidget(self.exports_page.central_widget)

        self.init_toolbar()

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
        scans_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        api_keys_action = QAction("2. API Keys", self)
        api_keys_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        cache_action = QAction("3. Cache", self)
        cache_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(2))
   
        create_report_action = QAction("4. Create Report", self)
        create_report_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        
        exports_action = QAction("5. Exports", self)
        exports_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        
        toolbar.addAction(scans_action)
        toolbar.addAction(api_keys_action)
        toolbar.addAction(cache_action)
        toolbar.addAction(create_report_action)
        toolbar.addAction(exports_action)

if __name__ == "__main__":
    app = QApplication([])
    window = MainAppWindow()
    window.show()
    app.exec_()
