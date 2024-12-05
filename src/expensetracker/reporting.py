from toga.widgets import button, label, box
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import webbrowser


class ReportingScreen:
    def __init__(self, name, app, main_screen_layout):
        try:
            print("Initializing ReportingScreen...")
            self.app = app
            self.name = name
            self.main_screen_layout = main_screen_layout

            # Use the existing database instance from the app
            if not hasattr(self.app, 'database'):
                raise AttributeError("App instance does not have a 'database' attribute.")
            self.database = self.app.database
            print("Database instance accessed")

            # Main container
            self.layout = box.Box(style=Pack(direction=COLUMN, padding=10))

            # Header
            header_label = label.Label(
                'Trip Report',
                style=Pack(text_align='center', padding_top=10, font_size=18)
            )
            self.layout.add(header_label)

            # Main screen container
            self.main_screen = box.Box(style=Pack(direction=COLUMN, padding=5))
            self.layout.add(self.main_screen)

            # Footer buttons
            footer_buttons = box.Box(style=Pack(direction=ROW, padding=5))

            # Share Report button
            report_button = button.Button(
                'Share Report',
                on_press=self.generate_report,
                style=Pack(padding=3, width=150)
            )
            footer_buttons.add(report_button)

            # Back button
            back_button = button.Button(
                'Back',
                on_press=self.goto_main,
                style=Pack(padding=3, width=150)
            )
            footer_buttons.add(back_button)

            self.layout.add(footer_buttons)

            # Update the UI with current data
            self.update_ui()
            print("ReportingScreen initialized successfully")

        except Exception as e:
            print(f"Error initializing ReportingScreen: {e}")
            self.show_error(f"Error initializing screen: {str(e)}")

    def update_ui(self):
        """Update the UI with trip report data."""
        try:
            print("Updating UI...")
            self.main_screen.clear()

            # Get active trip using the existing database instance
            active_trip = self.database.get_active_trip()
            if not active_trip:
                self.show_error("No active trip found")
                return

            # Create and add sections
            sections = [
                ("Trip Details", self.create_trip_details(active_trip)),
                ("Family Details", self.create_family_details_table(active_trip)),
                ("Expense Details", self.create_expenses_table(active_trip)),
                ("Settlement Details", self.create_settlement_details_table(active_trip))
            ]

            for title, content in sections:
                section = self.create_section(title, content)
                self.main_screen.add(section)

            print("UI updated successfully")

        except Exception as e:
            print(f"Error updating UI: {e}")
            self.show_error(f"Error updating report: {str(e)}")

    def create_section(self, title, content):
        """Create a section with a title and content."""
        section = box.Box(style=Pack(direction=COLUMN, padding=5))
        title_label = label.Label(
            title,
            style=Pack(font_size=16, padding=(5, 5), font_weight='bold')
        )
        section.add(title_label)
        section.add(content)
        return section

    def create_trip_details(self, active_trip):
        """Create trip details section."""
        layout = box.Box(style=Pack(direction=COLUMN, padding=5))
        if active_trip:
            layout.add(label.Label(
                f'Trip Name: {active_trip[1]}',
                style=Pack(padding=(2, 5), font_size=14)
            ))
            layout.add(label.Label(
                f'Start Date: {active_trip[2]}',
                style=Pack(padding=(2, 5), font_size=14)
            ))
        else:
            layout.add(label.Label(
                'No Active Trip',
                style=Pack(padding=(2, 5), font_size=14, color='red')
            ))
        return layout

    def create_family_details_table(self, active_trip):
        """Create family details section."""
        layout = box.Box(style=Pack(direction=COLUMN, padding=5))
        if active_trip:
            family_details = self.database.get_family_details()
            for family in family_details:
                layout.add(label.Label(
                    f'Family: {family[1]}',
                    style=Pack(padding=(2, 2), font_size=14)
                ))
                layout.add(label.Label(
                    f'Members: {family[2]}',
                    style=Pack(padding=(2, 2), font_size=14)
                ))
        else:
            layout.add(label.Label(
                'No Family Details',
                style=Pack(padding=(2, 5), font_size=14)
            ))
        return layout

    def create_expenses_table(self, active_trip):
        """Create expense details section."""
        layout = box.Box(style=Pack(direction=COLUMN, padding=5))
        if active_trip:
            expenses = self.database.get_expenses_with_payer_name(active_trip[0])
            if not expenses:
                layout.add(label.Label(
                    'No Expense Details',
                    style=Pack(padding=(2, 5), font_size=14)
                ))
                return layout

            total_amount = sum(expense[3] for expense in expenses)
            layout.add(label.Label(
                f'Total Expenses: {total_amount:.2f}',
                style=Pack(padding=(2, 5), font_size=14, font_weight='bold')
            ))

            for expense in expenses:
                layout.add(label.Label(
                    f'{expense[2]} - {expense[3]:.2f} (Paid by {expense[6]})',
                    style=Pack(padding=(2, 2), font_size=14)
                ))
        else:
            layout.add(label.Label(
                'No Expense Details',
                style=Pack(padding=(2, 5), font_size=14)
            ))
        return layout

    def create_settlement_details_table(self, active_trip):
        """Create settlement details section."""
        layout = box.Box(style=Pack(direction=COLUMN, padding=5))
        if active_trip:
            settlements = self.database.settle_expenses(active_trip[0])
            if not settlements:
                layout.add(label.Label(
                    'No Settlement Details',
                    style=Pack(padding=(2, 5), font_size=14)
                ))
                return layout

            for settlement in settlements:
                layout.add(label.Label(
                    f'{settlement[0]} → {settlement[1]}: {settlement[2]:.2f}',
                    style=Pack(padding=(2, 2), font_size=14)
                ))
        else:
            layout.add(label.Label(
                'No Settlement Details',
                style=Pack(padding=(2, 5), font_size=14)
            ))
        return layout

    def generate_report(self, sender):
        """Generate and share the trip report."""
        try:
            active_trip = self.database.get_active_trip()
            if not active_trip:
                self.show_error("No active trip to generate a report.")
                return

            # Generate report content
            report_content = self.create_report_content(active_trip)

            # Share the report via WhatsApp
            whatsapp_url = f"https://wa.me/?text={report_content}"
            webbrowser.open(whatsapp_url)
            print("Report shared successfully")

        except Exception as e:
            print(f"Error generating report: {e}")
            self.show_error(f"Error generating report: {str(e)}")

    def create_report_content(self, active_trip):
        """Create the report content string."""
        try:
            report_lines = [
                "◆ TRIP EXPENSE REPORT ◆",
                f"Trip Name: {active_trip[1]}",
                f"Start Date: {active_trip[2]}",
                "",
                "◆ FAMILY DETAILS ◆"
            ]

            # Add family details
            family_details = self.database.get_family_details()
            if family_details:
                for family in family_details:
                    report_lines.append(f"{family[1]}: {family[2]} members")

            # Add expense details
            expenses = self.database.get_expenses_with_payer_name(active_trip[0])
            total_amount = sum(expense[3] for expense in expenses)
            report_lines.extend([
                "",
                f"◆ EXPENSE DETAILS (Total: {total_amount:.2f}) ◆"
            ])

            if expenses:
                for expense in expenses:
                    report_lines.append(
                        f"{expense[4]}: {expense[2]} (Paid by {expense[6]}): {expense[3]:.2f}"
                    )

            # Add settlement details
            settlements = self.database.settle_expenses(active_trip[0])
            report_lines.extend([
                "",
                "◆ SETTLEMENT DETAILS ◆"
            ])

            if settlements:
                for settlement in settlements:
                    report_lines.append(
                        f"{settlement[0]} → {settlement[1]}: {settlement[2]:.2f}"
                    )

            report_lines.extend([
                "",
                "◆ Generated using Trip Expense Tracker ◆"
            ])

            return "\n".join(report_lines)

        except Exception as e:
            print(f"Error creating report content: {e}")
            raise

    def show_error(self, message):
        """Show error message."""
        self.main_screen.add(label.Label(
            message,
            style=Pack(padding=5, color='red', font_size=14)
        ))

    def goto_main(self, sender):
        """Return to main screen."""
        try:
            self.app.main_window.content = self.main_screen_layout
        except Exception as e:
            print(f"Error returning to main screen: {e}")
