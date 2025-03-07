"""
Unit tests for cve_processing.py module
"""
import csv
import sqlite3
import requests
import pytest
from processing.cve_processing import (
    get_v3_metrics,
    get_v2_metrics,
    map_cvss_v2_impact,
    map_cvss_v2_user_interaction,
    check_for_cve_record,
    process_single_cve
)

class FakeResponse:
    """Creates a fake NVD API response to subvert real api use."""
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json_data = json_data
    def json(self):
        """Returns a 200 response with json data."""
        return self._json_data

### FIXTURES FOR SQLITE3 DB ###
@pytest.fixture
def test_db_path(tmp_path):
    """Create a test database with required schema."""
    db_file = tmp_path / "test_vuln_data.db"

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cves (
        cve_id TEXT PRIMARY KEY,
        base_score REAL,
        severity TEXT,
        attack_vector TEXT,
        attack_complexity TEXT,
        privileges_required TEXT,
        user_interaction TEXT,
        confidentiality_impact TEXT,
        integrity_impact TEXT,
        availability_impact TEXT
    )
    """)

    conn.commit()
    conn.close()

    return str(db_file)

### FIXTURES FOR METRIC JSON DATA ###
@pytest.fixture
def v3_metrics_data():
    """Sample CVSS v3 metrics data."""
    return [
        {
            "type": "Primary",
            "cvssData": {
                "baseScore": 8.8,
                "baseSeverity": "HIGH",
                "attackVector": "NETWORK",
                "attackComplexity": "LOW",
                "privilegesRequired": "NONE",
                "userInteraction": "NONE",
                "confidentialityImpact": "HIGH",
                "integrityImpact": "HIGH",
                "availabilityImpact": "HIGH"
            }
        }
    ]

@pytest.fixture
def v2_metrics_data():
    """Sample CVSS v2 metrics data."""
    return [
        {
            "type": "Primary",
            "cvssData": {
                "baseScore": 7.5,
                "accessVector": "NETWORK",
                "accessComplexity": "LOW", 
                "authentication": "NONE",
                "confidentialityImpact": "PARTIAL",
                "integrityImpact": "PARTIAL", 
                "availabilityImpact": "PARTIAL"
            },
            "baseSeverity": "HIGH",
            "userInteractionRequired": True
        }
    ]

@pytest.fixture
def nvd_api_response():
    """Sample response from NVD API."""
    return {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2021-1234",
                    "metrics": {
                        "cvssMetricV31": [
                            {
                                "type": "Primary",
                                "cvssData": {
                                    "baseScore": 8.8,
                                    "baseSeverity": "HIGH",
                                    "attackVector": "NETWORK",
                                    "attackComplexity": "LOW",
                                    "privilegesRequired": "NONE",
                                    "userInteraction": "NONE",
                                    "confidentialityImpact": "HIGH",
                                    "integrityImpact": "HIGH",
                                    "availabilityImpact": "HIGH"
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }


def test_map_cvss_v2_impact():
    """
    Test mapping CVSS v2 impact values to v3 equivalents.
    
    The function tests the following:
    1. Turns v2 terms into v3 terms.
        a. NONE -> NONE (case insensitive)
        b. PARTIAL -> LOW (case insensitive)
        c. COMPLETE -> HIGH (case insensitive)
        d. UNKOWN -> UNKOWN
    """
    assert map_cvss_v2_impact("NONE") == "NONE" # Test 1a.
    assert map_cvss_v2_impact("none") == "NONE" # Test 1a.
    assert map_cvss_v2_impact("PARTIAL") == "LOW" # Test 1b.
    assert map_cvss_v2_impact("partial") == "LOW" # Test 1b.
    assert map_cvss_v2_impact("COMPLETE") == "HIGH" # Test 1c.
    assert map_cvss_v2_impact("complete") == "HIGH" # Test 1c.

    assert map_cvss_v2_impact("UNKNOWN") == "UNKNOWN" # Test 1d.

def test_map_cvss_v2_user_interaction():
    """
    Test mapping CVSS v2 user interaction values to v3 equivalents.

    The function tests the following:
    1. Converts v2 values to v3 if they're boolean.
    2. Converts v2 values to v3 if they're numeric.
    3. Converts v2 values to v3 if they're strings.
    """
    assert map_cvss_v2_user_interaction(True) == "Required" # Test 1.
    assert map_cvss_v2_user_interaction(False) == "None" # Test 1.

    assert map_cvss_v2_user_interaction(1) == "Required" # Test 2.
    assert map_cvss_v2_user_interaction(0) == "None" # Test 2.

    assert map_cvss_v2_user_interaction("required") == "Required" # Test 3.
    assert map_cvss_v2_user_interaction("yes") == "Required" # Test 3.
    assert map_cvss_v2_user_interaction("true") == "Required" # Test 3.
    assert map_cvss_v2_user_interaction("REQUIRED") == "Required" # Test 3.
    assert map_cvss_v2_user_interaction("no") == "None" # Test 3.
    assert map_cvss_v2_user_interaction("none") == "None" # Test 3.

def test_get_v3_metrics_primary(v3_metrics_data):
    """
    Test extracting CVSS v3 metrics with primary metric present.

    The functions tests the following:
    1. Ensure base score is returned correctly.
    2. Ensure severity is returned correctly.
    3. Ensure attack vector is returned correctly.
    4. Ensure attack complexity is returned correctly.
    5. Ensure privileges required is returned correctly.
    6. Ensure user itneraction is returned correctly.
    7. Ensure confidentiality impact is returned correctly.
    8. Ensure integrity impact is returned correctly.
    9. Ensure availability is returned correctly. 
    """
    result = get_v3_metrics(v3_metrics_data)

    assert result[0] == 8.8 # Test 1.
    assert result[1] == "HIGH" # Test 2.
    assert result[2] == "NETWORK" # Test 3.
    assert result[3] == "LOW" # Test 4.
    assert result[4] == "NONE" # Test 5.
    assert result[5] == "NONE" # Test 6.
    assert result[6] == "HIGH" # Test 7.
    assert result[7] == "HIGH" # Test 8.
    assert result [8] == "HIGH" # Test 9.

def test_get_v2_metrics_primary(v2_metrics_data):
    """
    Test extracting CVSS v2 metrics with primary metric present

    The functions tests the following:
    1. Ensure base score is returned correctly.
    2. Ensure severity is returned correctly.
    3. Ensure attack vector is returned correctly.
    4. Ensure attack complexity is returned correctly.
    5. Ensure privileges required is returned correctly.
    6. Ensure user itneraction is returned correctly.
    7. Ensure confidentiality impact is returned correctly.
    8. Ensure integrity impact is returned correctly.
    9. Ensure availability is returned correctly. 
    """
    result = get_v2_metrics(v2_metrics_data)

    assert result[0] == 7.5 # Test 1.
    assert result[1] == "HIGH" # Test 2.
    assert result[2] == "NETWORK" # Test 3.
    assert result[3] == "LOW" # Test 4.
    assert result[4] == "NONE" # Test 5.
    assert result[5] == "Required" # Test 6.
    assert result[6] == "LOW" # Test 7.
    assert result[7] == "LOW" # Test 8.
    assert result [8] == "LOW" # Test 9.

def test_check_for_cve_record_not_found(test_db_path):
    """
    Test that check_for_cve_record returns False when no record exists.

    This function tests the following:
    1. Given a cve id not in the cves table, return a false value.
    """
    result = check_for_cve_record("CVE-NOT-FOUND", test_db_path)
    assert result is False # Test 1.

def test_check_for_cve_record_valid_record(test_db_path):
    """
    Test that check_for_cve_record returns True when a record exists 
    with valid metric values.

    The function tests the following:
    1. Given a cve id with non-NULL values, return true.
    """
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    valid_values = (7.5, "HIGH", "NETWORK", "LOW", "NONE", "Required", "LOW", "LOW", "LOW")
    cursor.execute("""
        INSERT OR REPLACE INTO cves (
            cve_id, base_score, severity, attack_vector, attack_complexity,
            privileges_required, user_interaction, confidentiality_impact,
            integrity_impact, availability_impact
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("CVE-VALID", *valid_values))
    conn.commit()
    conn.close()

    result = check_for_cve_record("CVE-VALID", test_db_path)
    assert result is True # Test 1.

