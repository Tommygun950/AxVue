"""
This file contains backend functionality for the API Keys Window.
"""
import sqlite3
from gui.api_keys_window.dialogs_api_keys import GeneralErrorDialog


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
            error_dialog = GeneralErrorDialog(
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
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}")
        error_dialog.exec_()
        return (False, f"Database error: {str(e)}")


def _edit_api_key(
        id: int,
        key_name: str,
        key_value: str,
        status: bool,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Given an API key ID, name, value, & status, update the API
    key entry in the nvd_api_key table in the db.

    This function should:
    1. Check if there's data in key_name & key_value.
        a. If not, return an error dialog.
    2. Process the following values for the API kye before updating
    it in the db:
        a. status.
    3. Take the given & processed values & update the API key in the db.
    """
    if key_name == "" or key_value == "":
        error_dialog = GeneralErrorDialog(
            "Key name and value cannot be empty."
        )
        error_dialog.exec_()
        return (
            False,
            "Empty Key Name &/or Key Value."
        )

    status_int = 1 if status else 0

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        update_query = """
        UPDATE nvd_api_key
        SET
            key_name = ?,
            key_value = ?,
            status = ?
        WHERE id = ?
        """
        cursor.execute(update_query, (
            key_name,
            key_value,
            status_int,
            id
        ))

        conn.commit()
        conn.close()

        return (
            True,
            f"Successfully updated Key: {key_name}"
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


def _delete_api_key(
        id: int,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Deletes an API key from the db given an ID.

    This function should:
    1. Connect to the db.
    2. Delete the API key with the ID from the nvd_api_key table.
    3. Return a tuple with (success flag, message).
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM nvd_api_key
            WHERE id = ?
            """, (id,)
        )

        conn.commit()
        conn.close()

        return (
            True,
            f"Successfully deleted API Key with ID: {id}"
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


def _update_api_key_selected_status(
        id: int,
        selected: bool,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Updates the selected status of an API key.

    This function should:
    1. Connect to the db.
    2. Update the "selected" field of a given key ID.
    3. Return a tuple with (success flag, message).
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        selected_int = 1 if selected else 0

        cursor.execute(
            """
            UPDATE nvd_api_key
            SET selected = ?
            WHERE id = ?
            """,
            (selected_int, id)
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


def _get_all_api_key_data(
        db_file: str = "vuln_data.db"
) -> list[dict]:
    """
    Retrieves all API keys from nvd_api_key table & formats them for display.

    This function should:
    1. Connect to the db.
    2. Query all of the API kyes from nvd_api_key table.
    3. Format the query return into a list of dictionary values for each scan.
    4. If the SQL query fails, return a GeneralErrorDialog for a db error.
    """
    try:
        conn = sqlite3.connect(db_file)
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
            """
        )

        api_key_rows = cursor.fetchall()

        formatted_api_keys = []
        for row in api_key_rows:
            (
                key_id,
                key_name,
                key_value,
                status,
                error_count,
                selected
            ) = row

            formatted_api_key = {
                "id": key_id,
                "key_name": key_name,
                "key_value": key_value,
                "status": "Valid" if status else "Invalid",
                "error_count": error_count,
                "selected": bool(selected)
            }
            formatted_api_keys.append(formatted_api_key)

        conn.close()
        return formatted_api_keys

    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return []


def _get_api_key_data(
        id: int,
        db_file: str = "vuln_data.db"
) -> dict:
    """
    Retrieves the details of a specific API key given an ID.

    This function should:
    1. Connect to the db.
    2. Query the API key with the ID from the nvd_api_key table.
    3. Return the dict with the API key details or None if not found.
    4. If the SQL query fails, show a GeneralErrorDialog for a db error.
    """
    try:
        conn = sqlite3.connect(db_file)
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
            return {
                "key_name": api_key_data[0],
                "key_value": api_key_data[1],
                "status": bool(api_key_data[2]),
                "error_count": api_key_data[3],
                "selected": api_key_data[4]
            }
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
