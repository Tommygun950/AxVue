"""
This file contains styling code for the Scans window.
"""
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QTableWidget, QGroupBox
from PyQt5.QtCore import Qt


def apply_scans_window_style(window):
    """
    Applies styling to the entire Scans window.

    This function should:
    1. Set the background color of the main window to #e7e2f3.
    2. Call helper functions to apply specific styles to each component.

    Parameters:
    window (ScansWindow): The main ScansWindow instance to style.
    """
    # Set window background color
    window_palette = window.central_widget.palette()
    window_palette.setColor(QPalette.Window, QColor("#e7e2f3"))
    window.central_widget.setAutoFillBackground(True)
    window.central_widget.setPalette(window_palette)

    # Apply styles to various components
    style_scans_summary_group(window.scans_summary_group)
    style_scan_table(window.scan_table)
    style_add_scan_button(window.add_scan_button)


def style_scans_summary_group(group_box):
    """
    Applies styling to the Scans Summary group box.

    This function should:
    1. Set the background color of the group box to #2d3c67.
    2. Set the title text color to #e7e2f3.
    3. Make the title text bold.
    4. Set the text color of all child QLabels to #e7e2f3.

    Parameters:
    group_box (QGroupBox): The Scans Summary group box to style.
    """
    group_box.setStyleSheet("""
        QGroupBox {
            background-color: #2d3c67;
            color: #e7e2f3;
            border: 1px solid #1a2233;
            border-radius: 5px;
            margin-top: 20px;
            padding-top: 10px;
            font-weight: bold;
            font-size: 14pt;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 2px 15px;
            background-color: #2d3c67;
            border: 1px solid black;
            border-radius: 8px;
            margin-bottom: 1px;
        }
        QLabel {
            color: #e7e2f3;
        }
    """)


def style_scans_group(group_box):
    """
    Applies styling to the Scans group box.

    This function should:
    1. Set the background color of the group box to #688cca.
    2. Set the title text color to #e7e2f3.
    3. Make the title text bold.

    Parameters:
    group_box (QGroupBox): The Scans group box to style.
    """
    group_box.setStyleSheet("""
        QGroupBox {
            background-color: #2d3c67;
            color: #e7e2f3;
            border: 1px solid #4a6790;
            border-radius: 5px;
            margin-top: 20px;
            padding-top: 10px;
            font-weight: bold;
            font-size: 14pt;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 2px 15px;
            background-color: #2d3c67;
            border: 1px solid black;
            border-radius: 8px;
            margin-bottom: 1px;
        }
    """)


def style_add_scan_button(button):
    """
    Applies styling to the Add Scan button.

    This function should:
    1. Set the background color of the button to #88E788.
    2. Set the text color to white.
    3. Make the text bold.
    4. Add visual improvements for hover and pressed states.

    Parameters:
    button (QPushButton): The Add Scan button to style.
    """
    # Style button
    button.setStyleSheet("""
        QPushButton {
            background-color: #88E788;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #6BC96B;
        }
        QPushButton:pressed {
            background-color: #5AAF5A;
        }
    """)


def style_scan_table(table):
    """
    Applies styling to the Scans table.

    This function should:
    1. Style the header with:
       a. Background color #688cca.
       b. Text color #e7e2f3.
       c. Bold font.
    2. Style the table cells with:
       a. Background color #e7e2f3.
       b. Text color #2d3c67.
       c. Centered text alignment.
    3. Apply additional styling for visual separators and selection states.

    Parameters:
    table (QTableWidget): The Scans table to style.
    """
    table.setStyleSheet("""
        QTableWidget {
            background-color: #e7e2f3;
            alternate-background-color: #d7d2e3;
            gridline-color: #b8b2d3;
            border: 1px solid #b8b2d3;
            border-radius: 4px;
        }
        QTableWidget::item {
            color: #2d3c67;
            padding: 4px;
            text-align: center;
        }
        QTableWidget::item:selected {
            background-color: #a0b8e0;
            color: #2d3c67;
        }
        QHeaderView::section {
            background-color: #688cca;
            color: #e7e2f3;
            font-weight: bold;
            padding: 5px;
            border: 1px solid #5a7db0;
            text-align: center;
        }
        QCheckBox {
            margin: 0px;
            padding: 0px;
        }
        QCheckBox::indicator {
            width: 15px;
            height: 15px;
        }
    """)

    # Enable alternating row colors for better readability
    table.setAlternatingRowColors(True)

    # Set selection behavior
    table.setSelectionBehavior(QTableWidget.SelectRows)

    # Set table header font
    header = table.horizontalHeader()
    font = header.font()
    font.setBold(True)
    header.setFont(font)

    # Center align the text in each cell
    for row in range(table.rowCount()):
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                item.setTextAlignment(Qt.AlignCenter)


def style_table_buttons(table):
    """
    Applies styling to the Edit and Delete buttons in the table.
    
    This function should:
    1. Style the Edit buttons with:
       a. Background color #688cca.
       b. Text color white.
    2. Style the Delete buttons with:
       a. Background color #e74c3c.
       b. Text color white.
    
    Parameters:
    table (QTableWidget): The table containing the buttons to style.
    """
    rows = table.rowCount()

    for row in range(rows):
        # Style Edit button
        edit_button = table.cellWidget(row, 6)
        if edit_button:
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #688cca;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #5a7db0;
                }
                QPushButton:pressed {
                    background-color: #4c6c9c;
                }
            """)

        # Style Delete button
        delete_button = table.cellWidget(row, 7)
        if delete_button:
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #c94032;
                }
                QPushButton:pressed {
                    background-color: #a73529;
                }
            """)


def integrate_all_styling(window):
    """
    Integrates all styling functions to apply a cohesive look to the Scans window.

    This function should:
    1. Apply the window background style.
    2. Style all group boxes.
    3. Style the scans table.
    4. Style the Add Scan button.
    5. Set up a mechanism to style table buttons whenever the table is updated.

    Parameters:
    window (ScansWindow): The ScansWindow instance to style.
    """
    # Apply main styles
    apply_scans_window_style(window)

    # Style all group boxes (we need to get all group boxes from the layout)
    for i in range(window.layout.count()):
        widget = window.layout.itemAt(i).widget()
        if isinstance(widget, QGroupBox):
            if widget.title() == "Scans Summary":
                style_scans_summary_group(widget)
            elif widget.title() == "Scans":
                style_scans_group(widget)

    # Connect table population to button styling
    original_populate_function = window.populate_scans_table

    def styled_populate_function(*args, **kwargs):
        original_populate_function(*args, **kwargs)
        style_table_buttons(window.scan_table)

    window.populate_scans_table = styled_populate_function
