"""
Main GUI file for the project.
"""
import sqlite3
import json
import datetime
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout,
    QTableWidget, QPushButton, QTableWidgetItem,
    QToolBar, QAction, QDialog, QLineEdit, QLabel, QDialogButtonBox,
    QFileDialog, QHBoxLayout, QGroupBox, QComboBox, QCheckBox, QMessageBox
)
from processing.database_processing import(
    initialize_database,
)
from PyQt5.QtCore import Qt, pyqtSignal


class MainWindow(QMainWindow):
    """Main window for vulnerability scan analyzer application."""

    exportTriggered = pyqtSignal(list, list, str, list, int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer")
        self.resize(1200, 800)

        self.init_db()
        self.init_ui()

        self.load_data()

    def init_db(self):
        """Initializes the SQLite database and creates required tables."""
        self.conn = sqlite3.connect("vuln_data.db")
        cur = self.conn.cursor()

        # Create scan table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                total_vulnerabilities INTEGER,
                unique_cve_list TEXT
            )
        """)

        # Create past_exports table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS past_exports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                export_name TEXT NOT NULL,
                num_scans INTEGER NOT NULL,
                export_type TEXT NOT NULL,
                export_date TEXT NOT NULL,
                generation_time REAL,
                file_path TEXT
            )
        """)

        # Check if generation_time column exists
        cur.execute("PRAGMA table_info(past_exports)")
        columns = [column[1] for column in cur.fetchall()]
        if 'generation_time' not in columns:
            cur.execute("ALTER TABLE past_exports ADD COLUMN generation_time REAL")

        # Create API key table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS api_key (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT NOT NULL,
                key_value TEXT NOT NULL,
                status TEXT DEFAULT 'Valid',
                error_count INTEGER DEFAULT 0
            )
        """)

        # Add missing columns if table exists
        cur.execute("PRAGMA table_info(api_key)")
        cols = [col[1] for col in cur.fetchall()]
        if "status" not in cols:
            cur.execute("ALTER TABLE api_key ADD COLUMN status TEXT DEFAULT 'Valid'")
        if "error_count" not in cols:
            cur.execute("ALTER TABLE api_key ADD COLUMN error_count INTEGER DEFAULT 0")

        # Create CVE tracking table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT NOT NULL UNIQUE,
                data TEXT,
                last_updated TEXT
            )
        """)

        self.conn.commit()

    def init_ui(self):
        """Initialize the UI components."""
        # Setup central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create toolbar
        self.init_toolbar()

        # Setup UI sections
        self._setup_api_key_section()
        self._setup_scan_table()
        self._setup_export_configuration()

    def load_data(self):
        """Load all data from database."""
        self.load_api_keys()
        self.load_scans()
        self.load_past_exports()

    def init_toolbar(self):
        """Creates a toolbar with actions."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Add Scan action
        add_scan_action = QAction("Add Scan", self)
        add_scan_action.setStatusTip("Add a new scan to the list.")
        add_scan_action.triggered.connect(self.add_scan)
        toolbar.addAction(add_scan_action)

        # Add API Key action
        add_api_key_action = QAction("Add API Key", self)
        add_api_key_action.setStatusTip("Add a new API key.")
        add_api_key_action.triggered.connect(self.add_api_key)
        toolbar.addAction(add_api_key_action)

        # Flush Cache action
        flush_cache_action = QAction("Flush Cache", self)
        flush_cache_action.setStatusTip("Clear the CVE database cache.")
        flush_cache_action.triggered.connect(self.flush_cache)
        toolbar.addAction(flush_cache_action)

    def _setup_api_key_section(self):
        """Set up the API Key section."""

        self.api_key_table = QTableWidget()
        gui_style.style_api_key_table(self.api_key_table)
        self.layout.addWidget(self.api_key_table)

    def _setup_scan_table(self):
        """Set up the table for displaying vulnerability scans."""
        self.scan_table = QTableWidget()
        gui_style.style_scan_table(self.scan_table)
        self.layout.addWidget(self.scan_table)

    def _setup_export_configuration(self):
        """Set up the export configuration section."""
        # Create export config group
        self.export_config_group = QGroupBox("Export Configuration")
        export_main_layout = QHBoxLayout(self.export_config_group)

        # Left column: Export settings
        export_settings_layout = self._create_export_settings_layout()

        # Right column: Past exports table
        past_exports_layout = self._create_past_exports_layout()

        export_main_layout.addLayout(export_settings_layout)
        export_main_layout.addLayout(past_exports_layout)

        self.layout.addWidget(self.export_config_group)

    def _create_export_settings_layout(self):
        """Create the export settings layout."""
        export_settings_layout = QVBoxLayout()

        # Export type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Export Type:"))
        self.export_type_combo = QComboBox()
        self.export_type_combo.addItems(["PDF", "Excel"])
        type_layout.addWidget(self.export_type_combo)
        export_settings_layout.addLayout(type_layout)

        # Add some spacing between sections
        export_settings_layout.addSpacing(10)

        # Data to export section with minimal spacing
        export_settings_layout.addWidget(QLabel("Data to Export:"))

        # Create container widget for checkboxes
        checkbox_widget = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_widget)
        checkbox_layout.setContentsMargins(5, 0, 0, 0)  # Minimal left margin, no top margin
        checkbox_layout.setSpacing(2)  # Minimum spacing between checkboxes

        self.data_checkboxes = {}
        data_options = [
            "Kev Catalog Comparison", 
            "Base Metrics", 
            "Temporal Metrics"
        ]

        for option in data_options:
            checkbox = QCheckBox(option)
            checkbox.setChecked(True)
            self.data_checkboxes[option] = checkbox
            checkbox_layout.addWidget(checkbox)

        export_settings_layout.addWidget(checkbox_widget)

        # Add some spacing before the button
        export_settings_layout.addSpacing(15)

        # Create Report button
        self.create_report_button = QPushButton("Create Report")
        gui_style.style_create_report_button(self.create_report_button)
        self.create_report_button.clicked.connect(self.export_report)
        export_settings_layout.addWidget(self.create_report_button)

        return export_settings_layout

    def _create_past_exports_layout(self):
        """Create the past exports layout."""
        past_exports_layout = QVBoxLayout()
        past_exports_layout.addWidget(QLabel("Past Exports:"))
        
        self.past_exports_table = QTableWidget()
        gui_style.style_past_exports_table(self.past_exports_table)
        past_exports_layout.addWidget(self.past_exports_table)
        
        return past_exports_layout
    
    # ------------------------------------------------------------------------
    # API Key Management
    # ------------------------------------------------------------------------
    
    def load_api_keys(self):
        """Loads all stored API keys from the database."""
        cur = self.conn.cursor()
        cur.execute("SELECT id, key_name, key_value, status FROM api_key")
        self.api_key_table.setRowCount(0)
        
        for key_id, key_name, key_value, status in cur.fetchall():
            self.add_api_key_row(key_id, key_name, key_value, status)
    
    def add_api_key(self):
        """Opens dialog to add a new API key."""
        dialog = AddAPIKeyDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            key_name, key_value, status = dialog.get_data()
            if key_name and key_value:
                cur = self.conn.cursor()
                cur.execute(
                    "INSERT INTO api_key (key_name, key_value, status) VALUES (?, ?, ?)",
                    (key_name, key_value, status)
                )
                self.conn.commit()
                key_id = cur.lastrowid
                self.add_api_key_row(key_id, key_name, key_value, status)
    
    def add_api_key_row(self, key_id, key_name, key_value, status="Valid"):
        """Adds a row to the API key table."""
        row_position = self.api_key_table.rowCount()
        self.api_key_table.insertRow(row_position)
        
        # Column 0: Key Name (with checkbox)
        item = QTableWidgetItem(key_name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, key_id)
        self.api_key_table.setItem(row_position, 0, item)
        
        # Column 1: Key Value (masked)
        key_item = QTableWidgetItem("*" * len(key_value))
        key_item.setData(Qt.UserRole, key_value)
        self.api_key_table.setItem(row_position, 1, key_item)
        
        # Column 2: Status with colored background and centered text
        status_item = QTableWidgetItem(status)
        status_item.setBackground(gui_style.get_status_color(status))
        status_item.setTextAlignment(Qt.AlignCenter)
        self.api_key_table.setItem(row_position, 2, status_item)
        
        # Column 3: Edit button
        btn_edit = QPushButton("Edit")
        gui_style.style_edit_button(btn_edit)
        btn_edit.clicked.connect(lambda _, kid=key_id: self.edit_api_key(kid))
        self.api_key_table.setCellWidget(row_position, 3, btn_edit)
        
        # Column 4: Delete button
        btn_delete = QPushButton("Delete")
        gui_style.style_delete_button(btn_delete)
        btn_delete.clicked.connect(lambda _, kid=key_id: self.delete_api_key(kid))
        self.api_key_table.setCellWidget(row_position, 4, btn_delete)
    
    def edit_api_key(self, key_id):
        """Opens a dialog to edit an API key."""
        row = self.find_row_by_id(self.api_key_table, key_id)
        if row is None:
            return
        
        current_name = self.api_key_table.item(row, 0).text()
        current_value = self.api_key_table.item(row, 1).data(Qt.UserRole)
        current_status = self.api_key_table.item(row, 2).text()
        
        dialog = AddAPIKeyDialog(current_name, current_value, current_status, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            new_name, new_value, new_status = dialog.get_data()
            if new_name and new_value:
                # Update in database
                cur = self.conn.cursor()
                cur.execute(
                    "UPDATE api_key SET key_name = ?, key_value = ?, status = ? WHERE id = ?",
                    (new_name, new_value, new_status, key_id)
                )
                self.conn.commit()
                
                # Update table row
                self.api_key_table.item(row, 0).setText(new_name)
                masked_value = "*" * len(new_value)
                self.api_key_table.item(row, 1).setText(masked_value)
                self.api_key_table.item(row, 1).setData(Qt.UserRole, new_value)
                
                # Update status with appropriate color
                status_item = QTableWidgetItem(new_status)
                status_item.setBackground(gui_style.get_status_color(new_status))
                self.api_key_table.setItem(row, 2, status_item)
    
    def delete_api_key(self, key_id):
        """Deletes an API key after confirmation."""
        row = self.find_row_by_id(self.api_key_table, key_id)
        if row is None:
            return
        
        if self.confirm_deletion("API key"):
            cur = self.conn.cursor()
            cur.execute("DELETE FROM api_key WHERE id = ?", (key_id,))
            self.conn.commit()
            self.api_key_table.removeRow(row)
    
    def update_api_key_status(self, key_value, error_count):
        """Updates an API key's status based on error count."""
        for row in range(self.api_key_table.rowCount()):
            stored_key = self.api_key_table.item(row, 1).data(Qt.UserRole)
            if stored_key == key_value:
                new_status = "Valid" if error_count < 5 else "Invalid"
                
                # Update database
                cur = self.conn.cursor()
                cur.execute(
                    "UPDATE api_key SET status = ? WHERE key_value = ?", 
                    (new_status, key_value)
                )
                self.conn.commit()
                
                # Update table UI
                status_item = QTableWidgetItem(new_status)
                status_item.setBackground(gui_style.get_status_color(new_status))
                self.api_key_table.setItem(row, 2, status_item)
                break
    
    # ------------------------------------------------------------------------
    # Scan Management
    # ------------------------------------------------------------------------
    
    def load_scans(self):
        """Loads all stored scans from the database."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, scan_name, file_path, total_vulnerabilities, unique_cve_list FROM scan"
        )
        
        self.scan_table.setRowCount(0)
        for scan_id, scan_name, file_path, total_vulns, unique_cve_list in cur.fetchall():
            self.add_scan_row(scan_id, scan_name, file_path, str(total_vulns), unique_cve_list)
    
    def add_scan(self):
        """Opens dialog to add a new scan."""
        dialog = AddScanDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            scan_name, file_path = dialog.get_data()
            if scan_name and file_path:
                try:
                    cve_id_list, cve_id_set = store_cves_from_csv(file_path, "vuln_data.db")
                    total_vulns = len(cve_id_list)
                    unique_cve_list_json = json.dumps(list(cve_id_set))
                    scan_id = self.insert_scan(scan_name, file_path, total_vulns, unique_cve_list_json)
                    self.add_scan_row(scan_id, scan_name, file_path, str(total_vulns), unique_cve_list_json)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to process scan: {str(e)}")
    
    def insert_scan(self, scan_name, file_path, total_vulnerabilities, unique_cve_list):
        """Inserts a new scan record into the database."""
        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO scan (scan_name, file_path, total_vulnerabilities, unique_cve_list)
               VALUES (?, ?, ?, ?)""",
            (scan_name, file_path, total_vulnerabilities, unique_cve_list)
        )
        self.conn.commit()
        return cur.lastrowid
    
    def add_scan_row(self, scan_id, scan_name, file_path, total_vulnerabilities, unique_cve_list):
        """Adds a row to the scan table."""
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
        total_item = QTableWidgetItem(total_vulnerabilities)
        total_item.setTextAlignment(Qt.AlignCenter)
        self.scan_table.setItem(row_position, 2, total_item)
        
        # Column 3: Unique Vulnerabilities
        try:
            unique_list = json.loads(unique_cve_list) if unique_cve_list else []
            unique_count = len(unique_list)
        except json.JSONDecodeError:
            unique_count = 0
        unique_item = QTableWidgetItem(str(unique_count))
        unique_item.setTextAlignment(Qt.AlignCenter)
        self.scan_table.setItem(row_position, 3, unique_item)
        
        # Column 4: Cached %
        cached_pct = return_cached_percentage(
            json.loads(unique_cve_list) if unique_cve_list else [], 
            "vuln_data.db"
        )
        cached_item = QTableWidgetItem(f"{cached_pct}%")
        cached_item.setTextAlignment(Qt.AlignCenter)
        self.scan_table.setItem(row_position, 4, cached_item)
        
        # Column 5: Edit button
        btn_edit = QPushButton("Edit")
        gui_style.style_edit_button(btn_edit)
        btn_edit.clicked.connect(lambda _, sid=scan_id: self.edit_scan(sid))
        self.scan_table.setCellWidget(row_position, 5, btn_edit)
        
        # Column 6: Delete button
        btn_delete = QPushButton("Delete")
        gui_style.style_delete_button(btn_delete)
        btn_delete.clicked.connect(lambda _, sid=scan_id: self.delete_scan(sid))
        self.scan_table.setCellWidget(row_position, 6, btn_delete)
        
    def edit_scan(self, scan_id):
        """Opens dialog to edit a scan."""
        row = self.find_row_by_id(self.scan_table, scan_id)
        if row is None:
            return
        
        current_name = self.scan_table.item(row, 0).text()
        current_path = self.scan_table.item(row, 1).text()
        
        dialog = AddScanDialog(current_name, current_path, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            new_name, new_path = dialog.get_data()
            if new_name and new_path:
                try:
                    cve_id_list, cve_id_set = store_cves_from_csv(new_path, "vuln_data.db")
                    total_vulns = len(cve_id_list)
                    unique_cve_list_json = json.dumps(list(cve_id_set))
                    
                    # Update database
                    cur = self.conn.cursor()
                    cur.execute(
                        """UPDATE scan SET scan_name = ?, file_path = ?,
                           total_vulnerabilities = ?, unique_cve_list = ? WHERE id = ?""",
                        (new_name, new_path, total_vulns, unique_cve_list_json, scan_id)
                    )
                    self.conn.commit()
                    
                    # Update table row
                    self._update_scan_row(row, scan_id, new_name, new_path, total_vulns, unique_cve_list_json)
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to process scan: {str(e)}")
    
    def _update_scan_row(self, row, scan_id, name, path, total_vulns, unique_cve_list_json):
        """Updates an existing row in the scan table."""
        # Update name cell with checkbox
        item = QTableWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(self.scan_table.item(row, 0).checkState())
        item.setData(Qt.UserRole, scan_id)
        item.setData(Qt.UserRole + 1, unique_cve_list_json)
        self.scan_table.setItem(row, 0, item)
        
        # Update file path
        self.scan_table.setItem(row, 1, QTableWidgetItem(path))
        
        # Update total vulnerabilities with centered text
        total_item = QTableWidgetItem(str(total_vulns))
        total_item.setTextAlignment(Qt.AlignCenter)
        self.scan_table.setItem(row, 2, total_item)
        
        # Update unique vulnerabilities count with centered text
        try:
            unique_list = json.loads(unique_cve_list_json) if unique_cve_list_json else []
            unique_count = len(unique_list)
        except json.JSONDecodeError:
            unique_count = 0
        unique_item = QTableWidgetItem(str(unique_count))
        unique_item.setTextAlignment(Qt.AlignCenter)
        self.scan_table.setItem(row, 3, unique_item)
        
        # Update cached percentage with centered text
        cached_pct = return_cached_percentage(unique_list, "vuln_data.db")
        cached_item = QTableWidgetItem(f"{cached_pct}%")
        cached_item.setTextAlignment(Qt.AlignCenter)
        self.scan_table.setItem(row, 4, cached_item)
    
    def delete_scan(self, scan_id):
        """Deletes a scan after confirmation."""
        row = self.find_row_by_id(self.scan_table, scan_id)
        if row is None:
            return
        
        if self.confirm_deletion("scan"):
            cur = self.conn.cursor()
            cur.execute("DELETE FROM scan WHERE id = ?", (scan_id,))
            self.conn.commit()
            self.scan_table.removeRow(row)
    
    # ------------------------------------------------------------------------
    # Export Management
    # ------------------------------------------------------------------------
    
    def load_past_exports(self):
        """Loads all past exports from the database."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, export_name, num_scans, export_type, export_date, file_path, generation_time
            FROM past_exports ORDER BY id DESC
        """)
        
        self.past_exports_table.setRowCount(0)
        for record in cur.fetchall():
            export_id, export_name, num_scans, export_type, export_date, file_path = record[:6]
            generation_time = record[6] if len(record) > 6 else None
            self.add_export_row(export_id, export_name, num_scans, export_type, export_date, file_path, generation_time)
    
    def add_export_record(self, export_name, num_scans, export_type, export_date, file_path, generation_time=None):
        """Adds a new export record to the database."""
        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO past_exports 
               (export_name, num_scans, export_type, export_date, file_path, generation_time)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (export_name, num_scans, export_type, export_date, file_path, generation_time)
        )
        
        self.conn.commit()
        export_id = cur.lastrowid
        self.add_export_row(export_id, export_name, num_scans, export_type, export_date, file_path, generation_time)
    
    def add_export_row(self, export_id, export_name, num_scans, export_type, export_date, file_path, generation_time=None):
        """Adds a row to the past exports table."""
        row_position = 0  # Insert at top
        self.past_exports_table.insertRow(row_position)
        
        # Column 0: Export Name
        item = QTableWidgetItem(export_name)
        item.setData(Qt.UserRole, export_id)
        self.past_exports_table.setItem(row_position, 0, item)
        
        # Column 1: # of Scans (centered)
        num_scans_item = QTableWidgetItem(str(num_scans))
        num_scans_item.setTextAlignment(Qt.AlignCenter)
        self.past_exports_table.setItem(row_position, 1, num_scans_item)
        
        # Column 2: Export Type (centered)
        export_type_item = QTableWidgetItem(export_type)
        export_type_item.setTextAlignment(Qt.AlignCenter)
        self.past_exports_table.setItem(row_position, 2, export_type_item)
        
        # Column 3: Export Date (centered)
        export_date_item = QTableWidgetItem(export_date)
        export_date_item.setTextAlignment(Qt.AlignCenter)
        self.past_exports_table.setItem(row_position, 3, export_date_item)
        
        # Column 4: Generation Time (centered)
        if generation_time is not None:
            try:
                gen_time_float = float(generation_time)
                time_text = f"{gen_time_float:.2f} sec"
            except ValueError:
                time_text = str(generation_time)
        else:
            time_text = "N/A"
        gen_time_item = QTableWidgetItem(time_text)
        gen_time_item.setTextAlignment(Qt.AlignCenter)
        self.past_exports_table.setItem(row_position, 4, gen_time_item)
        
        # Column 5: Export Report button
        btn_export = QPushButton("Export")
        gui_style.style_export_button(btn_export)
        btn_export.clicked.connect(lambda _, eid=export_id: self.export_row_action(eid))
        self.past_exports_table.setCellWidget(row_position, 5, btn_export)
        
        # Column 6: Delete button
        btn_delete = QPushButton("Delete")
        gui_style.style_delete_button(btn_delete)
        btn_delete.clicked.connect(lambda _, eid=export_id: self.delete_export(eid))
        self.past_exports_table.setCellWidget(row_position, 6, btn_delete)
        
    def delete_export(self, export_id):
        """Deletes an export record after confirmation."""
        row = self.find_row_by_id(self.past_exports_table, export_id)
        if row is None:
            return
        
        if self.confirm_deletion("export record"):
            cur = self.conn.cursor()
            cur.execute("DELETE FROM past_exports WHERE id = ?", (export_id,))
            self.conn.commit()
            self.past_exports_table.removeRow(row)
    
    def export_row_action(self, export_id):
        """Exports a previously generated report to a user-selected location."""
        cur = self.conn.cursor()
        cur.execute("SELECT file_path FROM past_exports WHERE id = ?", (export_id,))
        row = cur.fetchone()
        
        if row is None or not row[0]:
            QMessageBox.warning(
                self, "Error", 
                "No saved report found for this export record."
            )
            return
        
        saved_file_path = row[0]
        destination, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "", "PDF Files (*.pdf)"
        )
        
        if not destination:
            return
        
        try:
            shutil.copy(saved_file_path, destination)
            QMessageBox.information(
                self, "Success", 
                f"Report exported successfully to:\n{destination}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Failed to export report:\n{str(e)}"
            )
    
    def export_report(self):
        """Collects export settings and triggers report generation."""
        # Get selected scans
        scans = self._get_selected_scans()
        if not scans:
            QMessageBox.warning(
                self, "Warning", 
                "Please select at least one scan to include in the report."
            )
            return
        
        # Get export settings
        export_type = self.export_type_combo.currentText()
        data_to_export = [
            option for option, checkbox in self.data_checkboxes.items() 
            if checkbox.isChecked()
        ]
        
        # Check for KEV scan if Kev Catalog Comparison is selected
        if self._is_kev_comparison_missing(data_to_export, scans):
            return
        
        # Gather selected API keys
        nvd_api_keys = self._get_selected_api_keys()
        
        # Start timing the report generation
        start_time = datetime.datetime.now()
        self.report_start_time = start_time
        
        # Create temporary export info (don't add to database yet)
        export_date = start_time.strftime("%Y-%m-%d %H:%M:%S")
        export_name = f"Export {export_date}"
        
        # Emit the signal with temporary export info
        self.exportTriggered.emit(nvd_api_keys, scans, export_type, data_to_export, {
            'export_name': export_name,
            'num_scans': len(scans),
            'export_type': export_type,
            'export_date': export_date
        })

    # New method to be added to gui.py:
    def add_successful_export(self, export_info, file_path, generation_time):
        """Adds a successful export to the database and UI after report creation."""
        # Now add the record to the database
        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO past_exports 
            (export_name, num_scans, export_type, export_date, file_path, generation_time)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (export_info['export_name'], export_info['num_scans'], 
            export_info['export_type'], export_info['export_date'], 
            file_path, generation_time)
        )
        self.conn.commit()
        export_id = cur.lastrowid
        
        # Add to the UI table
        self.add_export_row(
            export_id, 
            export_info['export_name'], 
            export_info['num_scans'], 
            export_info['export_type'], 
            export_info['export_date'], 
            file_path, 
            generation_time
        )
        
        return export_id
    
    def _get_selected_scans(self):
        """Get list of selected scans from the scan table."""
        scans = []
        for row in range(self.scan_table.rowCount()):
            scan_item = self.scan_table.item(row, 0)
            if scan_item and scan_item.checkState() == Qt.Checked:
                scan_name = scan_item.text()
                file_path = self.scan_table.item(row, 1).text()
                total_vulns = int(self.scan_table.item(row, 2).text())
                
                unique_json = scan_item.data(Qt.UserRole + 1)
                try:
                    unique_vulns = json.loads(unique_json) if unique_json else []
                except Exception:
                    unique_vulns = []
                
                scans.append([scan_name, file_path, total_vulns, unique_vulns])
        return scans
    
    def _get_selected_api_keys(self):
        """Get list of selected API keys from the API key table."""
        api_keys = []
        for row in range(self.api_key_table.rowCount()):
            key_item = self.api_key_table.item(row, 0)
            if key_item and key_item.checkState() == Qt.Checked:
                key_value = self.api_key_table.item(row, 1).data(Qt.UserRole)
                api_keys.append(key_value)
        return api_keys
    
    def _is_kev_comparison_missing(self, data_to_export, scans):
        """Check if KEV Catalog Comparison is selected but no KEV scan is included."""
        if "Kev Catalog Comparison" in data_to_export and not any("kev" in scan[0].lower() for scan in scans):
            QMessageBox.warning(
                self, "Missing KEV Scan",
                "KEV Catalog Comparison is selected, but no KEV scan is selected. "
                "Please select a scan that includes 'kev' in its name."
            )
            return True
        return False
    
    def _create_export_record(self, export_name, num_scans, export_type, export_date):
        """Create a new export record in the database."""
        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO past_exports 
               (export_name, num_scans, export_type, export_date, file_path, generation_time)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (export_name, num_scans, export_type, export_date, None, None)
        )
        self.conn.commit()
        export_id = cur.lastrowid
        
        # Add to the UI table
        self.add_export_row(export_id, export_name, num_scans, export_type, export_date, None)
        
        return export_id
    
    def update_export_with_generation_time(self, export_id, file_path=None):
        """Updates an export record with generation time and file path."""
        if hasattr(self, 'report_start_time'):
            end_time = datetime.datetime.now()
            generation_time = (end_time - self.report_start_time).total_seconds()
            
            cur = self.conn.cursor()
            
            if file_path:
                cur.execute(
                    "UPDATE past_exports SET generation_time = ?, file_path = ? WHERE id = ?",
                    (generation_time, file_path, export_id)
                )
            else:
                cur.execute(
                    "UPDATE past_exports SET generation_time = ? WHERE id = ?",
                    (generation_time, export_id)
                )
                
            self.conn.commit()
            
            # Update the display in the export table
            row = self.find_row_by_id(self.past_exports_table, export_id)
            if row is not None:
                time_text = f"{generation_time:.2f} sec"
                time_item = QTableWidgetItem(time_text)
                time_item.setTextAlignment(Qt.AlignCenter)  # Center the text
                self.past_exports_table.setItem(row, 4, time_item)
            
            # Update cached percentages
            self.update_all_cached_percentages()
    
    # ------------------------------------------------------------------------
    # Cache and Utility Functions
    # ------------------------------------------------------------------------
    
    def flush_cache(self):
        """Clears the CVEs table and updates cached percentages."""
        if self.confirm_deletion("CVE cache"):
            try:
                # Clear the cves table
                cur = self.conn.cursor()
                cur.execute("DELETE FROM cves")
                self.conn.commit()
                
                # Update cached percentages for all scans
                self.update_all_cached_percentages()
                
                QMessageBox.information(
                    self, "Success", 
                    "CVE cache successfully flushed and scan statistics updated."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", 
                    f"Failed to flush CVE cache: {str(e)}"
                )
    
    def update_all_cached_percentages(self):
        """Updates the cached percentage for all scans."""
        for row in range(self.scan_table.rowCount()):
            scan_item = self.scan_table.item(row, 0)
            if scan_item:
                unique_cve_list_json = scan_item.data(Qt.UserRole + 1)
                try:
                    unique_list = json.loads(unique_cve_list_json) if unique_cve_list_json else []
                except json.JSONDecodeError:
                    unique_list = []
                cached_pct = return_cached_percentage(unique_list, "vuln_data.db")
                self.scan_table.setItem(row, 4, QTableWidgetItem(f"{cached_pct}%"))
    
    def find_row_by_id(self, table, id_value, id_column=0):
        """Generic method to find a row by ID in a table."""
        for row in range(table.rowCount()):
            item = table.item(row, id_column)
            if item and item.data(Qt.UserRole) == id_value:
                return row
        return None
    
    def confirm_deletion(self, item_type):
        """Generic confirmation dialog for deletion."""
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete this {item_type}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()