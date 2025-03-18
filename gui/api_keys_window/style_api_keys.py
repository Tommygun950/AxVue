"""
This file contains styling code for the API Keys window.
"""
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtCore import Qt


# VARS FOR COLOR PALETTE #


bg_color = "#e7e2f3"
second_bg_color = "#2d3c67"

border_color = "#1a2233"

table_bg_color = "#ccd9f0"
table__header_color = "#688cca"
table_header_txt_color = "#688cca"

groupbox_txt_color = "#e7e2f3"

add_button_txt_color = "white"
add_button_color = "#56d156"
add_button_hover_color = "#2ade2a"
add_button_pressed_color = "#5AAF5A"

edit_button_txt_color = "white"
edit_button_color = "#688cca"
edit_button_hover_color = "#5a7db0"
edit_button_pressed_color = "#4c6c9c"

delete_button_txt_color = "white"
delete_button_color = "#e74c3c"
delete_button_hover_color = "#c94032"
delete_button_pressed_color = "#a73529"


# FUNCTIONS FOR ESTABLISHING STYLE #


def style_api_keys_window(window):
    """
    Applies styling to the entire API Keys window.

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
        background-color: {second_bg_color};
        color: {groupbox_txt_color};

        border: 1px solid {border_color};
        border-radius: 8px;

        margin-bottom: 1px;
        padding: 2px 15px;

        subcontrol-origin: margin;
        subcontrol-position: top center;
    }}
    QGroupBox {{
        background-color: {second_bg_color};

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


def style_add_api_key_button(button):
    """
    Applies styling to the Add API Key button.

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


def style_key_table(table):
    """
    Applies styling to the API Key table.

    This function should:
    1. Style the following:
        a. The QTableWidget.
        b. The items in the QTableWidget.
        c. A selected item.
        d. The column headers.
        e. The QCheckBox.
        f. The outerspacing of the QCheckBox.
        g. The inner contents of the QCheckBox.
    2. Ensure the following for the tables:
        a. The headers are bold.
        b. The rows alternate colors.
    """
    style = f"""
    QTableWidget {{
        background-color: {bg_color};

        border: 1px solid {second_bg_color};
        border-radius: 4px;
    }}
    QTableWidget::item {{
        padding: 2px;

        text-align: center;
    }}
    QTableWidget::item:selected {{
        background-color: {table_bg_color};
        color: {second_bg_color};
    }}
    QHeaderView::section {{
        background-color: {table__header_color};
        color: {table_header_txt_color};

        font-weight: bold;

        border: 1px solid {border_color};

        padding: 5px;

        text-align: center;
    }}
    QCheckBox {{
        margin: 0px;
        padding: 0px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
    }}
    """
    table.setStyleSheet(style)

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
            edit_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {edit_button_color};
                    color: {edit_button_txt_color};

                    border: none;
                    border-radius: 4px;

                    padding: 5px;

                    font-size: 15px;
                }}
                QPushButton:hover {{
                    background-color: {edit_button_hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {edit_button_pressed_color};
                }}
            """)

        delete_button = table.cellWidget(row, 7)
        if delete_button:
            delete_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {delete_button_color};
                    color: {delete_button_txt_color};

                    border: none;
                    border-radius: 4px;

                    padding: 5px;

                    font-size: 15px;
                }}
                QPushButton:hover {{
                    background-color: {delete_button_hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {delete_button_pressed_color};
                }}
            """)


# FUNCTIONS FOR INTEGRATING STYLE INTO WINDOW #


def integrate_window_styling(window):
    """
    Integrates the style for the API Keys window.

    This function should:
    1. Style the overall window.
    """
    style_api_keys_window(window)


def integrate_summary_group_styling(window):
    """
    Integrates all styling for the summary group.

    This function should:
    1. Style all of the API Keys Summary QGroupBox.
    """
    style_group_box(window.api_keys_summary_group)


def integrate_api_keys_group_styling(window):
    """
    Integrates all styling for the api keys group.
    This function styles:
      1. The api keys group box.
      2. The Add API Key button.
      3. The API Key table.
      4. The buttons in the table.
    """
    style_group_box(window.api_keys_group)

    style_add_api_key_button(window.add_api_key_button)
    style_key_table(window.api_keys_table)

    original_populate_function = window.populate_api_keys_table

    def styled_populate_function(*args, **kwargs):
        original_populate_function(*args, **kwargs)
        style_table_buttons(window.api_keys_table)

    window.populate_api_keys_table = styled_populate_function
