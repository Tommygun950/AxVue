"""Main file for this project."""
import sys
from gui import MainWindow
from PyQt5.QtWidgets import QApplication
from cve_processing import retrieve_nvd_data
from scan_class import SCAN
from pdf_export import create_full_report

def main():
    """Main function for this project."""
    app = QApplication(sys.argv)
    window = MainWindow()

    def on_export(nvd_api_key, scans, export_type, pages_to_export):
        """Returns all data when export button is clicked."""
        window.export_data = (nvd_api_key, scans, export_type, pages_to_export)

        nvd_api_key = window.export_data[0]
        scans = window.export_data[1]
        export_type = window.export_data[2]
        pages_to_export = window.export_data[3]

        scan_obj_list = []
        for scan in scans:
            scan_obj = SCAN(scan["scan_name"], scan["total_vulns"], scan["unique_vulns"])
            scan_obj_list.append(scan_obj)

        #retrieve_nvd_data("vuln_data.db", nvd_api_key)
        create_full_report("PDF_EXPORT.pdf", scan_obj_list)

    window.exportTriggered.connect(on_export)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
