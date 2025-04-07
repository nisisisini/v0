# views\login_view.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QCheckBox, QPushButton, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from controllers.auth_controller import AuthController

class LoginView(QDialog):
    """Login dialog for user authentication."""
    
    login_successful = pyqtSignal(str, bool)
    
    def __init__(self, db_manager, settings, translation_manager):
        super().__init__()
        self.db_manager = db_manager
        self.settings = settings
        self.translation_manager = translation_manager
        self.tr = self.translation_manager.get_translation
        self.auth_controller = AuthController(db_manager)
        
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle(self.tr("login.title"))
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel(self.tr("app_title"))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Username
        username_label = QLabel(self.tr("login.username"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(self.tr("login.username"))
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        
        # Password field with integrated eye icon
        password_label = QLabel(self.tr("login.password"))
        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(self.tr("login.password"))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(self.username_input.width())  # Match fixed width with username input
        password_layout.addWidget(self.password_input)
        
        # Eye icon button
        self.toggle_password_button = QPushButton()
        self.toggle_password_button.setFixedSize(30, 30)
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        self.toggle_password_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0;
                margin: 0;
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(0,0,0,0.1);
            }
        """)
        self.toggle_password_button.setIcon(QIcon("resources/assets/icons/eye-closed.png"))
        password_layout.addWidget(self.toggle_password_button)
        
        layout.addWidget(password_label)
        layout.addLayout(password_layout)
        
        # Remember me
        self.remember_me = QCheckBox(self.tr("login.remember_me"))
        layout.addWidget(self.remember_me)
        
        # Login button
        self.login_button = QPushButton(self.tr("login.login_button"))
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        
        # Set layout
        self.setLayout(layout)
        
        # Connect enter key to login
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)
    
    def toggle_password_visibility(self):
        if self.toggle_password_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_button.setIcon(QIcon("resources/assets/icons/eye-open.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_button.setIcon(QIcon("resources/assets/icons/eye-closed.png"))
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, self.tr("common.error"), self.tr("login.error"))
            return
        
        success, is_admin = self.auth_controller.login(username, password)
        
        if success:
            self.login_successful.emit(username, is_admin)
        else:
            QMessageBox.warning(self, self.tr("common.error"), self.tr("login.error"))
    
    def clear_fields(self):
        if not self.remember_me.isChecked():
            self.username_input.clear()
            self.password_input.clear()

