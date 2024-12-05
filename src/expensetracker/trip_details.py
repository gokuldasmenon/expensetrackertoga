from toga.style import Pack
from toga.style.pack import COLUMN
from toga.widgets import label

from .database import ExpenseTracker


class TripDetailsScreen:
    def __init__(self, name, app):
        self.app = app
        self.name = name
        self.layout = Pack(direction=COLUMN)
        self.database = app.database

        header_label = label.Label('Trip Details', style=Pack(text_align=COLUMN, padding_top=50))
        self.layout.add(header_label)

        self.trip_details_layout = Pack(direction=COLUMN)
        self.layout.add(self.trip_details_layout)

        self.family_details_layout = Pack(direction=COLUMN)
        self.layout.add(self.family_details_layout)

        footer_label = label.Label('Developed by GDN', style=Pack(text_align=COLUMN, padding_top=50))
        self.layout.add(footer_label)

        self.load_trip_details()

    def load_trip_details(self):
        self.trip_details_layout.children = []
        self.family_details_layout.children = []
        expense_tracker = ExpenseTracker('expense_tracker.db')
        trip_id = self.get_active_trip_id()

        trip_details = expense_tracker.get_trip_details(trip_id)
        if trip_details:
            self.display_trip_details(trip_details)
        else:
            self.trip_details_layout.add(label.Label('No active trip', style=Pack(font_size=20)))

        family_details = expense_tracker.get_family_details(trip_id)
        if family_details:
            self.display_family_details(family_details)
        else:
            self.family_details_layout.add(label.Label('No family details', style=Pack(font_size=20)))

    def display_trip_details(self, trip_details):
        labels = [
            ('Trip Name:', trip_details['name']),
            ('Trip Start Date:', trip_details['start_date']),
            ('Trip Type:', trip_details['trip_type'])
        ]

        for label_text, value in labels:
            self.trip_details_layout.add(label.Label(label_text, style=Pack(font_size=20)))
            self.trip_details_layout.add(label.Label(str(value), style=Pack(font_size=20)))

    def get_active_trip_id(self):
        expense_tracker = ExpenseTracker('expense_tracker.db')
        return expense_tracker.get_active_trip_id()

    def display_family_details(self, family_details):
        for family in family_details:
            self.family_details_layout.add(label.Label('Family Name:', style=Pack(font_size=20)))
            self.family_details_layout.add(label.Label(family[1], style=Pack(font_size=20)))
            self.family_details_layout.add(label.Label('Number of Members:', style=Pack(font_size=20)))
            self.family_details_layout.add(label.Label(str(family[2]), style=Pack(font_size=20)))
