"""This code is the main file for the gui feature."""
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QToolBar, QAction
)

from create_report_window.gui_create_report import MainWindow as CreateReportWindow
from exports_window.gui_exports import ExportsWindow
from scans_window.gui_scans import ScansWindow
from api_keys_window.gui_api_keys import ApiKeysWindow
from cache_window.gui_cache import CacheWindow

class MainAppWindow(QMainWindow):
    """
    Main application window that contains all pages in a stacked widget.

    This function should:
    1. Establish the name & window size of the gui.
    2. Create a stacked widget to allow for multiple pages.
    3. Initialize the page instances for the following:
        a. Create Report.
        b. Exports.
        c. Scans.
        d. API Keys.
        e. Cache.
    4. Add those pages to the stacked widget.
    5. Initialize the toolbar with the buttons to access thos pages.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer")
        self.resize(1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.create_report_page = CreateReportWindow()
        self.exports_page = ExportsWindow()
        self.scans_page = ScansWindow()
        self.api_keys_page = ApiKeysWindow()
        self.cache_page = CacheWindow()

        self.stacked_widget.addWidget(self.create_report_page.central_widget)
        self.stacked_widget.addWidget(self.exports_page.central_widget)
        self.stacked_widget.addWidget(self.scans_page.central_widget)
        self.stacked_widget.addWidget(self.api_keys_page.central_widget)
        self.stacked_widget.addWidget(self.cache_page.central_widget)

        self.init_toolbar()

    def init_toolbar(self):
        """
        Creates a toolbar with actions to switch between pages.

        This function should:
        1. Create the main toolbar.
        2. Create the following buttons:
            a. Create Report -> opens CreateReportWindow.
            b. Exports -> opens ExportsWindow.
            c. Scans -> opens ScansWindow.
            d. Api Keys -> opens ApiKeysWindow.
            e. Cache -> opens CacheWindow.
        3. Add the buttons to the toolbar.
        """
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        create_report_action = QAction("Create Report", self)
        create_report_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        exports_action = QAction("Exports", self)
        exports_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        scans_action = QAction("Scans", self)
        scans_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        
        api_keys_action = QAction("API Keys", self)
        api_keys_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        
        cache_action = QAction("Cache", self)
        cache_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        
        toolbar.addAction(create_report_action)
        toolbar.addAction(exports_action)
        toolbar.addAction(scans_action)
        toolbar.addAction(api_keys_action)
        toolbar.addAction(cache_action)

if __name__ == "__main__":
    app = QApplication([])
    window = MainAppWindow()
    window.show()
    app.exec_()
