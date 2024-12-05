from toga.style import Pack
from toga.style.pack import COLUMN
from toga.widgets import box, button, label, table
from .database import ExpenseTracker
from .settlement import SettlementScreen



class SettlementDetailsPage:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout
        self.database = app.database

        # Main container
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=10))

        # Header
        header_label = label.Label(
            'Settlement Details',
            style=Pack(text_align='center', padding_top=10, font_size=18, font_weight='bold')
        )
        self.layout.add(header_label)

        # Trip name and total expense labels
        self.trip_name_label = label.Label('Trip Name: Loading...', style=Pack(padding=5))
        self.layout.add(self.trip_name_label)

        self.total_label = label.Label('Total Expense: Loading...', style=Pack(padding=5))
        self.layout.add(self.total_label)

        # Cost summary table
        self.cost_summary_table = table.Table(
            headings=['Family Count', 'Individual Count', 'Per Head Cost'],
            style=Pack(padding=5)
        )
        self.layout.add(self.cost_summary_table)

        # Settlement details table
        self.settlement_details_table = table.Table(
            headings=['Payer', 'Receiver', 'Amount'],
            style=Pack(padding=5)
        )
        self.layout.add(self.settlement_details_table)

        # Back button
        back_button = button.Button(
            'Back',
            on_press=self.goto_settlement_page,
            style=Pack(padding=5, width=150)
        )
        self.layout.add(back_button)

        # Update UI with data
        self.update_ui()

    def update_ui(self):
        """Update the UI with trip and settlement details."""
        try:
            active_trip = self.database.get_active_trip()

            if active_trip:
                # Update trip name and total expense
                self.trip_name_label.text = f'Trip Name: {active_trip[1]}'
                total_expenses = self.database.get_total_expenses(active_trip[0])
                self.total_label.text = (
                    f'Total Expense: {total_expenses:.2f}' if total_expenses else 'No Expenses Added Yet'
                )

                # Update tables
                self.update_cost_summary_table(active_trip[0])
                self.update_settlement_details_table(active_trip[0])
            else:
                self.trip_name_label.text = 'No Active Trip'
                self.total_label.text = 'No Expenses Added Yet'

        except Exception as e:
            print(f"Error updating UI: {e}")
            self.show_error(f"Error updating UI: {str(e)}")

    def update_cost_summary_table(self, active_trip_id):
        """Update the cost summary table."""
        try:
            self.cost_summary_table.data = []
            families = self.database.get_family_count(active_trip_id)
            total_members = self.database.get_total_members(active_trip_id)
            total_expenses = self.database.get_total_expenses(active_trip_id)

            if total_expenses is None or total_members is None or total_members == 0:
                per_head_cost = 'N/A'
            else:
                per_head_cost = f'{total_expenses / total_members:.2f}'

            self.cost_summary_table.data.append([families, total_members, per_head_cost])

        except Exception as e:
            print(f"Error updating cost summary table: {e}")
            self.show_error(f"Error updating cost summary: {str(e)}")

    def update_settlement_details_table(self, active_trip_id):
        """Update the settlement details table."""
        try:
            self.settlement_details_table.data = []
            settlements = self.database.settle_expenses(active_trip_id)

            for payer, receiver, amount in settlements:
                self.settlement_details_table.data.append([payer, receiver, f'{amount:.2f}'])

        except Exception as e:
            print(f"Error updating settlement details table: {e}")
            self.show_error(f"Error updating settlement details: {str(e)}")

    def goto_settlement_page(self, sender):
        """Navigate back to the SettlementScreen."""
        self.app.main_window.content = SettlementScreen('settlement', self.app, self.main_screen_layout).layout

    def show_error(self, message):
        """Show error message."""
        error_box = box.Box(style=Pack(direction=COLUMN, padding=5))
        error_label = label.Label(
            message,
            style=Pack(padding=5, color='red')
        )
        error_box.add(error_label)
        self.layout.add(error_box)