def test_process_single_cve_cached(test_db_path):
    """
    Test that process_single_cve returns (True, "cached") when the CVE record
    already exists in the database with valid metric values.

    The function tests the following:
    1. If a cve already exists with non-NULL values, return (True, "cached").
    """
    valid_values = (7.5, "HIGH", "NETWORK", "LOW", "NONE", "Required", "LOW", "LOW", "LOW")

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO cves (
            cve_id, base_score, severity, attack_vector, attack_complexity,
            privileges_required, user_interaction, confidentiality_impact,
            integrity_impact, availability_impact
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("CVE-ALREADY", *valid_values))

    conn.commit()
    conn.close()

    result = process_single_cve("CVE-ALREADY", "fake-api-key", test_db_path)
    assert result == (True, "cached") # Test 1.

def test_process_single_cve_success(monkeypatch, test_db_path, nvd_api_response):
    """
    Test successful processing of a single CVE.

    This function tests the following:
    1. A successful (True, "success") tuple is returned.
    2. Ensure cve was also entered into the vuln_data.bd in the cves table.
    3. Ensure correct values were entered into the db for that cve.
    """
    def fake_get(*args, **kwargs):
        return FakeResponse(200, nvd_api_response)
    monkeypatch.setattr(requests, "get", fake_get)

    result = process_single_cve("CVE-2021-1234", "fake-api-key", test_db_path)

    assert result == (True, "success") # Test 1.

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cves WHERE cve_id = ?", ("CVE-2021-1234",))
    entry = cursor.fetchone()
    conn.close()

    assert entry is not None # Test 2.

    assert entry[0] == "CVE-2021-1234" # Test 3.
    assert entry[1] == 8.8 # Test 3.
    assert entry[2] == "HIGH" # Test 3.

