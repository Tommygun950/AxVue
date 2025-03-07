"""
This file provides all necessary functions for processing the scan data.
"""
import csv

def return_cve_ids_from_csv(csv_file: str) -> tuple[list, list]:
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

