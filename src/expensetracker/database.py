import sqlite3
import os
from datetime import datetime



import os

import os

class ExpenseTracker:
    def __init__(self, app=None, db_path=None):
        try:
            # Use app.paths.app if app is provided, otherwise use db_path
            if app:
                self.app = app
                self.db_path = os.path.join(app.paths.app, "expensetracker.db")
            elif db_path:
                self.db_path = db_path
            else:
                raise ValueError("Either 'app' or 'db_path' must be provided to initialize ExpenseTracker.")

            print(f"Initializing database at: {self.db_path}")

            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            # Connect to the database
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # Create tables
            self.create_trips_table()
            self.create_expenses_table()
            self.create_family_details_table()
            self.create_archived_trips_table()

            print("Database initialized successfully")

        except Exception as e:
            print(f"Database initialization error: {e}")
            raise






    def create_trips_table(self):
        try:
            # SQL query formatted for better readability
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY,
                name TEXT,
                start_date DATE,
                trip_type TEXT,
                family_name TEXT,
                individual_name TEXT,
                num_family_members INTEGER,
                status TEXT DEFAULT 'INACTIVE'
            )
            '''

            # Execute the create table query
            self.cursor.execute(create_table_query)
            self.conn.commit()
            print("Trips table created successfully")

            # Verify table creation by trying to select from it
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trips'")
            if self.cursor.fetchone():
                print("Verified: trips table exists")

        except sqlite3.Error as e:
            print(f"Error creating trips table: {str(e)}")
            # Optionally show error in UI if available
            if hasattr(self, 'main_window'):
                self.main_window.info_dialog(
                    "Database Error",
                    f"Failed to create trips table: {str(e)}"
                )
            raise  # Re-raise the exception for higher-level handling

        except Exception as e:
            print(f"Unexpected error creating trips table: {str(e)}")
            raise

    def initialize_database(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.create_trips_table()
            print(f"Database initialized at: {self.db_path}")
        except Exception as e:
            print(f"Database initialization failed: {str(e)}")
            raise

    def get_connection(self):
        """Get the current database connection or create a new one if needed"""
        try:
            # Test if connection is active
            self.conn.cursor()
            return self.conn
        except (sqlite3.Error, AttributeError):
            # Reconnect if connection is closed or invalid
            self.conn = sqlite3.connect(self.db_path)
            return self.conn

    def __del__(self):
        """Ensure database connection is properly closed"""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                print("Database connection closed")
        except Exception as e:
            print(f"Error closing database connection: {e}")

    def create_archived_trips_table(self):
        self.cursor.execute('''  
        CREATE TABLE IF NOT EXISTS archived_trips (  
           id INTEGER PRIMARY KEY AUTOINCREMENT,  
           trip_name TEXT NOT NULL,  
           archive_path TEXT NOT NULL,  
           archived_date TEXT NOT NULL  
        );  
      ''')
        self.conn.commit()

    def archive_trip(self):
        try:
            # Get the trip name
            self.cursor.execute("SELECT name FROM trips WHERE id = (SELECT MAX(id) FROM trips)")
            result = self.cursor.fetchone()
            trip_name = result[0] if result else "Unnamed Trip"

            # Create archives directory in app's private storage
            archives_dir = os.path.join(self.app.paths.app, "archives")
            if not os.path.exists(archives_dir):
                os.makedirs(archives_dir)

            # Create archive file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_filename = f"trip_archive_{timestamp}.db"
            archive_path = os.path.join(archives_dir, archive_filename)

            print(f"Creating archive at: {archive_path}")

            try:
                # Create and initialize archive database
                archive_conn = sqlite3.connect(archive_path)
                archive_cur = archive_conn.cursor()

                # Enable foreign keys in the archive database
                archive_cur.execute("PRAGMA foreign_keys = ON")

                # Create tables in archive database
                archive_cur.executescript('''  
                    CREATE TABLE IF NOT EXISTS trips (  
                        id INTEGER PRIMARY KEY,  
                        name TEXT,  
                        start_date DATE,  
                        trip_type TEXT,  
                        family_name TEXT,  
                        individual_name TEXT,  
                        num_family_members INTEGER,  
                        status TEXT DEFAULT 'INACTIVE'  
                    );  

                    CREATE TABLE IF NOT EXISTS expenses (  
                        id INTEGER PRIMARY KEY,  
                        trip_id INTEGER,  
                        name TEXT,  
                        amount REAL,  
                        date DATE,  
                        trip_type TEXT,  
                        payer_id INTEGER,  
                        FOREIGN KEY (trip_id) REFERENCES trips (id)  
                    );  

                    CREATE TABLE IF NOT EXISTS family_details (  
                        id INTEGER PRIMARY KEY,  
                        name TEXT,  
                        members INTEGER  
                    );  
                ''')

                # Begin transaction for data copy
                archive_conn.execute('BEGIN TRANSACTION')

                try:
                    # Copy trips data
                    print("Copying trips data...")
                    self.cursor.execute("SELECT * FROM trips")
                    trips = self.cursor.fetchall()
                    for trip in trips:
                        archive_cur.execute('''  
                            INSERT INTO trips (id, name, start_date, trip_type, family_name, 
                                            individual_name, num_family_members, status)  
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)  
                        ''', trip)

                    # Copy expenses data
                    print("Copying expenses data...")
                    self.cursor.execute("SELECT * FROM expenses")
                    expenses = self.cursor.fetchall()
                    for expense in expenses:
                        archive_cur.execute('''  
                            INSERT INTO expenses (id, trip_id, name, amount, date, trip_type, payer_id)  
                            VALUES (?, ?, ?, ?, ?, ?, ?)  
                        ''', expense)

                    # Copy family details data
                    print("Copying family details...")
                    self.cursor.execute("SELECT id, family_name, num_members FROM family_details")
                    family_details = self.cursor.fetchall()
                    for family in family_details:
                        archive_cur.execute('''  
                            INSERT INTO family_details (id, name, members)  
                            VALUES (?, ?, ?)  
                        ''', family)

                    # Record archive in main database
                    archived_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.cursor.execute('''  
                        INSERT INTO archived_trips (trip_name, archive_path, archived_date)  
                        VALUES (?, ?, ?)  
                    ''', (trip_name, archive_filename, archived_date))

                    # Commit both transactions
                    archive_conn.commit()
                    self.conn.commit()
                    print("Archive created successfully")

                except sqlite3.Error as e:
                    # Rollback both transactions on error
                    archive_conn.rollback()
                    self.conn.rollback()
                    print(f"Error during data copy: {e}")
                    raise

            except sqlite3.Error as e:
                print(f"Database error during archiving: {e}")
                raise
            finally:
                # Ensure archive connection is closed
                if 'archive_conn' in locals():
                    archive_conn.close()

            return archive_filename  # Return just the filename, not the full path

        except Exception as e:
            print(f"Error creating archive: {e}")
            raise

    def get_archive_path(self, archive_filename):
        """Helper method to get the full path of an archive file"""
        return os.path.join(self.app.paths.app, "archives", archive_filename)

    def get_active_trip(self):
        self.cursor.execute('SELECT * FROM trips  WHERE status = "active"')
        return self.cursor.fetchone()

    def load_archived_trip(self, archive_path):
        archive_conn = sqlite3.connect(archive_path)
        archive_cursor = archive_conn.cursor()

        self.clear_trips()
        self.clear_expenses()
        self.clear_family_details()

        archive_cursor.execute("SELECT * FROM trips")
        trips = archive_cursor.fetchall()
        for trip in trips:
            self.cursor.execute('''  
           INSERT INTO trips (id, name, start_date, trip_type, family_name, individual_name, num_family_members, status)  
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)  
        ''', trip)

        archive_cursor.execute("SELECT * FROM expenses")
        expenses = archive_cursor.fetchall()
        for expense in expenses:
            self.cursor.execute('''  
           INSERT INTO expenses (id, trip_id, name, amount, date, trip_type, payer_id)  
           VALUES (?, ?, ?, ?, ?, ?, ?)  
        ''', expense)

        archive_cursor.execute("SELECT id, name, members FROM family_details")
        family_details = archive_cursor.fetchall()
        for family in family_details:
            self.cursor.execute('''  
           INSERT INTO family_details (id, name, members)  
           VALUES (?, ?, ?)  
        ''', family)

        self.conn.commit()
        archive_conn.close()

    def get_active_trip_id(self):
        self.cursor.execute('SELECT id FROM trips WHERE status = "active"')
        active_trip = self.cursor.fetchone()
        if active_trip:
            return active_trip[0]
        else:
            return None

    def create_expenses_table(self):
        self.cursor.execute('''    
            CREATE TABLE IF NOT EXISTS expenses (    
            id INTEGER PRIMARY KEY,    
            trip_id INTEGER,    
            name TEXT,    
            amount REAL,    
            date DATE,    
            trip_type TEXT,   
            payer_id INTEGER  
            );    
        ''')
        self.conn.commit()

    def create_family_details_table(self):
        self.cursor.execute('''   
       CREATE TABLE IF NOT EXISTS family_details (   
         id INTEGER PRIMARY KEY,   
         family_name TEXT,   
         num_members INTEGER,  
         trip_id INTEGER  
       );   
      ''')
        self.conn.commit()

    def add_expense(self, name, amount, date, payer_id):
        self.cursor.execute('''INSERT INTO expenses (name, amount, date, payer_id)  
                     VALUES (?, ?, ?, ?)''', (name, amount, date, payer_id))
        self.conn.commit()
        return True

    def get_total_expenses(self, trip_id):
        self.cursor.execute('SELECT SUM(amount) FROM expenses WHERE trip_id = ?', (trip_id,))
        total_expenses = self.cursor.fetchone()[0]
        return total_expenses

    def get_families(self, trip_id):
        self.cursor.execute("""  
        SELECT fd.family_name, fd.num_members  
        FROM family_details fd  
        INNER JOIN trips t ON fd.family_name = t.family_name  
        WHERE t.id = ?  
      """, (trip_id,))
        return self.cursor.fetchall()

    def delete_archive(self, archive_path):
        if os.path.exists(archive_path):
            os.remove(archive_path)
        self.cursor.execute("DELETE FROM archived_trips WHERE archive_path = ?", (archive_path,))
        self.conn.commit()

    def get_all_family_names(self, trip_id):
        self.cursor.execute('SELECT family_name FROM family_details')
        all_family_names = [row[0] for row in self.cursor.fetchall()]
        return all_family_names

    def get_family_count(self, trip_id):
        self.cursor.execute('SELECT COUNT(*) FROM family_details WHERE trip_id = ?', (trip_id,))
        count = self.cursor.fetchone()[0]
        return count

    def get_expenses_by_family(self, trip_id):
        self.cursor.execute('''   
       SELECT family_details.family_name, SUM(expenses.amount) AS total_amount   
       FROM expenses   
       JOIN family_details ON expenses.payer_id = family_details.id   
       WHERE expenses.trip_id = ?   
       GROUP BY family_details.family_name   
      ''', (trip_id,))
        expenses_by_family = self.cursor.fetchall()
        return expenses_by_family

    def get_family_names(self):
        self.cursor.execute("SELECT DISTINCT family_name FROM family_details")
        family_names = [row[0] for row in self.cursor.fetchall()]
        return family_names

    def check_family_name(self, family_name):
        self.cursor.execute('SELECT * FROM family_details WHERE family_name = ?', (family_name,))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def get_expenses(self, trip_id):
        self.cursor.execute("""  
        SELECT id, name, amount, date, payer_id  
        FROM expenses  
        WHERE trip_id = ?  
      """, (trip_id,))
        return self.cursor.fetchall()

    def get_per_head_cost(self, trip_id):
        total_expenses = self.get_total_expenses(trip_id)
        total_members = self.get_total_members(trip_id)
        if not total_expenses or not total_members:
            return 0.0
        per_head_cost = total_expenses / total_members
        return per_head_cost

    def settle_expenses(self, trip_id):
        all_family_names = self.get_all_family_names(trip_id)
        expenses_by_family = self.get_expenses_by_family(trip_id)
        per_head_cost = self.get_per_head_cost(trip_id)
        settlement = []
        for family_name in all_family_names:
            total_amount = 0
            for expense_family_name, expense_amount in expenses_by_family:
                if expense_family_name == family_name:
                    total_amount = expense_amount
                    break
            family_members = self.get_family_members(family_name)
            amount_to_pay = total_amount - per_head_cost * family_members
            settlement.append((family_name, amount_to_pay))
        payers = [(family_name, amount) for family_name, amount in settlement if amount < 0]
        receivers = [(family_name, amount) for family_name, amount in settlement if amount > 0]
        transactions = []
        while payers and receivers:
            payer_name, payer_amount = payers.pop(0)
            receiver_name, receiver_amount = receivers.pop(0)
            settlement_amount = min(abs(payer_amount), receiver_amount)
            transactions.append((payer_name, receiver_name, settlement_amount))
            payer_amount += settlement_amount
            receiver_amount -= settlement_amount
            if payer_amount < 0:
                payers.insert(0, (payer_name, payer_amount))
            if receiver_amount > 0:
                receivers.insert(0, (receiver_name, receiver_amount))
        return transactions

    def get_total_members(self, trip_id=None):
        self.cursor.execute('SELECT SUM(num_members) FROM family_details')
        total_members = self.cursor.fetchone()[0]
        return total_members

    def get_family_members(self, family_name):
        self.cursor.execute('SELECT num_members FROM family_details WHERE family_name = ?', (family_name,))
        num_members = self.cursor.fetchone()
        return num_members[0] if num_members else 0

    def get_family_by_name(self, family_name):
        self.cursor.execute("SELECT id FROM family_details WHERE family_name = ?", (family_name,))
        return self.cursor.fetchone()

    def save_expense(self, trip_id, name, amount, date, payer_id):
        try:
            self.conn.execute('BEGIN TRANSACTION')
            self.cursor.execute('''
                INSERT INTO expenses (trip_id, name, amount, date, payer_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (trip_id, name, amount, date, payer_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error saving expense: {e}")
            return False

    def expense(self, trip_id):
        self.cursor.execute('''   
        SELECT expenses.id, expenses.trip_id, expenses.name, expenses.amount, expenses.date, family_details.family_name   
        FROM expenses   
        JOIN family_details ON expenses.payer_id = family_details.id   
        WHERE expenses.trip_id = ?  
      ''', (trip_id,))
        return self.cursor.fetchall()

    def check_database_integrity(self):
        try:
            self.cursor.execute("PRAGMA integrity_check")
            result = self.cursor.fetchone()
            return result[0] == "ok"
        except sqlite3.Error as e:
            print(f"Database integrity check failed: {e}")
            return False

    def save_trip(self, trip_name, trip_start_date, trip_type, family_name, individual_name, num_family_members):
        try:
            if family_name is None:
                self.cursor.execute(
                    'INSERT INTO trips (name, start_date, trip_type, individual_name, num_family_members, status) VALUES (?, ?, ?, ?, ?, "active")',
                    (trip_name, trip_start_date, trip_type, individual_name, num_family_members))
            else:
                self.cursor.execute(
                    'INSERT INTO trips (name, start_date, trip_type, family_name, individual_name, num_family_members, status) VALUES (?, ?, ?, ?, ?, ?, "active")',
                    (trip_name, trip_start_date, trip_type, family_name, individual_name, num_family_members))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving trip: {e}")
            return False

    def delete_family_record(self, family_id):
        self.cursor.execute("DELETE FROM family_details WHERE id=?", (family_id,))
        self.conn.commit()

    def delete_expense(self, expense_id):
        self.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        if self.cursor.rowcount == 0:
            return False
        else:
            return True

    def get_trips(self):
        self.cursor.execute('SELECT * FROM trips')
        return self.cursor.fetchall()

    def get_expenses(self):
        self.cursor.execute("SELECT * FROM expenses")
        return self.cursor.fetchall()

    def get_trip_details(self, trip_id):
        self.cursor.execute('''  
        SELECT name, start_date, trip_type  
        FROM trips  
        WHERE id = ?  
      ''', (trip_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                'name': result[0],
                'start_date': result[1],
                'trip_type': result[2]
            }
        return None

    def get_family_id(self, family_name):
        self.cursor.execute("SELECT id FROM family_details WHERE family_name = ?", (family_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def get_expenses_with_payer_name(self, trip_id):
        query = '''  
        SELECT expenses.id, expenses.trip_id, expenses.name, expenses.amount, expenses.date,  
             expenses.payer_id,  
             COALESCE(family_details.family_name, 'Unknown') AS payer_name  
        FROM expenses  
        LEFT JOIN family_details ON expenses.payer_id = family_details.id  
        WHERE expenses.trip_id = ?  
      '''
        self.cursor.execute(query, (trip_id,))
        return self.cursor.fetchall()

    def update_trip_family_details(self, family_name, num_members):
        self.cursor.execute(
            'UPDATE trips SET family_name = COALESCE(family_name, ?), num_family_members = COALESCE(num_family_members, ?) WHERE status = "active"',
            (family_name, num_members))
        self.conn.commit()

    def get_expenses(self, trip_id):
        self.cursor.execute('SELECT * FROM expenses WHERE trip_id = ?', (trip_id,))
        return self.cursor.fetchall()

    def clear_expenses(self):
        self.cursor.execute("DELETE FROM expenses")
        self.conn.commit()

    def clear_trips(self):
        self.cursor.execute('DELETE FROM trips WHERE status = "active"')
        self.conn.commit()

    def save_family_details(self, family_name, num_members, trip_id):
        self.cursor.execute(
            'INSERT INTO family_details (family_name, num_members, trip_id) VALUES (?, ?, ?)',
            (family_name, num_members, trip_id)
        )
        self.conn.commit()

    def get_settlements(self):
        # Retrieve settlement data from the database
        settlements = []
        # ... database query to retrieve settlement data ...
        return settlements

    def get_family_details(self):
        self.cursor.execute('SELECT * FROM family_details')
        self.conn.commit()
        return self.cursor.fetchall()
    def get_family_details_active(self, trip_id):
        """Fetch family details for the given trip ID."""
        self.cursor.execute('SELECT * FROM family_details WHERE trip_id = ?', (trip_id,))
        self.conn.commit()
        return self.cursor.fetchall()
    def clear_family_details(self):
        self.cursor.execute('DELETE FROM family_details')
        self.conn.commit()

    def update_family_record(self, family_id, new_family_name, new_num_members):
        self.cursor.execute("UPDATE family_details SET family_name = ?, num_members = ? WHERE id = ?",
                            (new_family_name, new_num_members, family_id))
        self.conn.commit()