def test_process_single_cve_timeout(monkeypatch, test_db_path):
    """
    Test handling of request timeout.

    The function tests the following:
    1. Ensure timeout exception is returned.
    2. Ensure a (False, "timeout") tuple is retuned in case of timeout.
    """
    def fake_get(*args, **kwargs):
        raise requests.exceptions.Timeout() # Test 1.
    monkeypatch.setattr(requests, "get", fake_get)

    result = process_single_cve("CVE-2021-1234", "fake-api-key", test_db_path)

    assert result == (False, "timeout") # Test 2.

def test_process_single_cve_request_error(monkeypatch, test_db_path):
    """
    Test handling of general request error.

    The function tests the following:
    1. If a non-200 code is returned, ensure a request exception is raised.
    2. If a non-200 code is returned, ensure a (False, "error") tuple is returned.
    """
    def fake_get(*args, **kwargs):
        raise requests.exceptions.RequestException() # Test 1.
    monkeypatch.setattr(requests, "get", fake_get)

    result = process_single_cve("CVE-2021-1234", "fake-api-key", test_db_path)

    assert result == (False, "error") # Test 2.

def test_process_single_cve_error_status(monkeypatch, test_db_path):
    """
    Test handling of 404 responses.

    The function tests the following:
    1. If an api request returns a 404, return a (False, 404) tuple.
    """
    def fake_get(*args, **kwargs):
        return FakeResponse(404)
    monkeypatch.setattr(requests, "get", fake_get)

    result = process_single_cve("CVE-2021-1234", "fake-api-key", test_db_path)

    assert result == (False, 404) # Test 1.

