"""
file for testing the layout of gui_scans.py.
"""
import pytest
from PyQt5.QtWidgets import QApplication, QGroupBox, QLabel, QTableWidget
from gui.exports_window.gui_exports import ExportsWindow

@pytest.fixture
def app():
    """Creates a QApplication instance for testing."""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def exports_window(app):
    """Creates an ExportsWindow instance for testing."""
    window = ExportsWindow()
    window.show()
    yield window
    window.close()

def test_init(exports_window):
    """
    Tests that ExportsWindow is initialized correctly.
    
    This function tests:
    1. exports_window exists.
    2. The central widget within exports_window exists.
    3. The layout within exports_window exists.
    """
    assert exports_window is not None  # Test 1.
    assert exports_window.central_widget is not None  # Test 2.
    assert exports_window.layout is not None  # Test 3.

def test_init_exports_content(exports_window):
    """
    Tests that the Exports page content is initialized correctly.
    
    This function tests:
    1. Exports Summary Section:
        a. The group exists with the title "Exports Summary".
        b. A summary QLabel exists and contains text.
    2. Past Exports Section:
        a. The group exists with the title "Past Exports".
        b. The past exports table exists with 6 columns and correct headers.
    """
    exports_summary_group = exports_window.exports_summary_group  # Test 1a.
    assert exports_summary_group is not None  # Test 1a.
    assert exports_summary_group.title() == "Exports Summary"  # Test 1a.

    summary_labels = exports_summary_group.findChildren(QLabel)
    assert len(summary_labels) > 0  # Test 1b.
    assert any(label.text().strip() for label in summary_labels), "Summary label text is empty"  # Test 1b.

    past_exports_group = None  # Test 2a.
    for group in exports_window.central_widget.findChildren(QGroupBox):
        if group.title() == "Past Exports":
            past_exports_group = group
            break
    assert past_exports_group is not None, "Past Exports group not found"  # Test 2a.

    past_exports_table = exports_window.past_exports_table  # Test 2b.
    assert past_exports_table is not None  # Test 2b.
    assert isinstance(past_exports_table, QTableWidget)  # Test 2b.
    assert past_exports_table.columnCount() == 6  # Test 2b.
    expected_headers = ["Export Name", "# of Scans", "Export Type", "Export Date", "Export", "Delete"]
    for i, header in enumerate(expected_headers):
        header_item = past_exports_table.horizontalHeaderItem(i)
        assert header_item.text() == header  # Test 2c.
