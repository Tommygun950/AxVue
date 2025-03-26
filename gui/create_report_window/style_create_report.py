"""
This file contains styling code for the Create Report window.
"""
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QTableWidget, QPushButton, QLabel
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
COLOR_BTN_CREATE = "#56d156"  # Create button color
COLOR_BTN_CREATE_HOVER = "#2ade2a"  # Create button hover color
COLOR_BTN_CREATE_PRESSED = "#5AAF5A"  # Create button pressed color

# Table header colors
COLOR_TABLE_HEADER_BG = "#688cca"  # Table header background
COLOR_TABLE_HEADER_BORDER = "#5a7db0"  # Table header border
COLOR_TABLE_SELECTED_BG = "#ccd9f0"  # Selected row background
COLOR_TABLE_SELECTED_TEXT = "#2d3c67"  # Selected row text

# Status colors
COLOR_STATUS_VALID_BG = "#56d156"  # Valid status background
COLOR_STATUS_INVALID_BG = "#e74c3c"  # Invalid status background
COLOR_STATUS_TEXT = "white"  # Status text color

# Remove button colors
COLOR_BTN_REMOVE = "#e74c3c"  # Remove button color
COLOR_BTN_REMOVE_HOVER = "#c94032"  # Remove button hover color
COLOR_BTN_REMOVE_PRESSED = "#a73529"  # Remove button pressed color

# Cached percentage colors
COLOR_CACHE_LOW = "#ffb3b3"    # Light red for < 33%
COLOR_CACHE_MED = "#ffffb3"    # Light yellow for 33-66%
COLOR_CACHE_HIGH = "#b3ffb3"   # Light green for > 66%
COLOR_CACHE_TEXT = "#333333"   # Dark text for better contrast

# Export configuration colors
COLOR_EXPORT_BG = "#f5f5f5"  # Light background for export config
COLOR_CHECKBOX_CHECKED = "#5a7db0"  # Checkbox checked color


# FUNCTIONS FOR ESTABLISHING STYLE #


def style_create_report_window(window):
    """
    Applies styling to the entire Create Report window.

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
            color: {COLOR_GROUPBOX_TEXT};

            font-weight: bold;
            font-size: 10pt;
        }}
    """

    group_box.setStyleSheet(style)


def style_table(table):
    """
    Applies styling to the tables in the Create Report window.

    This function should:
    1. Style the following:
        a. The QTableWidget.
        b. The items in the QTableWidget.
        c. A selected item.
        d. The column headers.
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


def style_api_keys_table_buttons(table):
    """
    Applies styling to the buttons in the API Keys table.

    This function should:
    1. Style the Status buttons.
    2. Style the Remove buttons.
    """
    def get_status_button_style(status: str):
        """
        Returns the appropriate styling for a status button based on its value.
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

    remove_button_style = f"""
        QPushButton {{
            background-color: {COLOR_BTN_REMOVE};
            color: {COLOR_BTN_TEXT};

            border: none;
            border-radius: 4px;

            padding: 5px;

            font-size: 15px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_BTN_REMOVE_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_BTN_REMOVE_PRESSED};
        }}
    """

    rows = table.rowCount()
    for row in range(rows):
        # Status button is at column 3 in the API Keys table
        status_button = table.cellWidget(row, 2)
        if status_button:
            status_text = status_button.text()
            status_button.setStyleSheet(get_status_button_style(status_text))

        # Remove button is at column 4 in the API Keys table
        remove_button = table.cellWidget(row, 3)
        if remove_button:
            remove_button.setStyleSheet(remove_button_style)


def style_scans_table_buttons(table):
    """
    Applies styling to the buttons in the Scans table.

    This function should:
    1. Style the Cache buttons.
    2. Style the Cached percentage buttons.
    3. Style the Remove buttons.
    """
    def get_cache_button_style(status: str):
        """
        Returns the appropriate styling for a cache button based on its value.
        """
        if status == "Enabled":
            return f"""
                QPushButton:disabled {{
                    background-color: {COLOR_STATUS_VALID_BG};
                    color: {COLOR_STATUS_TEXT};

                    font-weight: bold;

                    border: none;
                    border-radius: 4px;

                    padding: 5px;
                    font-size: 10px;
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
                    font-size: 10px;
                }}
            """

    remove_button_style = f"""
        QPushButton {{
            background-color: {COLOR_BTN_REMOVE};
            color: {COLOR_BTN_TEXT};

            border: none;
            border-radius: 4px;

            padding: 5px;

            font-size: 15px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_BTN_REMOVE_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_BTN_REMOVE_PRESSED};
        }}
    """

    rows = table.rowCount()
    for row in range(rows):
        # Cache button is at column 3 in the Scans table
        cache_button = table.cellWidget(row, 3)
        if cache_button:
            cache_status = cache_button.text()
            cache_button.setStyleSheet(get_cache_button_style(cache_status))

        # Cached percentage button is at column 4 in the Scans table
        cached_perc_button = table.cellWidget(row, 4)
        if cached_perc_button:
            button_text = cached_perc_button.text()
            percentage_text = button_text.replace('%', '')
            try:
                percentage = float(percentage_text)

                # Apply different colors based on percentage ranges
                if percentage < 33:
                    bg_color = COLOR_CACHE_LOW    # Light red
                elif percentage <= 66:
                    bg_color = COLOR_CACHE_MED    # Light yellow
                else:
                    bg_color = COLOR_CACHE_HIGH   # Light green

                cached_perc_button.setStyleSheet(f"""
                    QPushButton:disabled {{
                        background-color: {bg_color};
                        color: {COLOR_CACHE_TEXT};

                        font-weight: bold;

                        border: none;
                        border-radius: 4px;

                        padding: 5px;
                        font-size: 10px;
                    }}
                """)
            except ValueError:
                # Fallback if percentage cannot be parsed
                cached_perc_button.setStyleSheet(f"""
                    QPushButton:disabled {{
                        background-color: {COLOR_TABLE_HEADER_BG};
                        color: {COLOR_BTN_TEXT};

                        border: none;
                        border-radius: 4px;

                        padding: 5px;
                        font-size: 10px;
                    }}
                """)

        # Remove button is at column 5 in the Scans table
        remove_button = table.cellWidget(row, 5)
        if remove_button:
            remove_button.setStyleSheet(remove_button_style)


