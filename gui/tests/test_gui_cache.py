"""
File for testing the funcitonality of the gui cache window.
"""
import pytest
from PyQt5.QtWidgets import QApplication, QGroupBox, QPushButton, QTableWidget
from gui.cache_window.gui_cache import CacheWindow

@pytest.fixture
def app():
    """Creates a QApplication instance for testing."""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def cache_window(app):
    """Creates a CacheWindow instance for testing."""
    window = CacheWindow()
    window.show()
    yield window
    window.close()

def test_init(cache_window):
    """
    Tests that CacheWindow is initialized correctly.
    
    This function tests:
    1. The CacheWindow instance exists.
    2. The central widget within CacheWindow exists.
    3. The layout within CacheWindow exists.
    """
    assert cache_window is not None  # Test 1.
    assert cache_window.central_widget is not None  # Test 2.
    assert cache_window.layout is not None  # Test 3.

def test_cache_window_content(cache_window):
    """
    Tests that the CacheWindow content is initialized correctly.

    This function tests:
    1. Queried NVD Data Feed Section:
        a. Group exists with title "NVD Data Feed Selection".
        b. The "Query Data Feeds" button exists.
        c. The queried feed table exists with 4 columns and correct headers.
    2. Stored NVD Data Feeds Section:
        a. Group exists with title "Stored NVD Data Feeds".
        b. The "Check For Updates" and "Clear Data Feeds" buttons exist.
        c. The stored feed table exists with 6 columns and correct headers.
    3. Pre Cache Scans Section (within horizontal layout):
        a. Group exists with title "Pre Cache Scans".
        b. The "Clear Scan CVEs" button exists.
        c. The pre cache scan table exists with 4 columns and correct headers.
    4. Cached CVEs Section (within horizontal layout):
        a. Group exists with title "Cached CVEs".
        b. The "Clear Entire Cache" button exists.
        c. The cached CVEs table exists with 2 columns and correct headers.
    """
    queried_group = cache_window.queried_nvd_data_group
    assert queried_group is not None # Test 1a.
    assert queried_group.title() == "NVD Data Feed Selection" # Test 1a.

    refresh_btn = cache_window.refresh_button
    assert refresh_btn is not None # Test 1b.
    assert refresh_btn.text() == "Query Data Feeds" # Test 1b.

    queried_table = cache_window.queried_feed_table
    assert queried_table is not None # Test 1c.
    assert isinstance(queried_table, QTableWidget) # Test 1c.
    assert queried_table.columnCount() == 4 # Test 1c.
    expected_queried_headers = ["Year", "File Size", "Last Queried", "Status"]
    for i, header in enumerate(expected_queried_headers):
        header_item = queried_table.horizontalHeaderItem(i)
        assert header_item.text() == header # Test 1c.

    stored_group = cache_window.stored_nvd_data_group
    assert stored_group is not None # Test 2a.
    assert stored_group.title() == "Stored NVD Data Feeds" # Test 2a.

    check_updates_btn = cache_window.check_for_updates_button
    assert check_updates_btn is not None # Test 2b.
    assert check_updates_btn.text() == "Check For Updates" # Test 2b.

    clear_btn = cache_window.clear_button
    assert clear_btn is not None # Test 2b.
    assert clear_btn.text() == "Clear Data Feeds" # Test 2b.

    stored_table = cache_window.stored_feed_table
    assert stored_table is not None # Test 2c.
    assert isinstance(stored_table, QTableWidget) # Test 2c.
    assert stored_table.columnCount() == 6 # Test 2c.
    expected_stored_headers = ["Year", "File Size", "CVE Count", "Last Updated", "Status", "Cache"]
    for i, header in enumerate(expected_stored_headers):
        header_item = stored_table.horizontalHeaderItem(i)
        assert header_item.text() == header # Test 2c.

    group_boxes = cache_window.central_widget.findChildren(QGroupBox)
    pre_cache_group = None # Test 3a.
    cached_cves_group = None # Test 4a.
    for group in group_boxes:
        if group.title() == "Pre Cache Scans":
            pre_cache_group = group
        elif group.title() == "Cached CVEs":
            cached_cves_group = group
    assert pre_cache_group is not None, "Pre Cache Scans group not found" # Test 3a.
    assert cached_cves_group is not None, "Cached CVEs group not found" # Test 4a.

    pre_cache_buttons = pre_cache_group.findChildren(QPushButton)
    assert any(btn.text() == "Clear Scan CVEs" for btn in pre_cache_buttons), \
        "Clear Scan CVEs button not found in Pre Cache Scans section" # Test 3b.

    pre_cache_tables = pre_cache_group.findChildren(QTableWidget)
    assert pre_cache_tables, "No table found in Pre Cache Scans section" # Test 3c.
    pre_cache_table = pre_cache_tables[0]
    assert pre_cache_table.columnCount() == 4 # Test 3c.
    expected_pre_cache_headers = ["Scan name", "Unique CVE IDs", "Cache %", "Cache"]
    for i, header in enumerate(expected_pre_cache_headers):
        header_item = pre_cache_table.horizontalHeaderItem(i)
        assert header_item.text() == header # Test 3c.

    cached_cves_buttons = cached_cves_group.findChildren(QPushButton)
    assert any(btn.text() == "Clear Entire Cache" for btn in cached_cves_buttons), \
        "Clear Entire Cache button not found in Cached CVEs section" # Test 3b.

    cached_cves_tables = cached_cves_group.findChildren(QTableWidget)
    assert cached_cves_tables, "No table found in Cached CVEs section" # Test 3c.
    cached_cves_table = cached_cves_tables[0]
    assert cached_cves_table.columnCount() == 2 # Test 3c.
    expected_cached_cves_headers = ["CVE ID", "Remove"]
    for i, header in enumerate(expected_cached_cves_headers):
        header_item = cached_cves_table.horizontalHeaderItem(i)
        assert header_item.text() == header # Test 3c.
