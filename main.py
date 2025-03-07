"""
This is the main file for the project.
"""
from gui.gui import (
    MainAppWindow, QApplication
)
from processing.database_processing import(
    initialize_database
)

def main():
    """
    Main function of the application.

    This function should:
    1. Initialize the sqlite3 database.
    2. Open the GUI application.
    """
    initialize_database()

    app = QApplication([])
    window = MainAppWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()