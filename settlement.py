from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import button, label, box
from database import ExpenseTracker


class SettlementScreen:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout
        self.expense_tracker = ExpenseTracker('expense_tracker.db')

        # Main container
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))

        # Header
        header_label = label.Label(
            'Expense Details',
            style=Pack(text_align='center', padding_top=50, font_size=20)
        )
        self.layout.add(header_label)

        # Expense details container
        self.expenses_container = box.Box(style=Pack(direction=COLUMN, padding=10))
        self.layout.add(self.expenses_container)

        # Buttons container
        button_container = box.Box(style=Pack(direction=ROW, padding=10))

        # Settlement Details button
        settlement_details_button = button.Button(
            'Settlement Details',
            style=Pack(padding=5, width=200)
        )
        settlement_details_button.on_press = self.goto_settlement_details
        button_container.add(settlement_details_button)

        # Back button
        back_button = button.Button(
            'Back to Main',
            style=Pack(padding=5, width=200)
        )
        back_button.on_press = self.goto_main
        button_container.add(back_button)

        self.layout.add(button_container)

        # Load expense details after UI is set up
        self.load_expense_details()

    def load_expense_details(self):
        """Load and display expense details with payer names."""
        try:
            # Get the active trip
            active_trip = self.expense_tracker.get_active_trip()
            if not active_trip:
                self.show_no_expenses_message()
                return

            trip_id = active_trip[0]
            expenses = self.expense_tracker.get_expenses_with_payer_name(trip_id)

            if not expenses:
                self.show_no_expenses_message()
            else:
                self.display_expenses(expenses)
        except Exception as e:
            self.show_error(f"Error loading expenses: {str(e)}")

    def show_no_expenses_message(self):
        """Display message when no expenses are available."""
        self.expenses_container.clear()
        no_expenses_label = label.Label(
            'No expenses available for this trip.',
            style=Pack(padding=10, text_align='center')
        )
        self.expenses_container.add(no_expenses_label)

    def display_expenses(self, expenses):
        """Display the list of expenses with payer names."""
        self.expenses_container.clear()

        # Add table headers
        header_box = box.Box(style=Pack(direction=ROW, padding=5))
        header_box.add(label.Label('Sl. No.', style=Pack(flex=1, padding=5, font_weight='bold')))
        header_box.add(label.Label('Date', style=Pack(flex=2, padding=5, font_weight='bold')))
        header_box.add(label.Label('Expense Item', style=Pack(flex=3, padding=5, font_weight='bold')))
        header_box.add(label.Label('Payer Family', style=Pack(flex=2, padding=5, font_weight='bold')))
        header_box.add(label.Label('Amount', style=Pack(flex=1, padding=5, font_weight='bold')))
        self.expenses_container.add(header_box)

        # Add expense rows
        for index, expense in enumerate(expenses, start=1):
            expense_box = box.Box(style=Pack(direction=ROW, padding=5))

            expense_box.add(label.Label(f'{index}', style=Pack(flex=1, padding=5)))
            expense_box.add(label.Label(f'{expense[4]}', style=Pack(flex=2, padding=5)))  # Date
            expense_box.add(label.Label(f'{expense[2]}', style=Pack(flex=3, padding=5)))  # Expense Item
            expense_box.add(label.Label(f'{expense[6]}', style=Pack(flex=2, padding=5)))  # Payer Family
            expense_box.add(label.Label(f'{expense[3]:.2f}', style=Pack(flex=1, padding=5)))  # Amount

            self.expenses_container.add(expense_box)

    def goto_settlement_details(self, sender):
        """Navigate to settlement details page."""
        from settlement_details import SettlementDetailsPage
        details_screen = SettlementDetailsPage(
            name='settlement_details',
            app=self.app,
            main_screen_layout=self.main_screen_layout
        )
        self.app.main_window.content = details_screen.layout

    def goto_main(self, sender):
        """Return to main screen."""
        self.app.main_window.content = self.main_screen_layout

    def show_error(self, message):
        """Show error message."""
        error_box = box.Box(style=Pack(direction=COLUMN, padding=10))
        error_label = label.Label(
            message,
            style=Pack(padding=5, color='red')
        )
        error_box.add(error_label)
        self.expenses_container.add(error_box)
