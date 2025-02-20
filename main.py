"""Main imports"""
import tkinter as tk
from tkinter import filedialog


def export_to_pdf():
    """Exports data to PDF"""
    print("Exporting to PDF...")
    # You can read export_type_var and page_vars here to determine configuration

def export_to_excel():
    """Exports data to Excel"""
    print("Exporting to Excel...")
    # You can read export_type_var and page_vars here to determine configuration

def flush_database():
    """Clears the entire SQL database"""
    print("Flushing database...")

def select_file(file_type, index=None):
    """Opens file explorer to select a file and stores the path."""
    file_path = filedialog.askopenfilename(title="Select a File")
    if file_path:
        if file_type == "KEV":
            kev_file_var.set(file_path)
            print(f"Selected KEV file: {file_path}")
        elif file_type == "Scan" and index is not None:
            scan_file_vars[index].set(file_path)
            print(f"Selected Scan File {index+1}: {file_path}")

def update_scan_widgets():
    """
    Updates the scan file selection buttons in column 1 and
    the corresponding scan name entries in column 2 based on the spinbox value.
    """
    try:
        num = int(scan_count_var.get())
    except ValueError:
        num = 1

    # Clear previous scan file buttons
    for widget in scan_files_frame.winfo_children():
        widget.destroy()
    # Clear previous scan name entries
    for widget in scan_names_frame.winfo_children():
        widget.destroy()

    # Create new scan file buttons and scan name entries
    for i in range(num):
        btn = tk.Button(
            scan_files_frame,
            text=f"Select Scan File {i+1}",
            command=lambda i=i: select_file("Scan", i),
            font=('Arial', 10, 'bold'),
            bg="white", fg="gray10", width=20
        )
        btn.pack(pady=5)

        lbl = tk.Label(
            scan_names_frame,
            text=f"Scan {i+1} Name:",
            bg="lightblue", fg="gray10",
            font=('Arial', 10)
        )
        lbl.pack(pady=(5, 0))
        entry = tk.Entry(scan_names_frame, font=('Arial', 10), width=25)
        entry.pack(pady=(0, 5))

