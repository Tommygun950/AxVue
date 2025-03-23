"""
This file contains unit tests for the style_api_keys.py module.

The tests validate the styling functions for the API Keys window:
1. test_style_api_keys_window -> tests window styling application.
2. test_style_group_box -> tests group box styling application.
3. test_style_add_api_key_button -> tests Add API Key button styling.
4. test_style_api_key_table -> tests API Key table styling.
5. test_style_functional_table_buttons -> tests table button styling.
6. test_integration_functions -> tests integration function behavior.
"""
import pytest
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGroupBox, QPushButton, QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtGui import QColor, QPalette

from gui.api_keys_window.style_api_keys import (
    COLOR_BG_MAIN, COLOR_BTN_ADD, COLOR_STATUS_VALID_BG,
    COLOR_STATUS_INVALID_BG, COLOR_BTN_EDIT, COLOR_BTN_DELETE,
    style_api_keys_window, style_group_box,
    style_add_api_key_button, style_api_key_table,
    style_functional_table_buttons,
    integrate_window_styling, integrate_summary_group_styling,
    integrate_api_keys_group_styling
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
    """Fixture to create a mock API Keys window for testing."""
    window = QMainWindow()
    window.central_widget = QWidget()
    window.setCentralWidget(window.central_widget)

    window.api_keys_summary_group = QGroupBox("API Keys Summary")
    window.api_keys_group = QGroupBox("API Keys")

    window.add_api_key_button = QPushButton("Add API Key")

    # Create table with minimal content for testing
    window.api_keys_table = QTableWidget()
    window.api_keys_table.setColumnCount(6)
    window.api_keys_table.setRowCount(2)

    # Only create minimal essential widgets
    window.populate_api_keys_table = lambda: None

    # Add items and widgets as needed but minimize complexity
    for row in range(2):
        for col in range(3):
            if col != 0:
                window.api_keys_table.setItem(
                    row, col, QTableWidgetItem(f"Item {row},{col}")
                )

        status_button = QPushButton("Valid" if row == 0 else "Invalid")
        status_button.setEnabled(False)
        window.api_keys_table.setCellWidget(row, 3, status_button)

        edit_button = QPushButton("Edit")
        window.api_keys_table.setCellWidget(row, 4, edit_button)

        delete_button = QPushButton("Delete")
        window.api_keys_table.setCellWidget(row, 5, delete_button)

    yield window

    # Explicit cleanup to avoid memory issues with Qt widgets
    for row in range(window.api_keys_table.rowCount()):
        for col in range(window.api_keys_table.columnCount()):
            window.api_keys_table.setItem(row, col, None)
            widget = window.api_keys_table.cellWidget(row, col)
            if widget:
                widget.deleteLater()

    window.api_keys_table.clear()
    window.deleteLater()


# TESTS FOR STYLING FUNCTIONS #

def test_style_api_keys_window(app, mock_window):
    """
    Tests style_api_keys_window function.

    This test should:
    1. Call style_api_keys_window on a mock window.
    2. Verify the window's palette color matches COLOR_BG_MAIN.
    3. Verify that autoFillBackground is set to True.
    """
    style_api_keys_window(mock_window)

    palette = mock_window.central_widget.palette()
    bg_color = palette.color(QPalette.Window)

    assert bg_color.name() == QColor(COLOR_BG_MAIN).name()
    assert mock_window.central_widget.autoFillBackground()


def test_style_group_box(app, mock_window):
    """
    Tests style_group_box function.

    This test should:
    1. Call style_group_box on a mock GroupBox.
    2. Verify that the style sheet is set and contains expected colors.
    """
    group_box = mock_window.api_keys_summary_group

    style_group_box(group_box)

    style_sheet = group_box.styleSheet()

    assert "QGroupBox" in style_sheet
    assert "QGroupBox::title" in style_sheet
    assert "QGroupBox QLabel" in style_sheet


def test_style_add_api_key_button(app, mock_window):
    """
    Tests style_add_api_key_button function.

    This test should:
    1. Call style_add_api_key_button on a mock button.
    2. Verify that the style sheet is set and contains expected colors.
    """
    button = mock_window.add_api_key_button

    style_add_api_key_button(button)

    style_sheet = button.styleSheet()

    assert "QPushButton" in style_sheet
    assert f"background-color: {COLOR_BTN_ADD}" in style_sheet
    assert "QPushButton:hover" in style_sheet
    assert "QPushButton:pressed" in style_sheet


def test_style_api_key_table(app, mock_window):
    """
    Tests style_api_key_table function.

    This test should:
    1. Call style_api_key_table on a mock table.
    2. Verify that the style sheet is set with expected selectors.
    3. Verify that alternatingRowColors is enabled.
    4. Verify that selectionBehavior is set to SelectRows.
    """
    table = mock_window.api_keys_table

    style_api_key_table(table)

    style_sheet = table.styleSheet()

    assert "QTableWidget" in style_sheet
    assert "QTableWidget::item" in style_sheet
    assert "QTableWidget::item:selected" in style_sheet
    assert "QHeaderView::section" in style_sheet
    assert "QCheckBox" in style_sheet

    assert table.alternatingRowColors()
    assert table.selectionBehavior() == QTableWidget.SelectRows


def test_style_functional_table_buttons(app, mock_window):
    """
    Tests style_functional_table_buttons function.

    This test should:
    1. Call style_functional_table_buttons on a mock table.
    2. Verify that Valid status buttons have proper styling.
    3. Verify that Invalid status buttons have proper styling.
    4. Verify that Edit buttons have proper styling.
    5. Verify that Delete buttons have proper styling.
    """
    table = mock_window.api_keys_table

    style_functional_table_buttons(table)

    valid_status_button = table.cellWidget(0, 3)
    invalid_status_button = table.cellWidget(1, 3)
    edit_button = table.cellWidget(0, 4)
    delete_button = table.cellWidget(0, 5)

    # Verify buttons exist
    assert valid_status_button is not None
    assert invalid_status_button is not None
    assert edit_button is not None
    assert delete_button is not None

    # Verify style content
    assert COLOR_STATUS_VALID_BG in valid_status_button.styleSheet()
    assert COLOR_STATUS_INVALID_BG in invalid_status_button.styleSheet()
    assert COLOR_BTN_EDIT in edit_button.styleSheet()
    assert COLOR_BTN_DELETE in delete_button.styleSheet()


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
            self.api_keys_summary_group = object()
            self.api_keys_group = object()
            self.add_api_key_button = object()
            self.api_keys_table = object()
            self.populate_api_keys_table = lambda: None

    mock_window = SimpleMockWindow()

    # Track function calls
    called_functions = []

    # Create mock functions
    def mock_style_api_keys_window(window):
        called_functions.append(("style_api_keys_window", window))

    def mock_style_group_box(group_box):
        called_functions.append(("style_group_box", group_box))

    def mock_style_add_api_key_button(button):
        called_functions.append(("style_add_api_key_button", button))

    def mock_style_api_key_table(table):
        called_functions.append(("style_api_key_table", table))

    def mock_style_functional_table_buttons(table):
        called_functions.append(("style_functional_table_buttons", table))

    # Apply monkeypatching
    monkeypatch.setattr(
        "gui.api_keys_window.style_api_keys.style_api_keys_window",
        mock_style_api_keys_window
    )
    monkeypatch.setattr(
        "gui.api_keys_window.style_api_keys.style_group_box",
        mock_style_group_box
    )
    monkeypatch.setattr(
        "gui.api_keys_window.style_api_keys.style_add_api_key_button",
        mock_style_add_api_key_button
    )
    monkeypatch.setattr(
        "gui.api_keys_window.style_api_keys.style_api_key_table",
        mock_style_api_key_table
    )
    monkeypatch.setattr(
        "gui.api_keys_window.style_api_keys.style_functional_table_buttons",
        mock_style_functional_table_buttons
    )

    # Test integrate_window_styling
    integrate_window_styling(mock_window)
    assert ("style_api_keys_window", mock_window) in called_functions

    # Test integrate_summary_group_styling
    integrate_summary_group_styling(mock_window)
    assert (
        "style_group_box",
        mock_window.api_keys_summary_group
    ) in called_functions

    # Test integrate_api_keys_group_styling
    integrate_api_keys_group_styling(mock_window)
    assert (
        "style_group_box",
        mock_window.api_keys_group
    ) in called_functions
    assert (
        "style_add_api_key_button",
        mock_window.add_api_key_button
    ) in called_functions
    assert (
        "style_api_key_table",
        mock_window.api_keys_table
    ) in called_functions


def test_populate_api_keys_table_wrapper(app, monkeypatch):
    """
    Tests that the wrapped populate_api_keys_table function calls
    style_functional_table_buttons.

    This test should:
    1. Create mock objects without using actual Qt widgets.
    2. Call integrate_api_keys_group_styling to wrap the populate function.
    3. Call the wrapped function and verify behavior.
    """
    # Create mock objects
    class SimpleMockWindow:
        def __init__(self):
            self.api_keys_group = object()
            self.add_api_key_button = object()
            self.api_keys_table = object()
            self.populate_api_keys_table = self.original_populate

        def original_populate(self):
            self.original_called = True

    mock_window = SimpleMockWindow()
    mock_window.original_called = False

    style_calls = []

    # Create mock styling functions
    def mock_style_group_box(group_box):
        pass

    def mock_style_add_api_key_button(button):
        pass

    def mock_style_api_key_table(table):
        pass

    def mock_style_functional_table_buttons(table):
        style_calls.append(table)

    # Apply monkeypatching
    monkeypatch.setattr(
        "gui.api_keys_window.style_api_keys.style_group_box",
        mock_style_group_box
    )
    monkeypatch.setattr(
        "gui.api_keys_window.style_api_keys.style_add_api_key_button",
        mock_style_add_api_key_button
    )
    monkeypatch.setattr(
        "gui.api_keys_window.style_api_keys.style_api_key_table",
        mock_style_api_key_table
    )
    monkeypatch.setattr(
        "gui.api_keys_window.style_api_keys.style_functional_table_buttons",
        mock_style_functional_table_buttons
    )

    # Run the integration function
    integrate_api_keys_group_styling(mock_window)

    # Call the wrapped function
    mock_window.populate_api_keys_table()

    # Verify behavior
    assert mock_window.original_called is True
    assert style_calls == [mock_window.api_keys_table]
