"""
Code for backend functionality for the Scans Window.

This file contains the following functions:
1. _add_scan -> adds a scan to the db user-given & calculated values.
2. _edit_scan -> updates a scan in db with new user-gven & recalculated vals.
3. _delete_scan -> deletes a specific scan from the db given an ID.
4. _update_scan_selected_field -> updates a scan's "selected" field w/ new val.
5. _get_all_scan_data -> returns a list of all scans as individual dicts.
6. _get_scan_data -> returns all data for a scan as a dict.
"""
import sqlite3
from gui.scans_window.dialogs_scans import (
    GeneralErrorDialog
)
from processing.scans_processing import (
    return_cve_ids_from_csv, return_cached_percentage
)


def _add_scan(
        scan_name: str,
        file_path: str,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Add a scan to the db given a name & file path.

    This function should:
    1. Check for any user-input errors.
    2. Connect to the db.
    3. Insert the user-given & calculated data.
    4. Return a GeneralErrorDialog if db query fails.
    """
    def check_for_errors() -> tuple[bool, str]:
        """
        Checks for errors with the user's entered in data.

        This function should:
        1. Open a GeneralErrorDialog for the following errors:
            a. scan_name or file_path are empty.
            b. The file extension isn't .csv.
        """
        if scan_name == "" or file_path == "":
            error_dialog = GeneralErrorDialog(
                "Scan name or file path cannot be empty."
            )
            error_dialog.exec_()
            return (False, "Empty Field")

        elif file_path[-4:].lower() != ".csv":
            error_dialog = GeneralErrorDialog(
                "Invalid File Format: File must be a CSV."
            )
            error_dialog.exec_()
            return (False, "Invalid File Format")

        return (True, "success")

    def calculate_fields() -> tuple[int, str, float]:
        """
        Calculates the total_vulnerabilities, unique_cve_list,
        and cached_percentage variables using the
        scans_processing functions.

        This function should:
        1. Parse the total & unique cves from file.
        2. Calculate total_vulnerabilities.
        3. Calculate unique_cve_list.
        4. Calculate cached_percentage.
        """
        cve_id_list, cve_id_set = return_cve_ids_from_csv(file_path)

        total_vulnerabilities = len(cve_id_list)
        unique_cve_list = ", ".join(cve_id_set)
        cached_percentage = return_cached_percentage(cve_id_set)

        return (
            total_vulnerabilities,
            unique_cve_list,
            cached_percentage
        )

    def add_scan_to_db() -> tuple[bool, str]:
        """
        Adds a scan to the db.

        This function should:
        1. Connect to the db.
        2. Create a scan in the db with the following fields:
            a. scan_name -> given by user in AddScanDialog.
            b. file_path -> given by user in AddScanDialog.
            c. total_vulnerabiltities -> calculated in calculate_fields.
            d. unique_cve_list -> calculated in calculate_fields.
            e. cache_enabled -> defaulted to "Enabled".
            f. cached_percentage -> calculated in calculate_fields.
        """
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        (
            total_vulnerabilities,
            unique_cve_list,
            cached_percentage
        ) = calculate_fields()

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
                "Enabled",
                cached_percentage
            ))

            conn.commit()
            conn.close()

            return (True, f"Successfully added scan: {scan_name}")

        except sqlite3.Error as e:
            conn.close()
            error_dialog = GeneralErrorDialog(f"Database error: {str(e)}")
            error_dialog.exec_()
            return (False, f"Database error: {str(e)}")

    user_input_success, user_input_message = check_for_errors()
    if user_input_success is False:
        return (user_input_success, user_input_message)

    db_entry_success, db_entry_message = add_scan_to_db()
    return (db_entry_success, db_entry_message)


def _edit_scan(
        id: int,
        scan_name: str,
        file_path: str,
        cache_enabled: str,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Updates an id-specific scan in the db based
    on the new values provided by the user.

    This function should:
    1. Return a GeneralErrorDialog for any user-input errors.
    2. Recalculate the non-given values.
    3. Update the scan in the db with the user-given and
    the calculated values.
    4. Return a GeneralErrorDialog if db update fails.
    """
    def check_for_errors() -> tuple[bool, str]:
        """
        Ensures user-input errors arent' passed
        before program failure.

        This function should:
        1. Ensure scan_name isn't empty.
        2. Ensure file_path isn't empty.
        """
        if scan_name == "" or file_path == "":
            error_dialog = GeneralErrorDialog(
                "Scan name and file path cannot be empty."
            )
            error_dialog.exec_()
            return (
                False,
                "Empty Scan Name and/or File Path."
            )

        elif file_path[-4:].lower() != ".csv":
            error_dialog = GeneralErrorDialog(
                "Invalid File Format: File must be a CSV."
            )
            error_dialog.exec_()
            return (False, "Invalid File Format")

        return (True, "success")

    def calculate_fields() -> tuple[int, str, float]:
        """
        Calculates the total_vulnerabilities, unique_cve_list,
        and cached_percentage variables using the
        scans_processing functions.

        This function should:
        1. Parse the total & unique cves from file.
        2. Calculate total_vulnerabilities.
        3. Calculate unique_cve_list.
        4. Calculate cached_percentage.
        """
        cve_id_list, cve_id_set = return_cve_ids_from_csv(file_path)

        total_vulnerabilities = len(cve_id_list)
        unique_cve_list = ", ".join(cve_id_set)
        cached_percentage = return_cached_percentage(cve_id_set)

        return (
            total_vulnerabilities,
            unique_cve_list,
            cached_percentage
        )

    def edit_scan_in_db() -> tuple[bool, str]:
        """
        Given the necessary data for a particular scan
        in the db, update it with the user given values.

        This function should:
        1. Connect to the db.
        2. Update scan in db.
        3. Return a GeneralErrorDialog if db update fails.
        """
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        (
            total_vulnerabilities,
            unique_cve_list,
            cached_percentage
        ) = calculate_fields()

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
                cache_enabled,
                cached_percentage,
                id
            ))

            conn.commit()
            conn.close()

            return (
                True,
                f"Successfully updated scan: {scan_name}"
            )

        except sqlite3.Error as e:
            conn.close()

            error_dialog = GeneralErrorDialog(
                f"Database error: {str(e)}", None
            )
            error_dialog.exec_()

            return (
                False,
                f"Database error: {str(e)}"
            )

    user_input_success, user_input_message = check_for_errors()
    if user_input_success is False:
        return (user_input_success, user_input_message)

    db_update_success, db_update_message = edit_scan_in_db()
    return (db_update_success, db_update_message)


