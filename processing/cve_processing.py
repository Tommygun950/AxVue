import csv
import sqlite3
import requests
import time

def return_cve_ids_from_csv(csv_file: str) -> tuple:
    """
    Reads a given csv file an returns a list of total vulns and a list of unique vulns.
    """
    cve_id_list = []
    cve_id_set = set()

    with open(csv_file, mode="r", encoding="utf-8") as file:
        rows = list(csv.reader(file))
        if not rows:
            raise ValueError("CSV file is empty.")

        def find_cve_index(rows):
            for row_num in range(min(2, len(rows))):
                for index, column in enumerate(rows[row_num]):
                    if "CVE" in column.upper():
                        return index
            raise ValueError("No column containing 'CVE' was found in the CSV file.")

        cve_index = find_cve_index(rows)

        for row in rows[1:]:
            if len(row) > cve_index:
                cve_cell = row[cve_index].strip()
                if cve_cell:
                    if "," in cve_cell:
                        for cve in cve_cell.split(","):
                            cve_stripped = cve.strip()
                            if cve_stripped:
                                cve_id_list.append(cve_stripped)
                                cve_id_set.add(cve_stripped)
                    else:
                        cve_id_list.append(cve_cell)
                        cve_id_set.add(cve_cell)

    return cve_id_list, cve_id_set

def get_v3_metrics(metric_list: list) -> tuple:
    """
    Extracts and returns CVSS v3 metrics from a list of metric dictionaries.
    Returns a tuple with all base metric data.
    """
    primary_metric = next((m for m in metric_list if m.get("type") == "Primary"), None)
    if primary_metric:
        return (
            primary_metric["cvssData"]["baseScore"],
            primary_metric["cvssData"]["baseSeverity"],
            primary_metric["cvssData"]["attackVector"],
            primary_metric["cvssData"]["attackComplexity"],
            primary_metric["cvssData"]["privilegesRequired"],
            primary_metric["cvssData"]["userInteraction"],
            primary_metric["cvssData"]["confidentialityImpact"],
            primary_metric["cvssData"]["integrityImpact"],
            primary_metric["cvssData"]["availabilityImpact"]
        )
    else:
        return (
            metric_list[0]["cvssData"]["baseScore"],
            metric_list[0]["cvssData"]["baseSeverity"],
            metric_list[0]["cvssData"]["attackVector"],
            metric_list[0]["cvssData"]["attackComplexity"],
            metric_list[0]["cvssData"]["privilegesRequired"],
            metric_list[0]["cvssData"]["userInteraction"],
            metric_list[0]["cvssData"]["confidentialityImpact"],
            metric_list[0]["cvssData"]["integrityImpact"],
            metric_list[0]["cvssData"]["availabilityImpact"]
        )

def map_cvss_v2_impact(value: str) -> str:
    """
    Maps CVSS v2 impact values to a common vocabulary.
    Specifically:
      - "NONE" stays as "NONE"
      - "PARTIAL" becomes "LOW"
      - "COMPLETE" becomes "HIGH"
    """
    mapping = {
        "NONE": "NONE",
        "PARTIAL": "LOW",
        "COMPLETE": "HIGH"
    }
    return mapping.get(value.upper(), value)

def map_cvss_v2_user_interaction(value) -> str:
    """
    Maps CVSS v2 user interaction data to a common string.
    """
    if isinstance(value, bool):
        return "Required" if value else "None"
    try:
        return "Required" if float(value) != 0 else "None"
    except (ValueError, TypeError):
        lower_val = str(value).lower()
        if lower_val in ("required", "yes", "true"):
            return "Required"
        return "None"

