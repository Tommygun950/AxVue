"""
This file contains backend functionality for the API Keys Window.
"""
import sqlite3
from gui.api_keys_window.dialogs_api_keys import GeneralErrordialog


def _add_api_key(
        key_name: str,
        key_value: str,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Given an API Key name & value, add it to the nvd_api_key table.

    This function should:
    1. Check if there's data in key_name & key_value.
        a. If not, return an error dialog.
    2. Process the following values for the api key before adding it to the db:
        a. key_name.
        b. key_value.
        c. status.
        d. error_count.
    3. Take the given & processed values & add the API key to the db.
    """
    def check_for_errors():
        """
        Check for errors with the user's entered in data.

        this function should:
        1. Ensure the key_name & key_value are not empty.
        """
        if key_name == "" or key_value == "":
            error_dialog = GeneralErrordialog(
                "Key name or value cannot be empty."
            )
            error_dialog.exec_()
            return (False, "Empty Field")

    success, message = check_for_errors()
    if success is False:
        return (success, message)

    status = True
    error_count = 0

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        insert_query = """
        INSERT INTO nvd_api_key (
            key_name,
            key_value,
            status,
            error_count
        ) VALUES (?, ?, ?, ?)
        """
        cursor.execute(insert_query, (
            key_name,
            key_value,
            status,
            error_count
        ))

        conn.commit()
        conn.close()

        return (True, f"Successfully added key: {key_name}")

    except sqlite3.Error as e:
        conn.close()
        error_dialog = GeneralErrordialog(f"Database error: {str(e)}")
        error_dialog.exec_()
        return (False, f"Database error: {str(e)}")


def _edit_scan(
        id: int,
        key_name: str,
        key_value: str,
        status: bool,
        error_count: int,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Given a key id, key_name, key_value, & status, update the API key
    entry in the nvd_api_key table in vuln_data.db.

    This function should:
    1. Check if there's data in the key_name & key_value.
        a. If not, return an error dialog.
    2. Process the following values for the API key before updating the db:
        a. status.
        b. error_count.
    3. Take the given & processed values & update the API key in the db.
    """
    if key_name == "" or key_value == "":
        error_dialog = GeneralErrordialog(
            "API Key name or value cannot be empty."
        )
        error_dialog.exec_()
        return (False, "Empty API Key and/or Value.")

    status_int = 1 if status else 0
    error_count = 0 if status else error_count

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        update_query = """
        UPDATE nvd_api_key
        SET key_name = ?,
            key_value = ?,
            status = ?,
            error_count = ?
        WHERE id = ?
        """
        cursor.execute(update_query, (
            key_name,
            key_value,
            status_int,
            error_count
        ))

        conn.commit()
        conn.close()

        return (True, f"Successfully updated key: {key_name}")

    except sqlite3.Error as e:
        conn.close()
        error_dialog = GeneralErrordialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return (False, f"Database error: {str(e)}")
