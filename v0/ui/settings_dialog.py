# ui/settings_dialog.py
from PyQt6.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QCheckBox, QSpinBox, QComboBox,
                           QFormLayout, QGroupBox, QFileDialog, QMessageBox,
                           QTableWidget, QTableWidgetItem, QDialogButtonBox, QWidget)
from PyQt6.QtCore import Qt
import os
import hashlib

class SettingsDialog(QDialog):
    def __init__(self, db_manager, theme_manager, language_manager, backup_manager, is_admin):
        super().__init__()
        self.db_manager = db_manager
        self.theme_manager = theme_manager
        self.language_manager = language_manager
        self.backup_manager = backup_manager
        self.is_admin = is_admin
        self.tr = self.language_manager.get_translation
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        self.setWindowTitle(self.tr("settings.title"))
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # General tab
        self.general_tab = QWidget()
        self.setup_general_tab()
        self.tab_widget.addTab(self.general_tab, self.tr("settings.general"))
        
        # Backup tab
        self.backup_tab = QWidget()
        self.setup_backup_tab()
        self.tab_widget.addTab(self.backup_tab, self.tr("settings.backup"))
        
        # Users tab (admin only)
        if self.is_admin:
            self.users_tab = QWidget()
            self.setup_users_tab()
            self.tab_widget.addTab(self.users_tab, self.tr("settings.users"))
        
        # About tab
        self.about_tab = QWidget()
        self.setup_about_tab()
        self.tab_widget.addTab(self.about_tab, self.tr("settings.about"))
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def setup_general_tab(self):
        layout = QVBoxLayout(self.general_tab)
        
        # Clinic info group
        clinic_group = QGroupBox(self.tr("settings.clinic_info"))
        clinic_layout = QFormLayout(clinic_group)
        
        self.clinic_name_edit = QLineEdit()
        clinic_layout.addRow(self.tr("settings.clinic_name"), self.clinic_name_edit)
        
        self.clinic_phone_edit = QLineEdit()
        clinic_layout.addRow(self.tr("settings.clinic_phone"), self.clinic_phone_edit)
        
        self.clinic_address_edit = QLineEdit()
        clinic_layout.addRow(self.tr("settings.clinic_address"), self.clinic_address_edit)
        
        self.clinic_email_edit = QLineEdit()
        clinic_layout.addRow(self.tr("settings.clinic_email"), self.clinic_email_edit)
        
        layout.addWidget(clinic_group)
        
        # Notifications group
        notifications_group = QGroupBox(self.tr("settings.notifications"))
        notifications_layout = QFormLayout(notifications_group)
        
        self.appointment_reminder_check = QCheckBox()
        notifications_layout.addRow(self.tr("settings.appointment_reminder"), self.appointment_reminder_check)
        
        self.reminder_hours_spin = QSpinBox()
        self.reminder_hours_spin.setRange(1, 72)
        notifications_layout.addRow(self.tr("settings.reminder_hours"), self.reminder_hours_spin)
        
        layout.addWidget(notifications_group)
        
        # Add spacer
        layout.addStretch()
    
    def setup_backup_tab(self):
        layout = QVBoxLayout(self.backup_tab)
        
        # Backup settings group
        backup_group = QGroupBox(self.tr("settings.backup"))
        backup_layout = QFormLayout(backup_group)
        
        self.auto_backup_check = QCheckBox()
        backup_layout.addRow(self.tr("settings.auto_backup"), self.auto_backup_check)
        
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 30)
        backup_layout.addRow(self.tr("settings.backup_interval"), self.backup_interval_spin)
        
        # Backup location
        backup_location_layout = QHBoxLayout()
        self.backup_location_edit = QLineEdit()
        self.backup_location_edit.setReadOnly(True)
        
        browse_button = QPushButton("...")
        browse_button.setMaximumWidth(30)
        browse_button.clicked.connect(self.browse_backup_location)
        
        backup_location_layout.addWidget(self.backup_location_edit)
        backup_location_layout.addWidget(browse_button)
        
        backup_layout.addRow(self.tr("settings.backup_location"), backup_location_layout)
        
        layout.addWidget(backup_group)
        
        # Backup actions group
        actions_group = QGroupBox(self.tr("common.actions"))
        actions_layout = QVBoxLayout(actions_group)
        
        # Backup now button
        backup_now_button = QPushButton(self.tr("settings.backup_now"))
        backup_now_button.clicked.connect(self.backup_now)
        actions_layout.addWidget(backup_now_button)
        
        # Restore backup button
        restore_backup_button = QPushButton(self.tr("settings.restore_backup"))
        restore_backup_button.clicked.connect(self.restore_backup)
        actions_layout.addWidget(restore_backup_button)
        
        layout.addWidget(actions_group)
        
        # Available backups group
        backups_group = QGroupBox(self.tr("available_backups"))
        backups_layout = QVBoxLayout(backups_group)
        
        self.backups_table = QTableWidget()
        self.backups_table.setColumnCount(3)
        self.backups_table.setHorizontalHeaderLabels([
            self.tr("filename"),
            self.tr("date"),
            self.tr("size")
        ])
        self.backups_table.horizontalHeader().setStretchLastSection(True)
        self.backups_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.backups_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        backups_layout.addWidget(self.backups_table)
        
        # Delete backup button
        delete_backup_button = QPushButton(self.tr("delete_backup"))
        delete_backup_button.clicked.connect(self.delete_backup)
        backups_layout.addWidget(delete_backup_button)
        
        layout.addWidget(backups_group)
        
        # Load available backups
        self.load_available_backups()
    
    def setup_users_tab(self):
        layout = QVBoxLayout(self.users_tab)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels([
            self.tr("settings.username"),
            self.tr("settings.is_admin"),
            self.tr("common.actions")
        ])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.users_table)
        
        # Add user button
        add_user_button = QPushButton(self.tr("settings.add_user"))
        add_user_button.clicked.connect(self.add_user)
        layout.addWidget(add_user_button)
        
        # Load users
        self.load_users()
    
    def setup_about_tab(self):
        layout = QVBoxLayout(self.about_tab)
        
        # App title
        title_label = QLabel(self.tr("app_title"))
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel(f"{self.tr('settings.version')}: 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Developer
        developer_label = QLabel(f"{self.tr('settings.developer')}: Guzel Beauty Clinic")
        developer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(developer_label)
        
        # Contact
        contact_label = QLabel("Contact: +963956961395")
        contact_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(contact_label)
        
        # Address
        address_label = QLabel("سوريا - ريف دمشق التل موقف طيبة مقابل امركز الثقافي الجديد")
        address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(address_label)
        
        # Add spacer
        layout.addStretch()
    
    def load_settings(self):
        # Load clinic info
        self.clinic_name_edit.setText(self.theme_manager.settings.get_setting("clinic_info.name", "مركز جوزيل للتجميل"))
        self.clinic_phone_edit.setText(self.theme_manager.settings.get_setting("clinic_info.phone", "+963956961395"))
        self.clinic_address_edit.setText(self.theme_manager.settings.get_setting("clinic_info.address", "سوريا - ريف دمشق التل موقف طيبة مقابل امركز الثقافي الجديد"))
        self.clinic_email_edit.setText(self.theme_manager.settings.get_setting("clinic_info.email", ""))
        
        # Load notification settings
        self.appointment_reminder_check.setChecked(self.theme_manager.settings.get_setting("notifications.appointment_reminder", True))
        self.reminder_hours_spin.setValue(self.theme_manager.settings.get_setting("notifications.reminder_hours_before", 24))
        
        # Load backup settings
        self.auto_backup_check.setChecked(self.theme_manager.settings.get_setting("backup.auto_backup", True))
        self.backup_interval_spin.setValue(self.theme_manager.settings.get_setting("backup.backup_interval_days", 1))
        self.backup_location_edit.setText(self.theme_manager.settings.get_setting("backup.backup_location", "backups/"))
    
    def save_settings(self):
        # Save clinic info
        self.theme_manager.settings.set_setting("clinic_info.name", self.clinic_name_edit.text())
        self.theme_manager.settings.set_setting("clinic_info.phone", self.clinic_phone_edit.text())
        self.theme_manager.settings.set_setting("clinic_info.address", self.clinic_address_edit.text())
        self.theme_manager.settings.set_setting("clinic_info.email", self.clinic_email_edit.text())
        
        # Save notification settings
        self.theme_manager.settings.set_setting("notifications.appointment_reminder", self.appointment_reminder_check.isChecked())
        self.theme_manager.settings.set_setting("notifications.reminder_hours_before", self.reminder_hours_spin.value())
        
        # Save backup settings
        self.theme_manager.settings.set_setting("backup.auto_backup", self.auto_backup_check.isChecked())
        self.theme_manager.settings.set_setting("backup.backup_interval_days", self.backup_interval_spin.value())
        self.theme_manager.settings.set_setting("backup.backup_location", self.backup_location_edit.text())
        
        self.accept()
    
    def browse_backup_location(self):
        directory = QFileDialog.getExistingDirectory(self, self.tr("select_backup_location"))
        if directory:
            # Ensure the path ends with a slash
            if not directory.endswith('/') and not directory.endswith('\\'):
                directory += '/'
            self.backup_location_edit.setText(directory)
    
    def backup_now(self):
        try:
            backup_path = self.backup_manager.create_backup()
            QMessageBox.information(self, self.tr("common.success"), 
                                   f"{self.tr('backup_created')}: {backup_path}")
            self.load_available_backups()
        except Exception as e:
            QMessageBox.critical(self, self.tr("common.error"), 
                               f"{self.tr('backup_failed')}: {str(e)}")
    
    def restore_backup(self):
        selected_rows = self.backups_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_backup_to_restore"))
            return
        
        # Get the backup path from the hidden data
        backup_path = self.backups_table.item(selected_rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        
        # Confirm restoration
        reply = QMessageBox.question(self, self.tr("common.confirm"), 
                                    self.tr("confirm_restore_backup"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.backup_manager.restore_backup(backup_path)
                QMessageBox.information(self, self.tr("common.success"), self.tr("backup_restored"))
                
                # Inform the user that the application needs to be restarted
                QMessageBox.information(self, self.tr("common.info"), self.tr("restart_required"))
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, self.tr("common.error"), 
                                   f"{self.tr('restore_failed')}: {str(e)}")
    
    def delete_backup(self):
        selected_rows = self.backups_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_backup_to_delete"))
            return
        
        # Get the backup path from the hidden data
        backup_path = self.backups_table.item(selected_rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        
        # Confirm deletion
        reply = QMessageBox.question(self, self.tr("common.confirm"), 
                                    self.tr("common.confirm_delete"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.backup_manager.delete_backup(backup_path)
                QMessageBox.information(self, self.tr("common.success"), self.tr("backup_deleted"))
                self.load_available_backups()
            except Exception as e:
                QMessageBox.critical(self, self.tr("common.error"), 
                                   f"{self.tr('delete_failed')}: {str(e)}")
    
    def load_available_backups(self):
        backups = self.backup_manager.get_available_backups()
        
        self.backups_table.setRowCount(len(backups))
        for i, backup in enumerate(backups):
            # Filename (with hidden path data)
            filename_item = QTableWidgetItem(backup["filename"])
            filename_item.setData(Qt.ItemDataRole.UserRole, backup["path"])
            self.backups_table.setItem(i, 0, filename_item)
            
            # Date
            date_str = backup["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            self.backups_table.setItem(i, 1, QTableWidgetItem(date_str))
            
            # Size
            size_str = self.format_size(backup["size"])
            self.backups_table.setItem(i, 2, QTableWidgetItem(size_str))
        
        # Resize columns to content
        self.backups_table.resizeColumnsToContents()
    
    def format_size(self, size_bytes):
        # Convert bytes to human-readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def load_users(self):
        # This is a simplified implementation
        # In a real application, you would fetch users from the database
        
        # Clear the table
        self.users_table.setRowCount(0)
        
        # Add admin user
        self.users_table.insertRow(0)
        self.users_table.setItem(0, 0, QTableWidgetItem("admin"))
        self.users_table.setItem(0, 1, QTableWidgetItem("✓"))
        
        # Add edit button for admin
        edit_button = QPushButton(self.tr("common.edit"))
        edit_button.clicked.connect(lambda: self.edit_user("admin"))
        self.users_table.setCellWidget(0, 2, edit_button)
        
        # Add regular user
        self.users_table.insertRow(1)
        self.users_table.setItem(1, 0, QTableWidgetItem("user1"))
        self.users_table.setItem(1, 1, QTableWidgetItem(""))
        
        # Add edit and delete buttons for regular user
        user_actions_widget = QWidget()
        user_actions_layout = QHBoxLayout(user_actions_widget)
        user_actions_layout.setContentsMargins(0, 0, 0, 0)
        
        edit_user_button = QPushButton(self.tr("common.edit"))
        edit_user_button.clicked.connect(lambda: self.edit_user("user1"))
        user_actions_layout.addWidget(edit_user_button)
        
        delete_user_button = QPushButton(self.tr("common.delete"))
        delete_user_button.clicked.connect(lambda: self.delete_user("user1"))
        user_actions_layout.addWidget(delete_user_button)
        
        self.users_table.setCellWidget(1, 2, user_actions_widget)
    
    def add_user(self):
        dialog = UserDialog(self.db_manager, self.language_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()
    
    def edit_user(self, username):
        dialog = UserDialog(self.db_manager, self.language_manager, username)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()
    
    def delete_user(self, username):
        # Confirm deletion
        reply = QMessageBox.question(self, self.tr("common.confirm"), 
                                    self.tr("confirm_delete_user").format(username=username),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # In a real application, you would delete the user from the database
            QMessageBox.information(self, self.tr("common.success"), self.tr("user_deleted"))
            self.load_users()


class UserDialog(QDialog):
    def __init__(self, db_manager, language_manager, username=None):
        super().__init__()
        self.db_manager = db_manager
        self.language_manager = language_manager
        self.tr = self.language_manager.get_translation
        self.username = username
        
        self.setup_ui()
        
        if username:
            self.load_user(username)
    
    def setup_ui(self):
        if self.username:
            self.setWindowTitle(self.tr("settings.edit_user"))
        else:
            self.setWindowTitle(self.tr("settings.add_user"))
        
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Username
        self.username_edit = QLineEdit()
        form_layout.addRow(self.tr("settings.username"), self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(self.tr("settings.password"), self.password_edit)
        
        # Is admin
        self.is_admin_check = QCheckBox()
        form_layout.addRow(self.tr("settings.is_admin"), self.is_admin_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton(self.tr("common.save"))
        self.save_button.clicked.connect(self.save_user)
        buttons_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton(self.tr("common.cancel"))
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def load_user(self, username):
        # In a real application, you would fetch the user from the database
        self.username_edit.setText(username)
        self.username_edit.setReadOnly(True)
        
        # Set is_admin based on the username (simplified)
        self.is_admin_check.setChecked(username == "admin")
    
    def save_user(self):
        # Validate inputs
        if not self.username_edit.text():
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("enter_username"))
            return
        
        if not self.username and not self.password_edit.text():
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("enter_password"))
            return
        
        # In a real application, you would save the user to the database
        QMessageBox.information(self, self.tr("common.success"), self.tr("user_saved"))
        self.accept()

