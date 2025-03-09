"""
File for testing the functionality of the gui create report window.
"""
import pytest
from PyQt5.QtWidgets import (
    QApplication, QGroupBox, QLabel, QTableWidget, QComboBox, QCheckBox, QPushButton
)
from gui.create_report_window.gui_create_report import CreateReportWindow

@pytest.fixture
def app():
    """Creates a QApplication instance for testing."""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def main_window(app):
    """Creates a MainWindow instance for testing."""
    window = CreateReportWindow()
    window.show()
    yield window
    window.close()

def test_init(main_window):
    """
    Tests that MainWindow is initialized correctly.
    
    This function tests:
    1. The MainWindow instance exists.
    2. The central widget within MainWindow exists.
    3. The layout within MainWindow exists.
    """
    assert main_window is not None  # Test 1.
    assert main_window.central_widget is not None  # Test 2.
    assert main_window.layout is not None  # Test 3.

def test_create_report_content(main_window):
    """
    Tests that the Create Report window content is initialized correctly.
    
    This function tests:
    1. API Key Section:
        a. Group exists with title "Selected API Keys:".
        b. The API Keys table exists with 4 columns and correct headers.
    2. Scans Section:
        a. Group exists with title "Selected Scans:".
        b. The Scans table exists with 7 columns and correct headers.
    3. Export Configuration Section:
        a. Group exists with title "Export Configuration".
        b. The Export Type combo box exists with items "PDF" and "Excel".
        c. The Pages to Export label exists.
        d. The checkboxes for pages ("KEV Catalog Comparison", "Base Metrics", "Temporal Metrics") exist and are checked.
        e. The Create Report button exists with the correct label.
    """
    api_key_group = None  # Test 1a.
    for widget in main_window.central_widget.findChildren(QGroupBox):
        if widget.title() == "Selected API Keys:":
            api_key_group = widget
            break
    assert api_key_group is not None, "Selected API Keys group not found"  # Test 1a.

    api_key_table = main_window.api_key_table
    assert api_key_table is not None  # Test 1b.
    assert isinstance(api_key_table, QTableWidget)  # Test 1b.
    assert api_key_table.columnCount() == 4  # Test 1b.
    expected_api_key_headers = ["Key Name", "Value", "Status", "Remove"]
    for i, header in enumerate(expected_api_key_headers):
        header_item = api_key_table.horizontalHeaderItem(i)
        assert header_item.text() == header  # Test 1b.

    scans_group = None  # Test 2a.
    for widget in main_window.central_widget.findChildren(QGroupBox):
        if widget.title() == "Selected Scans:":
            scans_group = widget
            break
    assert scans_group is not None, "Selected Scans group not found"  # Test 2a.

    scan_table = main_window.scan_table
    assert scan_table is not None  # Test 2b.
    assert isinstance(scan_table, QTableWidget)  # Test 2b.
    assert scan_table.columnCount() == 7  # Test 2b.
    expected_scan_headers = [
        "Scan Name", "File Path", "Total CVE IDs", 
        "Unique CVE IDs", "Cache", "Cached %", "Remove"
    ]
    for i, header in enumerate(expected_scan_headers):
        header_item = scan_table.horizontalHeaderItem(i)
        assert header_item.text() == header  # Test 2b.

    export_group = main_window.export_config_group
    assert export_group is not None  # Test 3a.
    assert export_group.title() == "Export Configuration"  # Test 3a.

    export_type_combo = main_window.export_type_combo
    assert export_type_combo is not None  # Test 3b.
    assert isinstance(export_type_combo, QComboBox)  # Test 3b.
    expected_items = ["PDF", "Excel"]
    for item in expected_items:
        found = False
        for i in range(export_type_combo.count()):
            if export_type_combo.itemText(i) == item:
                found = True
                break
        assert found, f"Combo box item '{item}' not found"  # Test 3b.

    pages_label_found = any(
        isinstance(label, QLabel) and label.text() == "Pages to Export:"
        for label in export_group.findChildren(QLabel)
    )
    assert pages_label_found, "Pages to Export label not found"  # Test 3c.

    expected_pages = ["KEV Catalog Comparison", "Base Metrics", "Temporal Metrics"]
    for page in expected_pages:
        assert page in main_window.page_checkboxes, f"Checkbox for '{page}' not found"  # Test 3d.
        checkbox = main_window.page_checkboxes[page]
        assert isinstance(checkbox, QCheckBox), f"Widget for '{page}' is not a QCheckBox"  # Test 3d.
        assert checkbox.isChecked(), f"Checkbox for '{page}' is not checked"  # Test 3d.

    export_button = main_window.export_button
    assert export_button is not None  # Test 3e.
    assert isinstance(export_button, QPushButton)  # Test 3e.
    assert export_button.text() == "Create Report"  # Test 3e.

