# views/tabs/services_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QDialog,
                           QFormLayout, QLineEdit, QDoubleSpinBox, QMessageBox)
from PyQt6.QtCore import Qt

class ServicesTab(QWidget):
    def __init__(self, db_manager, language_manager, is_admin):
        super().__init__()
        self.db_manager = db_manager
        self.language_manager = language_manager
        self.is_admin = is_admin
        self.tr = self.language_manager.get_translation
        
        self.setup_ui()
        self.load_services()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self.tr("services.title"))
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Services table
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(3)
        self.services_table.setHorizontalHeaderLabels([
            self.tr("services.id"),
            self.tr("services.name"),
            self.tr("services.price")
        ])
        self.services_table.horizontalHeader().setStretchLastSection(True)
        self.services_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.services_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.services_table.doubleClicked.connect(self.view_service)
        
        layout.addWidget(self.services_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add service button
        self.add_button = QPushButton(self.tr("services.add"))
        self.add_button.clicked.connect(self.add_service)
        buttons_layout.addWidget(self.add_button)
        
        # Edit service button
        self.edit_button = QPushButton(self.tr("services.edit"))
        self.edit_button.clicked.connect(self.edit_service)
        buttons_layout.addWidget(self.edit_button)
        
        # Delete service button
        self.delete_button = QPushButton(self.tr("services.delete"))
        self.delete_button.clicked.connect(self.delete_service)
        buttons_layout.addWidget(self.delete_button)
        
        # Add buttons layout to main layout
        layout.addLayout(buttons_layout)
    
    def load_services(self):
        services = self.db_manager.get_all_services()
        
        self.services_table.setRowCount(len(services))
        for i, service in enumerate(services):
            # ID
            self.services_table.setItem(i, 0, QTableWidgetItem(str(service["id"])))
            
            # Name
            self.services_table.setItem(i, 1, QTableWidgetItem(service["name"]))
            
            # Price
            price_text = f"{service['price']:,.0f} {self.tr('services.price_currency')}"
            self.services_table.setItem(i, 2, QTableWidgetItem(price_text))
        
        # Resize columns to content
        self.services_table.resizeColumnsToContents()

    def refresh(self):
        # Clear existing data
        self.services_table.clearContents()
        # Reload data with updated language
        self.load_services()
    
    def search(self, text):
        if not text:
            self.load_services()
            return
        
        # Filter services by name
        services = self.db_manager.get_all_services()
        filtered_services = [s for s in services if text.lower() in s["name"].lower()]
        
        self.services_table.setRowCount(len(filtered_services))
        for i, service in enumerate(filtered_services):
            # ID
            self.services_table.setItem(i, 0, QTableWidgetItem(str(service["id"])))
            
            # Name
            self.services_table.setItem(i, 1, QTableWidgetItem(service["name"]))
            
            # Price
            price_text = f"{service['price']:,.0f} {self.tr('services.price_currency')}"
            self.services_table.setItem(i, 2, QTableWidgetItem(price_text))
        
        # Resize columns to content
        self.services_table.resizeColumnsToContents()
    
    def add_service(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
            
        dialog = ServiceDialog(self.db_manager, self.language_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_services()
    
    def edit_service(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
            
        selected_rows = self.services_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_service_to_edit"))
            return
        
        # Get the service ID from the first column
        service_id = int(self.services_table.item(selected_rows[0].row(), 0).text())
        
        dialog = ServiceDialog(self.db_manager, self.language_manager, service_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_services()
    
    def delete_service(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
            
        selected_rows = self.services_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_service_to_delete"))
            return
        
        # Get the service ID from the first column
        service_id = int(self.services_table.item(selected_rows[0].row(), 0).text())
        
        # Confirm deletion
        reply = QMessageBox.question(self, self.tr("common.confirm"), 
                                    self.tr("common.confirm_delete"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.delete_service(service_id)
                self.load_services()
                QMessageBox.information(self, self.tr("common.success"), self.tr("common.operation_success"))
            except Exception as e:
                QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")
    
    def view_service(self):
        selected_rows = self.services_table.selectedIndexes()
        if not selected_rows:
            return
        
        # Get the service ID from the first column
        service_id = int(self.services_table.item(selected_rows[0].row(), 0).text())
        
        dialog = ServiceDialog(self.db_manager, self.language_manager, service_id, view_only=True)
        dialog.exec()


class ServiceDialog(QDialog):
    def __init__(self, db_manager, language_manager, service_id=None, view_only=False):
        super().__init__()
        self.db_manager = db_manager
        self.language_manager = language_manager
        self.tr = self.language_manager.get_translation
        self.service_id = service_id
        self.view_only = view_only
        
        self.setup_ui()
        
        if service_id:
            self.load_service(service_id)
    
    def setup_ui(self):
        if self.service_id:
            if self.view_only:
                self.setWindowTitle(self.tr("services.service_details"))
            else:
                self.setWindowTitle(self.tr("services.edit"))
        else:
            self.setWindowTitle(self.tr("services.add"))
        
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Name
        self.name_edit = QLineEdit()
        form_layout.addRow(self.tr("services.name"), self.name_edit)
        
        # Price
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000000000)
        self.price_spin.setSingleStep(1000)
        self.price_spin.setSuffix(f" {self.tr('services.price_currency')}")
        form_layout.addRow(self.tr("services.price"), self.price_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        if not self.view_only:
            self.save_button = QPushButton(self.tr("common.save"))
            self.save_button.clicked.connect(self.save_service)
            buttons_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton(self.tr("common.cancel"))
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Set read-only if view only
        if self.view_only:
            self.name_edit.setReadOnly(True)
            self.price_spin.setReadOnly(True)
    
    def load_service(self, service_id):
        service = self.db_manager.get_service(service_id)
        
        # Set values
        self.name_edit.setText(service["name"])
        self.price_spin.setValue(service["price"])
    
    def save_service(self):
        # Validate inputs
        if not self.name_edit.text():
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("enter_service_name"))
            return
        
        # Collect data
        name = self.name_edit.text()
        price = self.price_spin.value()
        
        try:
            if self.service_id:
                # Update existing service
                self.db_manager.update_service(self.service_id, name, price)
            else:
                # Add new service
                self.db_manager.add_service(name, price)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")
