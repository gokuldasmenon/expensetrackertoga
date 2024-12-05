from datetime import datetime
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import button, label, textinput, box
from .database import ExpenseTracker

import toga


class TripHistoryScreen:
    def __init__(self, name, app, main_screen_layout):
        try:
            print("Initializing TripHistoryScreen...")
            self.app = app
            self.name = name
            self.main_screen_layout = main_screen_layout
            self.database = app.database

            # Main layout with scrolling
            self.layout = toga.ScrollContainer(style=Pack(flex=1))
            self.content_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

            # Header with mobile-friendly styling
            header_label = toga.Label(
                'Trip History',
                style=Pack(
                    text_align='center',
                    padding_top=20,
                    padding_bottom=10,
                    font_size=18,
                    font_weight='bold'
                )
            )
            self.content_box.add(header_label)

            # History container
            self.history_container = toga.Box(style=Pack(direction=COLUMN, padding=5))
            self.content_box.add(self.history_container)

            # Message container for status messages
            self.message_container = toga.Box(style=Pack(direction=COLUMN, padding=5))
            self.content_box.add(self.message_container)

            # Set the scrollable content
            self.layout.content = self.content_box

            # Load trip history
            self.load_history()
            print("TripHistoryScreen initialized successfully")

        except Exception as e:
            print(f"Error initializing TripHistoryScreen: {e}")
            self.show_error(f"Error initializing screen: {str(e)}")

    def load_history(self):
        """Load archived trips history"""
        try:
            print("Loading trip history...")
            self.history_container.clear()
            self.message_container.clear()

            # Get archived trips from database
            self.database.cursor.execute(
                "SELECT trip_name, archive_path, archived_date FROM archived_trips ORDER BY archived_date DESC"
            )
            archived_trips = self.database.cursor.fetchall()

            if not archived_trips:
                no_history_label = toga.Label(
                    'No archived trips found',
                    style=Pack(padding=10, font_size=14)
                )
                self.history_container.add(no_history_label)
                return

            for trip_name, archive_path, archived_date in archived_trips:
                # Create trip container with mobile-friendly styling
                trip_box = toga.Box(
                    style=Pack(
                        direction=COLUMN,
                        padding=5,
                        background_color='#f0f0f0',
                        width=180
                    )
                )

                # Trip details
                details_box = toga.Box(style=Pack(direction=COLUMN, padding=2))
                details_box.add(toga.Label(
                    f"Trip: {trip_name}",
                    style=Pack(padding=(0, 2), font_size=14, font_weight='bold')
                ))
                details_box.add(toga.Label(
                    f"Archived: {archived_date}",
                    style=Pack(padding=(0, 2), font_size=12)
                ))
                trip_box.add(details_box)

                # Buttons container
                button_box = toga.Box(style=Pack(direction=ROW, padding=2))

                # Load button
                load_button = toga.Button(
                    'Load',
                    on_press=lambda x, path=archive_path: self.load_archive(path),
                    style=Pack(padding=2, width=60, height=30)
                )
                button_box.add(load_button)

                # Delete button
                delete_button = toga.Button(
                    'Delete',
                    on_press=lambda x, path=archive_path: self.delete_archive(path),
                    style=Pack(padding=2, width=60, height=30)
                )
                button_box.add(delete_button)

                trip_box.add(button_box)
                self.history_container.add(trip_box)

            print("Trip history loaded successfully")

        except Exception as e:
            print(f"Error loading trip history: {e}")
            self.show_error(f"Error loading trip history: {str(e)}")

    def load_archive(self, archive_path):
        """Load an archived trip"""
        try:
            print(f"Loading archive: {archive_path}")

            # Show confirmation dialog
            confirm_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            confirm_label = toga.Label(
                'Loading this archive will replace the current trip. Continue?',
                style=Pack(padding=5)
            )
            confirm_box.add(confirm_label)

            def confirm_load(sender):
                try:
                    self.database.load_archived_trip(archive_path)
                    self.show_success("Archive loaded successfully!")
                    self.goto_main(None)
                except Exception as e:
                    self.show_error(f"Error loading archive: {str(e)}")
                finally:
                    self.content_box.remove(confirm_box)

            def cancel_load(sender):
                self.content_box.remove(confirm_box)

            # Add confirmation buttons
            button_box = toga.Box(style=Pack(direction=ROW, padding=5))
            yes_button = toga.Button(
                'Yes',
                on_press=confirm_load,
                style=Pack(padding=2, width=60)
            )
            no_button = toga.Button(
                'No',
                on_press=cancel_load,
                style=Pack(padding=2, width=60)
            )

            button_box.add(yes_button)
            button_box.add(no_button)
            confirm_box.add(button_box)

            self.content_box.add(confirm_box)

        except Exception as e:
            print(f"Error in load_archive: {e}")
            self.show_error(f"Error loading archive: {str(e)}")

    def delete_archive(self, archive_path):
        """Delete an archived trip"""
        try:
            print(f"Deleting archive: {archive_path}")

            # Show confirmation dialog
            confirm_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            confirm_label = toga.Label(
                'Are you sure you want to delete this archived trip?',
                style=Pack(padding=5)
            )
            confirm_box.add(confirm_label)

            def confirm_delete(sender):
                try:
                    self.database.delete_archive(archive_path)
                    self.show_success("Archive deleted successfully!")
                    self.load_history()
                except Exception as e:
                    self.show_error(f"Error deleting archive: {str(e)}")
                finally:
                    self.content_box.remove(confirm_box)

            def cancel_delete(sender):
                self.content_box.remove(confirm_box)

            # Add confirmation buttons
            button_box = toga.Box(style=Pack(direction=ROW, padding=5))
            yes_button = toga.Button(
                'Yes',
                on_press=confirm_delete,
                style=Pack(padding=2, width=60)
            )
            no_button = toga.Button(
                'No',
                on_press=cancel_delete,
                style=Pack(padding=2, width=60)
            )

            button_box.add(yes_button)
            button_box.add(no_button)
            confirm_box.add(button_box)

            self.content_box.add(confirm_box)

        except Exception as e:
            print(f"Error in delete_archive: {e}")
            self.show_error(f"Error deleting archive: {str(e)}")

    def show_error(self, message):
        """Show error message"""
        try:
            self.message_container.clear()
            error_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            error_label = toga.Label(
                message,
                style=Pack(padding=3, color='red', font_size=14)
            )
            error_box.add(error_label)
            self.message_container.add(error_box)
            print(f"Error message displayed: {message}")
        except Exception as e:
            print(f"Error showing error message: {e}")

    def show_success(self, message):
        """Show success message"""
        try:
            self.message_container.clear()
            success_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            success_label = toga.Label(
                message,
                style=Pack(padding=3, color='green', font_size=14)
            )
            success_box.add(success_label)
            self.message_container.add(success_box)
            print(f"Success message displayed: {message}")
        except Exception as e:
            print(f"Error showing success message: {e}")

    def goto_main(self, sender):
        """Return to main screen"""
        try:
            self.app.main_window.content = self.main_screen_layout
            print("Returned to main screen")
        except Exception as e:
            print(f"Error returning to main screen: {e}")

    # def goto_main(self, sender):
    #     """Go back to the main screen."""
    #     self.app.main_window.content = self.main_screen_layout

