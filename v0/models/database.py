# models\database.py
import sqlite3
import os
import datetime
import json
from config.constants import DB_FILE

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.db_path = DB_FILE
        self._ensure_data_dir()
        self._initialize_database()
    
    def _ensure_data_dir(self):
        """Ensure the database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _initialize_database(self):
        """Initialize the database schema if it doesn't exist."""
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
                ("admin", self._hash_password("admin"), True)
            )
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'user1'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                ("user1", self._hash_password("user1"), False)
            )
        
        # Insert default services
        self._insert_default_services(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_default_services(self, cursor):
        """Insert default services into the database."""
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
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def _hash_password(self, password):
        """Hash a password using SHA-256."""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_login(self, username, password):
        """Verify login credentials."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT password_hash, is_admin FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == self._hash_password(password):
            return True, result[1]  # Success, is_admin
        return False, False

