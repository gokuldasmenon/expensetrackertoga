"""
Expense tracking application for personal and family expenses.
"""
import toga
import os
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import box, label

from .main import MainScreen
from .database import ExpenseTracker


class ExpenseTrackerApp(toga.App):
    def startup(self):
        try:
            print("Starting ExpenseTracker application...")

            # Create the main window first
            self.main_window = toga.MainWindow(title="Expense Tracker")
            print("Main window created")

            # Initialize the database with the app instance
            self.database = ExpenseTracker(self)
            print("Database initialized successfully")

            # Create the main screen
            main_screen = MainScreen('main', self)
            print("Main screen created")

            # Set the content
            self.main_window.content = main_screen.layout
            self.main_window.show()

        except Exception as e:
            print(f"Error during startup: {e}")
            if hasattr(self, 'main_window'):
                self.main_window.info_dialog(
                    "Startup Error",
                    f"Error initializing application: {str(e)}"
                )


def main():
    return ExpenseTrackerApp(
        'Expense Tracker',
        'com.gokul.expensetracker'
    )
