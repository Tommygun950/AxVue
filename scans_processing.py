"""All functions pertaining to scan_list handling"""
from scan_class import SCAN

def get_scan_names_str(scans_list: list[SCAN]) -> str:
    """Lists all of the scans in this format (s1, s2, s3, ...)"""
    names = [scan.get_name() for scan in scans_list]
    return f"{', '.join(names)}"

def return_total_scans_vulns(scans_list: list[SCAN]) -> int:
    """Returns the total count of vulns parsed in export."""
    total_vulns = 0
    for scan in scans_list:
        total_vulns += scan.return_total_vulns()
    return total_vulns

def get_greatest_scan_name(scans_list: list[SCAN], scan_method: callable) -> str:
    """Returns the name of the scan with the greatest value returned by scan_method."""
    greatest_scan_name = ""
    greatest_quantity = 0
    for scan in scans_list:
        scan_value = scan_method(scan)
        if scan_value > greatest_quantity:
            greatest_quantity = scan_value
            greatest_scan_name = scan.get_name()
    return greatest_scan_name