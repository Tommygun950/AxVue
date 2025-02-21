"""GUI File"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QFileDialog, QSpinBox, QRadioButton, QCheckBox, QGroupBox,
    QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

class VulnerabilityScanAnalyzer(QMainWindow):
    """
    GUI for the Vulnerability Scan Analyzer.
    Emits a `export_data_signal` when Export is clicked.
    """
    # 1) Define a custom signal that sends a dictionary
    export_data_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vulnerability Scan Analyzer")
        self.setFixedSize(1000, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Header
        header_label = QLabel("Vulnerability Scan Analyzer")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        header_label.setFixedHeight(30)
        main_layout.addWidget(header_label)

        # Horizontal layout for the three columns
        columns_layout = QHBoxLayout()

        # Column 1
        col1_layout = QVBoxLayout()
        col1_layout.addWidget(self.create_file_selection_section())
        columns_layout.addLayout(col1_layout, 2)

        # Column 2
        col2_layout = QVBoxLayout()
        col2_layout.addWidget(self.create_scan_data_section())
        columns_layout.addLayout(col2_layout, 1)

        # Column 3
        col3_layout = QVBoxLayout()
        col3_layout.addWidget(self.create_export_config_section())
        columns_layout.addLayout(col3_layout, 1)

        main_layout.addLayout(columns_layout)

        # Footer buttons
        footer_layout = QHBoxLayout()
        export_button = QPushButton("Export")
        export_button.setStyleSheet("background-color: lightgreen; font-weight: bold;")
        export_button.clicked.connect(self.export_data)
        footer_layout.addWidget(export_button)

        flush_button = QPushButton("Flush Database")
        flush_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        flush_button.clicked.connect(self.flush_database)
        footer_layout.addWidget(flush_button)

        main_layout.addLayout(footer_layout)

        central_widget.setLayout(main_layout)

    # --- File Selection (Column 1)
    def create_file_selection_section(self):
        """Creates column 1."""
        section = QGroupBox("1. Select Your Files")
        layout = QVBoxLayout()

        # KEV file selection
        kev_layout = QFormLayout()
        self.kev_file_label = QLabel("No KEV file selected")
        kev_button = QPushButton("Select KEV File")
        kev_button.clicked.connect(lambda: self.select_file("KEV"))
        kev_layout.addRow(kev_button, self.kev_file_label)
        layout.addLayout(kev_layout)

        # Spinbox
        scan_count_layout = QFormLayout()
        self.scan_count_spinbox = QSpinBox()
        self.scan_count_spinbox.setRange(1, 3)
        self.scan_count_spinbox.setValue(1)
        self.scan_count_spinbox.valueChanged.connect(self.update_scan_widgets)
        scan_count_layout.addRow(QLabel("Number of Scan Files:"), self.scan_count_spinbox)
        layout.addLayout(scan_count_layout)

        self.scan_files_layout = QVBoxLayout()
        layout.addLayout(self.scan_files_layout)
        self.scan_file_labels = []
        self.scan_file_buttons = []

        section.setLayout(layout)
        return section

    def select_file(self, file_type, index=None):
        """Select file function"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File")
        if file_path:
            if file_type == "KEV":
                self.kev_file_label.setText(f"Selected: {file_path}")
            elif file_type == "Scan" and index is not None:
                self.scan_file_labels[index].setText(f"Selected: {file_path}")

    # --- Scan Data Entry (Column 2)
    def create_scan_data_section(self):
        """Creates column 2."""
        section = QGroupBox("2. Enter Scan Data")
        layout = QVBoxLayout()

        # Period
        layout.addWidget(QLabel("Enter Period (Days):"))
        self.period_entry = QLineEdit()
        layout.addWidget(self.period_entry)

        # Scope
        layout.addWidget(QLabel("Enter Scope:"))
        self.scope_entry = QLineEdit()
        layout.addWidget(self.scope_entry)

        # NVD API Key (hidden)
        layout.addWidget(QLabel("Enter NVD API Key:"))
        self.nvd_api_key_entry = QLineEdit()
        self.nvd_api_key_entry.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.nvd_api_key_entry)

        # Dynamic "Scan Name" text fields
        self.scan_name_form = QFormLayout()
        layout.addLayout(self.scan_name_form)
        self.scan_name_entries = []

        section.setLayout(layout)
        return section

    # --- Export Configuration (Column 3)
    def create_export_config_section(self):
        """"Creates column 3 section."""
        section = QGroupBox("3. Configure Export")
        layout = QVBoxLayout()

        export_type_group = QGroupBox("Select Export Type")
        export_layout = QVBoxLayout()
        self.export_type_pdf = QRadioButton("PDF")
        self.export_type_pdf.setChecked(True)
        self.export_type_excel = QRadioButton("Excel")
        export_layout.addWidget(self.export_type_pdf)
        export_layout.addWidget(self.export_type_excel)
        export_type_group.setLayout(export_layout)
        layout.addWidget(export_type_group)

        # Page Selection
        pages_group = QGroupBox("Select Pages to Include")
        pages_layout = QVBoxLayout()
        self.page_checkboxes = {}
        pages = [
            "cover", "disclosure statement", "overview", "kev comparison",
            "base score", "severity", "attack vector", "attack complexity",
            "privileges", "confidentiality", "integrity", "availability", "details"
        ]
        for page in pages:
            checkbox = QCheckBox(page.capitalize())
            checkbox.setChecked(True)
            pages_layout.addWidget(checkbox)
            self.page_checkboxes[page] = checkbox
        pages_group.setLayout(pages_layout)
        layout.addWidget(pages_group)

        section.setLayout(layout)
        return section

    # --- Updating the UI for # of scans
    def update_scan_widgets(self):
        """Dynamically updates GUI."""
        num = self.scan_count_spinbox.value()

        # Clear existing scan file buttons/labels
        for i in reversed(range(self.scan_files_layout.count())):
            widget = self.scan_files_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.scan_file_labels = []
        self.scan_file_buttons = []

        for i in range(num):
            btn = QPushButton(f"Select Scan File {i+1}")
            lbl = QLabel("No file selected")
            btn.clicked.connect(lambda checked, idx=i: self.select_file("Scan", idx))
            self.scan_files_layout.addWidget(btn)
            self.scan_files_layout.addWidget(lbl)
            self.scan_file_labels.append(lbl)
            self.scan_file_buttons.append(btn)

        # Clear existing scan name rows
        while self.scan_name_form.rowCount() > 0:
            self.scan_name_form.removeRow(0)
        self.scan_name_entries = []

        # Recreate scan name textboxes
        for i in range(num):
            line_edit = QLineEdit()
            self.scan_name_form.addRow(QLabel(f"Scan {i+1} Name:"), line_edit)
            self.scan_name_entries.append(line_edit)

    # --- Export logic
    def export_data(self):
        """Collects user inputs and emits them as a dictionary via `export_data_signal`."""
        # KEV file
        kev_label_text = self.kev_file_label.text()
        if kev_label_text.startswith("Selected:"):
            kev_file = kev_label_text.replace("Selected:", "").strip()
        else:
            None

        # Number of scans
        scan_count = self.scan_count_spinbox.value()

        # Scan file paths
        scan_paths = []
        for i in range(scan_count):
            lbl_text = self.scan_file_labels[i].text()
            if lbl_text.startswith("Selected:"):
                path = lbl_text.replace("Selected:", "").strip()
            else:
                None
            scan_paths.append(path)
        while len(scan_paths) < 3:
            scan_paths.append(None)

        # Scan names
        scan_names = []
        for i in range(scan_count):
            name_text = self.scan_name_entries[i].text()
            scan_names.append(name_text if name_text else None)
        while len(scan_names) < 3:
            scan_names.append(None)

        # Other inputs
        period = self.period_entry.text()
        scope = self.scope_entry.text()
        nvd_api_key = self.nvd_api_key_entry.text()

        # Export type
        export_type = "PDF" if self.export_type_pdf.isChecked() else "Excel"

        # Selected pages
        selected_pages = [page for page, cb in self.page_checkboxes.items() if cb.isChecked()]

        # Prepare the data dictionary
        data = {
            "nvd_api_key": nvd_api_key,
            "kev_file": kev_file,
            "scan_count": scan_count,
            "scan_paths": scan_paths,
            "scan_names": scan_names,
            "period": period,
            "scope": scope,
            "export_type": export_type,
            "selected_pages": selected_pages,
        }

        # 2) Emit the signal with the data
        self.export_data_signal.emit(data)

    def flush_database(self):
        """Clears entire database."""
        print("Flushing database...")
