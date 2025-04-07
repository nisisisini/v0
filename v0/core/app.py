# core/app.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale
from config.settings import Settings
from models.database import DatabaseManager
from utils.translator import TranslationManager
from backup_manager import BackupManager
from utils.whatsapp_sender import NotificationManager
from core.router import Router

class Application:
    """Main application class that initializes the app and manages global resources."""
    
    def __init__(self):
        # Create application instance
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Guzel Beauty Clinic")
        self.app.setOrganizationName("Guzel")
        
        # Ensure data directories exist
        self._ensure_directories()
        
        # Initialize managers
        self.settings = Settings()
        self.db_manager = DatabaseManager()
        self.translation_manager = TranslationManager(self.settings)
        self.backup_manager = BackupManager(self.db_manager)
        self.notification_manager = NotificationManager(self.settings)
        
        # Apply initial settings
        self._apply_settings()
        
        # Initialize router
        self.router = Router(
            self.db_manager,
            self.settings,
            self.translation_manager,
            self.backup_manager,
            self.notification_manager
        )
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            "data",
            "data/translations",
            "backups",
            "logs"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _apply_settings(self):
        """Apply initial application settings."""
        # Apply language
        self.translation_manager.apply_language()
        
        # Apply theme
        theme_name = self.settings.get_setting("theme", "light")
        theme_file = f"styles/{theme_name}.qss"
        
        if os.path.exists(theme_file):
            with open(theme_file, "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())
    
    def run(self):
        """Run the application."""
        # Show the login screen
        self.router.show_login()
        
        # Start the application event loop
        return self.app.exec()

