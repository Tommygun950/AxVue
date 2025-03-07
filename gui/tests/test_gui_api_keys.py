"""
File for testing the functionality of the gui_api_keys.py.
"""
import pytest
from PyQt5.QtWidgets import (
    QApplication, QLabel, QGroupBox
)
from gui.api_keys_window.gui_api_keys import ApiKeysWindow

@pytest.fixture
def app():
    """Creates a QApplication instance for testing."""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def api_keys_window(app):
    """Creates an ApiKeysWindow instance for testing."""
    window = ApiKeysWindow()
    yield window
    window.close()

def test_init(api_keys_window):
    """
    Tests that ApiKeysWindow is initialized correctly.

    This function tests:
    1. api_keys_window exists.
    2. The central widget within api_keys_window exists.
    3. The layout within api_keys_window exists.
    """
    assert api_keys_window is not None # Test 1.
    assert api_keys_window.central_widget is not None # Test 2.
    assert api_keys_window.layout is not None # Test 3.

def test_api_keys_content(api_keys_window):
    """
    Tests that the api keys page content is initialized correctly.

    This funciton tests:
    1. APi Keys summary group:
        a. The group exists.
        b. Has a title of "API Keys Summary".
        c. The summary test/QLabel exists and contains text.
    2. API Keys entries group:
        a. The group exists & has a title of "API Keys".
        b. Ensure the correct buttons exist.
        c. Ensure the buttons have the correct label.
        d. Ensure the API Keys table exists.
        e. Ensure the table has the correct # of columns.
        f. The columns have the correct titles/headers.
    """
    assert api_keys_window.api_keys_summary_group is not None # Test 1a.
    assert api_keys_window.api_keys_summary_group.title() == "API Keys Summary" # Test 1b.

    labels = api_keys_window.api_keys_summary_group.findChildren(QLabel)
    assert len(labels) > 0. # Test 1c.

    api_keys_groups = [box for box in api_keys_window.findChildren(QGroupBox) if box.title() == "API Keys"]
    assert len(api_keys_groups) == 1 # Test 2a.

    assert api_keys_window.add_api_key_button is not None # Test 2b.
    assert api_keys_window.add_api_key_button.text() == "Add API Key" # Test 2c.

    assert api_keys_window.api_keys_table is not None # Test 2d.
    assert api_keys_window.api_keys_table.columnCount() == 3 # Test 2e.

    expected_headers = [
        "Key Name", "Key Value", "Status"
    ]
    for i, header in enumerate(expected_headers):
        assert api_keys_window.api_keys_table.horizontalHeaderItem(i).text() == header # Test 2f.
