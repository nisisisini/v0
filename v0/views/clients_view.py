# views\clients_view.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QDialog,
                           QFormLayout, QLineEdit, QTextEdit, QMessageBox,
                           QSpinBox, QDoubleSpinBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import json
from utils.icon_loader import load_icon

class ClientsView(QWidget):
    """View for managing clients."""
    
    def __init__(self, db_manager, translation_manager, clients_controller, is_admin):
        super().__init__()
        self.db_manager = db_manager
        self.translation_manager = translation_manager
        self.clients_controller = clients_controller
        self.is_admin = is_admin
        self.tr = self.translation_manager.get_translation
        
        self.setup_ui()
        self.load_clients()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self.tr("customers.title"))
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Clients table
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(12)
        self.clients_table.setHorizontalHeaderLabels([
            self.tr("customers.id"),
            self.tr("customers.name"),
            self.tr("customers.phone"),
            self.tr("customers.email"),
            self.tr("customers.hair_type"),
            self.tr("customers.hair_color"),
            self.tr("customers.skin_type"),
            self.tr("customers.allergies"),
            self.tr("customers.current_sessions"),
            self.tr("customers.remaining_sessions"),
            self.tr("customers.most_requested_services"),
            self.tr("customers.remaining_payments")
        ])
        self.clients_table.horizontalHeader().setStretchLastSection(True)
        self.clients_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.clients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.clients_table.doubleClicked.connect(self.view_client)
        
        layout.addWidget(self.clients_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add client button
        self.add_button = QPushButton(self.tr("customers.add"))
        try:
            self.add_button.setIcon(QIcon(load_icon("add.png")))
        except FileNotFoundError:
            print("Warning: add.png icon not found")
        self.add_button.clicked.connect(self.add_client)
        buttons_layout.addWidget(self.add_button)
        
        # Edit client button
        self.edit_button = QPushButton(self.tr("customers.edit"))
        try:
            self.edit_button.setIcon(QIcon(load_icon("edit.png")))
        except FileNotFoundError:
            print("Warning: edit.png icon not found")
        self.edit_button.clicked.connect(self.edit_client)
        buttons_layout.addWidget(self.edit_button)
        
        # Delete client button
        self.delete_button = QPushButton(self.tr("customers.delete"))
        try:
            self.delete_button.setIcon(QIcon(load_icon("delete.png")))
        except FileNotFoundError:
            print("Warning: delete.png icon not found")
        self.delete_button.clicked.connect(self.delete_client)
        buttons_layout.addWidget(self.delete_button)
        
        # Add buttons layout to main layout
        layout.addLayout(buttons_layout)
    
    def load_clients(self):
        clients = self.clients_controller.get_all_clients()
        
        self.clients_table.setRowCount(len(clients))
        for i, client in enumerate(clients):
            # ID
            self.clients_table.setItem(i, 0, QTableWidgetItem(str(client["id"])))
            
            # Name
            self.clients_table.setItem(i, 1, QTableWidgetItem(client["name"]))
            
            # Phone
            self.clients_table.setItem(i, 2, QTableWidgetItem(client["phone"]))
            
            # Email
            self.clients_table.setItem(i, 3, QTableWidgetItem(client["email"] or ""))
            
            # Hair type
            self.clients_table.setItem(i, 4, QTableWidgetItem(client["hair_type"] or ""))
            
            # Hair color
            self.clients_table.setItem(i, 5, QTableWidgetItem(client["hair_color"] or ""))
            
            # Skin type
            self.clients_table.setItem(i, 6, QTableWidgetItem(client["skin_type"] or ""))
            
            # Allergies
            self.clients_table.setItem(i, 7, QTableWidgetItem(client["allergies"] or ""))
            
            # Current sessions
            self.clients_table.setItem(i, 8, QTableWidgetItem(str(client["current_sessions"])))
            
            # Remaining sessions
            self.clients_table.setItem(i, 9, QTableWidgetItem(str(client["remaining_sessions"])))
            
            # Most requested services
            most_requested = ", ".join(client["most_requested_services"]) if client["most_requested_services"] else ""
            self.clients_table.setItem(i, 10, QTableWidgetItem(most_requested))
            
            # Remaining payments
            remaining_payments = f"{client['remaining_payments']:,.0f} {self.tr('services.price_currency')}" if client["remaining_payments"] > 0 else ""
            self.clients_table.setItem(i, 11, QTableWidgetItem(remaining_payments))
        
        # Resize columns to content
        self.clients_table.resizeColumnsToContents()
    
    def search(self, text):
        if not text:
            self.load_clients()
            return
        
        clients = self.clients_controller.search_clients(text)
        
        self.clients_table.setRowCount(len(clients))
        for i, client in enumerate(clients):
            # ID
            self.clients_table.setItem(i, 0, QTableWidgetItem(str(client["id"])))
            
            # Name
            self.clients_table.setItem(i, 1, QTableWidgetItem(client["name"]))
            
            # Phone
            self.clients_table.setItem(i, 2, QTableWidgetItem(client["phone"]))
            
            # Email
            self.clients_table.setItem(i, 3, QTableWidgetItem(client["email"] or ""))
            
            # Hair type
            self.clients_table.setItem(i, 4, QTableWidgetItem(client["hair_type"] or ""))
            
            # Hair color
            self.clients_table.setItem(i, 5, QTableWidgetItem(client["hair_color"] or ""))
            
            # Skin type
            self.clients_table.setItem(i, 6, QTableWidgetItem(client["skin_type"] or ""))
            
            # Allergies
            self.clients_table.setItem(i, 7, QTableWidgetItem(client["allergies"] or ""))
            
            # Current sessions
            self.clients_table.setItem(i, 8, QTableWidgetItem(str(client["current_sessions"])))
            
            # Remaining sessions
            self.clients_table.setItem(i, 9, QTableWidgetItem(str(client["remaining_sessions"])))
            
            # Most requested services
            most_requested = ", ".join(client["most_requested_services"]) if client["most_requested_services"] else ""
            self.clients_table.setItem(i, 10, QTableWidgetItem(most_requested))
            
            # Remaining payments
            remaining_payments = f"{client['remaining_payments']:,.0f} {self.tr('services.price_currency')}" if client["remaining_payments"] > 0 else ""
            self.clients_table.setItem(i, 11, QTableWidgetItem(remaining_payments))
        
        # Resize columns to content
        self.clients_table.resizeColumnsToContents()
    
    def add_client(self):
        dialog = ClientDialog(self.db_manager, self.translation_manager, self.clients_controller)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_clients()
    
    def edit_client(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
        
        selected_rows = self.clients_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_customer_to_edit"))
            return
        
        # Get the client ID from the first column
        client_id = int(self.clients_table.item(selected_rows[0].row(), 0).text())
        
        dialog = ClientDialog(self.db_manager, self.translation_manager, self.clients_controller, client_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_clients()
    
    def delete_client(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
        
        selected_rows = self.clients_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_customer_to_delete"))
            return
        
        # Get the client ID from the first column
        client_id = int(self.clients_table.item(selected_rows[0].row(), 0).text())
        
        # Confirm deletion
        reply = QMessageBox.question(self, self.tr("common.confirm"), 
                                    self.tr("common.confirm_delete"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.clients_controller.delete_client(client_id)
                self.load_clients()
                QMessageBox.information(self, self.tr("common.success"), self.tr("common.operation_success"))
            except Exception as e:
                QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")
    
    def view_client(self):
        selected_rows = self.clients_table.selectedIndexes()
        if not selected_rows:
            return
        
        # Get the client ID from the first column
        client_id = int(self.clients_table.item(selected_rows[0].row(), 0).text())
        
        dialog = ClientDialog(self.db_manager, self.translation_manager, self.clients_controller, client_id, view_only=True)
        dialog.exec()


class ClientDialog(QDialog):
    """Dialog for adding, editing, or viewing a client."""
    
    def __init__(self, db_manager, translation_manager, clients_controller, client_id=None, view_only=False):
        super().__init__()
        self.db_manager = db_manager
        self.translation_manager = translation_manager
        self.clients_controller = clients_controller
        self.tr = self.translation_manager.get_translation
        self.client_id = client_id
        self.view_only = view_only
        
        self.setup_ui()
        
        if client_id:
            self.load_client(client_id)
    
    def setup_ui(self):
        if self.client_id:
            if self.view_only:
                self.setWindowTitle(self.tr("customers.customer_details"))
            else:
                self.setWindowTitle(self.tr("customers.edit"))
        else:
            self.setWindowTitle(self.tr("customers.add"))
        
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Name
        self.name_edit = QLineEdit()
        form_layout.addRow(self.tr("customers.name"), self.name_edit)
        
        # Phone
        self.phone_edit = QLineEdit()
        form_layout.addRow(self.tr("customers.phone"), self.phone_edit)
        
        # Email
        self.email_edit = QLineEdit()
        form_layout.addRow(self.tr("customers.email"), self.email_edit)
        
        # Hair type
        self.hair_type_edit = QLineEdit()
        form_layout.addRow(self.tr("customers.hair_type"), self.hair_type_edit)
        
        # Hair color
        self.hair_color_edit = QLineEdit()
        form_layout.addRow(self.tr("customers.hair_color"), self.hair_color_edit)
        
        # Skin type
        self.skin_type_edit = QLineEdit()
        form_layout.addRow(self.tr("customers.skin_type"), self.skin_type_edit)
        
        # Allergies
        self.allergies_edit = QLineEdit()
        form_layout.addRow(self.tr("customers.allergies"), self.allergies_edit)
        
        # Current sessions
        self.current_sessions_spin = QSpinBox()
        self.current_sessions_spin.setRange(0, 1000)
        form_layout.addRow(self.tr("customers.current_sessions"), self.current_sessions_spin)
        
        # Remaining sessions
        self.remaining_sessions_spin = QSpinBox()
        self.remaining_sessions_spin.setRange(0, 1000)
        form_layout.addRow(self.tr("customers.remaining_sessions"), self.remaining_sessions_spin)
        
        # Most requested services
        self.services_edit = QLineEdit()
        form_layout.addRow(self.tr("customers.most_requested_services"), self.services_edit)
        
        # Remaining payments
        self.remaining_payments_spin = QDoubleSpinBox()
        self.remaining_payments_spin.setRange(0, 1000000000)
        self.remaining_payments_spin.setSingleStep(1000)
        self.remaining_payments_spin.setSuffix(f" {self.tr('services.price_currency')}")
        form_layout.addRow(self.tr("customers.remaining_payments"), self.remaining_payments_spin)
        
        # Notes
        self.notes_edit = QTextEdit()
        form_layout.addRow(self.tr("customers.notes"), self.notes_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        if not self.view_only:
            self.save_button = QPushButton(self.tr("common.save"))
            self.save_button.clicked.connect(self.save_client)
            buttons_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton(self.tr("common.cancel"))
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Set read-only if view only
        if self.view_only:
            self.name_edit.setReadOnly(True)
            self.phone_edit.setReadOnly(True)
            self.email_edit.setReadOnly(True)
            self.hair_type_edit.setReadOnly(True)
            self.hair_color_edit.setReadOnly(True)
            self.skin_type_edit.setReadOnly(True)
            self.allergies_edit.setReadOnly(True)
            self.current_sessions_spin.setReadOnly(True)
            self.remaining_sessions_spin.setReadOnly(True)
            self.services_edit.setReadOnly(True)
            self.remaining_payments_spin.setReadOnly(True)
            self.notes_edit.setReadOnly(True)
    
    def load_client(self, client_id):
        client = self.clients_controller.get_client(client_id)
        
        # Set basic info
        self.name_edit.setText(client["name"])
        self.phone_edit.setText(client["phone"])
        self.email_edit.setText(client["email"] or "")
        self.hair_type_edit.setText(client["hair_type"] or "")
        self.hair_color_edit.setText(client["hair_color"] or "")
        self.skin_type_edit.setText(client["skin_type"] or "")
        self.allergies_edit.setText(client["allergies"] or "")
        
        # Set numeric values
        self.current_sessions_spin.setValue(client["current_sessions"])
        self.remaining_sessions_spin.setValue(client["remaining_sessions"])
        self.remaining_payments_spin.setValue(client["remaining_payments"])
        
        # Set most requested services
        self.services_edit.setText(", ".join(client["most_requested_services"]))
        
        # Set notes
        self.notes_edit.setText(client["notes"] or "")
    
    def save_client(self):
        # Validate inputs
        if not self.name_edit.text():
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("enter_customer_name"))
            return
        
        if not self.phone_edit.text():
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("enter_customer_phone"))
            return
        
        # Collect data
        name = self.name_edit.text()
        phone = self.phone_edit.text()
        email = self.email_edit.text()
        hair_type = self.hair_type_edit.text()
        hair_color = self.hair_color_edit.text()
        skin_type = self.skin_type_edit.text()
        allergies = self.allergies_edit.text()
        current_sessions = self.current_sessions_spin.value()
        remaining_sessions = self.remaining_sessions_spin.value()
        most_requested_services = [s.strip() for s in self.services_edit.text().split(",")] if self.services_edit.text() else []
        remaining_payments = self.remaining_payments_spin.value()
        notes = self.notes_edit.toPlainText()
        
        # Create client data
        client_data = {
            "name": name,
            "phone": phone,
            "email": email,
            "hair_type": hair_type,
            "hair_color": hair_color,
            "skin_type": skin_type,
            "allergies": allergies,
            "current_sessions": current_sessions,
            "remaining_sessions": remaining_sessions,
            "most_requested_services": most_requested_services,
            "remaining_payments": remaining_payments,
            "notes": notes
        }
        
        try:
            if self.client_id:
                # Update existing client
                self.clients_controller.update_client(self.client_id, client_data)
            else:
                # Add new client
                self.clients_controller.add_client(client_data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")

