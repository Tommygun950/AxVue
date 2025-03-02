import sqlite3
import json
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QHeaderView, QPushButton, QTableWidgetItem,
    QToolBar, QAction, QDialog, QLineEdit, QLabel, QDialogButtonBox,
    QFileDialog, QHBoxLayout, QGroupBox, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from cve_processing import store_cves_from_csv, return_cached_percentage

class AddScanDialog(QDialog):
    """Popup window for adding/editing a scan."""
    def __init__(self, scan_name="", file_path="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Scan" if not scan_name else "Edit Scan")
        self.resize(400, 150)

        self.layout = QVBoxLayout(self)

        # Scan Name input.
        self.name_label = QLabel("Scan Name:")
        self.scan_name_edit = QLineEdit()
        self.scan_name_edit.setText(scan_name)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.scan_name_edit)

        # File Path input with a Browse button.
        self.path_label = QLabel("File Path:")
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setText(file_path)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_button)
        self.layout.addWidget(self.path_label)
        self.layout.addLayout(file_layout)

        # OK and Cancel buttons.
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def browse_file(self):
        """Opens a file dialog to select a file and sets the file path."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_path:
            self.file_path_edit.setText(file_path)

    def get_data(self):
        """Returns the entered scan name and file path."""
        return self.scan_name_edit.text(), self.file_path_edit.text()

class MainWindow(QMainWindow):
    """Main window for GUI application."""
    # Signal to emit export variables.
    exportTriggered = pyqtSignal(str, list, str, list)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer")
        self.resize(1200, 800)

        # Variable to store the NVD API Key.
        self.nvd_api_key = ""

        self.init_db()
        self.init_toolbar()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # --- NVD API Key Section ---
        self.api_key_layout = QHBoxLayout()
        self.api_key_label = QLabel("NVD API Key:")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter NVD API Key")
        self.api_key_edit.textChanged.connect(self.update_api_key)
        self.api_key_layout.addWidget(self.api_key_label)
        self.api_key_layout.addWidget(self.api_key_edit)
        self.layout.addLayout(self.api_key_layout)
        # ----------------------------

        # Table Widget for displaying scans.
        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(7)
        self.scan_table.setHorizontalHeaderLabels([
            "Scan Name", "File Path", "Total Vulnerabilities",
            "Unique Vulnerabilities", "Cached %", "Edit", "Delete"
        ])
        self.scan_table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.scan_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.layout.addWidget(self.scan_table)

        self.load_scans()

        # --- Export Configuration Section ---
        self.export_config_group = QGroupBox("Export Configuration")
        export_main_layout = QHBoxLayout(self.export_config_group)

        # Left column: Export settings.
        export_settings_layout = QVBoxLayout()
        type_layout = QHBoxLayout()
        export_type_label = QLabel("Export Type:")
        self.export_type_combo = QComboBox()
        self.export_type_combo.addItems(["PDF", "Excel"])
        type_layout.addWidget(export_type_label)
        type_layout.addWidget(self.export_type_combo)
        export_settings_layout.addLayout(type_layout)

        pages_label = QLabel("Pages to Export:")
        export_settings_layout.addWidget(pages_label)
        self.page_checkboxes = {}
        # Updated pages list with "Details Page" added.
        pages = [
            "Title Page", "Disclosure", "Overview",
            "KEV Catalog Comparison", "Vulnerability Scores",
            "Severity Disposition", "Attack Vector Disposition",
            "Attack Complexity Disposition", "Privileges Required",
            "Confidentiality Impact", "Integrity Impact",
            "Availability Impact", "Details Page"
        ]
        for page in pages:
            checkbox = QCheckBox(page)
            checkbox.setChecked(True)
            self.page_checkboxes[page] = checkbox
            export_settings_layout.addWidget(checkbox)

        self.export_button = QPushButton("Export Report")
        self.export_button.clicked.connect(self.export_report)
        export_settings_layout.addWidget(self.export_button)

        # Right column: Past exports table.
        past_exports_layout = QVBoxLayout()
        past_exports_label = QLabel("Past Exports:")
        past_exports_layout.addWidget(past_exports_label)

        self.past_exports_table = QTableWidget()
        self.past_exports_table.setColumnCount(5)
        self.past_exports_table.setHorizontalHeaderLabels([
            "Export Name", "# of Scans", "Export Type", "Export Date", "Delete"
        ])
        # Set columns 0-3 to stretch and column 4 (Delete) to resize to contents.
        self.past_exports_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.past_exports_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.past_exports_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.past_exports_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.past_exports_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        past_exports_layout.addWidget(self.past_exports_table)
        export_main_layout.addLayout(export_settings_layout)
        export_main_layout.addLayout(past_exports_layout)

        self.layout.addWidget(self.export_config_group)
        # ------------------------------------

        self.load_past_exports()

    def update_api_key(self, text):
        """Updates the NVD API Key variable."""
        self.nvd_api_key = text

    def init_db(self):
        """Initializes the SQLite database and creates the 'scan' and 'past_exports' tables if they don't exist."""
        self.conn = sqlite3.connect("vuln_data.db")
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                total_vulnerabilities INTEGER,
                unique_cve_list TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS past_exports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                export_name TEXT NOT NULL,
                num_scans INTEGER NOT NULL,
                export_type TEXT NOT NULL,
                export_date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def init_toolbar(self):
        """Creates a toolbar with actions."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        add_scan_action = QAction("Add Scan", self)
        add_scan_action.setStatusTip("Add a new scan to the list.")
        add_scan_action.triggered.connect(self.add_scan)
        toolbar.addAction(add_scan_action)

    def load_scans(self):
        """Loads all stored scans from the database and populates the scan table."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, scan_name, file_path, total_vulnerabilities, unique_cve_list 
            FROM scan
        """)
        for scan_id, scan_name, file_path, total_vulns, unique_cve_list in cur.fetchall():
            self.add_scan_row(scan_id, scan_name, file_path, str(total_vulns), unique_cve_list)

    def load_past_exports(self):
        """Loads all past exports (in descending order) from the database and populates the past exports table."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, export_name, num_scans, export_type, export_date 
            FROM past_exports ORDER BY id DESC
        """)
        records = cur.fetchall()
        self.past_exports_table.setRowCount(0)
        for export_id, export_name, num_scans, export_type, export_date in records:
            self.add_export_row(export_id, export_name, num_scans, export_type, export_date)

    def add_scan(self):
        """Opens the AddScanDialog, processes the CSV, inserts a new scan into the database, and updates the scan table."""
        dialog = AddScanDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            scan_name, file_path = dialog.get_data()
            if scan_name and file_path:
                cve_id_list, cve_id_set = store_cves_from_csv(file_path, "vuln_data.db")
                total_vulns = len(cve_id_list)
                unique_cve_list_json = json.dumps(list(cve_id_set))
                scan_id = self.insert_scan(scan_name, file_path, total_vulns, unique_cve_list_json)
                self.add_scan_row(scan_id, scan_name, file_path, str(total_vulns), unique_cve_list_json)

    def insert_scan(self, scan_name, file_path, total_vulnerabilities, unique_cve_list):
        """Inserts a new scan record into the 'scan' table and returns its ID."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO scan (scan_name, file_path, total_vulnerabilities, unique_cve_list)
            VALUES (?, ?, ?, ?)
        """, (scan_name, file_path, total_vulnerabilities, unique_cve_list))
        self.conn.commit()
        return cur.lastrowid

    def add_scan_row(self, scan_id, scan_name, file_path, total_vulnerabilities, unique_cve_list):
        """Inserts a new row into the scan table."""
        row_position = self.scan_table.rowCount()
        self.scan_table.insertRow(row_position)

        # Column 0: Scan Name (with checkbox)
        item = QTableWidgetItem(scan_name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, scan_id)
        item.setData(Qt.UserRole + 1, unique_cve_list)
        self.scan_table.setItem(row_position, 0, item)

        # Column 1: File Path
        self.scan_table.setItem(row_position, 1, QTableWidgetItem(file_path))
        # Column 2: Total Vulnerabilities
        self.scan_table.setItem(row_position, 2, QTableWidgetItem(total_vulnerabilities))
        # Column 3: Unique Vulnerabilities (display count)
        try:
            unique_list = json.loads(unique_cve_list) if unique_cve_list else []
            unique_count = len(unique_list)
        except json.JSONDecodeError:
            unique_count = 0
        self.scan_table.setItem(row_position, 3, QTableWidgetItem(str(unique_count)))
        
        # Column 4: Cached %
        # Use return_cached_percentage to compute the percentage.
        cached_pct = return_cached_percentage(unique_list, "vuln_data.db")
        self.scan_table.setItem(row_position, 4, QTableWidgetItem(f"{cached_pct}%"))
        
        # Column 5: Edit button
        btn_edit = QPushButton("Edit")
        btn_edit.clicked.connect(lambda _, sid=scan_id: self.edit_scan(sid))
        self.scan_table.setCellWidget(row_position, 5, btn_edit)
        
        # Column 6: Delete button
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(lambda _, sid=scan_id: self.delete_scan(sid))
        self.scan_table.setCellWidget(row_position, 6, btn_delete)

    def find_row_by_scan_id(self, scan_id):
        """Returns the table row index for the given scan_id."""
        for row in range(self.scan_table.rowCount()):
            item = self.scan_table.item(row, 0)
            if item and item.data(Qt.UserRole) == scan_id:
                return row
        return None

    def edit_scan(self, scan_id):
        """Opens a dialog to edit a scan and updates the table."""
        row = self.find_row_by_scan_id(scan_id)
        if row is None:
            return

        current_name = self.scan_table.item(row, 0).text()
        current_path = self.scan_table.item(row, 1).text()

        dialog = AddScanDialog(current_name, current_path, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            new_name, new_path = dialog.get_data()
            if new_name and new_path:
                cve_id_list, cve_id_set = store_cves_from_csv(new_path, "vuln_data.db")
                total_vulns = len(cve_id_list)
                unique_cve_list_json = json.dumps(list(cve_id_set))

                cur = self.conn.cursor()
                cur.execute("""
                    UPDATE scan SET scan_name = ?, file_path = ?,
                    total_vulnerabilities = ?, unique_cve_list = ? WHERE id = ?
                """, (new_name, new_path, total_vulns, unique_cve_list_json, scan_id))
                self.conn.commit()

                item = QTableWidgetItem(new_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(self.scan_table.item(row, 0).checkState())
                item.setData(Qt.UserRole, scan_id)
                item.setData(Qt.UserRole + 1, unique_cve_list_json)
                self.scan_table.setItem(row, 0, item)
                self.scan_table.setItem(row, 1, QTableWidgetItem(new_path))
                self.scan_table.setItem(row, 2, QTableWidgetItem(str(total_vulns)))
                try:
                    unique_list = json.loads(unique_cve_list_json) if unique_cve_list_json else []
                    unique_count = len(unique_list)
                except json.JSONDecodeError:
                    unique_count = 0
                self.scan_table.setItem(row, 3, QTableWidgetItem(str(unique_count)))
                cached_pct = return_cached_percentage(unique_list, "vuln_data.db")
                self.scan_table.setItem(row, 4, QTableWidgetItem(f"{cached_pct}%"))

    def delete_scan(self, scan_id):
        """Deletes a scan from the database and table."""
        row = self.find_row_by_scan_id(scan_id)
        if row is None:
            return

        cur = self.conn.cursor()
        cur.execute("DELETE FROM scan WHERE id = ?", (scan_id,))
        self.conn.commit()
        self.scan_table.removeRow(row)

    def add_export_record(self, export_name, num_scans, export_type, export_date):
        """Inserts a new export record into the past_exports table and updates the widget."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO past_exports (export_name, num_scans, export_type, export_date)
            VALUES (?, ?, ?, ?)
        """, (export_name, num_scans, export_type, export_date))
        self.conn.commit()
        export_id = cur.lastrowid
        self.add_export_row(export_id, export_name, num_scans, export_type, export_date)

    def find_row_by_export_id(self, export_id):
        """Finds and returns the row index in the past exports table for the given export_id."""
        for row in range(self.past_exports_table.rowCount()):
            item = self.past_exports_table.item(row, 0)
            if item and item.data(Qt.UserRole) == export_id:
                return row
        return None

    def add_export_row(self, export_id, export_name, num_scans, export_type, export_date):
        """Inserts a new row at the top of the past exports table widget with a delete button."""
        row_position = 0
        self.past_exports_table.insertRow(row_position)

        # Store export_id in the first cell's data.
        item = QTableWidgetItem(export_name)
        item.setData(Qt.UserRole, export_id)
        self.past_exports_table.setItem(row_position, 0, item)
        self.past_exports_table.setItem(row_position, 1, QTableWidgetItem(str(num_scans)))
        self.past_exports_table.setItem(row_position, 2, QTableWidgetItem(export_type))
        self.past_exports_table.setItem(row_position, 3, QTableWidgetItem(export_date))

        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(lambda _, eid=export_id: self.delete_export(eid))
        self.past_exports_table.setCellWidget(row_position, 4, btn_delete)

    def delete_export(self, export_id):
        """Deletes an export record from the database and removes its row from the past exports table."""
        row = None
        for r in range(self.past_exports_table.rowCount()):
            item = self.past_exports_table.item(r, 0)
            if item and item.data(Qt.UserRole) == export_id:
                row = r
                break
        if row is None:
            return

        cur = self.conn.cursor()
        cur.execute("DELETE FROM past_exports WHERE id = ?", (export_id,))
        self.conn.commit()
        self.past_exports_table.removeRow(row)

    def load_past_exports(self):
        """Loads all past exports (in descending order) from the database and populates the past exports table."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, export_name, num_scans, export_type, export_date 
            FROM past_exports ORDER BY id DESC
        """)
        records = cur.fetchall()
        self.past_exports_table.setRowCount(0)
        for export_id, export_name, num_scans, export_type, export_date in records:
            self.add_export_row(export_id, export_name, num_scans, export_type, export_date)

    def export_report(self):
        """
        Collects export settings and emits them via exportTriggered.
        Only scans with their check box selected are included.
        Also creates a new past export record.
        """
        nvd_api_key = self.nvd_api_key

        scans = []
        for row in range(self.scan_table.rowCount()):
            scan_item = self.scan_table.item(row, 0)
            if scan_item and scan_item.checkState() == Qt.Checked:
                scan_name = scan_item.text()
                # Get the file path from column 1.
                file_path_item = self.scan_table.item(row, 1)
                file_path = file_path_item.text() if file_path_item is not None else ""
                total_vulns_item = self.scan_table.item(row, 2)
                total_vulns = int(total_vulns_item.text()) if total_vulns_item is not None else 0
                unique_json = scan_item.data(Qt.UserRole + 1)
                try:
                    unique_vulns = json.loads(unique_json) if unique_json else []
                except Exception:
                    unique_vulns = []
                # Append a list: [scan_name, file_path, total_vulns, unique_vulns]
                scans.append([scan_name, file_path, total_vulns, unique_vulns])

        export_type = self.export_type_combo.currentText()
        pages_to_export = [page for page, checkbox in self.page_checkboxes.items() if checkbox.isChecked()]

        # Emit the export variables.
        self.exportTriggered.emit(nvd_api_key, scans, export_type, pages_to_export)

        # Create a new export record.
        export_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        export_name = "Export " + export_date
        self.add_export_record(export_name, len(scans), export_type, export_date)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
