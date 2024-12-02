from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import button, label, textinput

from database import ExpenseTracker
from main import MainScreen


class FamilyDetailsScreen:
    def __init__(self, name, app):
        self.app = app
        self.name = name
        self.layout = Pack(direction=COLUMN)

        header_label = label.Label('Family Details', style=Pack(text_align=COLUMN, padding_top=50))
        self.layout.add(header_label)

        family_details_layout = Pack(direction=COLUMN)
        self.layout.add(family_details_layout)

        family_name_label = label.Label('Family Name:')
        family_details_layout.add(family_name_label)
        self.family_name_input = textinput.TextInput()
        family_details_layout.add(self.family_name_input)

        num_members_label = label.Label('Number of Members:')
        family_details_layout.add(num_members_label)
        self.num_members_input = textinput.TextInput()
        family_details_layout.add(self.num_members_input)

        add_family_button = button.Button('Add Family')
        add_family_button.on_press = self.add_family
        family_details_layout.add(add_family_button)

        footer_label = label.Label('Developed by GDN', style=Pack(text_align=COLUMN, padding_top=50))
        self.layout.add(footer_label)

    def add_family(self, sender):
        family_name = self.family_name_input.value
        num_members = self.num_members_input.value

        expense_tracker = ExpenseTracker('expense_tracker.db')
        active_trip_id = expense_tracker.get_active_trip_id()

        expense_tracker.save_family_details(family_name, num_members, active_trip_id)

        self.family_name_input.value = ''
        self.num_members_input.value = ''

    def get_family_id(self, family_name):
        expense_tracker = ExpenseTracker('expense_tracker.db')
        family_id = expense_tracker.get_family_id(family_name)
        return family_id
