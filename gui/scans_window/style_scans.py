"""
This file contains styling code for the Scans window.
"""
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtCore import Qt

# VARS FOR COLOR PALETTE #
bg_color = "#e7e2f3"
border_color = "#1a2233"

groupbox_bg_color = "#2d3c67"
groupbox_txt_color = "#e7e2f3"

add_button_txt_color = "white"
add_button_color = "#56d156"
add_button_hover_color = "#2ade2a"
add_button_pressed_color = "#5AAF5A"


# FUNCTIONS FOR ESTABLISHING STYLE #


def style_scans_window(window):
    """
    Applies styling to the entire Scans window.

    This function should:
    1. Set the color of the window.
    2. Set the auto fill of the background to true.
    3. Apply the pallete style.
    """
    window_palette = window.central_widget.palette()
    window_palette.setColor(QPalette.Window, QColor(bg_color))
    window.central_widget.setAutoFillBackground(True)
    window.central_widget.setPalette(window_palette)


def style_group_box(group_box):
    """
    Applies styling to a given QGroupBox.

    This function should:
    1. Format the QGroupBox title.
    2. Format the QGroupBox content.
    3. Format the content/QLabel words.
    """
    style = f"""
        QGroupBox::title {{
            background-color: {groupbox_bg_color};
            color: {groupbox_txt_color};

            border: 1px solid {border_color};
            border-radius: 8px;

            margin-bottom: 1px;
            padding: 2px 15px;

            subcontrol-origin: margin;
            subcontrol-position: top center;
        }}
        QGroupBox {{
            background-color:{groupbox_bg_color};

            font-weight: bold;
            font-size: 14pt;

            border: 1px solid {border_color};
            border-radius: 5px;

            margin-top: 20px;
            padding-top: 10px;
        }}
        QGroupBox QLabel {{
            color: {bg_color};

            font-weight: bold;
            font-size: 10pt;

            qproperty-alignment: 'AlignCenter';
        }}
    """

    group_box.setStyleSheet(style)


def style_add_scan_button(button):
    """
    Applies styling to the Add Scan button.

    This function should:
    1. Configure the style of the button when:
        a. Idle.
        b. Hovered over.
        c. Pressed.
    """
    style = f"""
        QPushButton {{
            background-color: {add_button_color};
            color: {add_button_txt_color};

            font-weight: bold;

            border: none;
            border-radius: 4px;

            padding: 6px 12px;
        }}
        QPushButton:hover {{
            background-color: {add_button_hover_color};
        }}
        QPushButton:pressed {{
            background-color: {add_button_pressed_color};
        }}
    """

    button.setStyleSheet(style)


def style_scan_table(table):
    """
    Applies styling to the Scans table.

    This function should:
    1. Style the following:
        a. The QTableWidget.
        b. The items in the QTableWidget.
        c. A selected item.
        d. The column headers.
        e. The QCheckBox.
        f. The outerspacing of the QCheckBox.
        g. The inner contents of the QCheckBox.
    """
    table.setStyleSheet("""
        QTableWidget {
            background-color: #e7e2f3;

            border: 1px solid #2d3c67;
            border-radius: 4px;
        }
        QTableWidget::item {
            padding: 2px;

            text-align: center;
        }
        QTableWidget::item:selected {
            background-color: #ccd9f0;
            color: #2d3c67;
        }
        QHeaderView::section {
            background-color: #688cca;
            color: #e7e2f3;

            font-weight: bold;

            border: 1px solid #5a7db0;

            padding: 5px;

            text-align: center;
        }
        QCheckBox {
            margin: 0px;
            padding: 0px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
    """)

    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectRows)

    header = table.horizontalHeader()
    font = header.font()
    font.setBold(True)
    header.setFont(font)

    for row in range(table.rowCount()):
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                item.setTextAlignment(Qt.AlignCenter)


def style_table_buttons(table):
    """
    Applies styling to the Edit and Delete buttons in the table.

    This function should:
    1. Style the Edit buttons.
    2. Style the Delete buttons.
    """
    rows = table.rowCount()
    for row in range(rows):
        edit_button = table.cellWidget(row, 6)
        if edit_button:
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #688cca;
                    color: white;

                    border: none;
                    border-radius: 4px;

                    padding: 5px;

                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #5a7db0;
                }
                QPushButton:pressed {
                    background-color: #4c6c9c;
                }
            """)

        delete_button = table.cellWidget(row, 7)
        if delete_button:
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;

                    border: none;
                    border-radius: 4px;

                    padding: 5px;

                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #c94032;
                }
                QPushButton:pressed {
                    background-color: #a73529;
                }
            """)

# FUNCTIONS FOR INTEGRATING STYLE INTO WINDOW #


def integrate_window_styling(window):
    """
    Integrates the style for the Scans window.

    This function should:
    1. Style the overall window.
    """
    style_scans_window(window)


def integrate_summary_group_styling(window):
    """
    Integrates all styling for the summary group.

    This function should:
    1. Style all of the Scans Summary QGroupBox.
    """
    style_group_box(window.scans_summary_group)


def integrate_scans_group_styling(window):
    """
    Integrates all styling for the scans group.
    This function styles:
      1. The scans group box.
      2. The Add Scan button.
      3. The scan table.
      4. The buttons in the table.
    """
    style_group_box(window.scans_group)

    style_add_scan_button(window.add_scan_button)
    style_scan_table(window.scan_table)

    original_populate_function = window.populate_scans_table

    def styled_populate_function(*args, **kwargs):
        original_populate_function(*args, **kwargs)
        style_table_buttons(window.scan_table)

    window.populate_scans_table = styled_populate_function
