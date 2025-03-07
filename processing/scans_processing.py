"""
This file provides all necessary functions for processing the scan data.
"""
import csv
import sqlite3

def return_cve_ids_from_csv(csv_file: str) -> tuple[list, set]:
    """
    Reads a given csv file and returns a list of total vulns and a list of unique vulns.

    This function should:
    1. Read the csv file row by row.
    2. Automatically identify the index where the cve id is.
    3. Identify if the cve index stores a single cve or multiple.
    4. Parse through the cve ids and return a list of total vulns.
    5. Parse through the cve ids and return a list of unique vulns.
    """
    def find_cve_index(rows):
        """
        Find the index of the column containing CVE information.

        This function should:
        1. Enumerate through each index in the first two rows.
        2. For each index, see if the string "cve" is inside that index.
        3. If found, return the index.
        4. If it's not found, return a value error.
        """
        for row_num in range(min(2, len(rows))):
            for index, column in enumerate(rows[row_num]):
                if "CVE" in column.upper():
                    return index
        raise ValueError("No column containing 'CVE' was found in the CSV file.")
    
    def process_cve_cell(cve_cell, cve_id_list, cve_id_set):
        """
        Process a cell that may contain one or more CVE IDs.

        This function should:
        1. If the cve index is a list, call process_multiple_cves.
        2. If the cve index is a single cve id, call add_cve.
        """
        if "," in cve_cell:
            process_multiple_cves(cve_cell, cve_id_list, cve_id_set)
        else:
            add_cve(cve_cell, cve_id_list, cve_id_set)
    
    def process_multiple_cves(cve_cell, cve_id_list, cve_id_set):
        """
        Process a cell containing multiple comma-separated CVE IDs.

        This function should:
        1. Split the data within the cve index by ",".
        2. If the index within the stripped cve index isn't empty, call add_cve.
        """
        for cve in cve_cell.split(","):
            cve_stripped = cve.strip()
            if cve_stripped:
                add_cve(cve_stripped, cve_id_list, cve_id_set)
    
    def add_cve(cve, cve_id_list, cve_id_set):
        """
        Add a single CVE ID to both the list and set.

        This function should:
        1. Given a successfully parsed cve id:
            a. Append it to the total vulns list.
            b. Add it to the unique vulns set.
        """
        cve_id_list.append(cve)
        cve_id_set.add(cve)
    
    cve_id_list = []
    cve_id_set = set()
    
    with open(csv_file, mode="r", encoding="utf-8") as file:
        rows = list(csv.reader(file))
        if not rows:
            raise ValueError("CSV file is empty.")
        
        cve_index = find_cve_index(rows)
        
        for row in rows[1:]:
            if len(row) > cve_index:
                cve_cell = row[cve_index].strip()
                process_cve_cell(cve_cell, cve_id_list, cve_id_set)
   
    return cve_id_list, cve_id_set

def return_cached_percentage(cve_id_set: set[str], chunk_size: int = 500 , db_file: str = "vuln_data.db") -> float:
    """
    Given a set of cve ids, it queries the cves table in vuln_data.db
    to return a percentage on how many of the cve ids in the set are in
    the table.
    This function should:
    1. If the cve id set is empty, return 0%.
    2. Connect to vuln_data.db.
    3. Query the cves table in chunks to prevent sqlite query errors.
    4. With the calculated total count and found count, calculate the percentage.
    """        
    def query_database_in_chunks(cve_list: list, cursor, chunk_size: int) -> int:
        """
        Queries the database in chunks to find how many CVEs exist in the database.
        This function should:
        1. Process the list of CVE IDs in chunks of the specified size.
        2. Create and execute parameterized queries for each chunk.
        3. Return the total count of found CVEs.
        """
        found_count = 0
        total_count = len(cve_list)
        
        for i in range(0, total_count, chunk_size):
            chunk = cve_list[i:i+chunk_size]
            
            placeholders = ','.join(['?' for _ in chunk])
            query = f"SELECT COUNT(*) FROM cves WHERE cve_id IN ({placeholders})"
            
            cursor.execute(query, chunk)
            result = cursor.fetchone()
            found_count += result[0]
            
        return found_count

    def calculate_percentage(found_count: int, total_count: int) -> float:
        """
        Calculates the percentage given the found and total count.
        This function should:
        1. Ensure the total count is above 0 to prevent x/0 error.
        2. Divide the found ct by the total ct and multiply by 100.
        3. Return the percentage rounded to the tenth's place.
        """
        if total_count > 0:
            return round((found_count / total_count) * 100.0, 1)
        else:
            return 0.0
    
    if not cve_id_set:
        return 0.0
        
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cve_list = list(cve_id_set)
    total_count = len(cve_list)
    
    found_count = query_database_in_chunks(cve_list, cursor, chunk_size)
    
    conn.close()
    
    return calculate_percentage(found_count, total_count)