def _delete_scan(
        id: int,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Deletes an id-specified scan from the db.

    This function should:
    1. Connect to the db.
    2. Deletes the scan with the specified id in the scan_data table.
    3. Return a tuple wiht (success flag, message).
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM scan_data WHERE id = ?", (id,))

        conn.commit()
        conn.close()

        return (
            True,
            f"Successfully deleted scan with ID: {id}"
        )

    except sqlite3.Error as e:
        conn.close()
        error_dialog = GeneralErrorDialog(
            f"Database error: {str(e)}"
        )
        error_dialog.exec_()
        return (
            False,
            f"Database error: {str(e)}"
        )


def _update_scan_selected_field(
        id: int,
        selected: int,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Updates the "selected" field for an id-specified scan.

    This functin should:
    1. Checks the following errors:
        a. "selected" field equals either 0 or 1.
    2. Update the scan in the db.
    3. Return a GeneralErrorDialog if db update fails.
    """
    def check_for_errors() -> tuple[bool, str]:
        """
        Ensures that there are no issues/errors with the
        input parameters of this main function.

        This function should:
        1. Ensure "selected" field is either "Valid" or "Invalid".
        """
        if selected != 0 and selected != 1:
            error_dialog = GeneralErrorDialog(
                f"Invalid input for 'selected' field: {selected}."
            )
            error_dialog.exec_()
            return (
                False,
                "Invalid input for selected field."
            )
        return (True, "success")

    def update_selected_in_db() -> tuple[bool, str]:
        """
        Updates the id-specified scan's "selected" value
        in the table/db.

        This function should:
        1. Connect to the db.
        2. Update the "selected" field for an id-specified scan.
        3. If the update was unsuccessful, return a
        GeneralErrorDialog with the db error message.
        """
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE scan_data
                SET selected = ?
                WHERE id = ?
                """,
                (selected, id)
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

    user_input_success, user_input_message = check_for_errors()
    if user_input_success is False:
        return (user_input_success, user_input_message)

    db_update_success, db_update_message = update_selected_in_db()
    return (db_update_success, db_update_message)


def _get_all_scan_data(
        db_file: str = "vuln_data.db"
) -> list[dict]:
    """
    Retrieves all scans from the db table & returns
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
            """
        )
        scan_rows = cursor.fetchall()

        all_scans = [dict(row) for row in scan_rows]

        conn.close()

        return all_scans

    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return []


def _get_scan_data(
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
