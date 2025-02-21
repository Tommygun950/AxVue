"""Main file"""
import sys
from PyQt6.QtWidgets import QApplication
from gui import VulnerabilityScanAnalyzer
from cve_processing import *

exported_data = {}

def on_export_data(data: dict):
    """Exports all gui information to data dict"""
    exported_data.update(data)

    
def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = VulnerabilityScanAnalyzer()
    window.export_data_signal.connect(on_export_data)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
