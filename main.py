"""Main file for this project."""
import sys
from PyQt5.QtWidgets import QApplication, QProgressDialog
from gui import MainWindow
from processing.cve_processing import store_cves_from_csv, NvdDataWorker
from scan_models.scan_class import SCAN
from pdf_export import create_full_report

def main():
    """Main function for this project."""
    app = QApplication(sys.argv)
    window = MainWindow()

    def on_export(nvd_api_key, scans, export_type, pages_to_export):
        """Triggered when export button is clicked."""
        window.export_data = (nvd_api_key, scans, export_type, pages_to_export)

        nvd_api_key, scans, export_type, pages_to_export = window.export_data

        scan_obj_list = []
        for scan in scans:
            scan_obj = SCAN(scan[0], scan[1], scan[2], scan[3])
            store_cves_from_csv(scan_obj.get_filepath(), "vuln_data.db")
            scan_obj_list.append(scan_obj)

        progress_dialog = QProgressDialog("Retrieving NVD data...", "Cancel", 0, 100, window)
        progress_dialog.setWindowTitle("Export Progress")
        progress_dialog.setWindowModality(1)
        progress_dialog.show()

        worker = NvdDataWorker("vuln_data.db", nvd_api_key)
        worker.progressChanged.connect(progress_dialog.setValue)
        worker.errorOccurred.connect(lambda msg: print("Error:", msg))

        def on_worker_finished():
            progress_dialog.close()
            create_full_report("PDF_EXPORT.pdf", scan_obj_list)
        worker.finished.connect(on_worker_finished)

        window.worker = worker
        worker.start()

    window.exportTriggered.connect(on_export)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
