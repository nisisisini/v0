# views/tabs/customers_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QDialog,
                           QFormLayout, QLineEdit, QTextEdit, QMessageBox,
                           QSpinBox, QDoubleSpinBox, QComboBox)
from PyQt6.QtCore import Qt
import json

class CustomersTab(QWidget):
    def __init__(self, db_manager, language_manager, is_admin):
        super().__init__()
        self.db_manager = db_manager
        self.language_manager = language_manager
        self.is_admin = is_admin
        self.tr = self.language_manager.get_translation
        
        self.setup_ui()
        self.load_customers()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self.tr("customers.title"))
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(12)
        self.customers_table.setHorizontalHeaderLabels([
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
        self.customers_table.horizontalHeader().setStretchLastSection(True)
        self.customers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.customers_table.doubleClicked.connect(self.view_customer)
        
        layout.addWidget(self.customers_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add customer button
        self.add_button = QPushButton(self.tr("customers.add"))
        self.add_button.clicked.connect(self.add_customer)
        buttons_layout.addWidget(self.add_button)
        
        # Edit customer button
        self.edit_button = QPushButton(self.tr("customers.edit"))
        self.edit_button.clicked.connect(self.edit_customer)
        buttons_layout.addWidget(self.edit_button)
        
        # Delete customer button
        self.delete_button = QPushButton(self.tr("customers.delete"))
        self.delete_button.clicked.connect(self.delete_customer)
        buttons_layout.addWidget(self.delete_button)
        
        # Add buttons layout to main layout
        layout.addLayout(buttons_layout)

        # Initialize table attribute
        self.table = self.customers_table
    
    def load_customers(self):
        customers = self.db_manager.get_all_customers()
        
        self.customers_table.setRowCount(len(customers))
        for i, customer in enumerate(customers):
            # ID
            self.customers_table.setItem(i, 0, QTableWidgetItem(str(customer["id"])))
            
            # Name
            self.customers_table.setItem(i, 1, QTableWidgetItem(customer["name"]))
            
            # Phone
            self.customers_table.setItem(i, 2, QTableWidgetItem(customer["phone"]))
            
            # Email
            self.customers_table.setItem(i, 3, QTableWidgetItem(customer["email"] or ""))
            
            # Hair type
            self.customers_table.setItem(i, 4, QTableWidgetItem(customer["hair_type"] or ""))
            
            # Hair color
            self.customers_table.setItem(i, 5, QTableWidgetItem(customer["hair_color"] or ""))
            
            # Skin type
            self.customers_table.setItem(i, 6, QTableWidgetItem(customer["skin_type"] or ""))
            
            # Allergies
            self.customers_table.setItem(i, 7, QTableWidgetItem(customer["allergies"] or ""))
            
            # Current sessions
            self.customers_table.setItem(i, 8, QTableWidgetItem(str(customer["current_sessions"])))
            
            # Remaining sessions
            self.customers_table.setItem(i, 9, QTableWidgetItem(str(customer["remaining_sessions"])))
            
            # Most requested services
            most_requested = ", ".join(customer["most_requested_services"]) if customer["most_requested_services"] else ""
            self.customers_table.setItem(i, 10, QTableWidgetItem(most_requested))
            
            # Remaining payments
            remaining_payments = f"{customer['remaining_payments']:,.0f} {self.tr('services.price_currency')}" if customer["remaining_payments"] > 0 else ""
            self.customers_table.setItem(i, 11, QTableWidgetItem(remaining_payments))
        
        # Resize columns to content
        self.customers_table.resizeColumnsToContents()
    
    def search(self, text):
        if not text:
            self.load_customers()
            return
        
        customers = self.db_manager.search_customers(text)
        
        self.customers_table.setRowCount(len(customers))
        for i, customer in enumerate(customers):
            # ID
            self.customers_table.setItem(i, 0, QTableWidgetItem(str(customer["id"])))
            
            # Name
            self.customers_table.setItem(i, 1, QTableWidgetItem(customer["name"]))
            
            # Phone
            self.customers_table.setItem(i, 2, QTableWidgetItem(customer["phone"]))
            
            # Email
            self.customers_table.setItem(i, 3, QTableWidgetItem(customer["email"] or ""))
            
            # Hair type
            self.customers_table.setItem(i, 4, QTableWidgetItem(customer["hair_type"] or ""))
            
            # Hair color
            self.customers_table.setItem(i, 5, QTableWidgetItem(customer["hair_color"] or ""))
            
            # Skin type
            self.customers_table.setItem(i, 6, QTableWidgetItem(customer["skin_type"] or ""))
            
            # Allergies
            self.customers_table.setItem(i, 7, QTableWidgetItem(customer["allergies"] or ""))
            
            # Current sessions
            self.customers_table.setItem(i, 8, QTableWidgetItem(str(customer["current_sessions"])))
            
            # Remaining sessions
            self.customers_table.setItem(i, 9, QTableWidgetItem(str(customer["remaining_sessions"])))
            
            # Most requested services
            most_requested = ", ".join(customer["most_requested_services"]) if customer["most_requested_services"] else ""
            self.customers_table.setItem(i, 10, QTableWidgetItem(most_requested))
            
            # Remaining payments
            remaining_payments = f"{customer['remaining_payments']:,.0f} {self.tr('services.price_currency')}" if customer["remaining_payments"] > 0 else ""
            self.customers_table.setItem(i, 11, QTableWidgetItem(remaining_payments))
        
        # Resize columns to content
        self.customers_table.resizeColumnsToContents()
    
    def add_customer(self):
        dialog = CustomerDialog(self.db_manager, self.language_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def edit_customer(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
        
        selected_rows = self.customers_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_customer_to_edit"))
            return
        
        # Get the customer ID from the first column
        customer_id = int(self.customers_table.item(selected_rows[0].row(), 0).text())
        
        dialog = CustomerDialog(self.db_manager, self.language_manager, customer_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def delete_customer(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
        
        selected_rows = self.customers_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_customer_to_delete"))
            return
        
        # Get the customer ID from the first column
        customer_id = int(self.customers_table.item(selected_rows[0].row(), 0).text())
        
        # Confirm deletion
        reply = QMessageBox.question(self, self.tr("common.confirm"), 
                                    self.tr("common.confirm_delete"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.delete_customer(customer_id)
                self.load_customers()
                QMessageBox.information(self, self.tr("common.success"), self.tr("common.operation_success"))
            except Exception as e:
                QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")
    
    def view_customer(self):
        selected_rows = self.customers_table.selectedIndexes()
        if not selected_rows:
            return
        
        # Get the customer ID from the first column
        customer_id = int(self.customers_table.item(selected_rows[0].row(), 0).text())
        
        dialog = CustomerDialog(self.db_manager, self.language_manager, customer_id, view_only=True)
        dialog.exec()

    def refresh(self):
        # Clear existing data
        self.table.clearContents()
        # Reload data with updated language
        self.load_customers()


class CustomerDialog(QDialog):
    def __init__(self, db_manager, language_manager, customer_id=None, view_only=False):
        super().__init__()
        self.db_manager = db_manager
        self.language_manager = language_manager
        self.tr = self.language_manager.get_translation
        self.customer_id = customer_id
        self.view_only = view_only
        
        self.setup_ui()
        
        if customer_id:
            self.load_customer(customer_id)
    
    def setup_ui(self):
        if self.customer_id:
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
        self.services_combo = QComboBox()
        self.load_services()
        form_layout.addRow(self.tr("customers.most_requested_services"), self.services_combo)
        
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
            self.save_button.clicked.connect(self.save_customer)
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
            self.services_combo.setEnabled(False)
            self.remaining_payments_spin.setReadOnly(True)
            self.notes_edit.setReadOnly(True)
    
    def load_services(self):
        services = self.db_manager.get_all_services()
        
        self.services_combo.clear()
        for service in services:
            self.services_combo.addItem(service["name"], service["id"])
    
    def load_customer(self, customer_id):
        customer = self.db_manager.get_customer(customer_id)
        
        # Set basic info
        self.name_edit.setText(customer["name"])
        self.phone_edit.setText(customer["phone"])
        self.email_edit.setText(customer["email"] or "")
        self.hair_type_edit.setText(customer["hair_type"] or "")
        self.hair_color_edit.setText(customer["hair_color"] or "")
        self.skin_type_edit.setText(customer["skin_type"] or "")
        self.allergies_edit.setText(customer["allergies"] or "")
        
        # Set numeric values
        self.current_sessions_spin.setValue(customer["current_sessions"])
        self.remaining_sessions_spin.setValue(customer["remaining_sessions"])
        self.remaining_payments_spin.setValue(customer["remaining_payments"])
        
        # Set notes
        self.notes_edit.setText(customer["notes"] or "")
        
        # Set most requested services
        if customer["most_requested_services"]:
            service_name = customer["most_requested_services"][0]
            index = self.services_combo.findText(service_name)
            if index >= 0:
                self.services_combo.setCurrentIndex(index)
    
    def save_customer(self):
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
        most_requested_services = [self.services_combo.currentText()] if self.services_combo.currentIndex() >= 0 else []
        remaining_payments = self.remaining_payments_spin.value()
        notes = self.notes_edit.toPlainText()
        
        # Create customer data
        customer_data = {
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
            if self.customer_id:
                # Update existing customer
                self.db_manager.update_customer(self.customer_id, customer_data)
            else:
                # Add new customer
                self.db_manager.add_customer(customer_data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")
