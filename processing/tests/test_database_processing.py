"""
This file tests the functionality of the
processing/test_database_processing.py file.
"""
import os
import sqlite3
import tempfile
import pytest
from processing.database_processing import (
    initialize_database,
)

# DATABASE FIXTURES #


@pytest.fixture
def temp_db_file():
    """Fixture to create a temporary database file for testing."""
    # 1. Create a temporary file path for the db.
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, "test_vuln_data.db")
    yield path

    # 2. Ensure all db connections are closed before deleting temp db.
    try:
        if os.path.exists(path):
            os.unlink(path)
        os.rmdir(temp_dir)
    except (PermissionError, OSError):
        print(f"Warning: Could not delete temporary file {path}")

# TEST FOR INITIALIZE_DATABASE #


def test_initialize_database(temp_db_file):
    """
    Test that the database and all tables are created correctly.

    This function tests the following:
    1. The database...
        a. was created upon running (initialize_database).
        b. exists as a file.
        c. contains data/tables.
    2. The tables...
        a. cves table was created.
        b. nvd_api_key table was created.
        c. scan_data table was created.
        d. past_exports table was created.
    """
    initialize_database(temp_db_file)

    assert [
        os.path.exists(temp_db_file),
        "Database file was not created"
    ]  # Test 1a.
    assert [
        os.path.isfile(temp_db_file),
        f"'{temp_db_file}' exists but is not a file"
    ]  # Test 1b.
    assert [
        os.path.getsize(temp_db_file) > 0,
        f"Database file '{temp_db_file}' has no tables"
    ]  # Test 1c.

    conn = sqlite3.connect(temp_db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    cursor.close()
    conn.close()

    table_names = [table[0] for table in tables]

    assert [
        'cves' in table_names,
        "cves table was not created"
    ]  # Test 2a.
    assert [
        'nvd_api_key' in table_names,
        "nvd_api_key table was not created"
    ]  # Test 2b.
    assert [
        'scan_data' in table_names,
        "scan_data table was not created"
    ]  # Test 2c.
    assert [
        'past_exports' in table_names,
        "past_exports table was not created"
    ]  # Test 2d.


def test_create_cves_table(temp_db_file):
    """
    Test that the cves table has the correct structure.

    This function tests the following:
    1. The table has the correct number of fields/columns.
    2. The primary key exists for each cve.
    3. The name of the primary key should be cve_id.
    4. All of the expected fields/columns exist.
    5. All columns should not be null.
    """
    initialize_database(temp_db_file)

    conn = sqlite3.connect(temp_db_file)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(cves);")
    columns = cursor.fetchall()

    cursor.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type='table' AND name='cves';
    """)

    create_stmt = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert [
        len(columns) == 10,
        f"Expected 10 columns in cves table, got {len(columns)}"
    ]  # Test 1.

    pk_column = next((col for col in columns if col[5] == 1), None)
    assert [
        pk_column is not None,
        "No primary key defined for cves table"
    ]  # Test 2.
    assert [
        pk_column[1] == 'cve_id',
        f"Expected primary key to be 'cve_id', got '{pk_column[1]}'"
    ]  # Test 3.

    column_names = [col[1] for col in columns]
    expected_columns = [
        'cve_id', 'base_score', 'severity', 'attack_vector',
        'attack_complexity', 'privileges_required',
        'user_interaction', 'confidentiality_impact',
        'integrity_impact', 'availability_impact'
    ]
    for expected_col in expected_columns:
        assert [
            expected_col in column_names,
            f"Column '{expected_col}' missing from cves table"
        ]  # Test 4.

    for expected_col in expected_columns:
        if expected_col != 'cve_id':
            assert f"{expected_col} TEXT NOT NULL" in create_stmt or \
                   f"{expected_col} REAL NOT NULL" in create_stmt or \
                   f"{expected_col} INTEGER NOT NULL" in create_stmt, \
                   f"""
                   NOT NULL constraint missing for '{expected_col}'
                   in CREATE TABLE statement
                   """  # Test 5.


def test_create_api_key_table(temp_db_file):
    """
    Test that the nvd_api_key table has the correct structure.

    This function tests the following:
    1. The table has the correct number of fields/columns.
    2. The primary key exists and is an integer with autoincrement.
    3. The name of the primary key should be id.
    4. All of the expected fields/columns exist with correct data types.
    5. Non-primary key columns should not be null.
    """
    initialize_database(temp_db_file)

    conn = sqlite3.connect(temp_db_file)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(nvd_api_key);")
    columns = cursor.fetchall()

    cursor.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type='table' AND name='nvd_api_key';
    """)

    create_stmt = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert [
        len(columns) == 6,
        f"Expected 6 columns in nvd_api_key table, got {len(columns)}"
    ]  # Test 1.

    pk_column = next((col for col in columns if col[5] == 1), None)
    assert [
        pk_column is not None,
        "No primary key defined for nvd_api_key table"
    ]  # Test 2.

    assert [
        pk_column[1] == 'id',
        f"Expected primary key to be 'id', got '{pk_column[1]}'"
    ]  # Test 3.

    assert [
        "PRIMARY KEY AUTOINCREMENT" in create_stmt,
        "id column should have PRIMARY KEY AUTOINCREMENT constraint"
    ]  # Test 2.

    column_names = [col[1] for col in columns]
    expected_columns = [
        'id', 'key_name', 'key_value', 'status', 'error_count'
    ]

    expected_types = {
        'id': 'INTEGER',
        'key_name': 'TEXT',
        'key_value': 'TEXT',
        'status': 'TEXT',
        'error_count': 'INTEGER',
        'selected': 'INTEGER'
    }

    for expected_col in expected_columns:
        assert [
            expected_col in column_names,
            f"Column '{expected_col}' missing from nvd_api_key table"
        ]  # Test 4.

        col_index = column_names.index(expected_col)
        col_type = columns[col_index][2]

        assert [
            col_type == expected_types[expected_col],
            "Column '{expected_col}' should be different, got {col_type}"
        ]  # Test 4.

    for expected_col in expected_columns:
        if expected_col != 'id':
            assert [
                f"""
                {expected_col} {expected_types[expected_col]}
                NOT NULL"""
                in create_stmt,
                f"""
                NOT NULL constraint missing for '{expected_col}'
                in CREATE TABLE statement
                """
            ]  # Test 5.


