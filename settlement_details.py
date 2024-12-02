from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import box, button, label, table

from database import ExpenseTracker
from settlement import SettlementScreen


class SettlementDetailsPage:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout
        self.layout = box.Box(style=Pack(direction=COLUMN))

        # Header
        header_label = label.Label('Settlement Details', style=Pack(text_align='center', padding_top=50))
        self.layout.add(header_label)

        # Trip name and total expense labels
        self.trip_name_label = label.Label('Trip Name: Loading...', style=Pack(padding=10))
        self.layout.add(self.trip_name_label)

        self.total_label = label.Label('Total Expense: Loading...', style=Pack(padding=10))
        self.layout.add(self.total_label)

        # Cost summary table
        self.cost_summary_table = table.Table(['Family Count', 'Individual Count', 'Per Head Cost'],
                                              style=Pack(padding=10))
        self.layout.add(self.cost_summary_table)

        # Settlement details table
        self.settlement_details_table = table.Table(['Payer', 'Receiver', 'Amount'], style=Pack(padding=10))
        self.layout.add(self.settlement_details_table)

        # Back button
        back_button = button.Button('Back', style=Pack(padding=10))
        back_button.on_press = self.goto_settlement_page
        self.layout.add(back_button)

        # Update UI with data
        self.update_ui()

    def update_ui(self):
        """Update the UI with trip and settlement details."""
        expense_tracker = ExpenseTracker('expense_tracker.db')
        active_trip = expense_tracker.get_active_trip()

        if active_trip:
            # Update trip name and total expense
            self.trip_name_label.text = f'Trip Name: {active_trip[1]}'
            total_expenses = expense_tracker.get_total_expenses(active_trip[0])
            self.total_label.text = (
                f'Total Expense: {total_expenses:.2f}' if total_expenses else 'No Expenses Added Yet'
            )

            # Update tables
            self.update_cost_summary_table(expense_tracker, active_trip[0])
            self.update_settlement_details_table(expense_tracker, active_trip[0])

    def update_cost_summary_table(self, expense_tracker, active_trip_id):
        """Update the cost summary table."""
        self.cost_summary_table.data = []
        families = expense_tracker.get_family_count(active_trip_id)
        total_members = expense_tracker.get_total_members(active_trip_id)
        total_expenses = expense_tracker.get_total_expenses(active_trip_id)

        if total_expenses is None or total_members is None or total_members == 0:
            per_head_cost = 0.0
            per_head_cost_message = 'No Expenses or No Members'
        else:
            per_head_cost = total_expenses / total_members
            per_head_cost_message = f'{per_head_cost:.2f}'

        self.cost_summary_table.data.append([families, total_members, per_head_cost_message])

    def update_settlement_details_table(self, expense_tracker, active_trip_id):
        """Update the settlement details table."""
        self.settlement_details_table.data = []
        settlements = expense_tracker.settle_expenses(active_trip_id)  # Ensure this method is implemented

        for payer, receiver, amount in settlements:
            self.settlement_details_table.data.append([payer, receiver, f'{amount:.2f}'])

    def goto_settlement_page(self, sender):
        """Navigate back to the SettlementScreen."""
        self.app.main_window.content = SettlementScreen('settlement', self.app, self.main_screen_layout).layout
