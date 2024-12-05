import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .database import ExpenseTracker
from datetime import datetime


class ExpenseEntryScreen:
    def __init__(self, name, app, main_screen_layout):
        try:
            print("Initializing ExpenseEntryScreen...")
            self.app = app
            self.name = name
            self.main_screen_layout = main_screen_layout

            # Access the database instance from the app
            if not hasattr(self.app, 'database'):
                raise AttributeError("App instance does not have a 'database' attribute")
            self.database = self.app.database

            # Create a scrollable container
            self.scroll_container = toga.ScrollContainer(style=Pack(flex=1))
            self.scrollable_content = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))

            # Header
            header_label = toga.Label(
                'Expense Entry',
                style=Pack(text_align='center', padding_top=10, font_size=18)
            )
            self.scrollable_content.add(header_label)

            # Form container
            form_container = toga.Box(style=Pack(direction=COLUMN, padding=5))

            # Expense Name input
            form_container.add(toga.Label('Expense Name:', style=Pack(padding=(2, 0))))
            self.expense_name_input = toga.TextInput(style=Pack(padding=(0, 5), width=180))
            form_container.add(self.expense_name_input)

            # Expense Amount input
            form_container.add(toga.Label('Expense Amount:', style=Pack(padding=(2, 0))))
            self.expense_amount_input = toga.TextInput(style=Pack(padding=(0, 5), width=180))
            form_container.add(self.expense_amount_input)

            # Expense Date input
            form_container.add(toga.Label('Expense Date:', style=Pack(padding=(2, 0))))
            today_date = datetime.now().strftime('%Y-%m-%d')
            self.expense_date_input = toga.TextInput(
                value=today_date,
                style=Pack(padding=(0, 5), width=180)
            )
            form_container.add(self.expense_date_input)

            # Payer Name dropdown
            form_container.add(toga.Label('Payer Name:', style=Pack(padding=(2, 0))))
            try:
                # Get family names from database
                family_details = self.database.get_family_details()
                self.family_names = [family[1] for family in family_details]
            except Exception as e:
                print(f"Error fetching family details: {e}")
                self.family_names = []

            # Use Selection widget for dropdown
            self.payer_name_input = toga.Selection(
                items=self.family_names if self.family_names else ['No families available'],
                style=Pack(padding=(0, 5), width=180)
            )
            if self.family_names:
                self.payer_name_input.value = self.family_names[0]
            form_container.add(self.payer_name_input)

            self.scrollable_content.add(form_container)

            # Buttons container
            button_container = toga.Box(style=Pack(direction=COLUMN, padding=5))

            # Save button
            save_expense_button = toga.Button(
                'Save Expense',
                on_press=self.save_expense,
                style=Pack(padding=3, width=150)
            )
            button_container.add(save_expense_button)

            # Back button
            back_button = toga.Button(
                'Back',
                on_press=self.goto_main,
                style=Pack(padding=3, width=150)
            )
            button_container.add(back_button)

            self.scrollable_content.add(button_container)

            # Message container for status messages
            self.message_container = toga.Box(style=Pack(direction=COLUMN, padding=5))
            self.scrollable_content.add(self.message_container)

            # Expense list container
            self.expense_list_container = toga.Box(style=Pack(direction=COLUMN, padding=5))
            self.scrollable_content.add(self.expense_list_container)

            # Set the scrollable content
            self.scroll_container.content = self.scrollable_content

            # Load existing expenses
            self.update_expense_list()
            print("ExpenseEntryScreen initialized successfully")

        except Exception as e:
            print(f"Error initializing ExpenseEntryScreen: {e}")
            raise

    def save_expense(self, sender):
        try:
            # Clear previous messages
            self.message_container.clear()

            # Validate inputs
            expense_name = self.expense_name_input.value.strip()
            expense_amount = self.expense_amount_input.value.strip()
            expense_date = self.expense_date_input.value.strip()
            payer_name = self.payer_name_input.value

            if not all([expense_name, expense_amount, expense_date, payer_name]):
                self.show_error("Please fill in all fields")
                return

            # Validate amount
            try:
                float_amount = float(expense_amount)
                if float_amount <= 0:
                    self.show_error("Amount must be greater than zero")
                    return
            except ValueError:
                self.show_error("Amount must be a valid number")
                return

            # Validate date format
            try:
                datetime.strptime(expense_date, '%Y-%m-%d')
            except ValueError:
                self.show_error("Date must be in YYYY-MM-DD format")
                return

            # Save expense using the database instance
            active_trip = self.database.get_active_trip()
            if not active_trip:
                self.show_error("No active trip found")
                return

            trip_id = active_trip[0]
            self.database.save_expense(trip_id, expense_name, float_amount, expense_date, 1)

            # Clear inputs and show success message
            self.clear_inputs()
            self.show_success("Expense saved successfully!")
            self.update_expense_list()

        except Exception as e:
            print(f"Error saving expense: {e}")
            self.show_error(f"Error saving expense: {str(e)}")

    def clear_inputs(self):
        """Clear all input fields"""
        self.expense_name_input.value = ''
        self.expense_amount_input.value = ''
        self.expense_date_input.value = datetime.now().strftime('%Y-%m-%d')
        if self.family_names:
            self.payer_name_input.value = self.family_names[0]

    def update_expense_list(self):
        """Update the list of expenses"""
        try:
            self.expense_list_container.clear()

            # Get active trip
            active_trip = self.database.get_active_trip()
            if not active_trip:
                no_trip_label = toga.Label(
                    'No active trip found. Please create a trip first.',
                    style=Pack(padding=10)
                )
                self.expense_list_container.add(no_trip_label)
                return

            trip_id = active_trip[0]
            expenses = self.database.get_expenses(trip_id)

            if not expenses:
                # Show "No expenses" message
                no_expenses_label = toga.Label(
                    'No expenses recorded yet.',
                    style=Pack(padding=10)
                )
                self.expense_list_container.add(no_expenses_label)
                return

            for expense in expenses:
                # Create container for each expense
                expense_box = toga.Box(
                    style=Pack(
                        direction=COLUMN,
                        padding=5,
                        background_color='#f0f0f0',
                        width=180
                    )
                )

                # Expense details
                details_box = toga.Box(style=Pack(direction=COLUMN, padding=2))
                details_box.add(toga.Label(
                    f'Name: {expense[2]}',
                    style=Pack(padding=(0, 2), font_size=14)
                ))
                details_box.add(toga.Label(
                    f'Amount: {expense[3]}',
                    style=Pack(padding=(0, 2), font_size=14)
                ))
                details_box.add(toga.Label(
                    f'Date: {expense[4]}',
                    style=Pack(padding=(0, 2), font_size=14)
                ))
                expense_box.add(details_box)

                # Delete button
                delete_button = toga.Button(
                    'Delete',
                    style=Pack(padding=2, width=80, height=30)
                )
                delete_button.on_press = lambda x, expense_id=expense[0]: self.delete_expense(expense_id)
                expense_box.add(delete_button)

                self.expense_list_container.add(expense_box)

        except Exception as e:
            print(f"Error updating expense list: {e}")
            self.show_error(f"Error updating expense list: {str(e)}")

    def delete_expense(self, expense_id):
        """Delete an expense"""
        try:
            self.database.delete_expense(expense_id)
            self.update_expense_list()
            self.show_success("Expense deleted successfully!")
        except Exception as e:
            self.show_error(f"Error deleting expense: {str(e)}")

    def show_error(self, message):
        """Show error message"""
        self.message_container.clear()
        error_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        error_label = toga.Label(
            message,
            style=Pack(padding=5, color='red')
        )
        error_box.add(error_label)
        self.message_container.add(error_box)

    def show_success(self, message):
        """Show success message"""
        self.message_container.clear()
        success_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        success_label = toga.Label(
            message,
            style=Pack(padding=5, color='green')
        )
        success_box.add(success_label)
        self.message_container.add(success_box)

    def goto_main(self, sender):
        """Navigate back to the main screen"""
        self.app.main_window.content = self.main_screen_layout

