import csv

def get_cves_from_csv(csv_file: str) -> list[str]:
    cve_list = []
    
    def find_cve_index(rows: list[list[str]]) -> int:
        cve_index = None
        
        for row_num in range(2):
            if len(rows) > row_num:
                for i, column in enumerate(rows[row_num]):
                    if "CVE" in column.upper().strip():
                        return i
        
        raise ValueError("No column containing 'CVE' was found in the CSV file.")
    
    def extract_cves(rows_iterator: iter, cve_index: int):
        for row in rows_iterator:
            if len(row) > cve_index:
                cve_row = row[cve_index].strip()
                
                if "," in cve_row:
                    for cve in cve_row.split(","):
                        cve_stripped = cve.strip()
                        cve_list.append(cve_stripped)
                else:
                    cve_list.append(cve_row)
    
    with open(csv_file, mode="r", encoding="utf-8") as file:
        rows = list(csv.reader(file))
        
        if not rows:
            raise ValueError("CSV file is empty.")
        
    cve_index = find_cve_index(rows)
    extract_cves(rows[1:], cve_index)
    
    return cve_list