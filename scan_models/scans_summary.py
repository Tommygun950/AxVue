"""All functions pertaining to scan_list handling"""
from scan_models.scan_class import SCAN

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

def call_scan_by_name(scan_list: list[SCAN], scan_name: str) -> SCAN:
    """Returns a scan based off the name of a scan."""
    for scan in scan_list:
        if scan_name == scan.get_name():
            return scan

def return_relation_percentage(scan1_method: callable, scan2_method: callable):
    """Given 2 scan and functions, will find the relation percentage."""
    scan1_value = scan1_method()
    scan2_value = scan2_method()

    if scan2_value == 0:
        return 0.0

    percentage = (scan1_value / scan2_value) * 100
    return round(percentage, 1)

def get_scan_values(scans_list, scan_method: callable) -> list:
    """Given a list of scans and a method, it'll store all scan values in a list."""
    return [scan_method(scan) for scan in scans_list]
