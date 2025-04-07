# models\user_model.py
import hashlib
import sqlite3
from models.database import DatabaseManager

class UserModel:
    """Model for user-related database operations."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    def get_all_users(self):
        """Get all users from the database."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin, created_at FROM users")
        users = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return users
    
    def get_user(self, user_id):
        """Get a user by ID."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    def get_user_by_username(self, username):
        """Get a user by username."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin, created_at FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    def add_user(self, username, password, is_admin):
        """Add a new user."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (username, self._hash_password(password), is_admin)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_user(self, user_id, username=None, password=None, is_admin=None):
        """Update a user."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get current user data
            cursor.execute("SELECT username, is_admin FROM users WHERE id = ?", (user_id,))
            current_user = cursor.fetchone()
            
            if not current_user:
                raise ValueError(f"User with ID {user_id} not found")
            
            # Update fields that are provided
            update_fields = []
            params = []
            
            if username is not None:
                update_fields.append("username = ?")
                params.append(username)
            
            if password is not None:
                update_fields.append("password_hash = ?")
                params.append(self._hash_password(password))
            
            if is_admin is not None:
                update_fields.append("is_admin = ?")
                params.append(is_admin)
            
            if update_fields:
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                params.append(user_id)
                cursor.execute(query, params)
                conn.commit()
                return True
            
            return False
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_user(self, user_id):
        """Delete a user."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cursor.fetchone():
                raise ValueError(f"User with ID {user_id} not found")
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def change_password(self, user_id, new_password):
        """Change a user's password."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (self._hash_password(new_password), user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _hash_password(self, password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