def test_create_scan_data_table(temp_db_file):
    """
    Test that the scan_data table has the correct structure.

    This function tests the following:
    1. The table has the correct number of fields/columns.
    2. The primary key exists and is an integer with autoincrement.
    3. The name of the primary key should be id.
    4. All of the expected fields/columns exist with correct data types.
    5. Required columns (scan_name and file_path) should not be null.
    """
    initialize_database(temp_db_file)

    conn = sqlite3.connect(temp_db_file)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(scan_data);")
    columns = cursor.fetchall()

    cursor.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type='table' AND name='scan_data';
    """)

    create_stmt = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert [
        len(columns) == 8,
        f"Expected 8 columns in scan_data table, got {len(columns)}"
    ]  # Test 1.

    pk_column = next((col for col in columns if col[5] == 1), None)
    assert [
        pk_column is not None,
        "No primary key defined for scan_data table"
    ]  # Test 2.

    assert [
        pk_column[1] == 'id',
        f"Expected primary key to be 'id', got '{pk_column[1]}'"
    ]  # Test 3.

    assert [
        "PRIMARY KEY AUTOINCREMENT" in create_stmt,
        "id column should have PRIMARY KEY AUTOINCREMENT constraint"
    ]  # Test 2.

    column_names = [col[1] for col in columns]
    expected_columns = [
        'id', 'scan_name', 'file_path',
        'total_vulnerabilities', 'unique_cve_list',
        'cache_enabled', 'cached_percentage', 'selected'
    ]

    expected_types = {
        'id': 'INTEGER',
        'scan_name': 'TEXT',
        'file_path': 'TEXT',
        'total_vulnerabilities': 'INTEGER',
        'unique_cve_list': 'TEXT',
        'cache_enabled': 'TEXT',
        'cached_percentage': 'FLOAT',
        'selected': 'INTEGER'
    }

    for expected_col in expected_columns:
        assert [
            expected_col in column_names,
            f"Column '{expected_col}' missing from scan_data table"  # Test 4.
        ]
        col_index = column_names.index(expected_col)
        col_type = columns[col_index][2]
        assert [
            col_type == expected_types[expected_col],
            f"""
                Column '{expected_col}' should be
                {expected_types[expected_col]},
                got {col_type}
            """
        ]  # Test 4.

    required_columns = ['scan_name', 'file_path']
    for required_col in required_columns:
        assert [
            f"""
                {required_col} {expected_types[required_col]} NOT NULL
            """ in create_stmt,
            f"""
                NOT NULL constraint missing for required column
                '{required_col}' in CREATE TABLE statement
            """
        ]  # Test 5.


def test_queried_nvd_data_feed_table(temp_db_file):
    """
    Test that the queried_nvd_data_feed table has the correct structure.

    This function tests the following:
    1. The table has the correct number of fields/columns.
    2. The primary key exists and is text/year.
    3. The name of the primary key should be year.
    4. All of the expected fields/columns exist with correct data types.
    5. All columns should not be null.
    """
    initialize_database(temp_db_file)

    conn = sqlite3.connect(temp_db_file)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(queried_nvd_data_feed);")
    columns = cursor.fetchall()

    cursor.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type='table' AND name='queried_nvd_data_feed';
    """)

    create_stmt = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert [
        len(columns) == 4,
        f"Expected 4 columns in queried data feed table, got {len(columns)}"
    ]  # Test 1.

    pk_column = next((col for col in columns if col[5] == 1), None)
    assert [
        pk_column is not None,
        "No primary key defined for queried_nvd_data_feed table"
    ]  # Test 2.

    assert pk_column[1] == 'year', f"""
        Expected primary key to be 'year', got '{pk_column[1]}'
    """  # Test 3.

    assert "TEXT PRIMARY KEY" in create_stmt, """
        year column should have TEXT PRIMARY KEY constraint
    """  # Test 2.

    column_names = [col[1] for col in columns]
    expected_columns = [
        'year', 'file_byte_size', 'last_queried', 'status'
    ]

    expected_types = {
        'year': 'TEXT',
        'file_byte_size': 'INTEGER',
        'last_queried': 'TEXT',
        'status': 'TEXT'
    }

    for expected_col in expected_columns:
        assert [
            expected_col in column_names,
            f"Column '{expected_col}' missing from queried_nvd_data_feed table"
        ]  # Test 4.
        col_index = column_names.index(expected_col)
        col_type = columns[col_index][2]
        assert [
            col_type == expected_types[expected_col],
            f"""
                Column '{expected_col}' should be
                {expected_types[expected_col]},
                got {col_type}
            """
        ]  # Test 4.

    required_columns = ['file_byte_size', 'last_queried', 'status']
    for required_col in required_columns:
        assert [
            f"""
                {required_col} {expected_types[required_col]} NOT NULL
            """ in create_stmt,
            f"""
            NOT NULL constraint missing for required column
             '{required_col}' in CREATE TABLE statement
            """
        ]  # Test 5.