def style_export_config(group_box):
    """
    Applies styling to the Export Configuration group box and its components.

    This function should:
    1. Style group box itself (already done by the style_group_box function)
    2. Style the export type combo box
    3. Style the checkboxes
    4. Style the create report button
    """
    # Apply specific styling to elements within the export config group
    style = f"""
        QGroupBox QComboBox {{
            background-color: {COLOR_BG_MAIN};
            border: 1px solid {COLOR_BORDER_DARK};
            border-radius: 4px;
            padding: 4px;
            min-width: 100px;
        }}

        QGroupBox QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QGroupBox QComboBox::down-arrow {{
            width: 12px;
            height: 12px;
        }}

        QGroupBox QComboBox:hover {{
            background-color: {COLOR_TABLE_SELECTED_BG};
        }}

        QGroupBox QCheckBox {{
            color: {COLOR_GROUPBOX_TEXT};
            font-weight: normal;
            font-size: 10pt;
            spacing: 8px;
            margin-left: 10px;
        }}

        QGroupBox QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {COLOR_BORDER_DARK};
            border-radius: 3px;
            background-color: {COLOR_BG_MAIN};
        }}

        QGroupBox QCheckBox::indicator:checked {{
            background-color: {COLOR_CHECKBOX_CHECKED};
            border: 1px solid {COLOR_BORDER_DARK};
            image: url(check.png);
        }}

        QGroupBox QLabel {{
            text-align: left;
            padding-left: 10px;
        }}
    """

    # Apply the additional style to the group box
    current_style = group_box.styleSheet()
    group_box.setStyleSheet(current_style + style)

    # Find all labels and align them to the left
    for label in group_box.findChildren(QLabel):
        label.setAlignment(Qt.AlignLeft)

    # Style the Create Report button
    create_report_button_style = f"""
        QPushButton {{
            background-color: {COLOR_BTN_CREATE};
            color: {COLOR_BTN_TEXT};

            font-weight: bold;
            font-size: 12pt;

            border: none;
            border-radius: 4px;

            padding: 10px 20px;
            margin-top: 10px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_BTN_CREATE_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_BTN_CREATE_PRESSED};
        }}
    """

    # Apply style to the Create Report button
    export_button = group_box.findChild(QPushButton, "export_button")
    if export_button:
        export_button.setStyleSheet(create_report_button_style)


# FUNCTIONS FOR INTEGRATING STYLE INTO WINDOW #


def integrate_window_styling(window):
    """
    Integrates the style for the Create Report window.

    This function should:
    1. Style the overall window.
    """
    style_create_report_window(window)


def integrate_all_styling(window):
    """
    Main function to integrate all styling for the Create Report window.

    This function should be called from the CreateReportWindow initialization
    to apply all styling to the window components.
    """
    integrate_window_styling(window)
    integrate_api_keys_group_styling(window)
    integrate_scans_group_styling(window)
    integrate_export_config_styling(window)


def integrate_api_keys_group_styling(window):
    """
    Integrates all styling for the API Keys group in the Create Report window.

    This function styles:
      1. The API Keys group box.
      2. The API Keys table.
      3. The buttons in the table.
    """
    style_group_box(window.api_key_group)
    style_table(window.api_keys_table)

    original_populate_function = window.populate_selected_api_keys_table

    def styled_populate_function(*args, **kwargs):
        original_populate_function(*args, **kwargs)
        style_api_keys_table_buttons(window.api_keys_table)

    window.populate_selected_api_keys_table = styled_populate_function


def integrate_scans_group_styling(window):
    """
    Integrates all styling for the Scans group in the Create Report window.

    This function styles:
      1. The Scans group box.
      2. The Scans table.
      3. The buttons in the table.
    """
    style_group_box(window.scans_group)
    style_table(window.scans_table)

    original_populate_function = window.populate_selected_scans_table

    def styled_populate_function(*args, **kwargs):
        original_populate_function(*args, **kwargs)
        style_scans_table_buttons(window.scans_table)

    window.populate_selected_scans_table = styled_populate_function


def integrate_export_config_styling(window):
    """
    Integrates all styling for the Export Configuration group.

    This function styles:
      1. The Export Configuration group box and its components.
      2. The export type combo box.
      3. The page checkboxes.
      4. The Create Report button.
    """
    style_group_box(window.export_config_group)
    style_export_config(window.export_config_group)
