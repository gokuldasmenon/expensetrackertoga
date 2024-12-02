import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from database import ExpenseTracker
from datetime import datetime


class ExpenseEntryScreen:
    def __init__(self, name, app, main_screen_layout):
        self.app = app
        self.name = name
        self.main_screen_layout = main_screen_layout

        # Create a scrollable container
        self.scroll_container = toga.ScrollContainer(style=Pack(flex=1))

        # Main container inside the scrollable container
        self.scrollable_content = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))

        # Header
        header_label = toga.Label(
            'Expense Entry',
            style=Pack(text_align='center', padding_top=20, font_size=20)
        )
        self.scrollable_content.add(header_label)

        # Form container
        form_container = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Expense Name input
        expense_name_label = toga.Label('Expense Name:', style=Pack(padding=(5, 0)))
        form_container.add(expense_name_label)
        self.expense_name_input = toga.TextInput(style=Pack(padding=(0, 10), width=200))
        form_container.add(self.expense_name_input)

        # Expense Amount input
        expense_amount_label = toga.Label('Expense Amount:', style=Pack(padding=(5, 0)))
        form_container.add(expense_amount_label)
        self.expense_amount_input = toga.TextInput(style=Pack(padding=(0, 10), width=200))
        form_container.add(self.expense_amount_input)

        # Expense Date input with today's date
        expense_date_label = toga.Label('Expense Date:', style=Pack(padding=(5, 0)))
        form_container.add(expense_date_label)
        today_date = datetime.now().strftime('%Y-%m-%d')
        self.expense_date_input = toga.TextInput(
            value=today_date,
            style=Pack(padding=(0, 10), width=200)
        )
        form_container.add(self.expense_date_input)

        # Payer Name dropdown
        payer_name_label = toga.Label('Payer Name:', style=Pack(padding=(5, 0)))
        form_container.add(payer_name_label)

        # Get family names from database
        expense_tracker = ExpenseTracker('expense_tracker.db')
        family_details = expense_tracker.get_family_details()
        self.family_names = [family[1] for family in family_details]  # Store family names as an instance variable

        # Use Selection widget for dropdown
        self.payer_name_input = toga.Selection(
            items=self.family_names,
            style=Pack(padding=(0, 10), width=200)
        )
        # Set a default value if family names exist
        if self.family_names:
            self.payer_name_input.value = self.family_names[0]  # Default to the first family name
        form_container.add(self.payer_name_input)

        self.scrollable_content.add(form_container)

        # Buttons container
        button_container = toga.Box(style=Pack(direction=ROW, padding=10))

        # Save button
        save_expense_button = toga.Button(
            'Save Expense',
            style=Pack(padding=5, width=200)
        )
        save_expense_button.on_press = self.save_expense
        button_container.add(save_expense_button)

        # Back button
        back_button = toga.Button(
            'Back',
            style=Pack(padding=5, width=200)
        )
        back_button.on_press = self.goto_main
        button_container.add(back_button)

        self.scrollable_content.add(button_container)

        # Expense list container
        self.expense_list_container = toga.Box(style=Pack(direction=COLUMN, padding=10))
        self.scrollable_content.add(self.expense_list_container)
        self.update_expense_list()

        # Add the scrollable content to the scroll container
        self.scroll_container.content = self.scrollable_content

    def goto_main(self, sender):
        self.app.main_window.content = self.main_screen_layout

    def save_expense(self, sender):
        try:
            expense_name = self.expense_name_input.value
            expense_amount = self.expense_amount_input.value
            expense_date = self.expense_date_input.value
            payer_name = self.payer_name_input.value

            if not all([expense_name, expense_amount, expense_date, payer_name]):
                self.show_error("Please fill in all fields")
                return

            try:
                # Validate amount is a number
                float(expense_amount)
            except ValueError:
                self.show_error("Amount must be a valid number")
                return

            # Validate date format
            try:
                datetime.strptime(expense_date, '%Y-%m-%d')
            except ValueError:
                self.show_error("Date must be in YYYY-MM-DD format")
                return

            expense_tracker = ExpenseTracker('expense_tracker.db')
            expense_tracker.save_expense(1, expense_name, expense_amount, expense_date, 1)

            # Clear inputs after successful save
            self.expense_name_input.value = ''
            self.expense_amount_input.value = ''
            self.expense_date_input.value = datetime.now().strftime('%Y-%m-%d')
            self.payer_name_input.value = self.family_names[0] if self.family_names else None

            self.update_expense_list()
            self.show_success("Expense saved successfully!")

        except Exception as e:
            self.show_error(f"Error saving expense: {str(e)}")

    def update_expense_list(self):
        self.expense_list_container.clear()
        expense_tracker = ExpenseTracker('expense_tracker.db')
        expenses = expense_tracker.get_expenses(1)

        for expense in expenses:
            # Create container for each expense
            expense_box = toga.Box(style=Pack(direction=COLUMN, padding=5, background_color='#f0f0f0'))

            # Expense details
            details_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            details_box.add(toga.Label(
                f'Expense Name: {expense[2]}',
                style=Pack(padding=(0, 5))
            ))
            details_box.add(toga.Label(
                f'Expense Amount: {expense[3]}',
                style=Pack(padding=(0, 5))
            ))
            details_box.add(toga.Label(
                f'Expense Date: {expense[4]}',
                style=Pack(padding=(0, 5))
            ))
            expense_box.add(details_box)

            # Delete button
            delete_button = toga.Button(
                'Delete',
                style=Pack(padding=5, width=100)
            )
            delete_button.on_press = lambda x, expense_id=expense[0]: self.delete_expense(expense_id)
            expense_box.add(delete_button)

            self.expense_list_container.add(expense_box)

    def delete_expense(self, expense_id):
        try:
            expense_tracker = ExpenseTracker('expense_tracker.db')
            expense_tracker.delete_expense(expense_id)
            self.update_expense_list()
            self.show_success("Expense deleted successfully!")
        except Exception as e:
            self.show_error(f"Error deleting expense: {str(e)}")

    def show_error(self, message):
        """Show error message"""
        error_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        error_label = toga.Label(
            message,
            style=Pack(padding=5, color='red')
        )
        error_box.add(error_label)
        self.scrollable_content.add(error_box)

    def show_success(self, message):
        """Show success message"""
        success_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        success_label = toga.Label(
            message,
            style=Pack(padding=5, color='green')
        )
        success_box.add(success_label)
        self.scrollable_content.add(success_box)
