"""
Unit tests for scans_processing.py module
"""
import csv
import sqlite3
import pytest
from processing.scans_processing import (
    return_cve_ids_from_csv,
    return_cached_percentage,
)

### FIXTURES FOR CSV FILES ###
@pytest.fixture
def single_cve_csv_path(tmp_path):
    """Create a temporary CSV file with one CVE ID per row."""
    csv_file = tmp_path / "single_cve.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Description", "CVE ID"])
        writer.writerow(["1", "Vulnerability A", "CVE-2021-1234"])
        writer.writerow(["2", "Vulnerability B", "CVE-2022-5678"])
        writer.writerow(["3", "Vulnerability C", "CVE-2023-9101"])

    return str(csv_file)

@pytest.fixture
def multiple_cve_csv_path(tmp_path):
    """Create a temporary CSV file with multiple CVE IDs per row."""
    csv_file = tmp_path / "multiple_cve.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Description", "CVE IDs"])
        writer.writerow(["1", "Multiple Vulns A", "CVE-2021-1234, CVE-2021-5678"])
        writer.writerow(["2", "Multiple Vulns B", "CVE-2022-1111, CVE-2022-2222, CVE-2022-3333"])
        writer.writerow(["3", "Multiple Vulns C", "CVE-2023-4444"])

    return str(csv_file)

@pytest.fixture
def empty_csv_path(tmp_path):
    """Create an empty CSV file."""
    csv_file = tmp_path / "empty.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

    return str(csv_file)

### FIXTURES FOR DATABASE ###
@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary SQLite database with the cves table."""
    db_file = tmp_path / "test_vuln_data.db"
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    cursor.execute("""
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
    """)
    
    sample_cves = [
        ("CVE-2021-1234", 7.5, "HIGH", "NETWORK", "LOW", "NONE", "NONE", "HIGH", "HIGH", "HIGH"),
        ("CVE-2022-5678", 5.5, "MEDIUM", "NETWORK", "HIGH", "NONE", "REQUIRED", "LOW", "LOW", "LOW"),
        ("CVE-2022-1111", 9.8, "CRITICAL", "NETWORK", "LOW", "NONE", "NONE", "HIGH", "HIGH", "HIGH")
    ]
    
    cursor.executemany("""
    INSERT INTO cves (
        cve_id, base_score, severity, attack_vector, attack_complexity, 
        privileges_required, user_interaction, confidentiality_impact, 
        integrity_impact, availability_impact
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_cves)
    
    conn.commit()
    conn.close()
    
    return str(db_file)

### TESTS FOR RETURN_CVE_IDS_FROM_CSV ###
def test_return_cve_ids_from_csv_single(single_cve_csv_path):
    """
    Test parsing CSV with one CVE ID per row.

    The function tests the following:
    1. The total vulnerabilities count is correct.
    2. The unique vulnerabilities count is correct.
    3. The cve ids are stored correctly in cve_list.
    4. The cve ids are stored correctly in cve_set.
    """
    cve_list, cve_set = return_cve_ids_from_csv(single_cve_csv_path)

    assert len(cve_list) == 3 # Test 1.
    assert len(cve_set) == 3 # Test 2.
    assert "CVE-2021-1234" in cve_list # Test 3.
    assert "CVE-2022-5678" in cve_list # Test 3.
    assert "CVE-2023-9101" in cve_list # Test 3.
    assert "CVE-2021-1234" in cve_set # Test 4.
    assert "CVE-2022-5678" in cve_set # Test 4.
    assert "CVE-2023-9101" in cve_set # Test 4.

def test_return_cve_ids_from_csv_multiple(multiple_cve_csv_path):
    """
    Test parsing CSV with multiple CVE IDs per row.

    The function tests the following:
    1. The total vulnerabilities count is correct.
    2. The unique vulnerabilities count is correct.
    3. The cve ids are stored correctly in cve_list.
    4. The cve ids are stored correctly in cve_set.
    """
    cve_list, cve_set = return_cve_ids_from_csv(multiple_cve_csv_path)

    assert len(cve_list) == 6 # Test 1.
    assert len(cve_set) == 6 # Test 2.
    assert "CVE-2021-1234" in cve_list # Test 3.
    assert "CVE-2021-5678" in cve_list # Test 3.
    assert "CVE-2022-1111" in cve_list # Test 3.
    assert "CVE-2022-2222" in cve_list # Test 3.
    assert "CVE-2022-3333" in cve_list # Test 3.
    assert "CVE-2023-4444" in cve_list # Test 3.

    assert "CVE-2021-1234" in cve_list # Test 4.
    assert "CVE-2021-5678" in cve_list # Test 4.
    assert "CVE-2022-1111" in cve_list # Test 4.
    assert "CVE-2022-2222" in cve_list # Test 4.
    assert "CVE-2022-3333" in cve_list # Test 4.
    assert "CVE-2023-4444" in cve_list # Test 4.

def test_return_cve_ids_from_csv_empty(empty_csv_path):
    """
    Test parsing an empty CSV file.
    
    The function tests the following:
    1. An error is raised for the csv file being empty.
    """
    with pytest.raises(ValueError, match="CSV file is empty."): # Test 1.
        return_cve_ids_from_csv(empty_csv_path)

### TESTS FOR RETURN_CACHED_PERCENTAGE ###
def test_return_cached_percentage_full_match(test_db_path):
    """
    Test cached percentage calculation when all CVEs are in the database.
    
    The function tests the following:
    1. When all CVEs in the set are found in the database, the function returns 100%.
    """
    cve_set = {"CVE-2021-1234", "CVE-2022-5678", "CVE-2022-1111"}
    
    percentage = return_cached_percentage(cve_set, db_file=test_db_path)
    assert percentage == 100.0  # Test 1.

def test_return_cached_percentage_partial_match(test_db_path):
    """
    Test cached percentage calculation when some CVEs are in the database.
    
    The function tests the following:
    1. When some CVEs in the set are found in the database, the function returns correct percentage.
    2. The returned percentage is rounded to the tenths place.
    """
    cve_set = {"CVE-2021-1234", "CVE-2022-5678", "CVE-2023-9101", "CVE-2023-4444", "CVE-2022-2222"}
    
    percentage = return_cached_percentage(cve_set, db_file=test_db_path)
    assert percentage == 40.0  # Test 1 & 2.

def test_return_cached_percentage_no_match(test_db_path):
    """
    Test cached percentage calculation when no CVEs are in the database.
    
    The function tests the following:
    1. When no CVEs in the set are found in the database, the function returns 0%.
    """
    cve_set = {"CVE-2023-9101", "CVE-2023-4444", "CVE-2022-2222"}
    
    percentage = return_cached_percentage(cve_set, db_file=test_db_path)
    assert percentage == 0.0  # Test 1.

def test_return_cached_percentage_empty_set(test_db_path):
    """
    Test cached percentage calculation with an empty set.
    
    The function tests the following:
    1. When the CVE set is empty, the function returns 0%.
    """
    cve_set = set()
    
    percentage = return_cached_percentage(cve_set, db_file=test_db_path)
    assert percentage == 0.0  # Test 1.

def test_return_cached_percentage_custom_chunk_size(test_db_path):
    """
    Test cached percentage calculation with a custom chunk size.
    
    The function tests the following:
    1. The function correctly calculates the percentage when using a smaller chunk size.
    """
    cve_set = {"CVE-2021-1234", "CVE-2022-5678", "CVE-2022-1111"}
    
    percentage = return_cached_percentage(cve_set, chunk_size=1, db_file=test_db_path)
    assert percentage == 100.0  # Test 1.