# core\router.py
from PyQt6.QtCore import QObject, pyqtSignal
from controllers.auth_controller import AuthController
from views.login_view import LoginView
from views.main_view import MainView

class Router(QObject):
    """Handles navigation between different screens in the application."""
    
    def __init__(self, db_manager, settings, translation_manager, backup_manager, notification_manager):
        super().__init__()
        self.db_manager = db_manager
        self.settings = settings
        self.translation_manager = translation_manager
        self.backup_manager = backup_manager
        self.notification_manager = notification_manager
        
        # Initialize controllers
        self.auth_controller = AuthController(db_manager)
        
        # Initialize views
        self.login_view = None
        self.main_view = None
    
    def show_login(self):
        """Show the login screen."""
        if self.main_view:
            self.main_view.close()
            self.main_view = None
        
        if not self.login_view:
            self.login_view = LoginView(
                self.db_manager,
                self.settings,
                self.translation_manager
            )
            self.login_view.login_successful.connect(self.show_main)
        
        self.login_view.show()
    
    def show_main(self, username, is_admin):
        """Show the main application window."""
        if self.login_view:
            self.login_view.hide()
        
        if not self.main_view:
            self.main_view = MainView(
                self.db_manager,
                self.settings,
                self.translation_manager,
                self.backup_manager,
                self.notification_manager,
                username,
                is_admin
            )
            self.main_view.logout_signal.connect(self.show_login)
        
        self.main_view.show()

