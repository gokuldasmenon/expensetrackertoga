from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import button, label, textinput, box
from toga.widgets.label import Label
from database import ExpenseTracker


class TripListScreen:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout  # Store the main screen layout
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))

        # Header
        header_label = label.Label(
            'Current trip details',
            style=Pack(text_align='center', padding_top=50)
        )
        self.layout.add(header_label)

        # Trip list container
        self.trip_list_container = box.Box(style=Pack(direction=COLUMN, padding=10))
        self.layout.add(self.trip_list_container)
        self.update_trip_list()

        # Buttons container
        button_container = box.Box(style=Pack(direction=COLUMN, padding=10))

        add_family_button = button.Button(
            'Add Family',
            style=Pack(padding=5, width=200)
        )
        add_family_button.on_press = self.goto_add_family
        button_container.add(add_family_button)

        # back_button = button.Button(
        #     'Back',
        #     style=Pack(padding=5, width=200)
        # )
        # back_button.on_press = self.goto_main
        # button_container.add(back_button)

        self.layout.add(button_container)

    def update_trip_list(self):
        self.trip_list_container.clear()
        expense_tracker = ExpenseTracker('expense_tracker.db')
        trips = expense_tracker.get_trips()

        for trip in trips:
            # Main trip box
            trip_box = box.Box(style=Pack(direction=COLUMN, padding=10))

            # Trip details section
            trip_details = box.Box(style=Pack(direction=COLUMN, padding=5))
            trip_details.add(label.Label(
                f'Current Trip Name: {trip[1]}',
                style=Pack(padding=(0, 10), font_weight='bold')
            ))
            trip_details.add(label.Label(
                f'Trip Type: {trip[3]}',
                style=Pack(padding=(0, 10))
            ))
            trip_details.add(label.Label(
                f'Start Date: {trip[2]}',
                style=Pack(padding=(0, 10))
            ))
            trip_box.add(trip_details)

            # Family section header
            family_header = label.Label(
                'Family Details',
                style=Pack(padding=(10, 5), font_weight='bold', font_size=16)
            )
            trip_box.add(family_header)

            # Family details section
            family_details = expense_tracker.get_family_details()
            for family in family_details:
                # Container for each family
                family_box = box.Box(style=Pack(direction=COLUMN, padding=5))

                # Family details row
                family_row = box.Box(style=Pack(direction=ROW, padding=5))

                # Family name input
                name_input = textinput.TextInput(
                    value=family[1],
                    style=Pack(padding=(0, 5), width=150)
                )
                family_row.add(name_input)

                # Members count input
                members_input = textinput.TextInput(
                    value=str(family[2]),
                    style=Pack(padding=(0, 5), width=100)
                )
                family_row.add(members_input)

                # Buttons container
                button_box = box.Box(style=Pack(direction=ROW, padding=5))

                # Save button
                save_button = button.Button(
                    'Save',
                    style=Pack(padding=(0, 5), width=80)
                )
                save_button.on_press = lambda x, f=family[0], n=name_input, m=members_input: self.save_family_changes(
                    x, f, n.value, m.value
                )
                button_box.add(save_button)

                # Delete button
                delete_button = button.Button(
                    'Delete',
                    style=Pack(padding=(0, 5), width=80)
                )
                delete_button.on_press = lambda x, f=family[0]: self.delete_family(x, f)
                button_box.add(delete_button)

                family_row.add(button_box)
                family_box.add(family_row)
                trip_box.add(family_box)

            self.trip_list_container.add(trip_box)

    def save_family_changes(self, sender, family_id, new_name, new_members):
        """Save changes to family details"""
        try:
            expense_tracker = ExpenseTracker('expense_tracker.db')
            expense_tracker.update_family_record(family_id, new_name, int(new_members))
            self.show_success("Family details updated successfully!")
            self.update_trip_list()  # Refresh the list
        except Exception as e:
            self.show_error(f"Error updating family details: {str(e)}")

    def delete_family(self, sender, family_id):
        """Delete a family record"""
        try:
            # Show confirmation dialog
            confirm_box = box.Box(style=Pack(direction=COLUMN, padding=10))
            confirm_box.add(label.Label(
                'Are you sure you want to delete this family record?',
                style=Pack(padding=10)
            ))

            button_box = box.Box(style=Pack(direction=ROW, padding=5))

            def confirm_delete(s):
                expense_tracker = ExpenseTracker('expense_tracker.db')
                expense_tracker.delete_family_record(family_id)
                self.show_success("Family deleted successfully!")
                self.update_trip_list()

            yes_button = button.Button(
                'Yes',
                style=Pack(padding=5, width=80)
            )
            yes_button.on_press = confirm_delete

            no_button = button.Button(
                'No',
                style=Pack(padding=5, width=80)
            )
            no_button.on_press = lambda x: self.update_trip_list()

            button_box.add(yes_button)
            button_box.add(no_button)
            confirm_box.add(button_box)

            self.trip_list_container.add(confirm_box)

        except Exception as e:
            self.show_error(f"Error deleting family: {str(e)}")

    def show_success(self, message):
        """Show success message"""
        success_box = box.Box(style=Pack(direction=COLUMN, padding=10))
        success_label = label.Label(
            message,
            style=Pack(padding=5, color='green')
        )
        success_box.add(success_label)
        self.trip_list_container.add(success_box)

    def show_error(self, message):
        """Show error message"""
        error_box = box.Box(style=Pack(direction=COLUMN, padding=10))
        error_label = label.Label(
            message,
            style=Pack(padding=5, color='red')
        )
        error_box.add(error_label)
        self.trip_list_container.add(error_box)

    def goto_add_family(self, sender):
        self.app.main_window.content = AddFamilyScreen('add_family', self.app, self.main_screen_layout).layout