def test_process_single_cve_v3_metrics(monkeypatch, test_db_path, nvd_api_response):
    """
    Test processing a CVE with v3.1 metrics.

    The function tests the following:
    1. Ensure v3 metric data is inserted into the database.
    2. Ensure result is (True, "success").
    2. Ensure v3 metric data is correct for cve's id.
    3. Ensure v3 metric data is correct for cve's data.
    """
    def fake_get(*args, **kwargs):
        return FakeResponse(200, nvd_api_response)
    monkeypatch.setattr(requests, "get", fake_get)

    result = process_single_cve("CVE-2021-1234", "fake-api-key", test_db_path)

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cves WHERE cve_id = ?", ("CVE-2021-1234",))
    entry = cursor.fetchone()
    conn.close()

    assert entry is not None # Test 1.

    assert result == (True, "success") # Test 2.

    assert entry[0] == "CVE-2021-1234" # Test 3.
    assert entry[1] == 8.8 # Test 3.
    assert entry[2] == "HIGH" # Test 3.
    assert entry[3] == "NETWORK" # Test 3.

def test_process_single_cve_v3_0_metrics(monkeypatch, test_db_path):
    """
    Test processing a CVE with v3.0 metrics.

    The function tests the following:
    1. Ensure the cve was added to vuln_data.db in the cves table.
    2. Ensure the result is (True, "success")
    3. Ensure the correct data is stored for the cve.
    """
    response_data = {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2021-1234",
                    "metrics": {
                        "cvssMetricV30": [
                            {
                                "type": "Primary",
                                "cvssData": {
                                    "baseScore": 7.5,
                                    "baseSeverity": "HIGH",
                                    "attackVector": "NETWORK",
                                    "attackComplexity": "LOW",
                                    "privilegesRequired": "NONE",
                                    "userInteraction": "REQUIRED",
                                    "confidentialityImpact": "HIGH",
                                    "integrityImpact": "HIGH",
                                    "availabilityImpact": "HIGH"
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }

    def fake_get(*args, **kwargs):
        return FakeResponse(200, response_data)
    monkeypatch.setattr(requests, "get", fake_get)

    result = process_single_cve("CVE-2021-1234", "fake-api-key", test_db_path)

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cves WHERE cve_id = ?", ("CVE-2021-1234",))
    entry = cursor.fetchone()
    conn.close()

    assert entry is not None # Test 1.

    assert result == (True, "success") # Test 2.

    assert entry[0] == "CVE-2021-1234" # Test 3.
    assert entry[1] == 7.5 # Test 3.
    assert entry[2] == "HIGH" # Test 3.
    assert entry[6] == "REQUIRED" # Test 3.

def test_process_single_cve_v2_metrics(monkeypatch, test_db_path):
    """
    Test processing a CVE with v2 metrics.

    The function tests the following:
    1. Ensure the cve entry exists in vuln_data.db in the cves table.
    2. Ensure the result is (True, "success")
    3. Ensure correct data is stored for the cve.
    """
    response_data = {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2021-1234",
                    "metrics": {
                        "cvssMetricV2": [
                            {
                                "type": "Primary",
                                "cvssData": {
                                    "baseScore": 6.8,
                                    "accessVector": "NETWORK",
                                    "accessComplexity": "MEDIUM", 
                                    "authentication": "NONE",
                                    "confidentialityImpact": "PARTIAL",
                                    "integrityImpact": "PARTIAL", 
                                    "availabilityImpact": "PARTIAL"
                                },
                                "baseSeverity": "MEDIUM",
                                "userInteractionRequired": True
                            }
                        ]
                    }
                }
            }
        ]
    }

    def fake_get(*args, **kwargs):
        return FakeResponse(200, response_data)
    monkeypatch.setattr(requests, "get", fake_get)

    result = process_single_cve("CVE-2021-1234", "fake-api-key", test_db_path)

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cves WHERE cve_id = ?", ("CVE-2021-1234",))
    entry = cursor.fetchone()
    conn.close()

    assert entry is not None # Test 1.

    assert result == (True, "success") # Test 2.

    assert entry[0] == "CVE-2021-1234" # Test 3.
    assert entry[1] == 6.8 # Test 3.
    assert entry[2] == "MEDIUM" # Test 3.
    assert entry[3] == "NETWORK" # Test 3.
    assert entry[6] == "Required" # Test 3.
    assert entry[7] == "LOW" # Test 3.