def get_v2_metrics(metric_list: list) -> tuple:
    """
    Extracts and returns CVSS v2 metrics from a list of metric dictionaries.
    Returns a tuple with base metric data.
    """
    primary_metric = next((m for m in metric_list if m.get("type") == "Primary"), None)
    if primary_metric:
        user_interaction = map_cvss_v2_user_interaction(primary_metric["userInteractionRequired"])
        return (
            primary_metric["cvssData"]["baseScore"],
            primary_metric["baseSeverity"],
            primary_metric["cvssData"]["accessVector"],
            primary_metric["cvssData"]["accessComplexity"],
            primary_metric["cvssData"]["authentication"],
            user_interaction,
            map_cvss_v2_impact(primary_metric["cvssData"]["confidentialityImpact"]),
            map_cvss_v2_impact(primary_metric["cvssData"]["integrityImpact"]),
            map_cvss_v2_impact(primary_metric["cvssData"]["availabilityImpact"])
        )
    else:
        user_interaction = map_cvss_v2_user_interaction(metric_list[0]["userInteraction"])
        return (
            metric_list[0]["cvssData"]["baseScore"],
            metric_list[0]["baseSeverity"],
            metric_list[0]["cvssData"]["accessVector"],
            metric_list[0]["attackComplexity"],
            metric_list[0]["privilegesRequired"],
            user_interaction,
            map_cvss_v2_impact(metric_list[0]["cvssData"]["confidentialityImpact"]),
            map_cvss_v2_impact(metric_list[0]["cvssData"]["integrityImpact"]),
            map_cvss_v2_impact(metric_list[0]["cvssData"]["availabilityImpact"])
        )

def check_for_cve_record(cve_id: str, db_file: str = "vuln_data.db") -> bool:
    """
    Given a cve id, it'll check the vuln_data.db and cves table if cve_id record exists.

    The function should do the following:
    1. Take a cve id, and query the cves table to see if base metric data comes back.
    2. If all of the cve data comes back, return true.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    query = """
    SELECT base_score, severity, attack_vector, attack_complexity,
           privileges_required, user_interaction, confidentiality_impact,
           integrity_impact, availability_impact
    FROM cves
    WHERE cve_id = ?
    """

    cursor.execute(query, (cve_id,))
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return False

    default_values = (0.0, "", "", "", "", "", "", "", "")
    
    if row != default_values:
        return True
    return False

def process_single_cve(cve_id: str, nvd_api_key: str, db_file: str = "vuln_data.db") -> tuple:
    """
    Processes a single CVE by ensuring it's existance in the vuln_data.db in the cves table.

    The function should do the following:
    1. Check to see if it exists already in the sql db, if so return a (True, "cached") tuple.
    2. Make an api request for the single cve id.
        a. Raise an exception for a request timeout.
        b. Raise an eception for a bad request.
        c. Return a (False, "status_code") if any other HTTP error is returned.
    3. Gather the correct metric data from the json return.
    4. Add the entire cve into the database.
    """

    if check_for_cve_record(cve_id, db_file):
        return (True, "cached")

    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    url = f"{base_url}?cveId={cve_id}"
    headers = {"apiKey": nvd_api_key}
    timeout_seconds = 90

    try:
        response = requests.get(url, headers=headers, timeout=timeout_seconds)
    except requests.exceptions.Timeout:
        return (False, "timeout")
    except requests.exceptions.RequestException:
        return (False, "error")

    if response.status_code != 200:
        return (False, response.status_code)

    data = response.json()
    values = (0.0, "", "", "", "", "", "", "", "")
    if "vulnerabilities" in data and data["vulnerabilities"]:
        item = data["vulnerabilities"][0]
        cve_info = item.get("cve", {})
        metrics = cve_info.get("metrics", {})
        if metrics.get("cvssMetricV31"):
            values = get_v3_metrics(metrics["cvssMetricV31"])
        elif metrics.get("cvssMetricV30"):
            values = get_v3_metrics(metrics["cvssMetricV30"])
        elif metrics.get("cvssMetricV2"):
            values = get_v2_metrics(metrics["cvssMetricV2"])

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    insert_cve_query = """
    INSERT OR REPLACE INTO cves (
        cve_id, base_score, severity, attack_vector, attack_complexity,
        privileges_required, user_interaction, confidentiality_impact,
        integrity_impact, availability_impact
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_cve_query, (cve_id, *values))
    conn.commit()
    conn.close()

    return (True, "success")
