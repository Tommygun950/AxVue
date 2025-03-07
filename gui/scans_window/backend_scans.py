"""
This file contains backend functionality for the Scans window.
"""
import sqlite3
from gui.scans_window.dialogs_scans import GeneralErrorDialog
from processing.scans_processing import return_cve_ids_from_csv, return_cached_percentage

def _add_scan(scan_name: str, file_path: str) -> tuple[bool, str]:
    """
    Given a scan name and file path to a valid CSV scan file,
    add it to the scan_data table in vuln_data.db.
    This function should:
    1. Check if there's data in scan_name and file_path.
        a. If not, return an error dialog.
    2. Process the following values for the scan before adding it to the db:
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
    
    cve_id_list, cve_id_set = return_cve_ids_from_csv(file_path)
    total_vulnerabilities = len(cve_id_list)
    unique_cve_list = ", ".join(cve_id_set)
    cached_percentage = return_cached_percentage(cve_id_set)
    
    cache_enabled = True
    
    conn = sqlite3.connect("vuln_data.db")
    cursor = conn.cursor()
    
    try:
        insert_query = """
        INSERT INTO scan_data (
            scan_name, 
            file_path, 
            total_vulnerabilities, 
            unique_cve_list, 
            cache_enabled, 
            cached_percentage
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_query, (
            scan_name, 
            file_path, 
            total_vulnerabilities, 
            unique_cve_list, 
            cache_enabled, 
            cached_percentage
        ))
        
        conn.commit()
        conn.close()
        
        return (True, f"Successfully added scan: {scan_name}")
    
    except sqlite3.Error as e:
        conn.close()
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return (False, f"Database error: {str(e)}")

def _get_formatted_scan_data(db_file: str = "vuln_data.db") -> list[dict]:
    """
    Retrieves all scans from the scan_data table and formats them for display.
   
    This function should:
    1. Connect to the database.
    2. Query all of the scans from the scan_data table.
    3. Format the query return into a list of dictionary values for each scan.
    4. If the SQL query fails, return a generalerrordialog for a db error.
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
       
        cursor.execute("SELECT id, scan_name, total_vulnerabilities, unique_cve_list, cache_enabled, cached_percentage FROM scan_data")
        scan_rows = cursor.fetchall()
       
        formatted_scans = []
        for row in scan_rows:
            scan_id, name, total_cves, unique_cves, cache_enabled, cached_percentage = row
            
            unique_cve_count = len(unique_cves.split(',')) if isinstance(unique_cves, str) and unique_cves else 0
           
            formatted_scan = {
                "id": scan_id,
                "scan_name": name,
                "total_cves": str(total_cves),
                "unique_cves": str(unique_cve_count),
                "cache_enabled": "Enabled" if cache_enabled else "Disabled",
                "cached_percentage": f"{cached_percentage}%"
            }
            formatted_scans.append(formatted_scan)
       
        conn.close()
        return formatted_scans
    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return []