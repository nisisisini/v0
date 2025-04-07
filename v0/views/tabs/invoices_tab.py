# views/tabs/invoices_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QDialog,
                           QFormLayout, QLineEdit, QDateEdit, QComboBox,
                           QTextEdit, QMessageBox, QCheckBox, QDoubleSpinBox, QSpinBox,
                           QFileDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
import json
import datetime
import os
from PyQt6.QtGui import QTextDocument
from PyQt6.QtGui import QPageSize  # استيراد QPageSize لتحديد حجم الصفحة

class InvoicesTab(QWidget):
    def __init__(self, db_manager, language_manager, is_admin):
        super().__init__()
        self.db_manager = db_manager
        self.language_manager = language_manager
        self.is_admin = is_admin
        self.tr = self.language_manager.get_translation
        
        self.setup_ui()
        self.load_invoices()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self.tr("invoices.title"))
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Invoices table
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(9)
        self.invoices_table.setHorizontalHeaderLabels([
            self.tr("invoices.id"),
            self.tr("invoices.customer_name"),
            self.tr("invoices.phone"),
            self.tr("invoices.date"),
            self.tr("invoices.services"),
            self.tr("invoices.payment_method"),
            self.tr("invoices.amount_paid"),
            self.tr("invoices.amount_remaining"),
            self.tr("invoices.total_amount")
        ])
        self.invoices_table.horizontalHeader().setStretchLastSection(True)
        self.invoices_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.invoices_table.doubleClicked.connect(self.view_invoice)
        
        layout.addWidget(self.invoices_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Create invoice button
        self.create_button = QPushButton(self.tr("invoices.add"))
        self.create_button.clicked.connect(self.create_invoice)
        buttons_layout.addWidget(self.create_button)
        
        # Edit invoice button
        self.edit_button = QPushButton(self.tr("invoices.edit"))
        self.edit_button.clicked.connect(self.edit_invoice)
        buttons_layout.addWidget(self.edit_button)
        
        # Delete invoice button
        self.delete_button = QPushButton(self.tr("invoices.delete"))
        self.delete_button.clicked.connect(self.delete_invoice)
        buttons_layout.addWidget(self.delete_button)
        
        # Print invoice button
        self.print_button = QPushButton(self.tr("invoices.print"))
        self.print_button.clicked.connect(self.print_invoice)
        buttons_layout.addWidget(self.print_button)
        
        # Add buttons layout to main layout
        layout.addLayout(buttons_layout)
        
        self.table = QTableWidget()  # Ensure the table is initialized
        self.load_data()

    def load_invoices(self):
        invoices = self.db_manager.get_all_invoices()
        
        self.invoices_table.setRowCount(len(invoices))
        for i, invoice in enumerate(invoices):
            # ID
            self.invoices_table.setItem(i, 0, QTableWidgetItem(str(invoice["id"])))
            
            # Customer name
            self.invoices_table.setItem(i, 1, QTableWidgetItem(invoice["customer_name"]))
            
            # Phone
            self.invoices_table.setItem(i, 2, QTableWidgetItem(invoice["customer_phone"]))
            
            # Date
            date = QDate.fromString(invoice["date"].split("T")[0], Qt.DateFormat.ISODate)
            self.invoices_table.setItem(i, 3, QTableWidgetItem(date.toString("yyyy-MM-dd")))
            
            # Services
            services = ", ".join([service["name"] for service in invoice["services"]])
            self.invoices_table.setItem(i, 4, QTableWidgetItem(services))
            
            # Payment method
            payment_method = self.tr("invoices.cash") if invoice["payment_method"] == "cash" else self.tr("invoices.installment")
            self.invoices_table.setItem(i, 5, QTableWidgetItem(payment_method))
            
            # Amount paid
            amount_paid = f"{invoice['amount_paid']:,.0f} {self.tr('invoices.price_currency')}"
            self.invoices_table.setItem(i, 6, QTableWidgetItem(amount_paid))
            
            # Amount remaining
            amount_remaining = f"{invoice['amount_remaining']:,.0f} {self.tr('invoices.price_currency')}" if invoice["amount_remaining"] > 0 else ""
            self.invoices_table.setItem(i, 7, QTableWidgetItem(amount_remaining))
            
            # Total amount
            total_amount = f"{invoice['total_amount']:,.0f} {self.tr('invoices.price_currency')}"
            self.invoices_table.setItem(i, 8, QTableWidgetItem(total_amount))
        
        # Resize columns to content
        self.invoices_table.resizeColumnsToContents()

    def load_data(self):
        # Call the existing method to load invoices
        self.load_invoices()

    def refresh(self):
        # Clear existing data
        self.invoices_table.clearContents()
        # Reload data with updated language
        self.load_data()
        # Update table headers with the current language
        self.invoices_table.setHorizontalHeaderLabels([
            self.tr("invoices.id"),
            self.tr("invoices.customer_name"),
            self.tr("invoices.phone"),
            self.tr("invoices.date"),
            self.tr("invoices.services"),
            self.tr("invoices.payment_method"),
            self.tr("invoices.amount_paid"),
            self.tr("invoices.amount_remaining"),
            self.tr("invoices.total_amount")
        ])
    
    def search(self, text):
        if not text:
            self.load_invoices()
            return
        
        invoices = self.db_manager.search_invoices(text)
        
        self.invoices_table.setRowCount(len(invoices))
        for i, invoice in enumerate(invoices):
            # ID
            self.invoices_table.setItem(i, 0, QTableWidgetItem(str(invoice["id"])))
            
            # Customer name
            self.invoices_table.setItem(i, 1, QTableWidgetItem(invoice["customer_name"]))
            
            # Phone
            self.invoices_table.setItem(i, 2, QTableWidgetItem(invoice["customer_phone"]))
            
            # Date
            date = QDate.fromString(invoice["date"].split("T")[0], Qt.DateFormat.ISODate)
            self.invoices_table.setItem(i, 3, QTableWidgetItem(date.toString("yyyy-MM-dd")))
            
            # Services
            services = ", ".join([service["name"] for service in invoice["services"]])
            self.invoices_table.setItem(i, 4, QTableWidgetItem(services))
            
            # Payment method
            payment_method = self.tr("invoices.cash") if invoice["payment_method"] == "cash" else self.tr("invoices.installment")
            self.invoices_table.setItem(i, 5, QTableWidgetItem(payment_method))
            
            # Amount paid
            amount_paid = f"{invoice['amount_paid']:,.0f} {self.tr('invoices.price_currency')}"
            self.invoices_table.setItem(i, 6, QTableWidgetItem(amount_paid))
            
            # Amount remaining
            amount_remaining = f"{invoice['amount_remaining']:,.0f} {self.tr('invoices.price_currency')}" if invoice["amount_remaining"] > 0 else ""
            self.invoices_table.setItem(i, 7, QTableWidgetItem(amount_remaining))
            
            # Total amount
            total_amount = f"{invoice['total_amount']:,.0f} {self.tr('invoices.price_currency')}"
            self.invoices_table.setItem(i, 8, QTableWidgetItem(total_amount))
        
        # Resize columns to content
        self.invoices_table.resizeColumnsToContents()
    
    def create_invoice(self):
        dialog = InvoiceDialog(self.db_manager, self.language_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_invoices()
    
    def edit_invoice(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
            
        selected_rows = self.invoices_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_invoice_to_edit"))
            return
        
        # Get the invoice ID from the first column
        invoice_id = int(self.invoices_table.item(selected_rows[0].row(), 0).text())
        
        dialog = InvoiceDialog(self.db_manager, self.language_manager, invoice_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_invoices()
    
    def delete_invoice(self):
        if not self.is_admin:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("admin_only"))
            return
            
        selected_rows = self.invoices_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_invoice_to_delete"))
            return
        
        # Get the invoice ID from the first column
        invoice_id = int(self.invoices_table.item(selected_rows[0].row(), 0).text())
        
        # Confirm deletion
        reply = QMessageBox.question(self, self.tr("common.confirm"), 
                                    self.tr("common.confirm_delete"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.delete_invoice(invoice_id)
                self.load_invoices()
                QMessageBox.information(self, self.tr("common.success"), self.tr("common.operation_success"))
            except Exception as e:
                QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")
    
    def view_invoice(self):
        selected_rows = self.invoices_table.selectedIndexes()
        if not selected_rows:
            return
        
        # Get the invoice ID from the first column
        invoice_id = int(self.invoices_table.item(selected_rows[0].row(), 0).text())
        
        dialog = InvoiceDialog(self.db_manager, self.language_manager, invoice_id, view_only=True)
        dialog.exec()
    
    def print_invoice(self):
        selected_rows = self.invoices_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_invoice_to_print"))
            return
        
        # Get the invoice ID from the first column
        invoice_id = int(self.invoices_table.item(selected_rows[0].row(), 0).text())
        
        # Get invoice data
        invoice = self.db_manager.get_invoice(invoice_id)
        
        # Create HTML content for the invoice
        html_content = self.generate_invoice_html(invoice)
        
        # Create printer
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))  # تحديد حجم الصفحة A4
        
        # Show print preview dialog
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.print_invoice_content(p, html_content))
        preview.exec()

    def export_invoice_to_pdf(self, invoice_id):
        # Get invoice data
        invoice = self.db_manager.get_invoice(invoice_id)
        
        # Create HTML content for the invoice
        html_content = self.generate_invoice_html(invoice)
        
        # Create printer for PDF
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))  # تحديد حجم الصفحة A4
        
        # Ask user for file location
        file_path, _ = QFileDialog.getSaveFileName(self, self.tr("save_pdf"), f"invoice_{invoice_id}.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return
        
        # Ensure the file has a .pdf extension
        if not file_path.endswith(".pdf"):
            file_path += ".pdf"
        
        printer.setOutputFileName(file_path)
        
        # Print to PDF
        document = QTextDocument()
        document.setHtml(html_content)
        document.print(printer)
        
        # Show success message
        QMessageBox.information(self, self.tr("common.success"), self.tr("pdf_saved_successfully"))

    def print_invoice_content(self, printer, html_content):
        document = QTextDocument()
        document.setHtml(html_content)
        document.print(printer)  # استبدل print_ بـ print
    
    def generate_invoice_html(self, invoice):
        # Get clinic info from settings
        try:
            from config.settings import Settings
        except ModuleNotFoundError:
            raise ImportError("The module 'utils.settings' could not be resolved. Ensure it exists and the path is correct.")
        settings = Settings()
        clinic_name = settings.get_setting("clinic_info.name", "مركز جوزيل للتجميل")
        clinic_phone = settings.get_setting("clinic_info.phone", "+963956961395")
        clinic_address = settings.get_setting("clinic_info.address", "سوريا - ريف دمشق التل موقف طيبة مقابل امركز الثقافي الجديد")
        
        # Format date
        date = QDate.fromString(invoice["date"].split("T")[0], Qt.DateFormat.ISODate)
        formatted_date = date.toString("yyyy-MM-dd")
        
        # Format payment method
        payment_method = self.tr("invoices.cash") if invoice["payment_method"] == "cash" else self.tr("invoices.installment")
        
        # Generate HTML
        html = f"""
        <html dir="rtl">
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .invoice-info {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                .invoice-info div {{ width: 45%; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
                th {{ background-color: #f2f2f2; }}
                .total {{ text-align: left; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{clinic_name}</h1>
                <p>{clinic_address}</p>
                <p>{clinic_phone}</p>
                <h2>{self.tr("invoices.title")} #{invoice["id"]}</h2>
            </div>
            
            <div class="invoice-info">
                <div>
                    <p><strong>{self.tr("invoices.customer_name")}:</strong> {invoice["customer_name"]}</p>
                    <p><strong>{self.tr("invoices.phone")}:</strong> {invoice["customer_phone"]}</p>
                </div>
                <div>
                    <p><strong>{self.tr("invoices.date")}:</strong> {formatted_date}</p>
                    <p><strong>{self.tr("invoices.payment_method")}:</strong> {payment_method}</p>
                </div>
            </div>
            
            <table>
                <tr>
                    <th>#</th>
                    <th>{self.tr("services.name")}</th>
                    <th>{self.tr("services.price")}</th>
                </tr>
        """
        
        # Add services
        for i, service in enumerate(invoice["services"]):
            html += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{service["name"]}</td>
                    <td>{float(service["price"]):,.0f} {self.tr("services.price_currency")}</td>
                </tr>
            """
        
        # Add totals
        html += f"""
                <tr>
                    <td colspan="2" class="total">{self.tr("invoices.total_amount")}</td>
                    <td>{invoice["total_amount"]:,.0f} {self.tr("services.price_currency")}</td>
                </tr>
                <tr>
                    <td colspan="2" class="total">{self.tr("invoices.amount_paid")}</td>
                    <td>{invoice["amount_paid"]:,.0f} {self.tr("services.price_currency")}</td>
                </tr>
        """
        
        if invoice["amount_remaining"] > 0:
            html += f"""
                <tr>
                    <td colspan="2" class="total">{self.tr("invoices.amount_remaining")}</td>
                    <td>{invoice["amount_remaining"]:,.0f} {self.tr("services.price_currency")}</td>
                </tr>
            """
        
        html += f"""
            </table>
            
            <div>
                <p><strong>{self.tr("invoices.service_provider")}:</strong> {invoice["service_provider"]}</p>
                <p><strong>{self.tr("invoices.invoice_creator")}:</strong> {invoice["invoice_creator"]}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    


class InvoiceDialog(QDialog):
    def __init__(self, db_manager, language_manager, invoice_id=None, view_only=False):
        super().__init__()
        self.db_manager = db_manager
        self.language_manager = language_manager
        self.tr = self.language_manager.get_translation
        self.invoice_id = invoice_id
        self.view_only = view_only
        self.total_amount_spin = QDoubleSpinBox()
        self.amount_paid_spin = QDoubleSpinBox()  # Initialize both spinboxes here
        self.amount_remaining_spin = QDoubleSpinBox()  # تأكد من تعريف الخاصية هنا
        
        self.setup_ui()
        
        if invoice_id:
            self.load_invoice(invoice_id)
    
    def setup_ui(self):
        if self.invoice_id:
            if self.view_only:
                self.setWindowTitle(self.tr("invoices.invoice_details"))
            else:
                self.setWindowTitle(self.tr("invoices.edit"))
        else:
            self.setWindowTitle(self.tr("invoices.add"))
        
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Customer selection
        self.customer_combo = QComboBox()
        self.load_customers()
        self.customer_combo.currentIndexChanged.connect(self.customer_changed)
        form_layout.addRow(self.tr("invoices.customer_name"), self.customer_combo)
        
        # Appointment selection (optional)
        self.appointment_combo = QComboBox()
        self.appointment_combo.addItem(self.tr("invoices.select_appointment"), None)
        self.appointment_combo.currentIndexChanged.connect(self.appointment_changed)
        form_layout.addRow(self.tr("invoices.appointment_id"), self.appointment_combo)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow(self.tr("invoices.date"), self.date_edit)
        
        # Services
        self.services_layout = QVBoxLayout()
        services_widget = QWidget()
        services_widget.setLayout(self.services_layout)
        
        self.service_rows = []
        self.add_service_row()
        
        add_service_button = QPushButton(self.tr("common.add"))
        add_service_button.clicked.connect(self.add_service_row)
        self.services_layout.addWidget(add_service_button)
        
        form_layout.addRow(self.tr("invoices.services"), services_widget)
        
        # Payment method
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItem(self.tr("invoices.cash"), "cash")
        self.payment_method_combo.addItem(self.tr("invoices.installment"), "installment")
        self.payment_method_combo.currentIndexChanged.connect(self.payment_method_changed)
        form_layout.addRow(self.tr("invoices.payment_method"), self.payment_method_combo)
        
        # Amount paid
        self.amount_paid_spin = QDoubleSpinBox()
        self.amount_paid_spin.setRange(0, 1000000000)
        self.amount_paid_spin.setSingleStep(1000)
        self.amount_paid_spin.setSuffix(f" {self.tr('invoices.price_currency')}")
        self.amount_paid_spin.valueChanged.connect(self.update_remaining_amount)
        form_layout.addRow(self.tr("invoices.amount_paid"), self.amount_paid_spin)
        
        # Amount remaining (read-only)
        self.amount_remaining_spin = QDoubleSpinBox()  # تأكد من تعريفها هنا أيضًا
        self.amount_remaining_spin.setRange(0, 1000000000)
        self.amount_remaining_spin.setSingleStep(1000)
        self.amount_remaining_spin.setSuffix(f" {self.tr('invoices.price_currency')}")
        self.amount_remaining_spin.setReadOnly(True)
        form_layout.addRow(self.tr("invoices.amount_remaining"), self.amount_remaining_spin)
        
        # Total amount (read-only)
        self.total_amount_spin.setRange(0, 1000000000)
        self.total_amount_spin.setSingleStep(1000)
        self.total_amount_spin.setSuffix(f" {self.tr('invoices.price_currency')}")
        self.total_amount_spin.setReadOnly(True)
        self.total_amount_spin.setValue(0)  # Initialize with 0 value
        form_layout.addRow(self.tr("invoices.total_amount"), self.total_amount_spin)
        
        # Invoice creator
        self.invoice_creator_edit = QLineEdit()
        form_layout.addRow(self.tr("invoices.invoice_creator"), self.invoice_creator_edit)
        
        # Service provider
        self.service_provider_edit = QLineEdit()
        form_layout.addRow(self.tr("invoices.service_provider"), self.service_provider_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        if not self.view_only:
            self.save_button = QPushButton(self.tr("common.save"))
            self.save_button.clicked.connect(self.save_invoice)
            buttons_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton(self.tr("common.cancel"))
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Set read-only if view only
        if self.view_only:
            self.customer_combo.setEnabled(False)
            self.appointment_combo.setEnabled(False)
            self.date_edit.setReadOnly(True)
            self.payment_method_combo.setEnabled(False)
            self.amount_paid_spin.setReadOnly(True)
            self.invoice_creator_edit.setReadOnly(True)
            self.service_provider_edit.setReadOnly(True)
    
    def load_customers(self):
        customers = self.db_manager.get_all_customers()
        
        self.customer_combo.clear()
        self.customer_combo.addItem(self.tr("invoices.select_customer"), None)
        
        for customer in customers:
            self.customer_combo.addItem(f"{customer['name']} ({customer['phone']})", customer["id"])
    
    def load_appointments_for_customer(self, customer_id):
        if not customer_id:
            self.appointment_combo.clear()
            self.appointment_combo.addItem(self.tr("invoices.select_appointment"), None)
            return
        
        appointments = self.db_manager.get_all_appointments()
        customer_appointments = [a for a in appointments if a["customer_id"] == customer_id]
        
        self.appointment_combo.clear()
        self.appointment_combo.addItem(self.tr("invoices.select_appointment"), None)
        
        for appointment in customer_appointments:
            date_time = appointment["date_time"].split("T")
            date = QDate.fromString(date_time[0], Qt.DateFormat.ISODate)
            services = ", ".join([s["name"] for s in appointment["services"]])
            self.appointment_combo.addItem(f"{date.toString('yyyy-MM-dd')} - {services}", appointment["id"])
    
    def load_services(self):
        services = self.db_manager.get_all_services()
        
        for row in self.service_rows:
            combo = row["combo"]
            current_id = combo.currentData()
            
            combo.clear()
            combo.addItem(self.tr("invoices.select_service"), None)
            
            for service in services:
                combo.addItem(f"{service['name']} ({service['price']} {self.tr('services.price_currency')})", service["id"])
            
            # Restore selection if possible
            if current_id:
                index = combo.findData(current_id)
                if index >= 0:
                    combo.setCurrentIndex(index)
    
    def add_service_row(self):
        row_layout = QHBoxLayout()
        
        # Service combo
        combo = QComboBox()
        combo.setMinimumWidth(300)
        
        # Quantity spin
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 1000)
        quantity_spin.setValue(1)
        
        # Price spin (read-only)
        price_spin = QDoubleSpinBox()
        price_spin.setRange(0, 1000000000)
        price_spin.setSingleStep(1000)
        price_spin.setSuffix(f" {self.tr('services.price_currency')}")
        price_spin.setReadOnly(True)
        
        # Remove button
        remove_button = QPushButton("X")
        remove_button.setMaximumWidth(30)
        
        row_layout.addWidget(combo)
        row_layout.addWidget(QLabel(self.tr("quantity")))
        row_layout.addWidget(quantity_spin)
        row_layout.addWidget(QLabel(self.tr("services.price")))
        row_layout.addWidget(price_spin)
        row_layout.addWidget(remove_button)
        
        row_widget = QWidget()
        row_widget.setLayout(row_layout)
        
        # Add to services layout before the add button
        self.services_layout.insertWidget(len(self.service_rows), row_widget)
        
        # Store references to the widgets
        row_data = {
            "widget": row_widget,
            "combo": combo,
            "quantity": quantity_spin,
            "price": price_spin,
            "remove": remove_button
        }
        
        self.service_rows.append(row_data)
        
        # Connect signals
        combo.currentIndexChanged.connect(self.update_service_price)
        quantity_spin.valueChanged.connect(self.update_total_amount)
        remove_button.clicked.connect(lambda: self.remove_service_row(row_data))
        
        # Load services
        self.load_services()
        
        # Set view-only if needed
        if self.view_only:
            combo.setEnabled(False)
            quantity_spin.setReadOnly(True)
            remove_button.setEnabled(False)
    
    def remove_service_row(self, row_data):
        if len(self.service_rows) <= 1:
            return  # Keep at least one row
        
        # Remove from layout and list
        self.services_layout.removeWidget(row_data["widget"])
        row_data["widget"].deleteLater()
        self.service_rows.remove(row_data)
        
        # Update totals
        self.update_total_amount()
    
    def update_service_price(self):
        sender = self.sender()
        
        for row in self.service_rows:
            if row["combo"] == sender:
                service_id = sender.currentData()
                if service_id:
                    service = self.db_manager.get_service(service_id)
                    row["price"].setValue(service["price"])
                else:
                    row["price"].setValue(0)
                break
        
        # تحديث السعر بناءً على الكمية وسعر الضربة الواحدة
        self.update_total_amount()

    def update_total_amount(self):
        total = 0
        price_per_hit = 1500  # سعر الضربة الواحدة بالليرة السورية
        
        for row in self.service_rows:
            service_id = row["combo"].currentData()
            if service_id:
                quantity = row["quantity"].value()
                price = price_per_hit * quantity  # حساب السعر بناءً على الكمية
                row["price"].setValue(price)  # تحديث السعر في واجهة المستخدم
                total += price
        
        self.total_amount_spin.setValue(total)
        self.update_remaining_amount()
    
    def update_remaining_amount(self):
        total = self.total_amount_spin.value()
        paid = self.amount_paid_spin.value()
        
        if paid > total:
            self.amount_paid_spin.setValue(total)
            paid = total
        
        remaining = total - paid
        self.amount_remaining_spin.setValue(remaining)  # الآن الخاصية موجودة ولن يحدث خطأ
    
    def payment_method_changed(self):
        method = self.payment_method_combo.currentData()
        
        if method == "cash":
            # For cash payments, set amount paid to total by default
            self.amount_paid_spin.setValue(self.total_amount_spin.value())
        else:
            # For installments, allow partial payment
            self.update_remaining_amount()
    
    def customer_changed(self):
        customer_id = self.customer_combo.currentData()
        self.load_appointments_for_customer(customer_id)
    
    def appointment_changed(self):
        appointment_id = self.appointment_combo.currentData()
        
        if not appointment_id:
            return
        
        # Load appointment data
        appointment = self.db_manager.get_appointment(appointment_id)
        
        # Set service provider
        self.service_provider_edit.setText(appointment["service_provider"])
        
        # Clear existing service rows
        for row in self.service_rows:
            self.services_layout.removeWidget(row["widget"])
            row["widget"].deleteLater()
        self.service_rows.clear()
        
        # Add service rows for each service in the appointment
        for service_data in appointment["services"]:
            self.add_service_row()
            row = self.service_rows[-1]
            
            # Find and select the service
            for i in range(row["combo"].count()):
                service_id = row["combo"].itemData(i)
                if service_id and service_data["id"] == service_id:
                    row["combo"].setCurrentIndex(i)
                    break
        
        # Update totals
        self.update_total_amount()
    
    def load_invoice(self, invoice_id):
        invoice = self.db_manager.get_invoice(invoice_id)
        
        # Set customer
        index = self.customer_combo.findData(invoice["customer_id"])
        if index >= 0:
            self.customer_combo.setCurrentIndex(index)
        
        # Set appointment if available
        if invoice["appointment_id"]:
            index = self.appointment_combo.findData(invoice["appointment_id"])
            if index >= 0:
                self.appointment_combo.setCurrentIndex(index)
        
        # Set date
        date = QDate.fromString(invoice["date"].split("T")[0], Qt.DateFormat.ISODate)
        self.date_edit.setDate(date)
        
        # Set services
        # First, remove existing service rows
        for row in self.service_rows:
            self.services_layout.removeWidget(row["widget"])
            row["widget"].deleteLater()
        self.service_rows.clear()
        
        # Add a row for each service
        services = self.db_manager.get_all_services()
        for service_data in invoice["services"]:
            self.add_service_row()
            row = self.service_rows[-1]
            
            # Find and select the service
            for service in services:
                if service["name"] == service_data["name"]:
                    for i in range(row["combo"].count()):
                        if row["combo"].itemData(i) == service["id"]:
                            row["combo"].setCurrentIndex(i)
                            break
                    break
            
            # Set quantity if available
            if "quantity" in service_data:
                row["quantity"].setValue(service_data["quantity"])
        
        # Set payment method
        index = self.payment_method_combo.findData(invoice["payment_method"])
        if index >= 0:
            self.payment_method_combo.setCurrentIndex(index)
        
        # Set amounts
        self.amount_paid_spin.setValue(invoice["amount_paid"])
        self.amount_remaining_spin.setValue(invoice["amount_remaining"])
        self.total_amount_spin.setValue(invoice["total_amount"])
        
        # Set creator and provider
        self.invoice_creator_edit.setText(invoice["invoice_creator"])
        self.service_provider_edit.setText(invoice["service_provider"])
    
    def save_invoice(self):
        # Validate inputs
        if self.customer_combo.currentIndex() <= 0:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_customer"))
            return
        
        if not self.date_edit.date().isValid():
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("enter_valid_date"))
            return
        
        # Check if at least one service is selected
        has_service = False
        for row in self.service_rows:
            if row["combo"].currentIndex() > 0:
                has_service = True
                break
        
        if not has_service:
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("select_at_least_one_service"))
            return
        
        if not self.invoice_creator_edit.text():
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("enter_invoice_creator"))
            return
        
        if not self.service_provider_edit.text():
            QMessageBox.warning(self, self.tr("common.warning"), self.tr("enter_service_provider"))
            return
        
        # Collect data
        customer_id = self.customer_combo.currentData()
        appointment_id = self.appointment_combo.currentData()
        date = self.date_edit.date().toString(Qt.DateFormat.ISODate)
        
        # Collect services
        services = []
        all_services = self.db_manager.get_all_services()
        for row in self.service_rows:
            if row["combo"].currentIndex() > 0:
                service_id = row["combo"].currentData()
                quantity = row["quantity"].value()
                
                # Find the service details
                for service in all_services:
                    if service["id"] == service_id:
                        services.append({
                            "id": service["id"],
                            "name": service["name"],
                            "price": service["price"],
                            "quantity": quantity
                        })
                        break
        
        payment_method = self.payment_method_combo.currentData()
        amount_paid = self.amount_paid_spin.value()
        amount_remaining = self.amount_remaining_spin.value()
        total_amount = self.total_amount_spin.value()
        invoice_creator = self.invoice_creator_edit.text()
        service_provider = self.service_provider_edit.text()
        
        # Create invoice data
        invoice_data = {
            "customer_id": customer_id,
            "appointment_id": appointment_id,
            "date": date,
            "services": services,
            "payment_method": payment_method,
            "amount_paid": amount_paid,
            "amount_remaining": amount_remaining,
            "invoice_creator": invoice_creator,
            "service_provider": service_provider,
            "total_amount": total_amount
        }
        
        try:
            if self.invoice_id:
                # Update existing invoice
                self.db_manager.update_invoice(self.invoice_id, invoice_data)
            else:
                # Add new invoice
                self.db_manager.add_invoice(invoice_data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, self.tr("common.error"), f"{self.tr('common.operation_failed')}: {str(e)}")

