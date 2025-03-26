"""
This file contains the backend functionality for Create Report Window.
"""
import sqlite3
from gui.create_report_window.dialogs_create_report import (
    GeneralErrorDialog
)


def _get_selected_api_keys(
        db_file: str = "vuln_data.db"
) -> list[dict]:
    """
    Retrieves all API Keys from the db table that
    have been selected by the user and returns them as
    a list of dicts for each API key.

    This function should:
    1. Connect to the db.
    2. Ensure each db row is returned as a dict.
    3. Add all selected API key dicts to the list.
    4. Return either a GeneralError dialog or the list.
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                key_name,
                key_value,
                status,
                error_count,
                selected
            FROM nvd_api_key
            WHERE selected = 1
            """
        )
        api_key_rows = cursor.fetchall()

        selected_api_keys = [dict(row) for row in api_key_rows]

        conn.close()

        return selected_api_keys

    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return []


def _get_selected_api_key(
        id: int,
        db_file: str = "vuln_data.db"
) -> dict:
    """
    Return a dictionary of an id-specified API key.

    This function should:
    1. Connect to the db.
    2. Ensure the query returns a dict value.
    3. Return the dictionary if query was successful,
    if not return a GeneralErrorDialog.
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                key_name,
                key_value,
                status,
                error_count,
                selected
            FROM nvd_api_key
            WHERE id = ?
            """, (id,)
        )

        api_key_data = cursor.fetchone()
        conn.close()

        if api_key_data:
            return dict(api_key_data)
        else:
            error_dialog = GeneralErrorDialog(
                f"Key with ID {id} was not found."
            )
            error_dialog.exec_()
            return None

    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return None


def _remove_api_key(
        id: int,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Updates the "selected" field for a specific API key
    by changing it to 0 which removes it from the selected
    API keys table but doesn't delete the key.

    This funciton should:
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE nvd_api_key
            SET selected = 0
            WHERE id = ?
            """,
            (id,)
        )

        conn.commit()
        conn.close()

        return (
            True,
            f"Successfully updated selection status for key ID: {id}"
        )

    except sqlite3.Error as e:
        conn.close()
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}")
        error_dialog.exec_()
        return (
            False,
            f"Database error: {str(e)}"
        )


def _get_selected_scans(
        db_file: str = "vuln_data.db"
) -> list[dict]:
    """
    Retrieves all selected scans from the db table & returns
    them as a list of dicts for each scan.

    This function should:
    1. Connect to the db.
    2. Ensure each db row is returned as a dict.
    3. Add all of the scan dicts to the list.
    4. Return a GeneralErrorDialog if the db query fails.
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                scan_name,
                total_vulnerabilities,
                unique_cve_list,
                cache_enabled,
                cached_percentage,
                selected
            FROM scan_data
            WHERE selected = 1
            """
        )
        scan_rows = cursor.fetchall()

        selected_scans = [dict(row) for row in scan_rows]

        conn.close()

        return selected_scans

    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return []


def _get_selected_scan(
        id: int,
        db_file: str = "vuln_data.db"
) -> dict:
    """
    Return a dictionary of an id-specified scan.

    This function should:
    1. Connect to the db.
    2. Ensure the query returns a dict value.
    3. Return a GeneralErrorDialog if db query failed.
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                scan_name,
                file_path,
                total_vulnerabilities,
                unique_cve_list,
                cache_enabled,
                cached_percentage,
                selected
            FROM scan_data
            WHERE id = ?
            """, (id,)
        )

        scan_data = cursor.fetchone()
        conn.close()

        if scan_data:
            return dict(scan_data)
        else:
            error_dialog = GeneralErrorDialog(
                f"Scan with ID {id} was not found."
            )
            error_dialog.exec_()
            return None

    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return None


def _remove_scan(
        id: int,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Updates the "selected" field for a specific scan
    by changing it to 0 which removes it from the selected
    scans table but doesn't delete the scan.

    This funciton should:
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE scan_data
            SET selected = 0
            WHERE id = ?
            """,
            (id,)
        )

        conn.commit()
        conn.close()

        return (
            True,
            f"Successfully updated selection status for scan ID: {id}"
        )

    except sqlite3.Error as e:
        conn.close()
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}")
        error_dialog.exec_()
        return (
            False,
            f"Database error: {str(e)}"
        )
