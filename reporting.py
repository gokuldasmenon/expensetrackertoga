from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import button, label, box
from database import ExpenseTracker
import webbrowser


class ReportingScreen:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout

        # Main container
        self.layout = box.Box(style=Pack(direction=COLUMN, padding=20))

        # Header
        header_label = label.Label(
            'Trip Report',
            style=Pack(text_align='center', padding_top=50, font_size=20)
        )
        self.layout.add(header_label)

        # Main screen container
        self.main_screen = box.Box(style=Pack(direction=COLUMN, padding=10))
        self.layout.add(self.main_screen)

        # Footer buttons
        footer_buttons = box.Box(style=Pack(direction=ROW, padding=10))

        # Share Report button
        report_button = button.Button(
            'Share Report',
            style=Pack(padding=5, width=150)
        )
        report_button.on_press = self.generate_report
        footer_buttons.add(report_button)

        # Back button
        back_button = button.Button(
            'Back',
            style=Pack(padding=5, width=150)
        )
        back_button.on_press = self.goto_main
        footer_buttons.add(back_button)

        self.layout.add(footer_buttons)

        # Update the UI
        self.update_ui()

    def update_ui(self):
        """Update the UI with trip report data."""
        self.main_screen.clear()
        expense_tracker = ExpenseTracker('expense_tracker.db')
        active_trip = expense_tracker.get_active_trip()

        sections = [
            ("Trip Details", self.create_trip_details(expense_tracker, active_trip)),
            ("Family Details", self.create_family_details_table(expense_tracker, active_trip)),
            ("Expense Details", self.create_expenses_table(expense_tracker, active_trip)),
            ("Settlement Details", self.create_settlement_details_table(expense_tracker, active_trip))
        ]

        for title, content in sections:
            section = self.create_section(title, content)
            self.main_screen.add(section)

    def create_section(self, title, content):
        """Create a section with a title and content."""
        section = box.Box(style=Pack(direction=COLUMN, padding=10))
        title_label = label.Label(title, style=Pack(font_size=18, padding=(0, 10)))
        section.add(title_label)
        section.add(content)
        return section

    def create_trip_details(self, expense_tracker, active_trip):
        """Create trip details section."""
        layout = box.Box(style=Pack(direction=COLUMN))
        if active_trip:
            layout.add(label.Label(f'Trip Name: {active_trip[1]}', style=Pack(padding=(0, 10))))
            layout.add(label.Label(f'Start Date: {active_trip[2]}', style=Pack(padding=(0, 10))))
        else:
            layout.add(label.Label('No Active Trip', style=Pack(padding=(0, 10))))
        return layout

    def create_family_details_table(self, expense_tracker, active_trip):
        """Create family details section."""
        layout = box.Box(style=Pack(direction=COLUMN))
        if active_trip:
            family_details = expense_tracker.get_family_details()
            for family in family_details:
                layout.add(label.Label(f'Family Name: {family[1]}', style=Pack(padding=(0, 10))))
                layout.add(label.Label(f'Number of Members: {family[2]}', style=Pack(padding=(0, 10))))
        else:
            layout.add(label.Label('No Family Details', style=Pack(padding=(0, 10))))
        return layout

    def create_expenses_table(self, expense_tracker, active_trip):
        """Create expense details section."""
        layout = box.Box(style=Pack(direction=COLUMN))
        if active_trip:
            expenses = expense_tracker.get_expenses_with_payer_name(active_trip[0])
            for expense in expenses:
                layout.add(label.Label(f'Date: {expense[4]}', style=Pack(padding=(0, 10))))
                layout.add(label.Label(f'Expense Item: {expense[2]}', style=Pack(padding=(0, 10))))
                layout.add(label.Label(f'Payer Family: {expense[6]}', style=Pack(padding=(0, 10))))
                layout.add(label.Label(f'Amount: {expense[3]}', style=Pack(padding=(0, 10))))
        else:
            layout.add(label.Label('No Expense Details', style=Pack(padding=(0, 10))))
        return layout

    def create_settlement_details_table(self, expense_tracker, active_trip):
        """Create settlement details section."""
        layout = box.Box(style=Pack(direction=COLUMN))
        if active_trip:
            settlements = expense_tracker.settle_expenses(active_trip[0])
            for settlement in settlements:
                layout.add(label.Label(f'Payer: {settlement[0]}', style=Pack(padding=(0, 10))))
                layout.add(label.Label(f'Receiver: {settlement[1]}', style=Pack(padding=(0, 10))))
                layout.add(label.Label(f'Amount: {settlement[2]}', style=Pack(padding=(0, 10))))
        else:
            layout.add(label.Label('No Settlement Details', style=Pack(padding=(0, 10))))
        return layout

    def generate_report(self, sender):
        """Generate and share the trip report."""
        expense_tracker = ExpenseTracker('expense_tracker.db')
        active_trip = expense_tracker.get_active_trip()
        if not active_trip:
            print("No active trip to generate a report.")
            return

        report_content = (
            f"◆ TRIP EXPENSE REPORT ◆\n"
            f"Trip Name: {active_trip[1]}\n"
            f"Start Date: {active_trip[2]}\n\n"
            "◆ FAMILY DETAILS ◆\n"
        )

        family_details = expense_tracker.get_family_details()
        if family_details:
            family_lines = [f"{family[1]}: {family[2]} members" for family in family_details]
            report_content += "\n".join(family_lines) + "\n\n"

        expenses = expense_tracker.get_expenses_with_payer_name(active_trip[0])
        total_amount = sum(expense[3] for expense in expenses)

        report_content += f"◆ EXPENSE DETAILS (Total: {total_amount:.2f}) ◆\n"
        if expenses:
            for expense in expenses:
                report_content += (
                    f"{expense[4]}: {expense[2]} (Paid by {expense[6]}): {expense[3]:.2f}\n"
                )

        settlements = expense_tracker.settle_expenses(active_trip[0])
        report_content += "\n◆ SETTLEMENT DETAILS ◆\n"
        if settlements:
            for settlement in settlements:
                report_content += f"{settlement[0]} → {settlement[1]}: {settlement[2]:.2f}\n"

        report_content += "\n◆ Generated using Trip Expense Tracker ◆"

        # Share the report via WhatsApp
        whatsapp_url = f"https://wa.me/?text={report_content}"
        webbrowser.open(whatsapp_url)

    def goto_main(self, sender):
        """Return to main screen."""
        self.app.main_window.content = self.main_screen_layout
