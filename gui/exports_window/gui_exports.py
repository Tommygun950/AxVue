"""
This file is used to construct the Exports window in the GUI.
"""
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QGroupBox,
    QLabel
)

class ExportsWindow(QMainWindow):
    """Main window for Exports page."""
    def __init__(self):
        """
        This function initializes the exports page & features.

        This function should:
        1. Create the vertical layout for all of the widgets.
        2. Establish the following widgets:
            a. An exerpt/summary on this page.
            b. Table of past exports.
        """
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_past_exports_summary()
        self.init_past_exports_section()

    def init_past_exports_summary(self):
        """
        Initializes the summary for the page.

        this function should:
        1. Creates a QGroupBox with the following:
            a. Title of "Exports Summary".
            b. The inclusion of the summary text.
        2. Displays the layout on the main layout.
        """
        self.exports_summary_group = QGroupBox("Exports Summary")
        group_layout = QVBoxLayout(self.exports_summary_group)

        summary_text = (
            "Each report in the table below is accompanied by detailed metadata, including the report's name, "
            "the number of scans incorporated, the export type, and the date of creation. To download a report, "
            "simply click the 'Export' button in the corresponding row. If you wish to remove a report from your history, "
            "click the 'Delete' button. This interface is designed to provide a clear, organized, and efficient way to review "
            "and manage your export history."
        )

        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        group_layout.addWidget(summary_label)
        
        self.layout.addWidget(self.exports_summary_group)

    def init_past_exports_section(self):
        """
        Initializes the past exports table.

        This function should:
        1. Create a QGroupBox with the title "Past Exports".
        2. Setup a table widget with the following columns:
            a. Export Name.
            b. # of Scans.
            c. Export Type.
            d. Export Date.
            e. Export.
            f. Delete.
        3. Ensure the resizing of the columns do the following:
            a. Export name -> Stretch.
            b. # of Scans -> Stretch.
            c. Export Type -> Stretch.
            d. Export Date -> Stretch.
            e. Export -> Resize to Contents.
            f. Delete -> Resize to Contents.
        4. Add the table to the QGroupBox.
        """
        past_exports_group = QGroupBox("Past Exports")
        group_layout = QVBoxLayout(past_exports_group)

        self.past_exports_table = QTableWidget()
        self.past_exports_table.setColumnCount(6)
        self.past_exports_table.setHorizontalHeaderLabels([
            "Export Name", "# of Scans", "Export Type",
            "Export Date", "Export", "Delete"
        ])

        self.past_exports_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.past_exports_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.past_exports_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.past_exports_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.past_exports_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.past_exports_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)

        group_layout.addWidget(self.past_exports_table)
        self.layout.addWidget(past_exports_group)
