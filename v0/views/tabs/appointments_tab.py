# views/tabs/appointments_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QDialog,
                           QFormLayout, QLineEdit, QDateTimeEdit, QComboBox,
                           QTextEdit, QMessageBox, QCheckBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDateTime
import json

class AppointmentsTab(QWidget):
    def __init__(self, db_manager, language_manager, is_admin):
        super().__init__()
        self.db_manager = db_manager
        self.language_manager = language_manager
        self.is_admin = is_admin
        self.tr = self.language_manager.get_translation
        
        self.setup_ui()
        self.load_appointments()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self.tr("appointments.title"))
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Appointments table
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(9)
        self.appointments_table.setHorizontalHeaderLabels([
            self.tr("appointments.id"),
            self.tr("appointments.customer_name"),
            self.tr("appointments.phone"),
            self.tr("appointments.date_time"),
            self.tr("appointments.services"),
            self.tr("appointments.service_provider"),
            self.tr("appointments.notes"),
            self.tr("appointments.status"),
            self.tr("appointments.remaining_payments")
        ])
        self.appointments_table.horizontalHeader().setStretchLastSection(True)
        self.appointments_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.appointments_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.appointments_table.doubleClicked.connect(self.view_appointment)
        
        layout.addWidget(self.appointments_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add appointment button
        self.add_button = QPushButton(self.tr("appointments.add"))
        self.add_button.clicked.connect(self.add_appointment)
        buttons_layout.addWidget(self.add_button)
        
        # Edit appointment button
        self.edit_button = QPushButton(self.tr("appointments.edit"))
        self.edit_button.clicked.connect(self.edit_appointment)
        buttons_layout.addWidget(self.edit_button)
        
        # Delete appointment button
        self.delete_button = QPushButton(self.tr("appointments.delete"))
        self.delete_button.clicked.connect(self.delete_appointment)
        buttons_layout.addWidget(self.delete_button)
        
        # Add buttons layout to main layout
        layout.addLayout(buttons_layout)
    
    def load_appointments(self):
        appointments = self.db_manager.get_all_appointments()
        
        self.appointments_table.setRowCount(len(appointments))
        for i, appointment in enumerate(appointments):
            # ID
            self.appointments_table.setItem(i, 0, QTableWidgetItem(str(appointment["id"])))
            
            # Customer name
            self.appointments_table.setItem(i, 1, QTableWidgetItem(appointment["customer_name"]))
            
            # Phone
            self.appointments_table.setItem(i, 2, QTableWidgetItem(appointment["customer_phone"]))
            
            # Date and time
            date_time = QDateTime.fromString(appointment["date_time"], Qt.DateFormat.ISODate)
            self.appointments_table.setItem(i, 3, QTableWidgetItem(date_time.toString("yyyy-MM-dd hh:mm")))
            
            # Services
            services = ", ".join([service["name"] for service in appointment["services"]])
            self.appointments_table.setItem(i, 4, QTableWidgetItem(services))
            
            # Service provider
            self.appointments_table.setItem(i, 5, QTableWidgetItem(appointment["service_provider"]))
            
            # Notes
            self.appointments_table.setItem(i, 6, QTableWidgetItem(appointment["notes"]))
            
            # Status
            status = self.tr("appointments.confirmed") if appointment["status"] == "confirmed" else self.tr("appointments.unconfirmed")
            self.appointments_table.setItem(i, 7, QTableWidgetItem(status))
            
            # Remaining payments
            remaining_payments = f"{appointment['remaining_payments']:,.0f} {self.tr('services.price_currency')}" if appointment["remaining_payments"] > 0 else ""
            self.appointments_table.setItem(i, 8, QTableWidgetItem(remaining_payments))
        
        # Resize columns to content
        self.appointments_table.resizeColumnsToContents()
    
    def search(self, text):
        if not text:
            self.load_appointments()
            return
        
        appointments = self.db_manager.search_appointments(text)
        
        self.appointments_table.setRowCount(len(appointments))
        for i, appointment in enumerate(appointments):
            # ID
            self.appointments_table.setItem(i, 0, QTableWidgetItem(str(appointment["id"])))
            
            # Customer name
            self.appointments_table.setItem(i, 1, QTableWidgetItem(appointment["customer_name"]))
            
            # Phone
            self.appointments_table.setItem(i, 2, QTableWidgetItem(appointment["customer_phone"]))
            
            # Date and time
            date_time = QDateTime.fromString(appointment["date_time"], Qt.DateFormat.ISODate)
            self.appointments_table.setItem(i, 3, QTableWidgetItem(date_time.toString("yyyy-MM-dd hh:mm")))
            
            # Services
            services = ", ".join([service["name"] for service in appointment["services"]])
            self.appointments_table.setItem(i, 4, QTableWidgetItem(services))
            
            # Service provider
            self.appointments_table.setItem(i, 5, QTableWidgetItem(appointment["service_provider"]))
            
            # Notes
            self.appointments_table.setItem(i, 6, QTableWidgetItem(appointment["notes"]))
            
            # Status
            status = self.tr("appointments.confirmed") if appointment["status"] == "confirmed" else self.tr("appointments.unconfirmed")
            self.appointments_table.setItem(i, 7, QTableWidgetItem(status))
            
            # Remaining payments
            remaining_payments = f"{appointment['remaining_payments']:,.0f} {self.tr('services.price_currency')}" if appointment["remaining_payments"] > 0 else ""
            self.appointments_table.setItem(i, 8, QTableWidgetItem(remaining_payments))
        
        # Resize columns to content
        self.appointments_table.resizeColumnsToContents()
    
    def add_appointment(self):
        dialog = AppointmentDialog(self.db_manager, self.language_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_appointments()
    
    def edit_appointment(self):
        selected_rows = self.appointments_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_appointment_to_edit"))
            return
        
        # Get the appointment ID from the first column
        appointment_id = int(self.appointments_table.item(selected_rows[0].row(), 0).text())
        
        dialog = AppointmentDialog(self.db_manager, self.language_manager, appointment_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_appointments()
    
    def delete_appointment(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
        
        selected_rows = self.appointments_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_appointment_to_delete"))
            return
        
        # Get the appointment ID from the first column
        appointment_id = int(self.appointments_table.item(selected_rows[0].row(), 0).text())
        
        # Confirm deletion
        reply = QMessageBox.question(self, self.tr("common.confirm"), 
                                    self.tr("common.confirm_delete"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.delete_appointment(appointment_id)
                self.load_appointments()
                QMessageBox.information(self, self.tr("common.success"), self.tr("common.operation_success"))
            except Exception as e:
                QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")
    
    def view_appointment(self):
        selected_rows = self.appointments_table.selectedIndexes()
        if not selected_rows:
            return
        
        # Get the appointment ID from the first column
        appointment_id = int(self.appointments_table.item(selected_rows[0].row(), 0).text())
        
        dialog = AppointmentDialog(self.db_manager, self.language_manager, appointment_id, view_only=True)
        dialog.exec()

    def refresh(self):
        # Clear existing data
        self.appointments_table.clearContents()
        # Reload data with updated language
        self.load_appointments()


class AppointmentDialog(QDialog):
    def __init__(self, db_manager, language_manager, appointment_id=None, view_only=False):
        super().__init__()
        self.db_manager = db_manager
        self.language_manager = language_manager
        self.tr = self.language_manager.get_translation
        self.appointment_id = appointment_id
        self.view_only = view_only
        
        self.setup_ui()
        
        if appointment_id:
            self.load_appointment(appointment_id)
    
    def setup_ui(self):
        if self.appointment_id:
            if self.view_only:
                self.setWindowTitle(self.tr("appointments.appointment_details"))
            else:
                self.setWindowTitle(self.tr("appointments.edit"))
        else:
            self.setWindowTitle(self.tr("appointments.add"))
        
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Customer selection
        self.customer_combo = QComboBox()
        self.load_customers()
        form_layout.addRow(self.tr("appointments.customer_name"), self.customer_combo)
        
        # Date and time
        self.date_time_edit = QDateTimeEdit()
        self.date_time_edit.setCalendarPopup(True)
        self.date_time_edit.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow(self.tr("appointments.date_time"), self.date_time_edit)
        
        # Services
        self.services_layout = QVBoxLayout()
        services_widget = QWidget()
        services_widget.setLayout(self.services_layout)
        
        self.service_combos = []
        self.add_service_combo()
        
        add_service_button = QPushButton(self.tr("common.add"))
        add_service_button.clicked.connect(self.add_service_combo)
        self.services_layout.addWidget(add_service_button)
        
        form_layout.addRow(self.tr("appointments.services"), services_widget)
        
        # Service provider
        self.service_provider_edit = QLineEdit()
        form_layout.addRow(self.tr("appointments.service_provider"), self.service_provider_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        form_layout.addRow(self.tr("appointments.notes"), self.notes_edit)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItem(self.tr("appointments.confirmed"), "confirmed")
        self.status_combo.addItem(self.tr("appointments.unconfirmed"), "unconfirmed")
        form_layout.addRow(self.tr("appointments.status"), self.status_combo)
        
        # Remaining payments
        self.remaining_payments_spin = QDoubleSpinBox()
        self.remaining_payments_spin.setRange(0, 1000000000)
        self.remaining_payments_spin.setSingleStep(1000)
        self.remaining_payments_spin.setSuffix(f" {self.tr('services.price_currency')}")
        form_layout.addRow(self.tr("appointments.remaining_payments"), self.remaining_payments_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        if not self.view_only:
            self.save_button = QPushButton(self.tr("common.save"))
            self.save_button.clicked.connect(self.save_appointment)
            buttons_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton(self.tr("common.cancel"))
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Set read-only if view only
        if self.view_only:
            self.customer_combo.setEnabled(False)
            self.date_time_edit.setReadOnly(True)
            self.service_provider_edit.setReadOnly(True)
            self.notes_edit.setReadOnly(True)
            self.status_combo.setEnabled(False)
            self.remaining_payments_spin.setReadOnly(True)
    
    def load_customers(self):
        customers = self.db_manager.get_all_customers()
        
        self.customer_combo.clear()
        for customer in customers:
            self.customer_combo.addItem(f"{customer['name']} ({customer['phone']})", customer["id"])
    
    def load_services(self):
        services = self.db_manager.get_all_services()
        
        for combo in self.service_combos:
            current_id = combo.currentData()
            
            combo.clear()
            for service in services:
                combo.addItem(f"{service['name']} ({service['price']} {self.tr('services.price_currency')})", service["id"])
            
            # Restore selection if possible
            if current_id:
                index = combo.findData(current_id)
                if index >= 0:
                    combo.setCurrentIndex(index)
    
    def add_service_combo(self):
        combo = QComboBox()
        self.service_combos.append(combo)
        
        # Add to layout before the add button
        self.services_layout.insertWidget(len(self.service_combos) - 1, combo)
        
        # Load services
        self.load_services()
    
    def load_appointment(self, appointment_id):
        appointment = self.db_manager.get_appointment(appointment_id)
        
        # Set customer
        index = self.customer_combo.findData(appointment["customer_id"])
        if index >= 0:
            self.customer_combo.setCurrentIndex(index)
        
        # Set date and time
        date_time = QDateTime.fromString(appointment["date_time"], Qt.DateFormat.ISODate)
        self.date_time_edit.setDateTime(date_time)
        
        # Set services
        # First, remove existing service combos
        for combo in self.service_combos:
            combo.deleteLater()
        self.service_combos.clear()
        
        # Add a combo for each service
        services = self.db_manager.get_all_services()
        for service_data in appointment["services"]:
            combo = QComboBox()
            self.service_combos.append(combo)
            self.services_layout.insertWidget(len(self.service_combos) - 1, combo)
            
            # Load all services
            for service in services:
                combo.addItem(f"{service['name']} ({service['price']} {self.tr('services.price_currency')})", service["id"])
            
            # Set the selected service
            for i, service in enumerate(services):
                if service["name"] == service_data["name"]:
                    combo.setCurrentIndex(i)
                    break
        
        # Set service provider
        self.service_provider_edit.setText(appointment["service_provider"])
        
        # Set notes
        self.notes_edit.setText(appointment["notes"])
        
        # Set status
        index = self.status_combo.findData(appointment["status"])
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        # Set remaining payments
        self.remaining_payments_spin.setValue(appointment["remaining_payments"])
    
    def save_appointment(self):
        # Validate inputs
        if self.customer_combo.currentIndex() < 0:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_customer"))
            return
        
        if not self.service_provider_edit.text():
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("enter_service_provider"))
            return
        
        # Collect data
        customer_id = self.customer_combo.currentData()
        date_time = self.date_time_edit.dateTime().toString(Qt.DateFormat.ISODate)
        
        # Collect services
        services = []
        all_services = self.db_manager.get_all_services()
        for combo in self.service_combos:
            if combo.currentIndex() >= 0:
                service_id = combo.currentData()
                
                # Find the service details
                for service in all_services:
                    if service["id"] == service_id:
                        services.append({
                            "id": service["id"],
                            "name": service["name"],
                            "price": service["price"]
                        })
                        break
        
        service_provider = self.service_provider_edit.text()
        notes = self.notes_edit.toPlainText()
        status = self.status_combo.currentData()
        remaining_payments = self.remaining_payments_spin.value()
        
        # Create appointment data
        appointment_data = {
            "customer_id": customer_id,
            "date_time": date_time,
            "services": services,
            "service_provider": service_provider,
            "notes": notes,
            "status": status,
            "remaining_payments": remaining_payments
        }
        
        try:
            if self.appointment_id:
                # Update existing appointment
                self.db_manager.update_appointment(self.appointment_id, appointment_data)
            else:
                # Add new appointment
                self.db_manager.add_appointment(appointment_data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")
