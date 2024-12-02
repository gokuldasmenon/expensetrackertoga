from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import button, label, box

from database import ExpenseTracker


class TripHistoryScreen:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout

        # Main container
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))

        # Header
        header_label = label.Label(
            'Trip History',
            style=Pack(text_align='center', padding_top=50, font_size=20)
        )
        self.layout.add(header_label)

        # History list container
        self.history_list = box.Box(style=Pack(direction=COLUMN, padding=10))
        self.layout.add(self.history_list)
        self.load_history()

        # Back button
        back_button = button.Button(
            'Back',
            style=Pack(padding=5, width=200)
        )
        back_button.on_press = self.goto_main
        self.layout.add(back_button)

    def load_history(self):
        """Load and display trip history."""
        self.history_list.clear()  # Clear the history list before adding new items

        import os
        archive_files = [f for f in os.listdir('.') if f.startswith('trip_archive_') and f.endswith('.db')]

        for archive_file in sorted(archive_files, reverse=True):
            # Create a row for each archive file
            archive_row = box.Box(style=Pack(direction=ROW, padding=5))

            # Archive file label
            archive_label = label.Label(
                f'Trip Archive: {archive_file}',
                style=Pack(flex=1, padding=(0, 5))
            )
            archive_row.add(archive_label)

            # Load button
            load_button = button.Button(
                'Load',
                style=Pack(padding=(0, 5))
            )
            load_button.on_press = lambda x, db=archive_file: self.load_archive(db)
            archive_row.add(load_button)

            # Add the row to the history list
            self.history_list.add(archive_row)

    def load_archive(self, archive_db):
        """Load details from the archive database."""
        expense_tracker = ExpenseTracker(archive_db)
        trips = expense_tracker.get_trips()

        # Create a container for trip details
        content = box.Box(style=Pack(direction=COLUMN, padding=10))
        for trip in trips:
            trip_details = f"Trip: {trip[1]}\nStart Date: {trip[2]}\nType: {trip[3]}"
            content.add(label.Label(trip_details))

        # Display trip details (replace this with a popup or another screen if needed)
        self.history_list.add(content)

    def goto_main(self, sender):
        """Return to the main screen."""
        self.app.main_window.content = self.main_screen_layout
