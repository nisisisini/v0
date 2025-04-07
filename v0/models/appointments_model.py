# models\appointments_model.py
import json
import sqlite3
import datetime
from models.database import DatabaseManager

class AppointmentsModel:
    """Model for appointment-related database operations."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    def get_all_appointments(self):
        """Get all appointments from the database."""
        conn = self.db_manager.get_connection()
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
        """Get an appointment by ID."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT a.*, c.name as customer_name, c.phone as customer_phone
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        WHERE a.id = ?
        ''', (appointment_id,))
        
        appointment = cursor.fetchone()
        
        conn.close()
        
        if not appointment:
            return None
        
        appointment_dict = dict(appointment)
        
        # Parse JSON fields
        appointment_dict['services'] = json.loads(appointment_dict['services'])
        
        return appointment_dict
    
    def get_appointments_by_date(self, date):
        """Get appointments for a specific date."""
        conn = self.db_manager.get_connection()
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
    
    def get_appointments_by_customer(self, customer_id):
        """Get appointments for a specific customer."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT a.*, c.name as customer_name, c.phone as customer_phone
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        WHERE a.customer_id = ?
        ORDER BY a.date_time
        ''', (customer_id,))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for appointment in appointments:
            appointment['services'] = json.loads(appointment['services'])
        
        return appointments
    
    def search_appointments(self, search_term):
        """Search for appointments by customer name, phone, or service provider."""
        conn = self.db_manager.get_connection()
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
    
    def add_appointment(self, appointment_data):
        """Add a new appointment."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
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
            return appointment_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_appointment(self, appointment_id, appointment_data):
        """Update an appointment."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
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
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_appointment(self, appointment_id):
        """Delete an appointment."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if appointment exists
            cursor.execute("SELECT id FROM appointments WHERE id = ?", (appointment_id,))
            if not cursor.fetchone():
                raise ValueError(f"Appointment with ID {appointment_id} not found")
            
            # Delete appointment
            cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_upcoming_appointments(self, days=7):
        """Get upcoming appointments for the next X days."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get current date and future date
        today = datetime.date.today()
        future_date = today + datetime.timedelta(days=days)
        
        # Format dates as YYYY-MM-DD
        today_str = today.strftime('%Y-%m-%d')
        future_str = future_date.strftime('%Y-%m-%d')
        
        cursor.execute('''
        SELECT a.*, c.name as customer_name, c.phone as customer_phone
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        WHERE date(a.date_time) BETWEEN ? AND ?
        ORDER BY a.date_time
        ''', (today_str, future_str))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for appointment in appointments:
            appointment['services'] = json.loads(appointment['services'])
        
        return appointments

