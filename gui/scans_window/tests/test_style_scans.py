"""
This file contains unit tests for the style_scans.py module.

The tests validate the styling functions for the Scans window:
1. test_style_scans_window -> tests window styling application.
2. test_style_group_box -> tests group box styling application.
3. test_style_add_scan_button -> tests Add Scan button styling.
4. test_style_scan_table -> tests Scan table styling.
5. test_style_table_buttons -> tests table button styling.
6. test_integration_functions -> tests integration function behavior.
"""
import pytest
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGroupBox, QPushButton, QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtGui import QColor, QPalette

from gui.scans_window.style_scans import (
    bg_color, add_button_color, cached_perc_low_color,
    cached_perc_high_color, delete_button_color,
    style_scans_window, style_group_box,
    style_add_scan_button, style_scan_table,
    style_table_buttons,
    integrate_window_styling, integrate_summary_group_styling,
    integrate_scans_group_styling
)


# FIXTURES FOR TESTING #

@pytest.fixture(scope="module")
def app():
    """Fixture to create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # We don't call app.quit() here as it might affect other tests
    # PyQt will clean up properly on Python exit


@pytest.fixture
def mock_window(app):
    """Fixture to create a mock Scans window for testing."""
    window = QMainWindow()
    window.central_widget = QWidget()
    window.setCentralWidget(window.central_widget)

    window.scans_summary_group = QGroupBox("Scans Summary")
    window.scans_group = QGroupBox("Scans")

    window.add_scan_button = QPushButton("Add Scan")

    # Create table with minimal content for testing
    window.scan_table = QTableWidget()
    window.scan_table.setColumnCount(8)
    window.scan_table.setRowCount(2)

    # Only create minimal essential widgets
    window.populate_scans_table = lambda: None

    # Add items and widgets as needed but minimize complexity
    for row in range(2):
        for col in range(3):
            if col > 0:  # Skip the first column (checkbox)
                window.scan_table.setItem(
                    row, col, QTableWidgetItem(f"Item {row},{col}")
                )

        # Create mock buttons for the table cells
        cache_button = QPushButton("Enabled" if row == 0 else "Disabled")
        cache_button.setEnabled(False)
        window.scan_table.setCellWidget(row, 4, cache_button)

        cached_perc = 75 if row == 0 else 25
        cached_perc_button = QPushButton(f"{cached_perc}%")
        cached_perc_button.setEnabled(False)
        window.scan_table.setCellWidget(row, 5, cached_perc_button)

        edit_button = QPushButton("Edit")
        window.scan_table.setCellWidget(row, 6, edit_button)

        delete_button = QPushButton("Delete")
        window.scan_table.setCellWidget(row, 7, delete_button)

    yield window

    # Explicit cleanup to avoid memory issues with Qt widgets
    for row in range(window.scan_table.rowCount()):
        for col in range(window.scan_table.columnCount()):
            window.scan_table.setItem(row, col, None)
            widget = window.scan_table.cellWidget(row, col)
            if widget:
                widget.deleteLater()

    window.scan_table.clear()
    window.deleteLater()


# TESTS FOR STYLING FUNCTIONS #

def test_style_scans_window(app, mock_window):
    """
    Tests style_scans_window function.

    This test should:
    1. Call style_scans_window on a mock window.
    2. Verify the window's palette color matches bg_color.
    3. Verify that autoFillBackground is set to True.
    """
    style_scans_window(mock_window)

    palette = mock_window.central_widget.palette()
    bg_palette_color = palette.color(QPalette.Window)

    assert bg_palette_color.name() == QColor(bg_color).name()
    assert mock_window.central_widget.autoFillBackground()


def test_style_group_box(app, mock_window):
    """
    Tests style_group_box function.

    This test should:
    1. Call style_group_box on a mock GroupBox.
    2. Verify that the style sheet is set and contains expected colors.
    """
    group_box = mock_window.scans_summary_group

    style_group_box(group_box)

    style_sheet = group_box.styleSheet()

    assert "QGroupBox" in style_sheet
    assert "QGroupBox::title" in style_sheet
    assert "QGroupBox QLabel" in style_sheet


def test_style_add_scan_button(app, mock_window):
    """
    Tests style_add_scan_button function.

    This test should:
    1. Call style_add_scan_button on a mock button.
    2. Verify that the style sheet is set and contains expected colors.
    """
    button = mock_window.add_scan_button

    style_add_scan_button(button)

    style_sheet = button.styleSheet()

    assert "QPushButton" in style_sheet
    assert f"background-color: {add_button_color}" in style_sheet
    assert "QPushButton:hover" in style_sheet
    assert "QPushButton:pressed" in style_sheet


def test_style_scan_table(app, mock_window):
    """
    Tests style_scan_table function.

    This test should:
    1. Call style_scan_table on a mock table.
    2. Verify that the style sheet is set with expected selectors.
    3. Verify that alternatingRowColors is enabled.
    4. Verify that selectionBehavior is set to SelectRows.
    """
    table = mock_window.scan_table

    style_scan_table(table)

    style_sheet = table.styleSheet()

    assert "QTableWidget" in style_sheet
    assert "QTableWidget::item" in style_sheet
    assert "QTableWidget::item:selected" in style_sheet
    assert "QHeaderView::section" in style_sheet
    assert "QCheckBox" in style_sheet

    assert table.alternatingRowColors()
    assert table.selectionBehavior() == QTableWidget.SelectRows


def test_style_table_buttons(app, mock_window):
    """
    Tests style_table_buttons function.

    This test should:
    1. Call style_table_buttons on a mock table.
    2. Verify that Enabled cache buttons have proper styling.
    3. Verify that Disabled cache buttons have proper styling.
    4. Verify that cached percentage buttons have proper styling.
    5. Verify that Edit buttons have proper styling.
    6. Verify that Delete buttons have proper styling.
    """
    table = mock_window.scan_table

    style_table_buttons(table)

    enabled_cache_button = table.cellWidget(0, 4)
    disabled_cache_button = table.cellWidget(1, 4)
    high_perc_button = table.cellWidget(0, 5)
    low_perc_button = table.cellWidget(1, 5)
    edit_button = table.cellWidget(0, 6)
    delete_button = table.cellWidget(0, 7)

    # Verify buttons exist
    assert enabled_cache_button is not None
    assert disabled_cache_button is not None
    assert high_perc_button is not None
    assert low_perc_button is not None
    assert edit_button is not None
    assert delete_button is not None

    # Verify style content
    assert add_button_color in enabled_cache_button.styleSheet()
    assert delete_button_color in disabled_cache_button.styleSheet()
    assert cached_perc_high_color in high_perc_button.styleSheet()
    assert cached_perc_low_color in low_perc_button.styleSheet()
    assert "QPushButton" in edit_button.styleSheet()
    assert delete_button_color in delete_button.styleSheet()


def test_integration_functions(app, monkeypatch):
    """
    Tests integration styling functions.

    This test should:
    1. Create mocks for the style functions to track calls.
    2. Call integration functions and verify they invoke the right mocks.
    """
    # Create a simple mock window without Qt widgets
    class SimpleMockWindow:
        def __init__(self):
            self.central_widget = object()
            self.scans_summary_group = object()
            self.scans_group = object()
            self.add_scan_button = object()
            self.scan_table = object()
            self.populate_scans_table = lambda: None

    mock_window = SimpleMockWindow()

    # Track function calls
    called_functions = []

    # Create mock functions
    def mock_style_scans_window(window):
        called_functions.append(("style_scans_window", window))

    def mock_style_group_box(group_box):
        called_functions.append(("style_group_box", group_box))

    def mock_style_add_scan_button(button):
        called_functions.append(("style_add_scan_button", button))

    def mock_style_scan_table(table):
        called_functions.append(("style_scan_table", table))

    def mock_style_table_buttons(table):
        called_functions.append(("style_table_buttons", table))

    # Apply monkeypatching
    monkeypatch.setattr(
        "gui.scans_window.style_scans.style_scans_window",
        mock_style_scans_window
    )
    monkeypatch.setattr(
        "gui.scans_window.style_scans.style_group_box",
        mock_style_group_box
    )
    monkeypatch.setattr(
        "gui.scans_window.style_scans.style_add_scan_button",
        mock_style_add_scan_button
    )
    monkeypatch.setattr(
        "gui.scans_window.style_scans.style_scan_table",
        mock_style_scan_table
    )
    monkeypatch.setattr(
        "gui.scans_window.style_scans.style_table_buttons",
        mock_style_table_buttons
    )

    # Test integrate_window_styling
    integrate_window_styling(mock_window)
    assert ("style_scans_window", mock_window) in called_functions

    # Test integrate_summary_group_styling
    integrate_summary_group_styling(mock_window)
    assert (
        "style_group_box",
        mock_window.scans_summary_group
    ) in called_functions

    # Test integrate_scans_group_styling
    integrate_scans_group_styling(mock_window)
    assert (
        "style_group_box",
        mock_window.scans_group
    ) in called_functions
    assert (
        "style_add_scan_button",
        mock_window.add_scan_button
    ) in called_functions
    assert (
        "style_scan_table",
        mock_window.scan_table
    ) in called_functions


def test_populate_scans_table_wrapper(app, monkeypatch):
    """
    Tests that the wrapped populate_scans_table function calls
    style_table_buttons.

    This test should:
    1. Create mock objects without using actual Qt widgets.
    2. Call integrate_scans_group_styling to wrap the populate function.
    3. Call the wrapped function and verify behavior.
    """
    # Create mock objects
    class SimpleMockWindow:
        def __init__(self):
            self.scans_group = object()
            self.add_scan_button = object()
            self.scan_table = object()
            self.populate_scans_table = self.original_populate

        def original_populate(self):
            self.original_called = True

    mock_window = SimpleMockWindow()
    mock_window.original_called = False

    style_calls = []

    # Create mock styling functions
    def mock_style_group_box(group_box):
        pass

    def mock_style_add_scan_button(button):
        pass

    def mock_style_scan_table(table):
        pass

    def mock_style_table_buttons(table):
        style_calls.append(table)

    # Apply monkeypatching
    monkeypatch.setattr(
        "gui.scans_window.style_scans.style_group_box",
        mock_style_group_box
    )
    monkeypatch.setattr(
        "gui.scans_window.style_scans.style_add_scan_button",
        mock_style_add_scan_button
    )
    monkeypatch.setattr(
        "gui.scans_window.style_scans.style_scan_table",
        mock_style_scan_table
    )
    monkeypatch.setattr(
        "gui.scans_window.style_scans.style_table_buttons",
        mock_style_table_buttons
    )

    # Run the integration function
    integrate_scans_group_styling(mock_window)

    # Call the wrapped function
    mock_window.populate_scans_table()

    # Verify behavior
    assert mock_window.original_called is True
    assert style_calls == [mock_window.scan_table]
