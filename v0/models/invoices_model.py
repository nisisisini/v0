# models\invoices_model.py
import json
import sqlite3
import datetime
from models.database import DatabaseManager

class InvoicesModel:
    """Model for invoice-related database operations."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    def get_all_invoices(self):
        """Get all invoices from the database."""
        conn = self.db_manager.get_connection()
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
        """Get an invoice by ID."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT i.*, c.name as customer_name, c.phone as customer_phone
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE i.id = ?
        ''', (invoice_id,))
        
        invoice = cursor.fetchone()
        
        conn.close()
        
        if not invoice:
            return None
        
        invoice_dict = dict(invoice)
        
        # Parse JSON fields
        invoice_dict['services'] = json.loads(invoice_dict['services'])
        
        return invoice_dict
    
    def search_invoices(self, search_term):
        """Search for invoices by customer name, phone, invoice creator, or service provider."""
        conn = self.db_manager.get_connection()
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
    
    def add_invoice(self, invoice_data):
        """Add a new invoice."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
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
            return invoice_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_invoice(self, invoice_id, invoice_data):
        """Update an invoice."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
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
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_invoice(self, invoice_id):
        """Delete an invoice."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
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
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_daily_revenue(self, date):
        """Get the total revenue for a specific date."""
        conn = self.db_manager.get_connection()
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
        """Get the total revenue for a week starting from a specific date."""
        conn = self.db_manager.get_connection()
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
        """Get the total revenue for a specific month."""
        conn = self.db_manager.get_connection()
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

