from datetime import datetime
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import button, label, textinput, box
from .database import ExpenseTracker

import toga


class TripListScreen:
    def __init__(self, name, app, main_screen_layout):
        try:
            print("Initializing TripListScreen...")
            self.app = app
            self.name = name
            self.main_screen_layout = main_screen_layout

            # Use the existing database instance instead of creating a new one
            self.database = app.database
            print("Database instance accessed")

            # Create a scrollable container
            self.scroll_container = toga.ScrollContainer(style=Pack(flex=1))
            print("Scroll container created")

            # Main content container inside the scrollable container
            self.scrollable_content = toga.Box(style=Pack(direction=COLUMN, padding=20))

            # Header
            header_label = toga.Label(
                'Current Trip Details',
                style=Pack(text_align='center', padding_top=20, font_size=20)
            )
            self.scrollable_content.add(header_label)

            # Trip list container
            self.trip_list_container = toga.Box(style=Pack(direction=COLUMN, padding=10))
            self.scrollable_content.add(self.trip_list_container)

            # Buttons container
            button_container = toga.Box(style=Pack(direction=COLUMN, padding=10))

            add_family_button = toga.Button(
                'Add Family',
                style=Pack(padding=5, width=200)
            )
            add_family_button.on_press = self.goto_add_family
            button_container.add(add_family_button)

            self.scrollable_content.add(button_container)

            # Set the scrollable content to the ScrollContainer
            self.scroll_container.content = self.scrollable_content

            # Load the trip list
            self.update_trip_list()
            print("TripListScreen initialized successfully")

        except Exception as e:
            print(f"Error initializing TripListScreen: {e}")
            raise

    def update_trip_list(self):
        """Update the trip list with trip and family details."""
        try:
            print("Updating trip list...")
            self.clear_messages()  # Clear any existing messages
            self.trip_list_container.clear()

            # Use the existing database instance
            active_trip = self.database.get_active_trip()
            print(f"Active trip retrieved: {active_trip}")

            if active_trip:
                trip_id = active_trip[0]

                # Main trip box
                trip_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

                # Trip details section
                trip_details = toga.Box(style=Pack(direction=COLUMN, padding=5))
                trip_details.add(toga.Label(
                    f'Current Trip Name: {active_trip[1]}',
                    style=Pack(padding=(0, 10), font_weight='bold')
                ))
                trip_details.add(toga.Label(
                    f'Trip Type: {active_trip[3]}',
                    style=Pack(padding=(0, 10))
                ))
                trip_details.add(toga.Label(
                    f'Start Date: {active_trip[2]}',
                    style=Pack(padding=(0, 10))
                ))
                trip_box.add(trip_details)

                # Family section header
                family_header = toga.Label(
                    'Family Details',
                    style=Pack(padding=(10, 5), font_weight='bold', font_size=16)
                )
                trip_box.add(family_header)

                # Fetch family details for the active trip
                family_details = self.database.get_family_details_active(trip_id)
                for family in family_details:
                    family_box = self.create_family_box(family)
                    trip_box.add(family_box)

                self.trip_list_container.add(trip_box)
                print("Trip list updated successfully")
            else:
                # Show "No active trip" message
                no_trip_label = toga.Label(
                    'No active trip found. Please create a new trip.',
                    style=Pack(padding=20)
                )
                self.trip_list_container.add(no_trip_label)
                print("No active trip found")

        except Exception as e:
            print(f"Error updating trip list: {e}")
            self.show_error(f"Error loading trip data: {str(e)}")

    def create_family_box(self, family):
        """Create a box to display family details."""
        try:
            # Unpack family details
            family_id = family[0]
            family_name = family[1]
            num_members = family[2]

            # Create a container for the family details
            family_box = toga.Box(style=Pack(direction=ROW, padding=5, background_color="#f9f9f9"))

            # Add family details
            family_box.add(toga.Label(
                f'Family Name: {family_name}',
                style=Pack(padding=(5, 10), flex=1)
            ))
            family_box.add(toga.Label(
                f'Members: {num_members}',
                style=Pack(padding=(5, 10), flex=1)
            ))

            # Buttons container
            button_box = toga.Box(style=Pack(direction=ROW, padding=5))

            # Delete button
            delete_button = toga.Button(
                'Delete',
                on_press=lambda sender: self.delete_family(sender, family_id),
                style=Pack(padding=(5, 10), width=80)
            )
            button_box.add(delete_button)

            # Add buttons to the family box
            family_box.add(button_box)

            return family_box

        except Exception as e:
            print(f"Error creating family box: {e}")
            error_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            error_label = toga.Label(
                f"Error displaying family details: {str(e)}",
                style=Pack(padding=5, color='red')
            )
            error_box.add(error_label)
            return error_box

    def goto_add_family(self, sender):
        """Navigate to Add Family Screen."""
        self.app.main_window.content = AddFamilyScreen(
            'add_family',
            self.app,
            self.main_screen_layout,
            caller_screen=self  # Pass the current TripListScreen instance
        ).layout

    def delete_family(self, sender, family_id):
        """Delete a family record."""
        try:
            # Create a confirmation dialog box
            confirm_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
            confirm_label = toga.Label(
                'Are you sure you want to delete this family record?',
                style=Pack(padding=10)
            )
            confirm_box.add(confirm_label)

            # Buttons container
            button_box = toga.Box(style=Pack(direction=ROW, padding=5))

            def confirm_delete(sender):
                """Handle 'Yes' button click."""
                try:
                    # Delete the family record from the database
                    expense_tracker = ExpenseTracker('expense_tracker.db')
                    expense_tracker.delete_family_record(family_id)

                    # Show success message and refresh the trip list
                    self.show_success("Family deleted successfully!")
                    self.update_trip_list()

                    # Remove the confirmation dialog
                    self.scrollable_content.remove(confirm_box)
                except Exception as e:
                    self.show_error(f"Error deleting family: {str(e)}")

            def cancel_delete(sender):
                """Handle 'No' button click."""
                # Remove the confirmation dialog
                self.scrollable_content.remove(confirm_box)

            # Yes button
            yes_button = toga.Button(
                'Yes',
                style=Pack(padding=5, width=80)
            )
            yes_button.on_press = confirm_delete

            # No button
            no_button = toga.Button(
                'No',
                style=Pack(padding=5, width=80)
            )
            no_button.on_press = cancel_delete

            # Add buttons to the button container
            button_box.add(yes_button)
            button_box.add(no_button)
            confirm_box.add(button_box)

            # Add the confirmation dialog to the scrollable content
            self.scrollable_content.add(confirm_box)
        except Exception as e:
            self.show_error(f"Error displaying confirmation dialog: {str(e)}")

    def show_error(self, message):
        """Show error message."""
        self.clear_messages()
        error_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        error_label = toga.Label(
            message,
            style=Pack(padding=5, color='red')
        )
        error_box.add(error_label)
        self.scrollable_content.add(error_box)

    def show_success(self, message):
        """Show success message."""
        self.clear_messages()
        success_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        success_label = toga.Label(
            message,
            style=Pack(padding=5, color='green')
        )
        success_box.add(success_label)
        self.scrollable_content.add(success_box)

    def clear_messages(self):
        """Remove all success and error messages from the screen."""
        for widget in list(self.scrollable_content.children):
            if isinstance(widget, toga.Box) and len(widget.children) > 0:
                if isinstance(widget.children[0], toga.Label) and widget.children[0].style.color in ['green', 'red']:
                    self.scrollable_content.remove(widget)


