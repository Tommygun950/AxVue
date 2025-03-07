"""
This file contains backend functionality for the Scans window.
"""
import sqlite3
from gui.scans_window.dialogs_scans import GeneralErrorDialog
from processing.scans_processing import return_cve_ids_from_csv

def _add_scan(scan_name, file_path) -> tuple[bool, str]:
    """
    Given a scan name and file path to a valid CSV scan file,
    add it to the scan_data table in vuln_data.db.

    This function should:
    1. Check if there's data in scan_name and file_path.
        a. If not, return an error dialog.
    2. Process the followin values for the scan before adding it to the db:
        a. total_vulnerbailities.
        b. unique_cve_list.
        c. cache_enabled.
        d. cached_percentage.
    3. Take the given and processed values and add the scan to the db.
    """
    if scan_name == "" or file_path == "":        
        error_dialog = GeneralErrorDialog("Scan name or file path cannot be empty.", None)
        error_dialog.exec_()
        return (False, "Empty Scan Name and/or File Path.")
