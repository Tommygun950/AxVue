"""
This file contains backend functionality for the Scans window.
"""
import sqlite3
from gui.scans_window.dialogs_scans import GeneralErrorDialog
from processing.scans_processing import (
    return_cve_ids_from_csv, return_cached_percentage
)


def _add_scan(
        scan_name: str,
        file_path: str,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Given a scan name and file path to a valid CSV scan file,
    add it to the scan_data table in the db file.

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
    def check_for_errors():
        """
        Check for errors with the user's entered in data.

        This function should:
        1. Ensure scan_name and file_path are not empty.
        2. Ensure the file is in csv format.
        """
        if scan_name == "" or file_path == "":
            error_dialog = GeneralErrorDialog(
                "Scan name or file path cannot be empty."
            )
            error_dialog.exec_()
            return (False, "Empty Field")

        if file_path[-4:].lower() != ".csv":
            error_dialog = GeneralErrorDialog(
                "Invalid File Format: File must be a CSV."
            )
            error_dialog.exec_()
            return (False, "Invalid File Format")

        success, message = check_for_errors()
        if success is False:
            return (success, message)

    cve_id_list, cve_id_set = return_cve_ids_from_csv(file_path)
    total_vulnerabilities = len(cve_id_list)
    unique_cve_list = ", ".join(cve_id_set)
    cached_percentage = return_cached_percentage(cve_id_set)

    cache_enabled = True

    conn = sqlite3.connect(db_file)
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


def _edit_scan(
        scan_id: int,
        scan_name: str,
        file_path: str,
        cache_enabled: bool,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Given a scan id, scan name, file path, and cache setting, update
    the scan entry in the scan_data table in vuln_data.db.

    This funciton should:
    1. Check if there's data in scan_name & file_path.
        a. If not, return an error dialog.
    2. Process the following values for the scan before updating it in the db:
        a. total_vulnerabilities.
        b. unique_cve_list.
        c. cache_enabled.
        d. cached_percentage.
    3. Take the given & processed values and update the scan in the db.
    """
    if scan_name == "" or file_path == "":
        error_dialog = GeneralErrorDialog(
            "Scan name or file path cannot be empty."
        )
        error_dialog.exec_()
        return (False, "Empty Scan Name and/or File Path.")

    cve_id_list, cve_id_set = return_cve_ids_from_csv(file_path)
    total_vulnerabilities = len(cve_id_list)
    unique_cve_list = ", ".join(cve_id_set)
    cached_percentage = return_cached_percentage(cve_id_list)

    cache_enabled_int = 1 if cache_enabled else 0

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        update_query = """
        UPDATE scan_data
        SET scan_name = ?,
            file_path = ?,
            total_vulnerabilities = ?,
            unique_cve_list = ?,
            cache_enabled = ?,
            cached_percentage = ?
        WHERE id = ?
        """
        cursor.execute(update_query, (
            scan_name,
            file_path,
            total_vulnerabilities,
            unique_cve_list,
            cache_enabled_int,
            cached_percentage,
            scan_id
        ))

        conn.commit()
        conn.close()

        return (True, f"Successfully updated scan: {scan_name}")

    except sqlite3.Error as e:
        conn.close()
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return (False, f"Database error: {str(e)}")


def _delete_scan(
        scan_id: int,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Deletes a scan from the database given a scan ID.

    This function should:
    1. Connect to the database.
    2. Delete the scan with the specified ID from the scan_data table.
    3. Return a tuple with (success flag, message).
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM scan_data WHERE id = ?", (scan_id,))

        conn.commit()
        conn.close()

        return (True, f"Successfully deleted scan with ID: {scan_id}")

    except sqlite3.Error as e:
        conn.close()
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}")
        error_dialog.exec_()
        return (False, f"Database error: {str(e)}")


def _update_scan_selected_status(
        scan_id: int,
        selected: bool,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Updates the selected status of a scan.

    This function should:
    1. Connect to the database.
    2. Update the "selected" field of the given scan ID.
    3. Return a tuple with (success flag, message).
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        selected_int = 1 if selected else 0

        cursor.execute(
            """
            UPDATE scan_data
            SET selected = ?
            WHERE id = ?
            """,
            (selected_int, scan_id)
        )

        conn.commit()
        conn.close()

        return (
            True,
            f"Successfully updated selection status for scan ID: {scan_id}"
        )

    except sqlite3.Error as e:
        conn.close()
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}")
        error_dialog.exec_()
        return (False, f"Database error: {str(e)}")


def _get_all_scan_data(
        db_file: str = "vuln_data.db"
) -> list[dict]:
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

        cursor.execute(
            """
            SELECT id, scan_name, total_vulnerabilities,
                unique_cve_list, cache_enabled, cached_percentage, selected
            FROM scan_data
            """
        )

        scan_rows = cursor.fetchall()

        formatted_scans = []
        for row in scan_rows:
            (
                scan_id, name, total_cves, unique_cves,
                cache_enabled, cached_percentage, selected
            ) = row

            unique_cve_count = 0
            if isinstance(unique_cves, str) and unique_cves:
                unique_cve_count = len(unique_cves.split(','))

            formatted_scan = {
                "id": scan_id,
                "scan_name": name,
                "total_cves": str(total_cves),
                "unique_cves": str(unique_cve_count),
                "cache_enabled": "Enabled" if cache_enabled else "Disabled",
                "cached_percentage": f"{cached_percentage}%",
                "selected": bool(selected)
            }
            formatted_scans.append(formatted_scan)

        conn.close()
        return formatted_scans
    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return []


def _get_scan_data(
        scan_id: int,
        db_file: str = "vuln_data.db"
) -> dict:
    """
    Retrieves the details of a specific scan given a scan id.

    This function should:
    1. Connect to the db.
    2. Query the scan with the specified ID from the scan_data table.
    3. Return the dictionary with the scan details or None if not found.
    4. If the SQL query fails, show a general error dialog for a db error.
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT scan_name, file_path, total_vulnerabilities,
                unique_cve_list, cache_enabled, cached_percentage
            FROM scan_data
            WHERE id = ?
            """, (scan_id,)
        )

        scan_data = cursor.fetchone()

        conn.close()

        if scan_data:
            return {
                "scan_name": scan_data[0],
                "file_path": scan_data[1],
                "total_vulnerabilities": scan_data[2],
                "unique_cve_list": scan_data[3],
                "cache_enabled": scan_data[4],
                "cached_percentage": scan_data[5]
            }
        else:
            error_dialog = GeneralErrorDialog(
                f"Scan with ID {scan_id} not found."
            )
            error_dialog.exec_()
            return None

    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return None