class CreateTripScreen:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout
        self.layout = toga.Box(style=Pack(direction=COLUMN, padding=20))
        self.database = app.database  # Use the existing database instance

        # Header
        header_label = toga.Label(
            'Create Trip',
            style=Pack(text_align='center', padding_top=50, font_size=20)
        )
        self.layout.add(header_label)

        # Form container
        form_container = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Trip name input
        trip_name_label = toga.Label('Trip Name:', style=Pack(padding=(5, 0)))
        form_container.add(trip_name_label)
        self.trip_name_input = toga.TextInput(style=Pack(padding=(0, 10), width=200))
        form_container.add(self.trip_name_input)

        # Trip start date input with today's date
        trip_start_date_label = toga.Label(
            'Trip Start Date (YYYY-MM-DD):',
            style=Pack(padding=(5, 0))
        )
        form_container.add(trip_start_date_label)
        today_date = datetime.now().strftime('%Y-%m-%d')
        self.trip_start_date_input = toga.TextInput(
            value=today_date,
            style=Pack(padding=(0, 10), width=200)
        )
        form_container.add(self.trip_start_date_input)

        self.layout.add(form_container)

        # Message container for displaying status messages
        self.message_container = toga.Box(style=Pack(direction=COLUMN, padding=10))
        self.layout.add(self.message_container)

        # Buttons container
        button_container = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Create Trip button
        create_trip_button = toga.Button(
            'Create Trip',
            style=Pack(padding=5, width=200)
        )
        create_trip_button.on_press = self.create_trip
        button_container.add(create_trip_button)

        self.layout.add(button_container)

    def create_trip(self, sender):
        """Handle creating a new trip."""
        try:
            trip_name = self.trip_name_input.value.strip()
            trip_start_date = self.trip_start_date_input.value.strip()

            # Validate inputs
            if not trip_name or not trip_start_date:
                self.show_error("Please fill in all required fields")
                return

            # Validate date format (YYYY-MM-DD)
            try:
                datetime.strptime(trip_start_date, '%Y-%m-%d')
            except ValueError:
                self.show_error("Invalid date format. Please use YYYY-MM-DD.")
                return

            # Check for an active trip
            active_trip = self.database.get_active_trip()
            if active_trip:
                # Show active trip warning and exit button
                self.message_container.clear()
                message_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

                warning_label = toga.Label(
                    f'Only one active trip is allowed. Current trip: {active_trip[1]}',
                    style=Pack(padding=5, color='red')
                )
                message_box.add(warning_label)

                exit_button = toga.Button(
                    'Exit Current Trip',
                    style=Pack(padding=5, width=200)
                )
                exit_button.on_press = lambda sender: self.exit_trip(active_trip)
                message_box.add(exit_button)

                self.message_container.add(message_box)
            else:
                # No active trip, create a new one
                self.database.clear_family_details()  # Clear previous family details
                self.database.save_trip(trip_name, trip_start_date, 'Family', None, None, 0)
                self.show_success("Trip created successfully!")
                self.goto_main(None)

        except Exception as e:
            print(f"Error creating trip: {e}")
            self.show_error(f"Error creating trip: {str(e)}")

    def exit_trip(self, active_trip):
        """Archive current trip and create new one."""
        try:
            # Archive current trip
            archive_path = self.database.archive_trip()

            # Clear current trip data
            self.database.clear_trips()
            self.database.clear_expenses()
            self.database.clear_family_details()

            # Create new trip
            trip_name = self.trip_name_input.value.strip()
            trip_start_date = self.trip_start_date_input.value.strip()
            self.database.save_trip(trip_name, trip_start_date, 'Family', None, None, 0)

            # Show success message
            self.show_success(f"Previous trip archived. New trip created successfully!")
            self.goto_main(None)

        except Exception as e:
            print(f"Error exiting trip: {e}")
            self.show_error(f"Error exiting trip: {str(e)}")

    def goto_main(self, sender):
        """Return to main screen."""
        self.app.main_window.content = self.main_screen_layout

    def show_error(self, message):
        """Show error message."""
        self.message_container.clear()
        error_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        error_label = toga.Label(
            message,
            style=Pack(padding=5, color='red')
        )
        error_box.add(error_label)
        self.message_container.add(error_box)

    def show_success(self, message):
        """Show success message."""
        self.message_container.clear()
        success_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        success_label = toga.Label(
            message,
            style=Pack(padding=5, color='green')
        )
        success_box.add(success_label)
        self.message_container.add(success_box)


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
        try:
            print("Initializing AddFamilyScreen...")
            self.app = app
            self.name = name
            self.main_screen_layout = main_screen_layout
            self.caller_screen = caller_screen  # Reference to the calling screen

            # Use the existing database instance from the app
            if not hasattr(self.app, 'database'):
                raise AttributeError("App instance does not have a database attribute")
            self.database = self.app.database

            # Main layout
            self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))

            # Header
            header_label = label.Label(
                'Add Family',
                style=Pack(text_align='center', padding_top=10, font_size=18)
            )
            self.layout.add(header_label)

            # Form container
            form_container = box.Box(style=Pack(direction=COLUMN, padding=10))

            # Family name input
            form_container.add(label.Label('Family Name:', style=Pack(padding=(5, 0))))
            self.family_name_input = textinput.TextInput(style=Pack(padding=(0, 10), width=200))
            form_container.add(self.family_name_input)

            # Number of members input
            form_container.add(label.Label('Number of Members:', style=Pack(padding=(5, 0))))
            self.num_members_input = textinput.TextInput(style=Pack(padding=(0, 10), width=200))
            form_container.add(self.num_members_input)

            self.layout.add(form_container)

            # Buttons container
            button_container = box.Box(style=Pack(direction=COLUMN, padding=10))

            # Add Family button
            add_family_button = button.Button(
                'Add Family',
                on_press=self.add_family,
                style=Pack(padding=5, width=200)
            )
            button_container.add(add_family_button)

            # Back button
            back_button = button.Button(
                'Back',
                on_press=self.goto_main,
                style=Pack(padding=5, width=200)
            )
            button_container.add(back_button)

            self.layout.add(button_container)

            # Message container for errors or success messages
            self.message_container = box.Box(style=Pack(direction=COLUMN, padding=10))
            self.layout.add(self.message_container)

            print("AddFamilyScreen initialized successfully")

        except Exception as e:
            print(f"Error initializing AddFamilyScreen: {e}")

    def goto_main(self, sender):
        """Go back to the main screen."""
        try:
            # Update the trip list on the calling screen if available
            if self.caller_screen and hasattr(self.caller_screen, 'update_trip_list'):
                self.caller_screen.update_trip_list()

            # Navigate back to the main screen
            self.app.main_window.content = self.main_screen_layout
            print("Navigated back to the main screen")
        except Exception as e:
            print(f"Error navigating back to main screen: {e}")

    def add_family(self, sender):
        """Add a new family and navigate back."""
        try:
            family_name = self.family_name_input.value
            num_members = self.num_members_input.value

            # Validate inputs
            if not all([family_name, num_members]):
                self.show_error("Please fill in all fields")
                return

            # Save family details using the existing database instance
            self.database.save_family_details(family_name, int(num_members), 1)

            # Navigate back to the calling screen
            self.goto_main(sender)
        except Exception as e:
            self.show_error(f"Error adding family: {str(e)}")

    def show_error(self, message):
        """Show an error message."""
        self.message_container.clear()
        error_label = label.Label(
            message,
            style=Pack(padding=5, color='red', font_size=14)
        )
        self.message_container.add(error_label)

    def show_success(self, message):
        """Show a success message."""
        self.message_container.clear()
        success_label = label.Label(
            message,
            style=Pack(padding=5, color='green', font_size=14)
        )
        self.message_container.add(success_label)








