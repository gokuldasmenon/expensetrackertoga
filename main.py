from toga import App as Application, MainWindow
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import button, label, box

from expense_entry import ExpenseEntryScreen
from reporting import ReportingScreen
from settlement_details import SettlementDetailsPage
from settlement import SettlementScreen
from trips import TripListScreen, CreateTripScreen
from trip_history import TripHistoryScreen
from add_family import AddFamilyScreen


class MainScreen:
    def __init__(self, name, app):
        self.app = app
        self.name = name

        # Main layout
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))

        # Header
        header_label = label.Label(
            'Expense Tracker',
            style=Pack(
                text_align='center',
                padding_bottom=20,
                font_size=24,
                font_weight='bold'
            )
        )
        self.layout.add(header_label)

        # Tab buttons container
        tab_buttons = box.Box(style=Pack(direction=ROW, padding=10))

        # Add tab buttons
        tabs = [
            ('Current Trip', self.show_current_trip),
            ('Expenses', self.show_expenses),
            ('Settlements', self.show_settlements),
            ('Settlement Details', self.show_settlement_details),
            ('New Trip', self.show_new_trip),
            ('Trip History', self.show_trip_history),
            ('Reports', self.show_reports)
        ]

        for tab_name, tab_handler in tabs:
            tab_button = button.Button(
                tab_name,
                on_press=tab_handler,
                style=Pack(padding=5, flex=1)
            )
            tab_buttons.add(tab_button)

        self.layout.add(tab_buttons)

        # Content area
        self.content_area = box.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        self.layout.add(self.content_area)

        # Footer
        footer_label = label.Label(
            'Developed by GDN',
            style=Pack(
                text_align='center',
                padding_top=20,
                font_size=12
            )
        )
        self.layout.add(footer_label)

        # Show default page
        self.show_default_page()

    def clear_content_area(self):
        self.content_area.clear()

    def show_default_page(self):
        self.clear_content_area()
        default_content = box.Box(style=Pack(direction=COLUMN, padding=20))
        welcome_label = label.Label(
            'Welcome to Expense Tracker!',
            style=Pack(
                text_align='center',
                padding=20,
                font_size=20,
                font_weight='bold'
            )
        )
        instruction_label = label.Label(
            'Please select a tab above to get started.',
            style=Pack(
                text_align='center',
                padding=10
            )
        )
        default_content.add(welcome_label)
        default_content.add(instruction_label)
        self.content_area.add(default_content)

    def show_current_trip(self, sender):
        self.clear_content_area()
        current_trip_screen = TripListScreen('trip_list', self.app, self.layout)
        self.content_area.add(current_trip_screen.layout)

    # In main.py

    def show_settlements(self, sender):
        """Display the Settlements tab."""
        self.clear_content_area()

        # Create a container for settlements content
        settlements_container = box.Box(style=Pack(direction=COLUMN, padding=10))

        # Add buttons for different settlement views
        button_container = box.Box(style=Pack(direction=ROW, padding=10))

        # Settlement List button
        settlements_button = button.Button(
            'Settlement List',
            style=Pack(padding=5, flex=1)
        )
        settlements_button.on_press = self.show_settlement_list
        button_container.add(settlements_button)

        # Settlement Details button
        details_button = button.Button(
            'Settlement Details',
            style=Pack(padding=5, flex=1)
        )
        details_button.on_press = self.show_settlement_details
        button_container.add(details_button)

        settlements_container.add(button_container)

        # Add the container to content area
        self.content_area.add(settlements_container)

        # Show settlement list by default
        self.show_settlement_list(None)

    def show_settlement_list(self, sender):
        """Display the Settlement List view."""
        self.clear_content_area()
        settlements_screen = SettlementScreen(
            'settlements',
            self.app,
            self.layout  # Pass the main screen layout
        )
        self.content_area.add(settlements_screen.layout)

    def show_settlement_details(self, sender):
        """Display the Settlement Details view."""
        self.clear_content_area()
        settlement_details_screen = SettlementDetailsPage(
            'settlement_details',
            self.app,
            self.layout  # Pass the main screen layout
        )
        self.content_area.add(settlement_details_screen.layout)


    def show_settlement_details(self, sender):
        """Display the Settlement Details tab."""
        self.clear_content_area()
        settlement_details_screen = SettlementDetailsPage(
            'settlement_details',
            self.app,
            self.layout  # Pass the main screen layout
        )
        self.content_area.add(settlement_details_screen.layout)

    def show_expenses(self, sender):
        """Display the Expenses tab."""
        self.clear_content_area()
        try:
            expenses_screen = ExpenseEntryScreen('expenses', self.app, self.layout)  # Pass self.layout
            self.content_area.add(expenses_screen.scroll_container)  # Use scroll_container for scrollable content
        except Exception as e:
            # Show error message if screen fails to load
            error_box = box.Box(style=Pack(direction=COLUMN, padding=20))
            error_label = label.Label(
                f'Error loading Expenses screen: {str(e)}',
                style=Pack(padding=10, color='red')
            )
            error_box.add(error_label)
            self.content_area.add(error_box)



    def show_new_trip(self, sender):
        self.clear_content_area()
        new_trip_screen = CreateTripScreen('create_trip', self.app, self.layout)
        self.content_area.add(new_trip_screen.layout)

    def show_trip_history(self, sender):
        self.clear_content_area()
        trip_history_screen = TripHistoryScreen('trip_history', self.app, self.layout)
        self.content_area.add(trip_history_screen.layout)

    def show_reports(self, sender):
        self.clear_content_area()
        reports_screen = ReportingScreen('reporting', self.app, self.layout)
        self.content_area.add(reports_screen.layout)


class ExpenseTrackerApp(Application):
    def startup(self):
        # Use formal_name instead of name
        self.main_window = MainWindow(
            title=self.formal_name,  # Replace self.name with self.formal_name
            size=(1024, 768)  # Set initial window size
        )

        # Create the main screen and set it as the content
        main_screen = MainScreen('main', self)
        self.main_window.content = main_screen.layout

        # Show the window
        self.main_window.show()

        main_screen = MainScreen('main', self)
        self.main_window.content = main_screen.layout
        self.main_window.show()


def main():
    return ExpenseTrackerApp('Expense Tracker', 'org.example.expense_tracker')


if __name__ == '__main__':
    app = main()
    app.main_loop()
