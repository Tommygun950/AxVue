class SCAN:
    """Class for scan objects."""
    def __init__(self, scan_name: str, total_vulns: int, unique_vulns: list[str]):
        self.scan_name = scan_name
        self.total_vulns = total_vulns
        self.unique_vulns = unique_vulns

    def get_name(self) -> str:
        """Returns the name of the scan."""
        return self.scan_name

    def return_total_vulns(self) -> int:
        """Returns the total vulns ct."""
        return self.total_vulns

    def return_unique_vulns(self) -> int:
        """Returns the unqiue vuln ct."""
        return len(self.unique_vulns)