class CreateTripScreen:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout  # Store the main screen layout
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))

        # Header
        header_label = label.Label(
            'Create Trip',
            style=Pack(text_align='center', padding_top=50)
        )
        self.layout.add(header_label)

        # Form container
        form_container = box.Box(style=Pack(direction=COLUMN, padding=10))

        # Trip name input
        trip_name_label = label.Label('Trip Name:', style=Pack(padding=(5, 0)))
        form_container.add(trip_name_label)
        self.trip_name_input = textinput.TextInput(style=Pack(padding=(0, 10), width=200))
        form_container.add(self.trip_name_input)

        # Trip start date input
        trip_start_date_label = label.Label(
            'Trip Start Date (YYYY-MM-DD):',
            style=Pack(padding=(5, 0))
        )
        form_container.add(trip_start_date_label)
        self.trip_start_date_input = textinput.TextInput(style=Pack(padding=(0, 10), width=200))
        form_container.add(self.trip_start_date_input)

        self.layout.add(form_container)

        # Buttons container
        button_container = box.Box(style=Pack(direction=COLUMN, padding=10))

        create_trip_button = button.Button(
            'Create Trip',
            style=Pack(padding=5, width=200)
        )
        create_trip_button.on_press = self.create_trip
        button_container.add(create_trip_button)

        back_button = button.Button(
            'Back',
            style=Pack(padding=5, width=200)
        )
        back_button.on_press = self.goto_main
        button_container.add(back_button)

        self.layout.add(button_container)

    def goto_main(self, sender):
        """Go back to the main screen."""
        self.app.main_window.content = self.main_screen_layout

    def create_trip(self, sender):
        trip_name = self.trip_name_input.value
        trip_start_date = self.trip_start_date_input.value
        expense_tracker = ExpenseTracker('expense_tracker.db')

        if expense_tracker.get_active_trip():
            error_box = box.Box(style=Pack(direction=COLUMN, padding=20))
            error_box.add(label.Label(
                'Only one active trip is allowed.',
                style=Pack(padding=10)
            ))
            self.app.main_window.content = error_box
        else:
            expense_tracker.clear_family_details()
            expense_tracker.save_trip(trip_name, trip_start_date, 'Family', None, None, 0)
            self.app.main_window.content = AddFamilyScreen('add_family', self.app, self.main_screen_layout).layout


class TripHistoryScreen:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout  # Store the main screen layout
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))

        # Header
        header_label = label.Label(
            'Trip History',
            style=Pack(text_align='center', padding_top=50)
        )
        self.layout.add(header_label)

        # History container
        self.history_container = box.Box(style=Pack(direction=COLUMN, padding=10))
        self.layout.add(self.history_container)
        self.load_history()

        # Back button
        # back_button = button.Button(
        #     'Back',
        #     style=Pack(padding=5, width=200)
        # )
        # back_button.on_press = self.goto_main
        # self.layout.add(back_button)

    def load_history(self):
        self.history_container.clear()
        expense_tracker = ExpenseTracker('expense_tracker.db')
        expense_tracker.cursor.execute("SELECT trip_name, archive_path, archived_date FROM archived_trips")
        archived_trips = expense_tracker.cursor.fetchall()

        for trip_name, archive_path, archived_date in archived_trips:
            trip_box = box.Box(style=Pack(direction=ROW, padding=5))

            trip_box.add(label.Label(
                f"{trip_name} ({archive_path}) - {archived_date}",
                style=Pack(flex=1, padding=5)
            ))

            button_box = box.Box(style=Pack(direction=ROW, padding=5))
            load_button = button.Button(
                'Load',
                style=Pack(padding=(0, 5))
            )
            load_button.on_press = lambda x, path=archive_path: self.load_archive(path)

            delete_button = button.Button(
                'Delete',
                style=Pack(padding=(0, 5))
            )
            delete_button.on_press = lambda x, path=archive_path: self.delete_archive(path)

            button_box.add(load_button)
            button_box.add(delete_button)
            trip_box.add(button_box)

            self.history_container.add(trip_box)

    # def goto_main(self, sender):
    #     """Go back to the main screen."""
    #     self.app.main_window.content = self.main_screen_layout


class AddFamilyScreen:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout  # Store the main screen layout
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))

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
        self.app.main_window.content = self.main_screen_layout

    def add_family(self, sender):
        family_name = self.family_name_input.value
        num_members = self.num_members_input.value
        expense_tracker = ExpenseTracker('expense_tracker.db')
        expense_tracker.save_family_details(family_name, num_members, 1)
        self.app.main_window.content = CreateTripScreen('create_trip', self.app, self.main_screen_layout).layout
