"""
File for testing the layout of gui_scans.py.
"""
import pytest
from PyQt5.QtWidgets import (
    QApplication, QLabel, QGroupBox,
)
from gui.scans_window.gui_scans import ScansWindow

@pytest.fixture
def app():
    """Creates a QApplication instance for testing."""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def scans_window(app):
    """Creates a ScansWindow instance for testing."""
    window = ScansWindow()
    yield window
    window.close()

def test_init(scans_window):
    """
    Tests that ScanWindow is initialized correctly.

    This function tests:
    1. scans_window exists.
    2. The central widget within scans_window exists.
    3. The layout within scans_window exists.
    """
    assert scans_window is not None # Test 1.
    assert scans_window.central_widget is not None # Test 2.
    assert scans_window.layout is not None # Test 3.

def test_init_scans_content(scans_window):
    """
    Tests that the scans page content is initialized correctly.

    This function tests:
    1. Scans summary group:
        a. The group exists.
        b. Has a title of "Scans Summary".
        c. The summary test/QLabel exists and contains text.
    2. Scan entries group:
        a. The group exists & has a title of "Scans".
        b. Ensure the correct buttons exist.
        c. Ensure the buttons have the correct label.
        d. Ensure the scans table exists.
        e. Ensure the table has the correct # of columns.
        f. The columns have the correct titles/headers.
    """
    assert scans_window.scans_summary_group is not None # Test 1a.
    assert scans_window.scans_summary_group.title() == "Scans Summary" # Test 1b.

    labels = scans_window.scans_summary_group.findChildren(QLabel)
    assert len(labels) > 0 # Test 1c.

    scans_groups = [box for box in scans_window.findChildren(QGroupBox) if box.title() == "Scans"]
    assert len(scans_groups) == 1 # Test 2a.

    assert scans_window.add_scan_button is not None # Test 2b.
    assert scans_window.add_scan_button.text() == "Add Scan" # Test 2c.

    assert scans_window.scan_table is not None # Test 2d.
    assert scans_window.scan_table.columnCount() == 8 # Test 2e.

    expected_headers = [
        "Scan Name", "File Path", "Total CVE IDs",
        "Unique CVE IDs", "Cache", "Cached %", "Edit", "Delete"
    ]
    for i, header in enumerate(expected_headers):
        assert scans_window.scan_table.horizontalHeaderItem(i).text() == header # Test 2f.