def test_stored_nvd_data_feed_table(temp_db_file):
    """
    Test that the stored_nvd_data_feed table has the correct structure.

    This function tests the following:
    1. The table has the correct number of fields/columns.
    2. The primary key exists and is text/year.
    3. The name of the primary key should be year.
    4. All of the expected fields/columns exist with correct data types.
    5. All columns should not be null.
    """
    initialize_database(temp_db_file)

    conn = sqlite3.connect(temp_db_file)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(stored_nvd_data_feed);")
    columns = cursor.fetchall()

    cursor.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type='table' AND name='stored_nvd_data_feed';
    """)

    create_stmt = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert [
        len(columns) == 6,
        f"Expected 6 columns in stored_nvd_data_feed table, got {len(columns)}"
    ]  # Test 1.

    pk_column = next((col for col in columns if col[5] == 1), None)
    assert [
        pk_column is not None,
        "No primary key defined for stored_nvd_data_feed table"
    ]  # Test 2.

    assert [
        pk_column[1] == 'year',
        f"Expected primary key to be 'year', got '{pk_column[1]}'"
    ]  # Test 3.

    assert [
        "TEXT PRIMARY KEY" in create_stmt,
        "year column should have TEXT PRIMARY KEY constraint"
    ]  # Test 2.

    column_names = [col[1] for col in columns]
    expected_columns = [
        'year', 'file_byte_size', 'cve_count',
        'last_updated', 'status', 'is_complete'
    ]

    expected_types = {
        'year': 'TEXT',
        'file_byte_size': 'INTEGER',
        'cve_count': 'INTEGER',
        'last_updated': 'TEXT',
        'status': 'TEXT',
        'is_complete': 'INTEGER'
    }

    for expected_col in expected_columns:
        assert [
            expected_col in column_names,
            f"Column '{expected_col}' missing from stored_nvd_data_feed table"
        ]  # Test 4.
        col_index = column_names.index(expected_col)
        col_type = columns[col_index][2]
        assert [
            col_type == expected_types[expected_col],
            f"""
                Column '{expected_col}' should be
                {expected_types[expected_col]},
                got {col_type}
            """
        ]  # Test 4.

    required_columns = [
        'file_byte_size',
        'cve_count',
        'last_updated',
        'status',
        'is_complete'
    ]

    for required_col in required_columns:
        assert [
            f"""
                {required_col} {expected_types[required_col]} NOT NULL
            """ in create_stmt,
            f"""
                NOT NULL constraint missing for required column
                '{required_col}' in CREATE TABLE statement
            """
        ]  # Test 5.


def test_past_exports_data_table(temp_db_file):
    """
    Test that the past_exports table has the correct structure.

    This function tests the following:
    1. The table has the correct number of fields/columns.
    2. The primary key exists and is an integer with autoincrement.
    3. The name of the primary key should be id.
    4. All of the expected fields/columns exist with correct data types.
    5. All columns should not be null.
    """
    initialize_database(temp_db_file)

    conn = sqlite3.connect(temp_db_file)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(past_exports);")
    columns = cursor.fetchall()

    cursor.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type='table' AND name='past_exports';
    """)

    create_stmt = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    assert [
        len(columns) == 7,
        f"Expected 7 columns in past_exports table, got {len(columns)}"
    ]  # Test 1.

    pk_column = next((col for col in columns if col[5] == 1), None)
    assert [
        pk_column is not None,
        "No primary key defined for past_exports table"
    ]  # Test 2.

    assert [
        pk_column[1] == 'id',
        f"Expected primary key to be 'id', got '{pk_column[1]}'"
    ]  # Test 3.

    assert [
        "PRIMARY KEY AUTOINCREMENT" in create_stmt,
        "id column should have PRIMARY KEY AUTOINCREMENT constraint"
    ]  # Test 2.

    column_names = [col[1] for col in columns]
    expected_columns = [
        'id', 'export_name', 'num_scans',
        'export_type', 'export_date',
        'generation_time', 'file_path'
    ]

    expected_types = {
        'id': 'INTEGER',
        'export_name': 'TEXT',
        'num_scans': 'INTEGER',
        'export_type': 'TEXT',
        'export_date': 'TEXT',
        'generation_time': 'REAL',
        'file_path': 'TEXT'
    }

    for expected_col in expected_columns:
        assert [
            expected_col in column_names,
            f"Column '{expected_col}' missing from scan_data table"
        ]  # Test 4.

        col_index = column_names.index(expected_col)
        col_type = columns[col_index][2]

        assert [
            col_type == expected_types[expected_col],
            f"""
                Column '{expected_col}' should be
                {expected_types[expected_col]}, got {col_type}
            """
        ]  # Test 4.

    required_columns = [
        'export_name',
        'num_scans',
        'export_type',
        'export_date',
        'generation_time',
        'file_path'
    ]
    for required_col in required_columns:
        assert [
            f"{required_col} {expected_types[required_col]} NOT NULL"
            in create_stmt,
            f"""
                NOT NULL constraint missing for required column
                '{required_col}' in CREATE TABLE statement
            """
        ]  # Test 5.
