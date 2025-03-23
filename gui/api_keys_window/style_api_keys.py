"""
This file contains styling code for the API Keys window.
"""
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtCore import Qt

# VARS FOR COLOR PALETTE #
# General colors
COLOR_BG_MAIN = "#e7e2f3"  # Main background color
COLOR_BORDER_DARK = "#1a2233"  # Dark border color

# Group box colors
COLOR_GROUPBOX_BG = "#2d3c67"  # Group box background
COLOR_GROUPBOX_TEXT = "#e7e2f3"  # Group box text

# Button colors
COLOR_BTN_TEXT = "white"  # Button text color
COLOR_BTN_ADD = "#56d156"  # Add button color
COLOR_BTN_ADD_HOVER = "#2ade2a"  # Add button hover color
COLOR_BTN_ADD_PRESSED = "#5AAF5A"  # Add button pressed color

# Table header colors
COLOR_TABLE_HEADER_BG = "#688cca"  # Table header background
COLOR_TABLE_HEADER_BORDER = "#5a7db0"  # Table header border
COLOR_TABLE_SELECTED_BG = "#ccd9f0"  # Selected row background
COLOR_TABLE_SELECTED_TEXT = "#2d3c67"  # Selected row text

# Status colors
COLOR_STATUS_VALID_BG = "#56d156"  # Valid status background
COLOR_STATUS_INVALID_BG = "#e74c3c"  # Invalid status background
COLOR_STATUS_TEXT = "white"  # Status text color

# Edit button colors
COLOR_BTN_EDIT = "#688cca"  # Edit button color
COLOR_BTN_EDIT_HOVER = "#5a7db0"  # Edit button hover color
COLOR_BTN_EDIT_PRESSED = "#4c6c9c"  # Edit button pressed color

# Delete button colors
COLOR_BTN_DELETE = "#e74c3c"  # Delete button color
COLOR_BTN_DELETE_HOVER = "#c94032"  # Delete button hover color
COLOR_BTN_DELETE_PRESSED = "#a73529"  # Delete button pressed color


# FUNCTIONS FOR ESTABLISHING STYLE #


def style_api_keys_window(window):
    """
    Applies styling to the entire API Keys window.

    This function should:
    1. Set the color of the window.
    2. Set the auto fill of the background to true.
    3. Apply the palette style.
    """
    window_palette = window.central_widget.palette()
    window_palette.setColor(QPalette.Window, QColor(COLOR_BG_MAIN))
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
            background-color: {COLOR_GROUPBOX_BG};
            color: {COLOR_GROUPBOX_TEXT};

            border: 1px solid {COLOR_BORDER_DARK};
            border-radius: 8px;

            margin-bottom: 1px;
            padding: 2px 15px;

            subcontrol-origin: margin;
            subcontrol-position: top center;
        }}
        QGroupBox {{
            background-color: {COLOR_GROUPBOX_BG};

            font-weight: bold;
            font-size: 14pt;

            border: 1px solid {COLOR_BORDER_DARK};
            border-radius: 5px;

            margin-top: 20px;
            padding-top: 10px;
        }}
        QGroupBox QLabel {{
            color: {COLOR_BG_MAIN};

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
            background-color: {COLOR_BTN_ADD};
            color: {COLOR_BTN_TEXT};

            font-weight: bold;

            border: none;
            border-radius: 4px;

            padding: 6px 12px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_BTN_ADD_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_BTN_ADD_PRESSED};
        }}
    """

    button.setStyleSheet(style)


def style_api_key_table(table):
    """
    Applies styling to the API Keys table.

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
    style = f"""
        QTableWidget {{
            background-color: {COLOR_BG_MAIN};

            border: 1px solid {COLOR_GROUPBOX_BG};
            border-radius: 4px;
        }}
        QTableWidget::item {{
            padding: 2px;

            text-align: center;
        }}
        QTableWidget::item:selected {{
            background-color: {COLOR_TABLE_SELECTED_BG};
            color: {COLOR_TABLE_SELECTED_TEXT};
        }}
        QHeaderView::section {{
            background-color: {COLOR_TABLE_HEADER_BG};
            color: {COLOR_GROUPBOX_TEXT};

            font-weight: bold;

            border: 1px solid {COLOR_TABLE_HEADER_BORDER};

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


def style_functional_table_buttons(table):
    """
    Applies styling to the Status, Edit, and Delete buttons in the table.

    This function should:
    1. Style the Status buttons.
    2. Style the Edit buttons.
    3. Style the Delete buttons.
    """
    def get_status_button_style(status: str):
        """
        Returns the appropriate styling for a status button based on its value.

        This function should:
        1. Given the status of a specific API key, style it based on whether
        it's "Valid" or "Invalid".
        """
        if status == "Valid":
            return f"""
                QPushButton:disabled {{
                    background-color: {COLOR_STATUS_VALID_BG};
                    color: {COLOR_STATUS_TEXT};

                    font-weight: bold;

                    border: none;
                    border-radius: 4px;

                    padding: 5px;
                }}
            """
        else:
            return f"""
                QPushButton:disabled {{
                    background-color: {COLOR_STATUS_INVALID_BG};
                    color: {COLOR_STATUS_TEXT};

                    font-weight: bold;

                    border: none;
                    border-radius: 4px;

                    padding: 5px;
                }}
            """

    edit_button_style = f"""
        QPushButton {{
            background-color: {COLOR_BTN_EDIT};
            color: {COLOR_BTN_TEXT};

            border: none;
            border-radius: 4px;

            padding: 5px;

            font-size: 15px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_BTN_EDIT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_BTN_EDIT_PRESSED};
        }}
    """

    delete_button_style = f"""
        QPushButton {{
            background-color: {COLOR_BTN_DELETE};
            color: {COLOR_BTN_TEXT};

            border: none;
            border-radius: 4px;

            padding: 5px;

            font-size: 15px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_BTN_DELETE_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_BTN_DELETE_PRESSED};
        }}
    """

    rows = table.rowCount()
    for row in range(rows):
        status_button = table.cellWidget(row, 3)
        if status_button:
            status_text = status_button.text()
            status_button.setStyleSheet(get_status_button_style(status_text))

        edit_button = table.cellWidget(row, 4)
        if edit_button:
            edit_button.setStyleSheet(edit_button_style)

        delete_button = table.cellWidget(row, 5)
        if delete_button:
            delete_button.setStyleSheet(delete_button_style)


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
    Integrates all styling for the api_keys group.
    This function styles:
      1. The api_keys group box.
      2. The Add API Key button.
      3. The api_key table.
      4. The buttons in the table.
    """
    style_group_box(window.api_keys_group)

    style_add_api_key_button(window.add_api_key_button)
    style_api_key_table(window.api_keys_table)

    original_populate_function = window.populate_api_keys_table

    def styled_populate_function(*args, **kwargs):
        original_populate_function(*args, **kwargs)
        style_functional_table_buttons(window.api_keys_table)

    window.populate_api_keys_table = styled_populate_function
