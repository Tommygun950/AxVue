"""This code is the main file for the gui feature."""
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QToolBar, QAction
)

from .create_report_window.gui_create_report import CreateReportWindow
from .exports_window.gui_exports import ExportsWindow
from .scans_window.gui_scans import ScansWindow
from .api_keys_window.gui_api_keys import APIKeysWindow
from .cache_window.gui_cache import CacheWindow
from .style_gui import integrate_toolbar_styling


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
    5. Initialize the toolbar with the buttons to access those pages.
    6. Apply styling to the toolbar.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer")
        self.resize(1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.scans_page = ScansWindow()
        self.api_keys_page = APIKeysWindow()
        self.cache_page = CacheWindow()
        self.create_report_page = CreateReportWindow()
        self.exports_page = ExportsWindow()

        self.stacked_widget.addWidget(self.scans_page.central_widget)
        self.stacked_widget.addWidget(self.api_keys_page.central_widget)
        self.stacked_widget.addWidget(self.cache_page.central_widget)
        self.stacked_widget.addWidget(self.create_report_page.central_widget)
        self.stacked_widget.addWidget(self.exports_page.central_widget)

        self.init_toolbar()
        integrate_toolbar_styling(self)

    def init_toolbar(self):
        """
        Creates a toolbar with actions to switch between pages.

        This function should:
        1. Create the main toolbar.
        2. Create the following buttons:
            a. 1. Scans -> opens ScansWindow.
            b. 2. API Keys -> opens APIKeysWindow.
            c. 3. Cache -> opens CacheWindow.
            d. 4. Create report -> opens CreateReportWindow.
            e. 5. Exports -> opens ExportsWindow.
        3. Add the buttons to the toolbar.
        4. Store the toolbar as an instance variable so it can be styled.
        """
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        def create_page_action(text, index):
            action = QAction(text, self)
            action.triggered.connect(
                lambda: self.switch_page(index)
            )
            return action

        scans_action = create_page_action("1. Scans", 0)
        api_keys_action = create_page_action("2. API Keys", 1)
        cache_action = create_page_action("3. Cache", 2)
        create_report_action = create_page_action("4. Create Report", 3)
        exports_action = create_page_action("5. Exports", 4)

        self.toolbar.addAction(scans_action)
        self.toolbar.addAction(api_keys_action)
        self.toolbar.addAction(cache_action)
        self.toolbar.addAction(create_report_action)
        self.toolbar.addAction(exports_action)

    def switch_page(self, index):
        """
        Switch to the specified page index and update toolbar action states.
        If switching to the Create Report page, refresh its tables.

        This function should:
        1. Set the current index of the stacked widget.
        2. Update the checked state of all actions to match the current page.
        3. If switching to Create Report page, refresh its tables.
        """
        self.stacked_widget.setCurrentIndex(index)

        for i, action in enumerate(self.toolbar.actions()):
            action.setChecked(i == index)

        if index == 0:
            self.scans_page.populate_scans_table()
        elif index == 1:
            self.api_keys_page.populate_api_keys_table()
        elif index == 3:
            self.create_report_page.populate_selected_api_keys_table()
            self.create_report_page.populate_selected_scans_table()


if __name__ == "__main__":
    app = QApplication([])
    window = MainAppWindow()
    window.show()
    app.exec_()