class AddFamilyScreen:
    def __init__(self, name, app, main_screen_layout, caller_screen=None):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout
        self.caller_screen = caller_screen  # Reference to the calling screen
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))
        self.database = app.database

        # Header
        header_label = label.Label(
            'Add Family',
            style=Pack(text_align='center', padding_top=50)
        )
        self.layout.add(header_label)

        # Form container
        form_container = box.Box(style=Pack(direction=COLUMN, padding=10))

        # Family name input
        family_name_label = label.Label('Family Name:', style=Pack(padding=(5, 0)))
        form_container.add(family_name_label)
        self.family_name_input = textinput.TextInput(style=Pack(padding=(0, 10), width=200))
        form_container.add(self.family_name_input)

        # Number of members input
        num_members_label = label.Label('Number of Members:', style=Pack(padding=(5, 0)))
        form_container.add(num_members_label)
        self.num_members_input = textinput.TextInput(style=Pack(padding=(0, 10), width=200))
        form_container.add(self.num_members_input)

        self.layout.add(form_container)

        # Buttons container
        button_container = box.Box(style=Pack(direction=COLUMN, padding=10))

        add_family_button = button.Button(
            'Add Family',
            style=Pack(padding=5, width=200)
        )
        add_family_button.on_press = self.add_family
        button_container.add(add_family_button)

        back_button = button.Button(
            'Back',
            style=Pack(padding=5, width=200)
        )
        back_button.on_press = self.goto_main
        button_container.add(back_button)

        self.layout.add(button_container)

    def goto_main(self, sender):
        """Go back to the main screen."""
        if self.caller_screen and hasattr(self.caller_screen, 'update_trip_list'):
            self.caller_screen.update_trip_list()  # Call update_trip_list on the calling screen
        self.app.main_window.content = self.main_screen_layout

    def add_family(self, sender):
        """Add a new family and navigate back."""
        try:
            family_name = self.family_name_input.value
            num_members = self.num_members_input.value

            # Validate inputs
            if not all([family_name, num_members]):
                self.show_error("Please fill in all fields")
                return

            # Save family details
            expense_tracker = ExpenseTracker('expense_tracker.db')
            expense_tracker.save_family_details(family_name, num_members, 1)

            # Navigate back to the calling screen
            self.goto_main(sender)
        except Exception as e:
            self.show_error(f"Error adding family: {str(e)}")

    def show_error(self, message):
        """Show error message."""
        error_box = box.Box(style=Pack(direction=COLUMN, padding=10))
        error_label = label.Label(
            message,
            style=Pack(padding=5, color='red')
        )
        error_box.add(error_label)
        self.layout.add(error_box)

