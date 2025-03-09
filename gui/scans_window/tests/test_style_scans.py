"""
File for testing the functionality of style_scans.py.
"""
import sys
import pytest
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGroupBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QVBoxLayout, QLabel
)
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
from gui.scans_window.style_scans import (
    style_scans_window, style_group_box, style_add_scan_button,
    style_scan_table, style_table_buttons, integrate_window_styling,
    integrate_summary_group_styling, integrate_scans_group_styling
)


# FIXTURES FOR TESTING #


@pytest.fixture
def app():
    """Create a QApplication instance for the tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_window():
    """
    Creates a mock window with the necessary components for styling tests.

    This fixture creates a QMainWindow with:
    1. central_widget
    2. scans_summary_group
    3. scans_group
    4. add_scan_button
    5. scan_table with sample data
    """
    window = QMainWindow()
    window.central_widget = QWidget()
    window.setCentralWidget(window.central_widget)

    main_layout = QVBoxLayout(window.central_widget)

    window.scans_summary_group = QGroupBox("Scans Summary")
    summary_layout = QVBoxLayout(window.scans_summary_group)
    summary_layout.addWidget(QLabel("Total Scans: 2"))
    main_layout.addWidget(window.scans_summary_group)

    window.scans_group = QGroupBox("Scans")
    scans_layout = QVBoxLayout(window.scans_group)

    button_layout = QHBoxLayout()
    window.add_scan_button = QPushButton("Add Scan")
    button_layout.addWidget(window.add_scan_button)
    button_layout.addStretch()
    scans_layout.addLayout(button_layout)

    window.scan_table = QTableWidget(2, 8)
    window.scan_table.setHorizontalHeaderLabels([
        "ID", "Name", "Path", "Size", "Date Added", "Cache", "Edit", "Delete"
    ])

    for row in range(2):
        window.scan_table.setItem(
            row, 0, QTableWidgetItem(str(row + 1))
        )
        window.scan_table.setItem(
            row, 1, QTableWidgetItem(f"Scan {row + 1}")
        )
        window.scan_table.setItem(
            row, 2, QTableWidgetItem(f"/path/to/scan{row + 1}.csv")
        )
        window.scan_table.setItem(
            row, 3, QTableWidgetItem(f"{(row + 1) * 100} KB")
        )
        window.scan_table.setItem(
            row, 4, QTableWidgetItem("2023-01-01")
        )
        window.scan_table.setItem(
            row, 5, QTableWidgetItem("Enabled")
        )

        edit_button = QPushButton("Edit")
        delete_button = QPushButton("Delete")
        window.scan_table.setCellWidget(row, 6, edit_button)
        window.scan_table.setCellWidget(row, 7, delete_button)

    scans_layout.addWidget(window.scan_table)
    main_layout.addWidget(window.scans_group)

    def populate_scans_table():
        pass

    window.populate_scans_table = populate_scans_table

    return window


# TESTS FOR TestStyleScansWindow #


class TestStyleScansWindow:
    def test_style_scans_window(self, app, mock_window):
        """
        Test that style_scans_window correctly applies styling to the window.

        This function should:
        1. Apply the style_scans_window function to the mock window.

        This function tests:
        1. The window color is set to the expected value (#e7e2f3).
        2. Auto fill background is enabled.
        3. The palette is applied to the central widget.
        """
        style_scans_window(mock_window)  # 1.

        palette = mock_window.central_widget.palette()
        window_color = palette.color(QPalette.Window)

        assert [  # Test 1.
            window_color.name() == "#e7e2f3",
            f"""
                Window color is incorrect. Expected: #e7e2f3,
                Got: {window_color.name()}
            """
        ]

        assert [  # Test 2.
            mock_window.central_widget.autoFillBackground() is True,
            "Auto fill background should be enabled."
        ]

        assert [  # Test 3.
            palette == mock_window.central_widget.palette(),
            "Palette was not applied correctly to the central widget."
        ]


# TESTS FOR TestStyleGroupBox #


class TestStyleGroupBox:
    def test_style_group_box(self, app, mock_window):
        """
        Test that style_group_box correctly applies styling to a QGroupBox.

        This function should:
        1. Apply the style_group_box function to the scans_summary_group.

        This function tests:
        1. The styleSheet property of the group box is not empty.
        2. The styleSheet contains the expected title
        background color (#2d3c67).
        3. The styleSheet contains the expected title text color (#e7e2f3).
        4. The styleSheet contains styling for QGroupBox QLabel.
        """
        group_box = mock_window.scans_summary_group
        style_group_box(group_box)  # 1.

        style_sheet = group_box.styleSheet()

        assert [  # Test 1.
            style_sheet != "",
            "Style sheet should not be empty."
        ]

        assert [  # Test 2.
            "background-color: #2d3c67" in style_sheet,
            "Style sheet should contain background-color: #2d3c67"
        ]

        assert [  # Test 3.
            "color: #e7e2f3" in style_sheet,
            "Style sheet should contain color: #e7e2f3"
        ]

        assert [  # Test 4.
            "QGroupBox QLabel" in style_sheet,
            "Style sheet should contain styling for QGroupBox QLabel"
        ]


# TESTS FOR TestStyleAddScanButton #


class TestStyleAddScanButton:
    def test_style_add_scan_button(self, app, mock_window):
        """
        Test that style_add_scan_button correctly applies
        styling to the button.

        This function should:
        1. Apply the style_add_scan_button function to the add_scan_button.

        This function tests:
        1. The styleSheet property of the button is not empty.
        2. The styleSheet contains expected idle background color (#56d156).
        3. The styleSheet contains expected hover background color (#2ade2a).
        4. The styleSheet contains expected pressed background color (#5AAF5A).
        """
        button = mock_window.add_scan_button
        style_add_scan_button(button)  # 1.

        style_sheet = button.styleSheet()

        assert [  # Test 1.
            style_sheet != "",
            "Style sheet should not be empty."
        ]

        assert [  # Test 2.
            "background-color: #56d156" in style_sheet,
            "Style should contain background-color: #56d156"
        ]

        assert [  # Test 3.
            "background-color: #2ade2a" in style_sheet,
            "Style should contain hover state background-color: #2ade2a"
        ]

        assert [  # Test 4.
            "background-color: #5AAF5A" in style_sheet,
            "Style should contain pressed state background-color: #5AAF5A"
        ]


# TESTS FOR TestStyleScanTable #


class TestStyleScanTable:
    def test_style_scan_table(self, app, mock_window):
        """
        Test that style_scan_table correctly applies styling to the table.

        This function should:
        1. Apply the style_scan_table function to the scan_table.

        This function tests:
        1. The styleSheet property of the table is not empty.
        2. The styleSheet contains styling for the QTableWidget.
        3. The styleSheet contains styling for the QTableWidget items.
        4. The styleSheet contains styling for the QHeaderView::section.
        5. Alternating row colors are enabled.
        6. Selection behavior is set to select rows.
        7. The header font is bold.
        """
        table = mock_window.scan_table
        style_scan_table(table)  # 1.

        style_sheet = table.styleSheet()

        assert [  # Test 1.
            style_sheet != "",
            "Style sheet should not be empty."
        ]

        assert [  # Test 2.
            "QTableWidget {" in style_sheet,
            "Style sheet should contain styling for QTableWidget"
        ]

        assert [  # Test 3.
            "QTableWidget::item {" in style_sheet,
            "Style sheet should contain styling for QTableWidget::item"
        ]

        assert [  # Test 4.
            "QHeaderView::section {" in style_sheet,
            "Style sheet should contain styling for QHeaderView::section"
        ]

        assert [  # Test 5.
            table.alternatingRowColors() is True,
            "Alternating row colors should be enabled."
        ]

        assert [  # Test 6.
            table.selectionBehavior() == QTableWidget.SelectRows,
            "Selection behavior should be set to select rows."
        ]

        assert [  # Test 7.
            table.horizontalHeader().font().bold() is True,
            "Header font should be bold."
        ]

    def test_item_text_alignment(self, app, mock_window):
        """
        Test that the text in table cells is properly center-aligned.

        This function should:
        1. Apply the style_scan_table function to the scan_table.

        This function tests:
        1. All items in the table have center alignment.
        """
        table = mock_window.scan_table
        style_scan_table(table)  # 1.

        all_centered = True
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and item.textAlignment() != Qt.AlignCenter:
                    all_centered = False
                    break

        assert [  # Test 1.
            all_centered is True,
            "All items in the table should have center alignment."
        ]


# TESTS FOR TestStyleTableButtons #


class TestStyleTableButtons:
    def test_style_table_buttons(self, app, mock_window):
        """
        Test style_table_buttons correctly applies styling to table buttons.

        This function should:
        1. Apply the style_table_buttons function to the scan_table.

        This function tests:
        1. The styleSheet of the Edit buttons is not empty.
        2. The styleSheet of the Delete buttons is not empty.
        3. The Edit buttons contain the expected background color (#688cca).
        4. The Delete buttons contain the expected background color (#e74c3c).
        """
        table = mock_window.scan_table
        style_table_buttons(table)  # 1.

        edit_button = table.cellWidget(0, 6)
        edit_style = edit_button.styleSheet()

        assert [  # Test 1.
            edit_style != "",
            "Edit button style sheet should not be empty."
        ]

        assert [  # Test 3.
            "background-color: #688cca" in edit_style,
            "Edit button style sheet should contain background-color: #688cca"
        ]

        delete_button = table.cellWidget(0, 7)
        delete_style = delete_button.styleSheet()

        assert [  # Test 2.
            delete_style != "",
            "Delete button style sheet should not be empty."
        ]

        assert [  # Test 4.
            "background-color: #e74c3c" in delete_style,
            "Delete button style should contain background-color: #e74c3c"
        ]


# TESTS FOR TestIntegrationFunctions #


class TestIntegrationFunctions:
    def test_integrate_window_styling(self, app, mock_window, monkeypatch):
        """
        Test integrate_window_styling correctly applies styling to the window.

        This function should:
        1. Create a mock for style_scans_window.
        2. Apply the mock.
        3. Call integrate_window_styling.

        This function tests:
        1. style_scans_window is called with the mock_window.
        """
        style_scans_window_called = False

        def mock_style_scans_window(window):  # 1.
            nonlocal style_scans_window_called
            style_scans_window_called = True
            assert [
                window == mock_window,
                "style_scans_window called with wrong window"
            ]

        monkeypatch.setattr(
            "gui.scans_window.style_scans.style_scans_window",
            mock_style_scans_window
        )  # 2.

        integrate_window_styling(mock_window)  # 3.

        assert [  # Test 1.
            style_scans_window_called is True,
            "style_scans_window should be called by integrate_window_styling"
        ]

    def test_integrate_summary_group_styling(
            self, app, mock_window, monkeypatch
    ):
        """
        Test that integrate_summary_group_styling correctly applies styling.

        This function should:
        1. Create a mock for style_group_box.
        2. Apply the mock.
        3. Call integrate_summary_group_styling.

        This function tests:
        1. style_group_box is called with the scans_summary_group.
        """
        style_group_box_called = False

        def mock_style_group_box(group_box):  # 1.
            nonlocal style_group_box_called
            style_group_box_called = True
            assert [
                group_box == mock_window.scans_summary_group,
                "style_group_box called with wrong group"
            ]

        monkeypatch.setattr(
            "gui.scans_window.style_scans.style_group_box",
            mock_style_group_box
        )  # 2.

        integrate_summary_group_styling(mock_window)  # 3.

        assert [  # Test 1.
            style_group_box_called is True,
            "style_group_box isn't called by integrate_summary_group_styling"
        ]

    def test_integrate_scans_group_styling(
            self, app, mock_window, monkeypatch
    ):
        """
        Test that integrate_scans_group_styling correctly applies styling.

        This function should:
        1. Create mocks for the style functions.
        2. Apply the mocks.
        3. Call integrate_scans_group_styling.

        This function tests:
        1. style_group_box is called with the scans_group.
        2. style_add_scan_button is called with the add_scan_button.
        3. style_scan_table is called with the scan_table.
        4. The populate_scans_table function is wrapped.
        5. After calling the wrapped function, style_table_buttons is called.
        """
        style_group_box_called = False
        style_add_scan_button_called = False
        style_scan_table_called = False
        style_table_buttons_called = False

        def mock_style_group_box(group_box):  # 1a.
            nonlocal style_group_box_called
            style_group_box_called = True
            assert [
                group_box == mock_window.scans_group,
                "style_group_box called with wrong group"
            ]

        def mock_style_add_scan_button(button):  # 1b.
            nonlocal style_add_scan_button_called
            style_add_scan_button_called = True
            assert [
                button == mock_window.add_scan_button,
                "style_add_scan_button called with wrong button"
            ]

        def mock_style_scan_table(table):  # 1c.
            nonlocal style_scan_table_called
            style_scan_table_called = True
            assert [
                table == mock_window.scan_table,
                "style_scan_table called with wrong table"
            ]

        def mock_style_table_buttons(table):  # 1d.
            nonlocal style_table_buttons_called
            style_table_buttons_called = True
            assert [
                table == mock_window.scan_table,
                "style_table_buttons called with wrong table"
            ]

        monkeypatch.setattr(
            "gui.scans_window.style_scans.style_group_box",
            mock_style_group_box
        )  # 2a.

        monkeypatch.setattr(
            "gui.scans_window.style_scans.style_add_scan_button",
            mock_style_add_scan_button
        )  # 2b.

        monkeypatch.setattr(
            "gui.scans_window.style_scans.style_scan_table",
            mock_style_scan_table
        )  # 2c.

        monkeypatch.setattr(
            "gui.scans_window.style_scans.style_table_buttons",
            mock_style_table_buttons
        )  # 2d.

        integrate_scans_group_styling(mock_window)  # 3.

        assert [  # Test 1.
            style_group_box_called is True,
            "style_group_box should be called by integrate_scans_group_styling"
        ]

        assert [  # Test 2.
            style_add_scan_button_called is True,
            """
                style_add_scan_button isn't called
                by integrate_scans_group_styling
            """
        ]

        assert [  # Test 3.
            style_scan_table_called is True,
            "style_scan_table isn't called by integrate_scans_group_styling"
        ]

        original_function = mock_window.populate_scans_table

        assert [  # Test 4.
            mock_window.populate_scans_table != original_function,
            "populate_scans_table function should be wrapped"
        ]

        mock_window.populate_scans_table()

        assert [  # Test 5.
            style_table_buttons_called is True,
            "style_table_buttons should be called after populate_scans_table"
        ]
