"""
This file provides all necessary functions for processing the sqlite3 database.
"""
import sqlite3

### FUNCTIONS FOR DATABASE/TABLE INITIALIZATION ###
def initialize_database(db_file: str = "vuln_data.db"):
    """
    Creates the entire sqlite3 db and tables if they don't exist yet.
    
    This includes:
    1. Initializing the "vuln_data.db".
    2. Initializing the table for cve data.
    3. Initializing the table for nvd api keys.
    4. Initializing the table for past exports.
    5. Initializing the table for scan data.
    """
    # 1. Establish a conneciton & database.
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 2. Create tables (if they don't exist yet).
    create_cves_table(cursor)
    create_api_key_table(cursor)
    create_scan_data_table(cursor)

def create_cves_table(cursor: sqlite3.Cursor):
    """
    Creates the table for cve id and CVSS metric data.
    
    Includes the following fields:
    1.  cve_id -> primary key for the table.
    2.  base_score
    3.  severity
    4.  attack_vector
    5.  attack_complexity
    6.  privileges_required
    7.  user_interaction
    8.  confidentiality_impact
    9.  integrity_impact
    10. availability_impact
    """
    create_cves_table_query = """
    CREATE TABLE IF NOT EXISTS cves (
        cve_id TEXT PRIMARY KEY,
        base_score REAL NOT NULL,
        severity TEXT NOT NULL,
        attack_vector TEXT NOT NULL,
        attack_complexity TEXT NOT NULL,
        privileges_required TEXT NOT NULL,
        user_interaction TEXT NOT NULL,
        confidentiality_impact TEXT NOT NULL,
        integrity_impact TEXT NOT NULL,
        availability_impact TEXT NOT NULL
    );
    """
    cursor.execute(create_cves_table_query)

def create_api_key_table(cursor: sqlite3.Cursor):
    """
    Creates the table for NVD API keys.
    
    Includes the following fields:
    1. id -> primary key for identifying nvd api keys.
    2. key_name -> the given name of an nvd api key given by the user.
    3. status -> notifies program if api key works.
    4. error_count -> used to count # of 404's returned from an api key.
    """
    create_nvd_api_key_table_query = """
    CREATE TABLE IF NOT EXISTS nvd_api_key (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_name TEXT NOT NULL,
        kev_value TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Valid',
        error_count INTEGER NOT NULL DEFAULT 0
    )
    """
    cursor.execute(create_nvd_api_key_table_query)

def create_scan_data_table(cursor: sqlite3.Cursor):
    """
    Creates the table for storing scan data.

    Includes the following fields:
    1. id -> primary key for identifying scans.
    3. scan_name -> the given name of a scan given by the user.
    4. file_path -> user's local file path to the scan's csv file.
    5. total_vulnerabilities -> count of all cve ids found in the csv file.
    6. unique_cve_list -> a list of all unique cve ids stored as a string.
    7. cached_percentage -> a float that represents the total # of unique cves
       that are currently in the cves table.
    """
    create_scan_data_table_query = """
    CREATE TABLE IF NOT EXISTS scan_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        total_vulnerabilities INTEGER,
        unique_cve_list TEXT,
        cached_percentage REAL NOT NULL DEFAULT 0.0
    )
    """
    cursor.execute(create_scan_data_table_query)