# models\clients_model.py
import json
import sqlite3
from models.database import DatabaseManager

class ClientsModel:
    """Model for client-related database operations."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    def get_all_clients(self):
        """Get all clients from the database."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers ORDER BY name")
        clients = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for client in clients:
            if client['most_requested_services']:
                client['most_requested_services'] = json.loads(client['most_requested_services'])
            else:
                client['most_requested_services'] = []
        
        return clients
    
    def get_client(self, client_id):
        """Get a client by ID."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers WHERE id = ?", (client_id,))
        client = cursor.fetchone()
        
        conn.close()
        
        if not client:
            return None
        
        client_dict = dict(client)
        
        # Parse JSON fields
        if client_dict['most_requested_services']:
            client_dict['most_requested_services'] = json.loads(client_dict['most_requested_services'])
        else:
            client_dict['most_requested_services'] = []
        
        return client_dict
    
    def search_clients(self, search_term):
        """Search for clients by name, phone, or email."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM customers 
        WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
        ORDER BY name
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        clients = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Parse JSON fields
        for client in clients:
            if client['most_requested_services']:
                client['most_requested_services'] = json.loads(client['most_requested_services'])
            else:
                client['most_requested_services'] = []
        
        return clients
    
    def add_client(self, client_data):
        """Add a new client."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO customers (
                name, phone, email, hair_type, hair_color, skin_type, 
                allergies, current_sessions, remaining_sessions, 
                most_requested_services, remaining_payments, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client_data['name'],
                client_data['phone'],
                client_data.get('email', ''),
                client_data.get('hair_type', ''),
                client_data.get('hair_color', ''),
                client_data.get('skin_type', ''),
                client_data.get('allergies', ''),
                client_data.get('current_sessions', 0),
                client_data.get('remaining_sessions', 0),
                json.dumps(client_data.get('most_requested_services', [])),
                client_data.get('remaining_payments', 0),
                client_data.get('notes', '')
            ))
            
            client_id = cursor.lastrowid
            conn.commit()
            return client_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_client(self, client_id, client_data):
        """Update a client."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
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
                client_data['name'],
                client_data['phone'],
                client_data.get('email', ''),
                client_data.get('hair_type', ''),
                client_data.get('hair_color', ''),
                client_data.get('skin_type', ''),
                client_data.get('allergies', ''),
                client_data.get('current_sessions', 0),
                client_data.get('remaining_sessions', 0),
                json.dumps(client_data.get('most_requested_services', [])),
                client_data.get('remaining_payments', 0),
                client_data.get('notes', ''),
                client_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_client(self, client_id):
        """Delete a client."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if client exists
            cursor.execute("SELECT id FROM customers WHERE id = ?", (client_id,))
            if not cursor.fetchone():
                raise ValueError(f"Client with ID {client_id} not found")
            
            # Delete client
            cursor.execute("DELETE FROM customers WHERE id = ?", (client_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

