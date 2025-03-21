"""
This file contains styling code for the main GUI toolbar.
"""
# VARS FOR COLOR PALETTE #
bg_color = "#e7e2f3"
border_color = "#1a2233"
toolbar_bg_color = "#2d3c67"
toolbar_txt_color = "#e7e2f3"
action_idle_color = "#2d3c67"
action_hover_color = "#688cca"
action_selected_color = "#5a7db0"

# FUNCTIONS FOR ESTABLISHING STYLE #


def style_toolbar(toolbar):
    """
    Applies styling to the main application toolbar.
    This function should:
    1. Set the background color of the toolbar.
    2. Set the text color of the toolbar.
    3. Apply border and padding styling.
    """
    style = f"""
        QToolBar {{
            background-color: {toolbar_bg_color};
            color: {toolbar_txt_color};
            spacing: 5px;
            border: 1px solid {border_color};
            padding: 2px;
        }}

        QToolBar QToolButton {{
            background-color: {action_idle_color};
            color: {toolbar_txt_color};
            font-weight: bold;
            font-size: 9pt;
            border: 1px solid {border_color};
            border-radius: 2px;
            padding: 2px 6px;
            margin: 1px;
        }}

        QToolBar QToolButton:hover {{
            background-color: {action_hover_color};
        }}

        QToolBar QToolButton:checked, QToolBar QToolButton:pressed {{
            background-color: {action_selected_color};
            border: 1px solid {toolbar_txt_color};
        }}
    """

    toolbar.setStyleSheet(style)
    toolbar.setMovable(False)
    toolbar.setFloatable(False)


def style_toolbar_actions(toolbar):
    """
    Apply additional styling to the toolbar actions.
    This function should:
    1. Set the checkable property of actions to True to show selection state.
    2. Make the first action (Scans) checked by default.
    """
    actions = toolbar.actions()

    for i, action in enumerate(actions):
        action.setCheckable(True)
        if i == 0:
            action.setChecked(True)

    def make_exclusive(checked_action):
        if checked_action.isChecked():
            for action in actions:
                if action != checked_action and action.isChecked():
                    action.setChecked(False)

    for action in actions:
        action.triggered.connect(lambda checked, a=action: make_exclusive(a))

# FUNCTIONS FOR INTEGRATING STYLE INTO WINDOW #


def integrate_toolbar_styling(main_window):
    """
    Integrates the styling for the main toolbar.
    This function should:
    1. Style the overall toolbar.
    2. Style the actions in the toolbar.
    """
    style_toolbar(main_window.toolbar)
    style_toolbar_actions(main_window.toolbar)
