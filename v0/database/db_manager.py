# database/db_manager.py
import sqlite3
import os
import datetime
import json

class DatabaseManager:
    def __init__(self):
        self.db_path = "data/guzel_clinic.db"
        self.ensure_data_dir()
        self.initialize_database()
    
    def ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def initialize_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create customers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            hair_type TEXT,
            hair_color TEXT,
            skin_type TEXT,
            allergies TEXT,
            current_sessions INTEGER DEFAULT 0,
            remaining_sessions INTEGER DEFAULT 0,
            most_requested_services TEXT,
            remaining_payments REAL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create services table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create appointments table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            date_time TIMESTAMP NOT NULL,
            services TEXT NOT NULL,
            service_provider TEXT NOT NULL,
            notes TEXT,
            status TEXT NOT NULL,
            remaining_payments REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
        ''')
        
        # Create invoices table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            appointment_id INTEGER,
            date TIMESTAMP NOT NULL,
            services TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            amount_paid REAL NOT NULL,
            amount_remaining REAL DEFAULT 0,
            invoice_creator TEXT NOT NULL,
            service_provider TEXT NOT NULL,
            total_amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (appointment_id) REFERENCES appointments (id)
        )
        ''')
        
        # Insert default admin and user if they don't exist
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                ("admin", self.hash_password("admin"), True)
            )
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'user1'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                ("user1", self.hash_password("user1"), False)
            )
        
        # Insert default services
        self.insert_default_services(cursor)
        
        conn.commit()
        conn.close()
    
    def insert_default_services(self, cursor):
        # Check if services table is empty
        cursor.execute("SELECT COUNT(*) FROM services")
        if cursor.fetchone()[0] > 0:
            return
        
        # Default services with prices
        default_services = [
            ("وجه كامل", 50000),
            ("شارب", 0),  # Price will be calculated based on laser shots
            ("ذقن", 0),   # Price will be calculated based on laser shots
            ("كف اليد", 0),  # Price will be calculated based on laser shots
            ("ايدين كاملين", 150000),
            ("ساعدين", 80000),
            ("عضدين", 90000),
            ("رجلين كاملين", 250000),
            ("ساقين", 120000),
            ("فخذين", 150000),
            ("ارداف", 50000),
            ("بيكيني", 50000),
            ("ابط", 50000),
            ("ابط + بيكيني", 100000),
            ("بطن", 120000),
            ("خط السرة", 80000),
            ("اسفل الظهر", 0),  # Price will be calculated based on laser shots
            ("ظهر", 130000),
            ("جسم كامل", 700000),
            ("جسم كامل مع وجه وارداف", 750000),
            ("جسم جزئي", 550000),
            ("ضربة الليزر", 1500),
        ]
        
        for service, price in default_services:
            cursor.execute(
                "INSERT INTO services (name, price) VALUES (?, ?)",
                (service, price)
            )
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def hash_password(self, password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_login(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT password_hash, is_admin FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == self.hash_password(password):
            return True, result[1]  # Success, is_admin
        return False, False
    
    # Customer methods
    def add_customer(self, customer_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO customers (
            name, phone, email, hair_type, hair_color, skin_type, 
            allergies, current_sessions, remaining_sessions, 
            most_requested_services, remaining_payments, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_data['name'],
            customer_data['phone'],
            customer_data.get('email', ''),
            customer_data.get('hair_type', ''),
            customer_data.get('hair_color', ''),
            customer_data.get('skin_type', ''),
            customer_data.get('allergies', ''),
            customer_data.get('current_sessions', 0),
            customer_data.get('remaining_sessions', 0),
            json.dumps(customer_data.get('most_requested_services', [])),
            customer_data.get('remaining_payments', 0),
            customer_data.get('notes', '')
        ))
        
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return customer_id
    
    def update_customer(self, customer_id, customer_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE customers SET
            name = ?,
            phone = ?,
            email = ?,
            hair_type = ?,
            hair_color = ?,
            skin_type = ?,
            allergies = ?,
            current_sessions = ?,
            remaining_sessions = ?,
            most_requested_services = ?,
            remaining_payments = ?,
            notes = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (
            customer_data['name'],
            customer_data['phone'],
            customer_data.get('email', ''),
            customer_data.get('hair_type', ''),
            customer_data.get('hair_color', ''),
            customer_data.get('skin_type', ''),
            customer_data.get('allergies', ''),
            customer_data.get('current_sessions', 0),
            customer_data.get('remaining_sessions', 0),
            json.dumps(customer_data.get('most_requested_services', [])),
            customer_data.get('remaining_payments', 0),
            customer_data.get('notes', ''),
            customer_id
        ))
        
        conn.commit()
        conn.close()
    
    def delete_customer(self, customer_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_customers(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers ORDER BY name")
        customers = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for customer in customers:
            if customer['most_requested_services']:
                customer['most_requested_services'] = json.loads(customer['most_requested_services'])
            else:
                customer['most_requested_services'] = []
        
        return customers
    
    def get_customer(self, customer_id):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        customer = dict(cursor.fetchone())
        
        conn.close()
        
        # Parse JSON fields
        if customer['most_requested_services']:
            customer['most_requested_services'] = json.loads(customer['most_requested_services'])
        else:
            customer['most_requested_services'] = []
        
        return customer
    
    def search_customers(self, search_term):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM customers 
        WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
        ORDER BY name
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        customers = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for customer in customers:
            if customer['most_requested_services']:
                customer['most_requested_services'] = json.loads(customer['most_requested_services'])
            else:
                customer['most_requested_services'] = []
        
        return customers
    
    # Service methods
    def add_service(self, name, price):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO services (name, price) VALUES (?, ?)",
            (name, price)
        )
        
        service_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return service_id
    
    def update_service(self, service_id, name, price):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE services SET name = ?, price = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, price, service_id)
        )
        
        conn.commit()
        conn.close()
    
    def delete_service(self, service_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_services(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM services ORDER BY name")
        services = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return services
    
    def get_service(self, service_id):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        service = dict(cursor.fetchone())
        
        conn.close()
        return service
    
    # Appointment methods
    def add_appointment(self, appointment_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO appointments (
            customer_id, date_time, services, service_provider, 
            notes, status, remaining_payments
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            appointment_data['customer_id'],
            appointment_data['date_time'],
            json.dumps(appointment_data['services']),
            appointment_data['service_provider'],
            appointment_data.get('notes', ''),
            appointment_data['status'],
            appointment_data.get('remaining_payments', 0)
        ))
        
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return appointment_id
    
    def update_appointment(self, appointment_id, appointment_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE appointments SET
            customer_id = ?,
            date_time = ?,
            services = ?,
            service_provider = ?,
            notes = ?,
            status = ?,
            remaining_payments = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (
            appointment_data['customer_id'],
            appointment_data['date_time'],
            json.dumps(appointment_data['services']),
            appointment_data['service_provider'],
            appointment_data.get('notes', ''),
            appointment_data['status'],
            appointment_data.get('remaining_payments', 0),
            appointment_id
        ))
        
        conn.commit()
        conn.close()
    
    def delete_appointment(self, appointment_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_appointments(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT a.*, c.name as customer_name, c.phone as customer_phone
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        ORDER BY a.date_time
        ''')
        
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for appointment in appointments:
            appointment['services'] = json.loads(appointment['services'])
        
        return appointments
    
    def get_appointment(self, appointment_id):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT a.*, c.name as customer_name, c.phone as customer_phone
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        WHERE a.id = ?
        ''', (appointment_id,))
        
        appointment = dict(cursor.fetchone())
        
        conn.close()
        
        # Parse JSON fields
        appointment['services'] = json.loads(appointment['services'])
        
        return appointment
    
    def get_appointments_by_date(self, date):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Format date as YYYY-MM-DD
        date_str = date.strftime('%Y-%m-%d')
        
        cursor.execute('''
        SELECT a.*, c.name as customer_name, c.phone as customer_phone
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        WHERE date(a.date_time) = ?
        ORDER BY a.date_time
        ''', (date_str,))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for appointment in appointments:
            appointment['services'] = json.loads(appointment['services'])
        
        return appointments
    
    def search_appointments(self, search_term):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT a.*, c.name as customer_name, c.phone as customer_phone
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        WHERE c.name LIKE ? OR c.phone LIKE ? OR a.service_provider LIKE ?
        ORDER BY a.date_time
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for appointment in appointments:
            appointment['services'] = json.loads(appointment['services'])
        
        return appointments
    
    # Invoice methods
    def add_invoice(self, invoice_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO invoices (
            customer_id, appointment_id, date, services, payment_method,
            amount_paid, amount_remaining, invoice_creator, service_provider, total_amount
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice_data['customer_id'],
            invoice_data.get('appointment_id'),
            invoice_data['date'],
            json.dumps(invoice_data['services']),
            invoice_data['payment_method'],
            invoice_data['amount_paid'],
            invoice_data.get('amount_remaining', 0),
            invoice_data['invoice_creator'],
            invoice_data['service_provider'],
            invoice_data['total_amount']
        ))
        
        invoice_id = cursor.lastrowid
        
        # Update customer's remaining payments if needed
        if invoice_data.get('amount_remaining', 0) > 0:
            cursor.execute('''
            UPDATE customers SET
                remaining_payments = remaining_payments + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (invoice_data.get('amount_remaining', 0), invoice_data['customer_id']))
        
        # Update appointment's remaining payments if needed
        if invoice_data.get('appointment_id') and invoice_data.get('amount_remaining', 0) > 0:
            cursor.execute('''
            UPDATE appointments SET
                remaining_payments = remaining_payments + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (invoice_data.get('amount_remaining', 0), invoice_data.get('appointment_id')))
        
        conn.commit()
        conn.close()
        return invoice_id
    
    def update_invoice(self, invoice_id, invoice_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get the original invoice to calculate payment differences
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        original_invoice = dict(cursor.fetchone())
        
        # Calculate the difference in remaining payments
        original_remaining = original_invoice['amount_remaining']
        new_remaining = invoice_data.get('amount_remaining', 0)
        remaining_difference = new_remaining - original_remaining
        
        cursor.execute('''
        UPDATE invoices SET
            customer_id = ?,
            appointment_id = ?,
            date = ?,
            services = ?,
            payment_method = ?,
            amount_paid = ?,
            amount_remaining = ?,
            invoice_creator = ?,
            service_provider = ?,
            total_amount = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (
            invoice_data['customer_id'],
            invoice_data.get('appointment_id'),
            invoice_data['date'],
            json.dumps(invoice_data['services']),
            invoice_data['payment_method'],
            invoice_data['amount_paid'],
            invoice_data.get('amount_remaining', 0),
            invoice_data['invoice_creator'],
            invoice_data['service_provider'],
            invoice_data['total_amount'],
            invoice_id
        ))
        
        # Update customer's remaining payments if needed
        if remaining_difference != 0:
            cursor.execute('''
            UPDATE customers SET
                remaining_payments = remaining_payments + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (remaining_difference, invoice_data['customer_id']))
        
        # Update appointment's remaining payments if needed
        if invoice_data.get('appointment_id') and remaining_difference != 0:
            cursor.execute('''
            UPDATE appointments SET
                remaining_payments = remaining_payments + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (remaining_difference, invoice_data.get('appointment_id')))
        
        conn.commit()
        conn.close()
    
    def delete_invoice(self, invoice_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get the invoice to update customer and appointment records
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        invoice = dict(cursor.fetchone())
        
        # Update customer's remaining payments
        if invoice['amount_remaining'] > 0:
            cursor.execute('''
            UPDATE customers SET
                remaining_payments = remaining_payments - ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (invoice['amount_remaining'], invoice['customer_id']))
        
        # Update appointment's remaining payments
        if invoice['appointment_id'] and invoice['amount_remaining'] > 0:
            cursor.execute('''
            UPDATE appointments SET
                remaining_payments = remaining_payments - ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (invoice['amount_remaining'], invoice['appointment_id']))
        
        # Delete the invoice
        cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_invoices(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT i.*, c.name as customer_name, c.phone as customer_phone
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        ORDER BY i.date DESC
        ''')
        
        invoices = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for invoice in invoices:
            invoice['services'] = json.loads(invoice['services'])
        
        return invoices
    
    def get_invoice(self, invoice_id):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT i.*, c.name as customer_name, c.phone as customer_phone
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE i.id = ?
        ''', (invoice_id,))
        
        invoice = dict(cursor.fetchone())
        
        conn.close()
        
        # Parse JSON fields
        invoice['services'] = json.loads(invoice['services'])
        
        return invoice
    
    def search_invoices(self, search_term):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT i.*, c.name as customer_name, c.phone as customer_phone
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE c.name LIKE ? OR c.phone LIKE ? OR i.invoice_creator LIKE ? OR i.service_provider LIKE ?
        ORDER BY i.date DESC
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        invoices = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for invoice in invoices:
            invoice['services'] = json.loads(invoice['services'])
        
        return invoices
    
    # Financial reporting methods
    def get_daily_revenue(self, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Format date as YYYY-MM-DD
        date_str = date.strftime('%Y-%m-%d')
        
        cursor.execute('''
        SELECT SUM(amount_paid) as total
        FROM invoices
        WHERE date(date) = ?
        ''', (date_str,))
        
        result = cursor.fetchone()
        total = result[0] if result[0] else 0
        
        conn.close()
        return total
    
    def get_weekly_revenue(self, start_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate end date (start_date + 6 days)
        end_date = start_date + datetime.timedelta(days=6)
        
        # Format dates as YYYY-MM-DD
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        cursor.execute('''
        SELECT SUM(amount_paid) as total
        FROM invoices
        WHERE date(date) BETWEEN ? AND ?
        ''', (start_date_str, end_date_str))
        
        result = cursor.fetchone()
        total = result[0] if result[0] else 0
        
        conn.close()
        return total
    
    def get_monthly_revenue(self, year, month):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT SUM(amount_paid) as total
        FROM invoices
        WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        ''', (str(year), str(month).zfill(2)))
        
        result = cursor.fetchone()
        total = result[0] if result[0] else 0
        
        conn.close()
        return total
    
    def get_revenue_by_service(self, start_date, end_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Format dates as YYYY-MM-DD
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # This query is more complex as we need to extract service data from JSON
        cursor.execute('''
        SELECT i.id, i.services, i.amount_paid, i.amount_remaining, i.total_amount
        FROM invoices i
        WHERE date(i.date) BETWEEN ? AND ?
        ''', (start_date_str, end_date_str))
        
        invoices = cursor.fetchall()
        
        # Process the results to calculate revenue by service
        service_revenue = {}
        for invoice in invoices:
            invoice_id, services_json, amount_paid, amount_remaining, total_amount = invoice
            services = json.loads(services_json)
            
            # Calculate the payment ratio if there's a partial payment
            payment_ratio = 1.0
            if total_amount > 0:
                payment_ratio = amount_paid / total_amount
            
            for service in services:
                service_name = service['name']
                service_price = service['price']
                
                # Allocate the revenue proportionally if partial payment
                allocated_revenue = service_price * payment_ratio
                
                if service_name in service_revenue:
                    service_revenue[service_name] += allocated_revenue
                else:
                    service_revenue[service_name] = allocated_revenue
        
        conn.close()
        return service_revenue
