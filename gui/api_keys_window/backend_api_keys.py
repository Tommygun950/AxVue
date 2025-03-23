"""
This file contains backend functionality for the API Keys Window.

This file includes the following backend functions:
1. _add_api_key -> adds user-given data to db.
2. _edit_api_key -> updates id-specific API key in db with new values.
3. _delete_api_key -> deletes id-specific API key in db.
4. _update_api_key_selected_field -> updates id-specific API
key's 'selected' field value.
5. _get_all_api_key_data -> returns all API keys from db as dicts.
6. _get_api_key_data -> returns a dict of an id-specific API key.
"""
import sqlite3
from gui.api_keys_window.dialogs_api_keys import (
    GeneralErrorDialog
)


def _add_api_key(
        key_name: str,
        key_value: str,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Given a key_name & key_value, create an API key & add it
    to the db.

    This function should:
        1. Check for user input errors like:
            a. key_name isn't empty.
            b. key_value isn't empty.
        2. Add the API key information to the db.
        3. Return either a succes or failure bool value
        and a message for debugging/dialog purposes.
    """
    def check_for_errors() -> tuple[bool, str]:
        """
        Checks for errors with the user's entered in data.

        This function should:
        1. Ensure the key_name & key_value are not empty.
        """
        if key_name == "" or key_value == "":
            error_dialog = GeneralErrorDialog(
                "Key name or value cannot be empty."
            )
            error_dialog.exec_()
            return (False, "Empty Field")
        return (True, "success")

    def add_key_to_db() -> tuple[bool, str]:
        """
        Adds the API key to the db given the key_name & key_value.

        This function should:
        1. Connect to the db file.
        2. Create an API key in the db with the following fields:
            a. key_name -> given by user in the AddAPIKeyDialog.
            b. key_value -> given by user in the APIKeyDialog.
            c. status -> defaults to "Valid".
            d. error_count -> defaults to "0" in db.
            e. selected -> defaults to 0.
        """
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        try:
            insert_query = """
            INSERT INTO nvd_api_key (
                key_name,
                key_value,
                status,
                error_count,
                selected
            ) VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                key_name,
                key_value,
                "Valid",
                0,
                0
            ))

            conn.commit()
            conn.close()

            return (True, f"Successfully added key: {key_name}")

        except sqlite3.Error as e:
            conn.close()
            error_dialog = GeneralErrorDialog(f"Database error: {str(e)}")
            error_dialog.exec_()
            return (False, f"Database error: {str(e)}")

    user_input_success, user_input_message = check_for_errors()
    if user_input_success is False:
        return (user_input_success, user_input_message)

    db_entry_success, db_entry_message = add_key_to_db()
    return (db_entry_success, db_entry_message)


def _edit_api_key(
        id: int,
        key_name: str,
        key_value: str,
        status: str,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Updates a specific API key in the db based on
    the user's changes in the EditAPIKeyDialog return.

    This function should:
    1.  Return a GeneralErrorDialog for the following:
        a. If key_name is empty.
        b. If key_value is empty.
    2. Edit the specific API key in the db & return either
    a success tuple or a GeneralErrorDialog.
    """
    def check_for_errors() -> tuple[bool, str]:
        """
        Ensures user-input errors aren't
        passed before program failure.

        This function should:
        1. Ensure key_name isn't empty.
        2. Ensure key_value isn't empty.
        3. Return a bool, str tuple for success &
        a possible error message.
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
        return (True, "success")

    def edit_key_in_db() -> tuple[bool, str]:
        """
        Given the necessary data for a particular API key
        in the database, update it with the user given values.

        This function should:
        1. Connect to the db.
        2. Update API key in db.
        3. Return a GeneralErrorDialog if db update fails.
        """
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
                status,
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

    user_input_success, user_input_message = check_for_errors()
    if user_input_success is False:
        return (user_input_success, user_input_message)

    db_update_success, db_update_message = edit_key_in_db()
    return (db_update_success, db_update_message)


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


def _update_api_key_selected_field(
        id: int,
        selected: int,
        db_file: str = "vuln_data.db"
) -> tuple[bool, str]:
    """
    Updates the "selected" field for a specific API key.

    This function should:
    1. Check for the following errors:
        a. "selected" field equals either 0 or 1.
    2. Update the API Key in the db.
    3. Return a GeneralErrorDialog if db update fails.
    """
    def check_for_errors() -> tuple[bool, str]:
        """
        Ensures that there are no issues/errors with the
        input parameters of this main function.

        This function should.
        1. Ensure "selected" field is  either "Valid" or "Invalid".
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
        Updates the id-specificed API key's "selected" value
        in the table/db.

        This function should:
        1. Connect to the db.
        2. Update the "selected" field for a specific key-id.
        3. If the update was unsuccessful, return a
        GeneralErrorDialog with the db error message.
        """
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE nvd_api_key
                SET selected = ?
                WHERE id = ?
                """,
                (selected, id)
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

    user_input_success, user_input_message = check_for_errors()
    if user_input_success is False:
        return (user_input_success, user_input_message)

    db_update_success, db_update_message = update_selected_in_db()
    return (db_update_success, db_update_message)


def _get_all_api_key_data(
        db_file: str = "vuln_data.db"
) -> list[dict]:
    """
    Retrieves all API keys from the db table and returns them
    as a list of dicts for each API key.

    This function should:
    1. Connect to the db.
    2. Ensure each db row is returned as a dict.
    3. Add all of the API key dicts to the list.
    4. Return either a GeneralErrorDialog or a succes
    tuple depending on the query outcome.
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
            """
        )
        api_key_rows = cursor.fetchall()

        all_api_keys = [dict(row) for row in api_key_rows]

        conn.close()

        return all_api_keys

    except sqlite3.Error as e:
        error_dialog = GeneralErrorDialog(f"Database error: {str(e)}", None)
        error_dialog.exec_()
        return []


def _get_api_key_data(
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
