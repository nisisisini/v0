# controller/auth_controller.py
import hashlib
from models.database import DatabaseManager
import sqlite3

class AuthController:
    """Controller for authentication-related operations."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    def login(self, username, password):
        """Authenticate a user."""
        if not username or not password:
            return False, False
        
        return self.db_manager.verify_login(username, password)
    
    def change_password(self, username, old_password, new_password):
        """Change a user's password."""
        # Verify current password
        success, _ = self.login(username, old_password)
        if not success:
            return False
        
        # Get user ID
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False
        
        user_id = user[0]
        
        # Update password
        try:
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (self._hash_password(new_password), user_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.rollback()
            conn.close()
            return False
    
    def add_user(self, username, password, is_admin):
        """Add a new user."""
        if not username or not password:
            return False
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                return False
            
            # Add new user
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (username, self._hash_password(password), is_admin)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.rollback()
            conn.close()
            return False
    
    def update_user(self, username, new_username=None, new_password=None, is_admin=None):
        """Update a user."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False
            
            user_id = user[0]
            
            # Update fields
            if new_username:
                # Check if new username already exists
                if new_username != username:
                    cursor.execute("SELECT id FROM users WHERE username = ?", (new_username,))
                    if cursor.fetchone():
                        conn.close()
                        return False
                
                cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
            
            if new_password:
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (self._hash_password(new_password), user_id)
                )
            
            if is_admin is not None:
                cursor.execute("UPDATE users SET is_admin = ? WHERE id = ?", (is_admin, user_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.rollback()
            conn.close()
            return False
    
    def delete_user(self, username):
        """Delete a user."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True
        except:
            conn.rollback()
            conn.close()
            return False
    
    def get_all_users(self):
        """Get all users."""
        conn = self.db_manager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin FROM users")
        users = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return users
    
    def _hash_password(self, password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