def main():
    """Main function that starts up gui"""
    global kev_file_var
    global scan_file_vars
    global scan_files_frame
    global scan_names_frame
    global scan_count_var
    global export_type_var, page_vars

    root = tk.Tk()
    root.geometry("1000x750")
    root.title("Vulnerability Scan Analyzer")
    root.configure(bg="gray14")

    # Configure grid layout
    for i in range(3):
        root.columnconfigure(i, weight=1)
    root.rowconfigure(0, weight=0)  # Header
    root.rowconfigure(1, weight=1)  # Main content
    root.rowconfigure(2, weight=0)  # Footer Buttons

    # --- Main Header ---
    main_header = tk.Label(
        root,
        text="Vulnerability Scan Analyzer",
        font=('Arial', 18, 'bold'),
        bg="gray14", fg="white"
    )
    main_header.grid(row=0, column=0, columnspan=3, pady=10, sticky="nsew")

    # --- Create three main columns ---
    column1 = tk.Frame(root, bg="lightblue")
    column1.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    column2 = tk.Frame(root, bg="lightblue")
    column2.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

    column3 = tk.Frame(root, bg="lightblue")
    column3.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

    # --- Section Headers ---
    header1 = tk.Label(
        column1, text="1. Select your files.",
        font=('Arial', 12, 'bold'),
        bg="lightblue", fg="gray10"
    )
    header1.pack(pady=5)

    header2 = tk.Label(
        column2, text="2. Enter scan data.",
        font=('Arial', 12, 'bold'),
        bg="lightblue", fg="gray10"
    )
    header2.pack(pady=5)

    header3 = tk.Label(
        column3, text="3. Configure export.",
        font=('Arial', 12, 'bold'),
        bg="lightblue", fg="gray10"
    )
    header3.pack(pady=5)

    # --- Column 1: File Selection ---
    # KEV file selection
    kev_file_var = tk.StringVar()
    kev_button = tk.Button(
        column1,
        text="Select KEV File",
        font=('Arial', 10, 'bold'),
        command=lambda: select_file("KEV"),
        bg="white", fg="gray10", width=20
    )
    kev_button.pack(pady=10)

    # Option to choose number of scan files
    scan_count_var = tk.StringVar(value="1")
    count_label = tk.Label(
        column1, text="Number of Scan Files:",
        bg="lightblue", fg="gray10", font=('Arial', 10)
    )
    count_label.pack(pady=(10, 0))
    scan_count_spinbox = tk.Spinbox(
        column1, from_=1, to=3,
        textvariable=scan_count_var,
        width=5,
        command=update_scan_widgets,
        font=('Arial', 10)
    )
    scan_count_spinbox.pack(pady=(0, 10))

    # Frame to hold dynamic scan file selection buttons
    scan_files_frame = tk.Frame(column1, bg="lightblue")
    scan_files_frame.pack(pady=10)

    # --- Column 2: Scan Data Input ---
    # Frame for dynamic scan name entries (one per scan file)
    scan_names_frame = tk.Frame(column2, bg="lightblue")
    scan_names_frame.pack(pady=10)

    # Prepare list to store scan file paths (as StringVars)
    scan_file_vars = [tk.StringVar() for _ in range(3)]

    # Initialize scan file selection widgets after scan_names_frame is created
    update_scan_widgets()

    # Shared Period entry
    period_label = tk.Label(
        column2, text="Enter Period (Days):",
        bg="lightblue", fg="gray10", font=('Arial', 10)
    )
    period_label.pack(pady=(20, 0))
    period_entry = tk.Entry(column2, font=('Arial', 10), width=25)
    period_entry.pack(pady=(0, 10))

    # Shared Scope entry
    scope_label = tk.Label(
        column2, text="Enter Scope:",
        bg="lightblue", fg="gray10", font=('Arial', 10)
    )
    scope_label.pack(pady=(10, 0))
    scope_entry = tk.Entry(column2, font=('Arial', 10), width=25)
    scope_entry.pack(pady=(0, 10))

    # --- Column 3: Export Configuration ---
    # Wrap the export configuration in a LabelFrame for a cleaner look
    export_config_frame = tk.LabelFrame(
        column3, text="",
        font=('Arial', 12, 'bold'),
        bg="lightblue", fg="gray10", padx=10, pady=10
    )
    export_config_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Section 1: Export Type Selection
    export_type_var = tk.StringVar(value="pdf")
    export_type_frame = tk.LabelFrame(
        export_config_frame, text="Select Export Type",
        font=('Arial', 10, 'bold'),
        bg="lightblue", fg="gray10", padx=10, pady=10
    )
    export_type_frame.pack(fill="x", padx=5, pady=5)

    pdf_radio = tk.Radiobutton(
        export_type_frame,
        text="PDF",
        variable=export_type_var,
        value="pdf",
        bg="lightblue", fg="gray10",
        font=('Arial', 10)
    )
    pdf_radio.pack(anchor="w", padx=20, pady=2)

    excel_radio = tk.Radiobutton(
        export_type_frame,
        text="Excel",
        variable=export_type_var,
        value="excel",
        bg="lightblue", fg="gray10",
        font=('Arial', 10)
    )
    excel_radio.pack(anchor="w", padx=20, pady=2)

    # Section 2: Page Selection for Export
    pages = [
        "cover", "disclosure statement", "overview", "kev comparison", 
        "base score", "severity", "attack vector", "attack complexity", 
        "privileges", "confidentiality", "integrity", "avaialability", "details"
    ]
    page_vars = {}
    pages_frame = tk.LabelFrame(
        export_config_frame, text="Select Pages to Include",
        font=('Arial', 10, 'bold'),
        bg="lightblue", fg="gray10", padx=10, pady=10
    )
    pages_frame.pack(fill="both", expand=True, padx=5, pady=5)

    for page in pages:
        var = tk.BooleanVar(value=True)
        page_vars[page] = var
        cb = tk.Checkbutton(
            pages_frame,
            text=page.capitalize(),
            variable=var,
            bg="lightblue", fg="gray10",
            font=('Arial', 10)
        )
        cb.pack(anchor="w", padx=20, pady=2)

    # --- Footer Buttons ---
    button_pdf = tk.Button(
        root, text="Export",
        font=('Arial', 10, 'bold'),
        command=export_to_pdf,
        bg="lightgreen", fg="gray10", width=20
    )
    button_pdf.grid(row=2, column=0, padx=5, pady=10, ipady=10)

    button_flush = tk.Button(
        root, text="Flush Database",
        font=('Arial', 10, 'bold'),
        command=flush_database,
        bg="red", fg="white", width=20
    )
    button_flush.grid(row=2, column=2, padx=5, pady=10, ipady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
