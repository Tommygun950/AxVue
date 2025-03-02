"""
This file provides all necessary functions for processing CVEs.
"""

import csv
import time
import sqlite3
import requests

# For the worker thread:
from PyQt5.QtCore import QThread, pyqtSignal


def store_cves_from_csv(csv_file: str, db_file: str) -> tuple:
    """Retrieves all CVEs from a CSV file and stores them in an SQLite database.
    This function will also return a total list of CVEs and a set of unique ones.
    """
    cve_id_list = []
    cve_id_set = set()

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    create_table_query = """
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
    );
    """
    cursor.execute(create_table_query)

    def add_cve_to_sql(cve_id: str):
        """Inserts a CVE into the database with NULL values for other fields."""
        insert_query = """
        INSERT OR IGNORE INTO cves (
            cve_id, base_score, severity, attack_vector, attack_complexity,
            privileges_required, user_interaction, confidentiality_impact,
            integrity_impact, availability_impact
        ) VALUES (?, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
        """
        cursor.execute(insert_query, (cve_id,))

    def find_cve_index(rows: list[list[str]]) -> int:
        """Automatically identifies the CSV column index containing the CVE IDs."""
        for row_num in range(2):
            if len(rows) > row_num:
                for index, column in enumerate(rows[row_num]):
                    if "CVE" in column.upper().strip():
                        return index
        raise ValueError("No column containing 'CVE' was found in the CSV file.")

    def insert_cves_from_rows(rows_iterator: iter, cve_index: int):
        """Processes CSV rows to extract CVE IDs and insert them into the database.
        Also adds CVE ids to list and set.
        """
        for row in rows_iterator:
            if len(row) > cve_index:
                cve_cell = row[cve_index].strip()
                if cve_cell:
                    if "," in cve_cell:
                        for cve in cve_cell.split(","):
                            cve_stripped = cve.strip()
                            if cve_stripped:
                                add_cve_to_sql(cve_stripped)
                                cve_id_list.append(cve_stripped)
                                cve_id_set.add(cve_stripped)
                    else:
                        add_cve_to_sql(cve_cell)
                        cve_id_list.append(cve_cell)
                        cve_id_set.add(cve_cell)

    with open(csv_file, mode="r", encoding="utf-8") as file:
        rows = list(csv.reader(file))
        if not rows:
            raise ValueError("CSV file is empty.")
        cve_index = find_cve_index(rows)
        rows_iterator = iter(rows[1:])
        insert_cves_from_rows(rows_iterator, cve_index)

    conn.commit()
    conn.close()

    return cve_id_list, cve_id_set


def return_cached_percentage(unique_cves: list[str], db_file: str) -> float:
    """Given a list of unique CVEs, determine what percentage of them have cached data (i.e.,
    a non-NULL base_score) in the 'cves' table of the specified database file.
    """
    if not unique_cves:
        return 0.0

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in unique_cves)
    query = f"SELECT COUNT(*) FROM cves WHERE cve_id IN ({placeholders}) AND base_score IS NOT NULL"
    cursor.execute(query, unique_cves)
    count = cursor.fetchone()[0]

    conn.close()

    percentage = (count / len(unique_cves)) * 100
    return round(percentage, 1)


# --- Helper functions for metrics ---
def get_v3_metrics(metric_list: list) -> tuple:
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
    Maps CVSS v2 impact values (confidentiality, integrity, availability) 
    to the common vocabulary: NONE, LOW, or HIGH.
    """
    mapping = {
        "NONE": "NONE",
        "PARTIAL": "LOW",
        "COMPLETE": "HIGH"
    }
    # Ensure the value is compared in uppercase.
    return mapping.get(value.upper(), value)

def map_cvss_v2_user_interaction(value) -> str:
    """
    Maps CVSS v2 user interaction data to a common string.
    For v2 this is typically a boolean value, so we convert it.
    """
    if isinstance(value, bool):
        return "Required" if value else "None"
    # If for some reason it's numeric (0/1), treat nonzero as True.
    try:
        return "Required" if float(value) != 0 else "None"
    except (ValueError, TypeError):
        # Fallback: if it's already a string, standardize its capitalization.
        lower_val = str(value).lower()
        if lower_val in ("required", "yes", "true"):
            return "Required"
        return "None"

# Then update your get_v2_metrics function to include these mappings:
def get_v2_metrics(metric_list: list) -> tuple:
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
            # Apply mapping for confidentiality, integrity, availability:
            map_cvss_v2_impact(primary_metric["cvssData"]["confidentialityImpact"]),
            map_cvss_v2_impact(primary_metric["cvssData"]["integrityImpact"]),
            map_cvss_v2_impact(primary_metric["cvssData"]["availabilityImpact"])
        )
    else:
        # Fallback for non-primary metrics; adjust similarly if needed.
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

# --- NVD Data Retrieval Worker Thread ---
class NvdDataWorker(QThread):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal()
    errorOccurred = pyqtSignal(str)

    def __init__(self, db_file: str, nvd_api_key: str, query_throttle_time: float = 0.7):
        super().__init__()
        self.db_file = db_file
        self.nvd_api_key = nvd_api_key
        self.query_throttle_time = query_throttle_time

    def run(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        select_query = """
        SELECT cve_id FROM cves
        WHERE base_score IS NULL
           OR severity IS NULL
           OR attack_vector IS NULL
           OR attack_complexity IS NULL
           OR privileges_required IS NULL
           OR user_interaction IS NULL
           OR confidentiality_impact IS NULL
           OR integrity_impact IS NULL
           OR availability_impact IS NULL
        """
        cursor.execute(select_query)
        incomplete_cves = cursor.fetchall()
        total = len(incomplete_cves)
        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

        for i, (cve_id,) in enumerate(incomplete_cves):
            start_time = time.time()
            url = f"{base_url}?cveId={cve_id}"
            headers = {"apiKey": self.nvd_api_key}
            timeout_seconds = 90
            try:
                response = requests.get(url, headers=headers, timeout=timeout_seconds)
            except requests.exceptions.Timeout:
                self.errorOccurred.emit(f"Timeout fetching data for {cve_id}")
                continue
            except requests.exceptions.RequestException as e:
                self.errorOccurred.emit(f"Error fetching data for {cve_id}: {e}")
                continue

            if response.status_code != 200:
                self.errorOccurred.emit(f"Failed to fetch data for {cve_id}. Status code: {response.status_code}")
                continue

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

            elapsed_time = time.time() - start_time
            remaining_time = self.query_throttle_time - elapsed_time
            if remaining_time > 0:
                time.sleep(remaining_time)

            update_query = """
            UPDATE cves
            SET base_score = ?,
                severity = ?,
                attack_vector = ?,
                attack_complexity = ?,
                privileges_required = ?,
                user_interaction = ?,
                confidentiality_impact = ?,
                integrity_impact = ?,
                availability_impact = ?
            WHERE cve_id = ?
            """
            cursor.execute(update_query, (*values, cve_id))
            conn.commit()

            progress = int(((i + 1) / total) * 100)
            self.progressChanged.emit(progress)

        conn.close()
        self.finished.emit()
