"""
Unit tests for scans_processing.py module
"""
import csv
import pytest
from processing.scans_processing import (
    return_cve_ids_from_csv,
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
