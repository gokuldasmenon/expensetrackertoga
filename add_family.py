from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets import button, label, textinput, selection

from database import ExpenseTracker

from trips import TripListScreen


class AddFamilyScreen:
    def __init__(self, name, app):
        self.app = app
        self.name = name
        self.layout = Pack(direction=COLUMN)

        header_label = label.Label('Add Family/Individual Details', style=Pack(text_align=COLUMN, padding_top=50))
        self.layout.add(header_label)

        type_label = label.Label('Type:')
        self.layout.add(type_label)

        self.type_selection = selection.Selection(items=['Family', 'Individual'])
        self.layout.add(self.type_selection)

        self.name_label = label.Label('Family Name:')
        self.layout.add(self.name_label)

        self.name_input = textinput.TextInput()
        self.layout.add(self.name_input)

        self.num_members_label = label.Label('Number of Members:')
        self.layout.add(self.num_members_label)

        self.num_members_input = textinput.TextInput()
        self.layout.add(self.num_members_input)

        save_button = button.Button('Save Details')
        save_button.on_press = self.save_details
        self.layout.add(save_button)

        back_button = button.Button('Back')
        back_button.on_press = self.goto_main
        self.layout.add(back_button)

        self.type_selection.on_select = self.update_labels

        footer_label = label.Label('Developed by GDN', style=Pack(text_align=COLUMN, padding_top=50))
        self.layout.add(footer_label)

    def goto_main(self, sender):
        self.app.goto_screen('main')

    def update_labels(self, sender):
        if sender.selection == 'Family':
            self.name_label.text = 'Family Name:'
            self.num_members_label.text = 'Number of Members:'
            self.num_members_input.enabled = True
        else:
            self.name_label.text = 'Individual Name:'
            self.num_members_label.text = ''
            self.num_members_input.enabled = False
            self.num_members_input.value = '1'

    def save_details(self, sender):
        name = self.name_input.value
        if self.type_selection.selection == 'Family':
            num_members = self.num_members_input.value
        else:
            num_members = '1'
        expense_tracker = ExpenseTracker('expense_tracker.db')
        active_trip_id = expense_tracker.get_active_trip_id()

        if expense_tracker.check_family_name(name):
            content = Pack(direction=COLUMN)
            content.add(label.Label('Family name already exists'))
            buttons = Pack(direction=ROW)
            ok_button = button.Button('OK')
            buttons.add(ok_button)
            content.add(buttons)
            # popup = Popup('Error', content, size=(400, 400))
            # ok_button.on_press = popup.dismiss
            # popup.show()
            return

        expense_tracker.save_family_details(name, num_members, active_trip_id)
        expense_tracker.update_trip_family_details(name, num_members)
        self.app.main_window.content = TripListScreen('trip_list', self.app).layout
