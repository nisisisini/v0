#main.py
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTableWidget, QTableWidgetItem, QCalendarWidget, 
                            QStackedWidget, QComboBox, QCheckBox, QTextEdit,
                            QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
                            QTabWidget, QGroupBox, QScrollArea, QSplitter)
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
import sqlite3
import json
import datetime
import hashlib
import uuid
import locale
from functools import partial

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from config.settings import Settings  # Corrected import path
from utils.theme_manager import ThemeManager
from utils.language_manager import LanguageManager
from backup_manager import BackupManager  # Corrected import path

class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Guzel Beauty Clinic")
        
        # Initialize managers
        self.settings = Settings()
        self.theme_manager = ThemeManager(self.settings)
        self.language_manager = LanguageManager(self.settings)
        self.db_manager = DatabaseManager()
        self.backup_manager = BackupManager(self.db_manager)
        
        # Apply initial theme and language
        self.theme_manager.apply_theme()
        self.language_manager.apply_language()
        
        # Show login window
        self.login_window = LoginWindow(self.db_manager, self.theme_manager, self.language_manager)
        self.login_window.login_successful.connect(self.show_main_window)
        self.login_window.show()
        
        sys.exit(self.app.exec())
    
    def show_main_window(self, username, is_admin):
        self.login_window.hide()
        self.main_window = MainWindow(
            self.db_manager, 
            self.theme_manager, 
            self.language_manager,
            self.backup_manager,
            username,
            is_admin
        )
        self.main_window.logout_signal.connect(self.logout)
        self.main_window.show()
    
    def logout(self):
        self.main_window.close()
        self.login_window.clear_fields()
        self.login_window.show()

if __name__ == "__main__":
    app = Application()
