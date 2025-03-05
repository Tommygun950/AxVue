"""Class file for creating & manipulating scan objects."""
import sqlite3

class SCAN:
    """Class for scan objects."""
    def __init__(self, scan_name: str, file_path: str, total_vulns: int, unique_vulns: list[str]):
        self.scan_name = scan_name
        self.file_path = file_path
        self.total_vulns = total_vulns
        self.unique_vulns = unique_vulns

    def get_name(self) -> str:
        """Returns the name of the scan."""
        return self.scan_name

    def get_filepath(self) -> str:
        """Returns the filepath of the csv file."""
        return self.file_path

    def return_total_vulns(self) -> int:
        """Returns the total vulns ct."""
        return self.total_vulns

    def return_unique_vulns(self) -> int:
        """Returns the unqiue vuln ct."""
        return len(self.unique_vulns)

    def return_kev_intersection(self, kev: "SCAN") -> int:
        """Returns the number of vulnerabilities that intersect with the KEV scan."""
        if kev is None:
            return 0
        self_vulns = set(self.unique_vulns)
        kev_vulns = set(kev.unique_vulns)
        return len(self_vulns.intersection(kev_vulns))

    def return_severity(self, severity: str, db_file: str = "vuln_data.db") -> int:
        """Given a severity type, returns the count of CVEs for a scan."""
        if not self.unique_vulns:
            return 0

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in self.unique_vulns)
        query = (
            f"SELECT COUNT(*) FROM cves "
            f"WHERE severity = ? COLLATE NOCASE AND cve_id IN ({placeholders})"
        )
        params = [severity] + list(self.unique_vulns)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def return_severity_percentage(self, severity: str, db_file: str = "vuln_data.db") -> float:
        """Given a scan and a severity type, return the percentage of that severity type."""
        total_ct = self.return_unique_vulns()
        if total_ct == 0:
            return 0.0

        severity_ct = self.return_severity(severity, db_file)
        percentage = (severity_ct / total_ct) * 100
        return round(percentage, 1)

    def return_attack_vector(self, vector: str, db_file: str = "vuln_data.db") -> int:
        """Given an attak vector type, it'll return the num of cves that have that type within a scan."""
        if not self.unique_vulns:
            return 0
        
        conn =sqlite3.connect(db_file)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in self.unique_vulns)
        query = (
            f"SELECT COUNT(*) FROM cves "
            f"WHERE attack_vector = ? COLLATE NOCASE AND cve_id IN ({placeholders})"
        )
        params = [vector] + list(self.unique_vulns)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]

        conn.close()
        return count    

    def return_attack_vector_percentage(self, vector: str, db_file: str = "vuln_data.db") -> float:
        """Given a scan and an attack vector type, return the percentage of that attack vector type."""
        total_ct = self.return_unique_vulns()
        if total_ct == 0:
            return 0.0

        attack_vector_ct = self.return_attack_vector(vector, db_file)
        percentage = (attack_vector_ct / total_ct) * 100
        return round(percentage, 1)

    def return_attack_complexity(self, complexity: str, db_file: str = "vuln_data.db") -> int:
        """Given an attak complexity type, it'll return the num of cves that have that type within a scan."""
        if not self.unique_vulns:
            return 0

        conn =sqlite3.connect(db_file)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in self.unique_vulns)
        query = (
            f"SELECT COUNT(*) FROM cves "
            f"WHERE attack_complexity = ? COLLATE NOCASE AND cve_id IN ({placeholders})"
        )
        params = [complexity] + list(self.unique_vulns)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]

        conn.close()
        return count 

    def return_attack_complexity_percentage(self, complexity: str, db_file: str = "vuln_data.db") -> float:
        """Given a scan and an attack complexity type, return the percentage of that attack complexity type."""
        total_ct = self.return_unique_vulns()
        if total_ct == 0:
            return 0.0

        attack_complexity_ct = self.return_attack_complexity(complexity, db_file)
        percentage = (attack_complexity_ct / total_ct) * 100
        return round(percentage, 1)

    def return_privileges_required(self, privilege: str, db_file: str = "vuln_data.db") -> int:
        """Given a privileges required type, it'll return the num of cves that have that type within a scan."""
        if not self.unique_vulns:
            return 0

        conn =sqlite3.connect(db_file)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in self.unique_vulns)
        query = (
            f"SELECT COUNT(*) FROM cves "
            f"WHERE privileges_required = ? COLLATE NOCASE AND cve_id IN ({placeholders})"
        )
        params = [privilege] + list(self.unique_vulns)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def return_privileges_required_percentage(self, privilege: str, db_file: str = "vuln_data.db") -> float:
        """Given a scan and a privileges required type, return the percentage,"""
        total_ct = self.return_unique_vulns()
        if total_ct == 0:
            return 0.0

        privileges_required_ct = self.return_privileges_required(privilege, db_file)
        percentage = (privileges_required_ct / total_ct) * 100
        return round(percentage, 1)

    def return_user_interaction(self, interaction: str, db_file: str = "vuln_data.db") -> int:
        """Given a user interaction type, it'll return the num of cves that have that type within a scan."""
        if not self.unique_vulns:
            return 0

        conn =sqlite3.connect(db_file)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in self.unique_vulns)
        query = (
            f"SELECT COUNT(*) FROM cves "
            f"WHERE user_interaction = ? COLLATE NOCASE AND cve_id IN ({placeholders})"
        )
        params = [interaction] + list(self.unique_vulns)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def return_user_interaction_percentage(self, interaction: str, db_file: str = "vuln_data.db") -> float:
        """Given a scan and a user interaction type, return the percentage."""
        total_ct = self.return_unique_vulns()
        if total_ct == 0:
            return 0.0

        user_interaction_ct = self.return_user_interaction(interaction, db_file)
        percentage = (user_interaction_ct / total_ct) * 100
        return round(percentage, 1)

    def return_confidentiality(self, impact: str, db_file: str = "vuln_data.db") -> int:
        """Given a confidentiality impact, it'll return the num of cves that have that type within a scan."""
        if not self.unique_vulns:
            return 0

        conn =sqlite3.connect(db_file)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in self.unique_vulns)
        query = (
            f"SELECT COUNT(*) FROM cves "
            f"WHERE confidentiality_impact = ? COLLATE NOCASE AND cve_id IN ({placeholders})"
        )
        params = [impact] + list(self.unique_vulns)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def return_confidentiality_percentage(self, impact: str, db_file: str = "vuln_data.db") -> float:
        """Given a scan and a user interaction type, return the percentage."""
        total_ct = self.return_unique_vulns()
        if total_ct == 0:
            return 0.0

        confidentiality_ct = self.return_confidentiality(impact, db_file)
        percentage = (confidentiality_ct / total_ct) * 100
        return round(percentage, 1)

    def return_integrity(self, impact: str, db_file: str = "vuln_data.db") -> int:
        """Given an integrity impact, it'll return the num of cves that have that type within a scan."""
        if not self.unique_vulns:
            return 0

        conn =sqlite3.connect(db_file)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in self.unique_vulns)
        query = (
            f"SELECT COUNT(*) FROM cves "
            f"WHERE integrity_impact = ? COLLATE NOCASE AND cve_id IN ({placeholders})"
        )
        params = [impact] + list(self.unique_vulns)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def return_integrity_percentage(self, impact: str, db_file: str = "vuln_data.db") -> float:
        """Given a scan and an intergrity impact type, return the percentage."""
        total_ct = self.return_unique_vulns()
        if total_ct == 0:
            return 0.0

        integrity_ct = self.return_integrity(impact, db_file)
        percentage = (integrity_ct / total_ct) * 100
        return round(percentage, 1)

    def return_availability(self, impact: str, db_file: str = "vuln_data.db") -> int:
        """Given an availability impact, it'll return the num of cves that have that type within a scan."""
        if not self.unique_vulns:
            return 0

        conn =sqlite3.connect(db_file)
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in self.unique_vulns)
        query = (
            f"SELECT COUNT(*) FROM cves "
            f"WHERE availability_impact = ? COLLATE NOCASE AND cve_id IN ({placeholders})"
        )
        params = [impact] + list(self.unique_vulns)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def return_availability_percentage(self, impact: str, db_file: str = "vuln_data.db") -> float:
        """Given a scan and an availability impact type, return the percentage."""
        total_ct = self.return_unique_vulns()
        if total_ct == 0:
            return 0.0

        availability_ct = self.return_availability(impact, db_file)
        percentage = (availability_ct / total_ct) * 100
        return round(percentage, 1)
