# models\services_model.py
import sqlite3
from models.database import DatabaseManager

class ServicesModel:
    """Model for service-related database operations."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    def get_all_services(self):
        """Get all services from the database."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM services ORDER BY name")
        services = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return services
    
    def get_service(self, service_id):
        """Get a service by ID."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        service = cursor.fetchone()
        
        conn.close()
        return dict(service) if service else None
    
    def search_services(self, search_term):
        """Search for services by name."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM services 
        WHERE name LIKE ?
        ORDER BY name
        ''', (f'%{search_term}%',))
        
        services = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return services
    
    def add_service(self, name, price):
        """Add a new service."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO services (name, price) VALUES (?, ?)",
                (name, price)
            )
            
            service_id = cursor.lastrowid
            conn.commit()
            return service_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_service(self, service_id, name, price):
        """Update a service."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE services SET name = ?, price = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (name, price, service_id)
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_service(self, service_id):
        """Delete a service."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if service exists
            cursor.execute("SELECT id FROM services WHERE id = ?", (service_id,))
            if not cursor.fetchone():
                raise ValueError(f"Service with ID {service_id} not found")
            
            # Delete service
            cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

