# ui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QCalendarWidget, 
                           QStackedWidget, QComboBox, QCheckBox, QTextEdit, QMessageBox,
                           QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QTabWidget,
                           QGroupBox, QScrollArea, QSplitter, QMenu, QToolBar, QStatusBar,
                           QFileDialog, QDateEdit, QTimeEdit, QDateTimeEdit, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QAction, QTextCharFormat
import datetime
import json
import os

from views.tabs.appointments_tab import AppointmentsTab
from views.tabs.customers_tab import CustomersTab
from views.tabs.services_tab import ServicesTab
from views.tabs.invoices_tab import InvoicesTab
from ui.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    logout_signal = pyqtSignal()
    
    def __init__(self, db_manager, theme_manager, language_manager, backup_manager, username, is_admin):
        super().__init__()
        self.db_manager = db_manager
        self.theme_manager = theme_manager
        self.language_manager = language_manager
        self.backup_manager = backup_manager
        self.username = username
        self.is_admin = is_admin
        self.tr = self.language_manager.get_translation
        
        self.setup_ui()
        self.setup_connections()
        
        # Perform auto backup if needed
        backup_interval = int(self.theme_manager.settings.get_setting("backup.backup_interval_days", 1))
        if self.theme_manager.settings.get_setting("backup.auto_backup", True):
            try:
                self.backup_manager.auto_backup(backup_interval)
            except Exception as e:
                print(f"Auto backup failed: {e}")
    
    def setup_ui(self):
        self.setWindowTitle(self.tr("app_title"))
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Content layout (sidebar + main content)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        
        # Create main content area
        main_content = self.create_main_content()
        
        # Create right sidebar (calendar and stats)
        right_sidebar = self.create_right_sidebar()
        
        # Add widgets to content layout
        content_layout.addWidget(sidebar, 1)
        content_layout.addWidget(main_content, 4)
        content_layout.addWidget(right_sidebar, 1)
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
        # Create bottom action bar
        self.bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(self.bottom_bar)
        
        # Set the active tab to appointments by default
        self.sidebar_buttons[0].click()
    
    def create_toolbar(self):
        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Add search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("main.search"))
        self.search_box.setMinimumWidth(300)
        self.toolbar.addWidget(self.search_box)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar.addWidget(spacer)
        
        # Add language button
        self.language_button = QAction(QIcon("assets/icons/language.png"), self.tr("main.languages"), self)
        self.language_button.triggered.connect(self.show_language_menu)
        self.toolbar.addAction(self.language_button)
        
        # Add theme button
        self.theme_button = QAction(QIcon("assets/icons/theme.png"), self.tr("main.themes"), self)
        self.theme_button.triggered.connect(self.show_theme_menu)
        self.toolbar.addAction(self.theme_button)
        
        # Add notifications button
        self.notifications_button = QAction(QIcon("assets/icons/notification.png"), self.tr("main.notifications"), self)
        self.notifications_button.triggered.connect(self.show_notifications)
        self.toolbar.addAction(self.notifications_button)
        
        # Add settings button
        self.settings_button = QAction(QIcon("assets/icons/settings.png"), self.tr("main.settings"), self)
        self.settings_button.triggered.connect(self.show_settings)
        self.toolbar.addAction(self.settings_button)
        
        # Add logout button
        self.logout_button = QAction(QIcon("assets/icons/logout.png"), self.tr("main.logout"), self)
        self.logout_button.triggered.connect(self.logout)
        self.toolbar.addAction(self.logout_button)
    
    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(250)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Create sidebar buttons
        self.sidebar_buttons = []
        
        # Appointments button
        appointments_button = QPushButton(self.tr("sidebar.appointments"))
        appointments_button.setIcon(QIcon("assets/icons/calendar.png"))
        appointments_button.setCheckable(True)
        appointments_button.clicked.connect(lambda: self.show_tab(0))
        sidebar_layout.addWidget(appointments_button)
        self.sidebar_buttons.append(appointments_button)
        
        # Customers button
        customers_button = QPushButton(self.tr("sidebar.customers"))
        customers_button.setIcon(QIcon("assets/icons/customers.png"))
        customers_button.setCheckable(True)
        customers_button.clicked.connect(lambda: self.show_tab(1))
        sidebar_layout.addWidget(customers_button)
        self.sidebar_buttons.append(customers_button)
        
        # Services button
        services_button = QPushButton(self.tr("sidebar.services"))
        services_button.setIcon(QIcon("assets/icons/services.png"))
        services_button.setCheckable(True)
        services_button.clicked.connect(lambda: self.show_tab(2))
        sidebar_layout.addWidget(services_button)
        self.sidebar_buttons.append(services_button)
        
        # Invoices button
        invoices_button = QPushButton(self.tr("sidebar.invoices"))
        invoices_button.setIcon(QIcon("assets/icons/invoice.png"))
        invoices_button.setCheckable(True)
        invoices_button.clicked.connect(lambda: self.show_tab(3))
        sidebar_layout.addWidget(invoices_button)
        self.sidebar_buttons.append(invoices_button)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sidebar_layout.addWidget(spacer)
        
        return sidebar
    
    def create_main_content(self):
        # Create stacked widget for main content
        self.content_stack = QStackedWidget()
        
        # Create tabs
        self.appointments_tab = AppointmentsTab(self.db_manager, self.language_manager, self.is_admin)
        self.customers_tab = CustomersTab(self.db_manager, self.language_manager, self.is_admin)
        self.services_tab = ServicesTab(self.db_manager, self.language_manager, self.is_admin)
        self.invoices_tab = InvoicesTab(self.db_manager, self.language_manager, self.is_admin)
        
        # Add tabs to stack
        self.content_stack.addWidget(self.appointments_tab)
        self.content_stack.addWidget(self.customers_tab)
        self.content_stack.addWidget(self.services_tab)
        self.content_stack.addWidget(self.invoices_tab)
        
        return self.content_stack
    
    def create_right_sidebar(self):
        right_sidebar = QWidget()
        right_sidebar.setObjectName("right_sidebar")
        right_sidebar.setMinimumWidth(250)
        right_sidebar.setMaximumWidth(300)
        
        right_sidebar_layout = QVBoxLayout(right_sidebar)
        right_sidebar_layout.setContentsMargins(10, 20, 10, 20)
        right_sidebar_layout.setSpacing(20)
        
        # Calendar
        calendar_group = QGroupBox(self.tr("calendar.upcoming_appointments"))
        calendar_layout = QVBoxLayout(calendar_group)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.clicked.connect(self.calendar_date_clicked)
        
        calendar_layout.addWidget(self.calendar)
        
        # Upcoming appointments list
        self.upcoming_appointments = QTableWidget()
        self.upcoming_appointments.setColumnCount(2)
        self.upcoming_appointments.setHorizontalHeaderLabels([self.tr("appointments.time"), self.tr("appointments.customer_name")])
        self.upcoming_appointments.horizontalHeader().setStretchLastSection(True)
        self.upcoming_appointments.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.upcoming_appointments.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.upcoming_appointments.setMaximumHeight(200)
        
        calendar_layout.addWidget(self.upcoming_appointments)
        
        right_sidebar_layout.addWidget(calendar_group)
        
        # Financial stats (only for admin)
        if self.is_admin:
            stats_group = QGroupBox(self.tr("financial_stats"))
            stats_layout = QVBoxLayout(stats_group)
            
            # Daily revenue
            daily_layout = QHBoxLayout()
            daily_label = QLabel(self.tr("daily_revenue"))
            self.daily_revenue = QLabel("0")
            daily_layout.addWidget(daily_label)
            daily_layout.addWidget(self.daily_revenue, alignment=Qt.AlignmentFlag.AlignRight)
            stats_layout.addLayout(daily_layout)
            
            # Weekly revenue
            weekly_layout = QHBoxLayout()
            weekly_label = QLabel(self.tr("weekly_revenue"))
            self.weekly_revenue = QLabel("0")
            weekly_layout.addWidget(weekly_label)
            weekly_layout.addWidget(self.weekly_revenue, alignment=Qt.AlignmentFlag.AlignRight)
            stats_layout.addLayout(weekly_layout)
            
            # Monthly revenue
            monthly_layout = QHBoxLayout()
            monthly_label = QLabel(self.tr("monthly_revenue"))
            self.monthly_revenue = QLabel("0")
            monthly_layout.addWidget(monthly_label)
            monthly_layout.addWidget(self.monthly_revenue, alignment=Qt.AlignmentFlag.AlignRight)
            stats_layout.addLayout(monthly_layout)
            
            right_sidebar_layout.addWidget(stats_group)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_sidebar_layout.addWidget(spacer)
        
        return right_sidebar
    
    def create_bottom_bar(self):
        bottom_bar = QWidget()
        bottom_bar.setObjectName("bottom_bar")
        bottom_bar.setMinimumHeight(60)
        bottom_bar.setMaximumHeight(60)
        
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(20, 10, 20, 10)
        bottom_layout.setSpacing(20)
        
        # Add appointment button
        add_appointment_button = QPushButton(self.tr("appointments.add"))
        add_appointment_button.setObjectName("add_appointment_button")
        add_appointment_button.setIcon(QIcon("assets/icons/add_appointment.png"))
        add_appointment_button.clicked.connect(self.add_appointment)
        bottom_layout.addWidget(add_appointment_button)
        
        # Add customer button
        add_customer_button = QPushButton(self.tr("customers.add"))
        add_customer_button.setObjectName("add_customer_button")
        add_customer_button.setIcon(QIcon("assets/icons/add_customer.png"))
        add_customer_button.clicked.connect(self.add_customer)
        bottom_layout.addWidget(add_customer_button)
        
        # Create invoice button
        create_invoice_button = QPushButton(self.tr("invoices.add"))
        create_invoice_button.setObjectName("create_invoice_button")
        create_invoice_button.setIcon(QIcon("assets/icons/add_invoice.png"))
        create_invoice_button.clicked.connect(self.create_invoice)
        bottom_layout.addWidget(create_invoice_button)
        
        return bottom_bar
    
    def setup_connections(self):
        # Connect search box
        self.search_box.textChanged.connect(self.search)
        
        # Connect calendar to update appointments
        self.calendar.selectionChanged.connect(self.update_appointments_for_date)
        
        # Update calendar with today's appointments
        self.update_appointments_for_date()
        
        # Update financial stats if admin
        if self.is_admin:
            self.update_financial_stats()
            
            # Set up timer to update stats every hour
            self.stats_timer = QTimer(self)
            self.stats_timer.timeout.connect(self.update_financial_stats)
            self.stats_timer.start(3600000)  # 1 hour in milliseconds
    
    def show_tab(self, index):
        # Update sidebar button states
        for i, button in enumerate(self.sidebar_buttons):
            button.setChecked(i == index)
        
        # Show the selected tab
        self.content_stack.setCurrentIndex(index)
        
        # Update search placeholder based on active tab
        if index == 0:
            self.search_box.setPlaceholderText(self.tr("appointments.search"))
        elif index == 1:
            self.search_box.setPlaceholderText(self.tr("customers.search"))
        elif index == 2:
            self.search_box.setPlaceholderText(self.tr("services.search"))
        elif index == 3:
            self.search_box.setPlaceholderText(self.tr("invoices.search"))
    
    def search(self, text):
        current_tab = self.content_stack.currentIndex()
        
        if current_tab == 0:
            self.appointments_tab.search(text)
        elif current_tab == 1:
            self.customers_tab.search(text)
        elif current_tab == 2:
            self.services_tab.search(text)
        elif current_tab == 3:
            self.invoices_tab.search(text)
    
    def calendar_date_clicked(self, date):
        # Show appointments for the selected date
        appointments = self.db_manager.get_appointments_by_date(date.toPyDate())
        
        if appointments:
            # Show appointments in a dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"{self.tr('appointments.title')} - {date.toString()}")
            dialog.setMinimumWidth(600)
            
            layout = QVBoxLayout(dialog)
            
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels([
                self.tr("appointments.time"),
                self.tr("appointments.customer_name"),
                self.tr("appointments.services"),
                self.tr("appointments.service_provider")
            ])
            table.horizontalHeader().setStretchLastSection(True)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            
            # Populate table
            table.setRowCount(len(appointments))
            for i, appointment in enumerate(appointments):
                # Time
                time = QDateTime.fromString(appointment["date_time"], Qt.DateFormat.ISODate).time().toString("hh:mm")
                table.setItem(i, 0, QTableWidgetItem(time))
                
                # Customer name
                table.setItem(i, 1, QTableWidgetItem(appointment["customer_name"]))
                
                # Services
                services = ", ".join([service["name"] for service in appointment["services"]])
                table.setItem(i, 2, QTableWidgetItem(services))
                
                # Service provider
                table.setItem(i, 3, QTableWidgetItem(appointment["service_provider"]))
            
            layout.addWidget(table)
            
            # Close button
            close_button = QPushButton(self.tr("common.close"))
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            
            dialog.exec()
    
    def update_appointments_for_date(self):
        # Get selected date
        selected_date = self.calendar.selectedDate().toPyDate()
        
        # Get appointments for the date
        appointments = self.db_manager.get_appointments_by_date(selected_date)
        
        # Update upcoming appointments table
        self.upcoming_appointments.setRowCount(len(appointments))
        for i, appointment in enumerate(appointments):
            # Time
            time = QDateTime.fromString(appointment["date_time"], Qt.DateFormat.ISODate).time().toString("hh:mm")
            self.upcoming_appointments.setItem(i, 0, QTableWidgetItem(time))
            
            # Customer name
            self.upcoming_appointments.setItem(i, 1, QTableWidgetItem(appointment["customer_name"]))
        
        # Resize columns to content
        self.upcoming_appointments.resizeColumnsToContents()
        
        # Mark dates with appointments on the calendar
        self.mark_calendar_dates()
    
    def mark_calendar_dates(self):
        # Get all appointments
        appointments = self.db_manager.get_all_appointments()
        
        # Create a set of dates with appointments
        dates_with_appointments = set()
        for appointment in appointments:
            date = QDateTime.fromString(appointment["date_time"], Qt.DateFormat.ISODate).date()
            dates_with_appointments.add(date.toString(Qt.DateFormat.ISODate))
        
        # Get the first day of the month
        first_day = QDate(self.calendar.yearShown(), self.calendar.monthShown(), 1)
        
        # Get the number of days in the month
        days_in_month = first_day.daysInMonth()
        
        # Mark dates with appointments
        for day in range(1, days_in_month + 1):
            date = QDate(self.calendar.yearShown(), self.calendar.monthShown(), day)
            date_str = date.toString(Qt.DateFormat.ISODate)
            
            if date_str in dates_with_appointments:
                # Set a bold font for dates with appointments
                format = self.calendar.dateTextFormat(date)
                font = format.font()
                font.setBold(True)
                format.setFont(font)
                self.calendar.setDateTextFormat(date, format)
            else:
                # Reset format for dates without appointments
                self.calendar.setDateTextFormat(date, QTextCharFormat())
    
    def update_financial_stats(self):
        if not self.is_admin:
            return
        
        # Get current date
        today = datetime.date.today()
        
        # Calculate daily revenue
        daily_revenue = self.db_manager.get_daily_revenue(today)
        self.daily_revenue.setText(f"{daily_revenue:,.0f} {self.tr('services.price_currency')}")
        
        # Calculate weekly revenue (starting from Monday)
        monday = today - datetime.timedelta(days=today.weekday())
        weekly_revenue = self.db_manager.get_weekly_revenue(monday)
        self.weekly_revenue.setText(f"{weekly_revenue:,.0f} {self.tr('services.price_currency')}")
        
        # Calculate monthly revenue
        monthly_revenue = self.db_manager.get_monthly_revenue(today.year, today.month)
        self.monthly_revenue.setText(f"{monthly_revenue:,.0f} {self.tr('services.price_currency')}")
    
    def show_language_menu(self):
        # Toggle between languages directly without popup menu
        current_lang = self.language_manager.get_current_language()
        new_lang = "en" if current_lang == "ar" else "ar"
        self.change_language(new_lang)
    
    def change_language(self, language_code):
        self.language_manager.set_language(language_code)
        
        # Apply RTL/LTR layout direction
        is_rtl = language_code == "ar"
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if is_rtl else Qt.LayoutDirection.LeftToRight)
        
        # Refresh UI to apply changes immediately
        self.refresh_ui()
    
    def show_theme_menu(self):
        # Toggle between themes directly without popup menu
        current_theme = self.theme_manager.get_current_theme()
        new_theme = "dark" if current_theme == "light" else "light"
        self.change_theme(new_theme)
    
    def change_theme(self, theme_name):
        self.theme_manager.set_theme(theme_name)
        self.refresh_ui()  # Apply changes immediately
    
    def show_notifications(self):
        # Show notifications dialog
        QMessageBox.information(self, self.tr("main.notifications"), self.tr("no_notifications"))
    
    def show_settings(self):
        # Show settings dialog
        settings_dialog = SettingsDialog(self.db_manager, self.theme_manager, self.language_manager, self.backup_manager, self.is_admin)
        settings_dialog.exec()
    
    def logout(self):
        # Confirm logout
        reply = QMessageBox.question(self, self.tr("main.logout"), 
                                    self.tr("confirm_logout"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()

    def retranslateUi(self):
        """Retranslate all UI elements"""
        self.setWindowTitle(self.tr("app_title"))
        self.search_box.setPlaceholderText(self.tr("main.search"))
        self.language_button.setText(self.tr("main.languages"))
        self.theme_button.setText(self.tr("main.themes"))
        self.notifications_button.setText(self.tr("main.notifications"))
        self.settings_button.setText(self.tr("main.settings"))
        self.logout_button.setText(self.tr("main.logout"))
        
        # Update sidebar buttons
        self.sidebar_buttons[0].setText(self.tr("sidebar.appointments"))
        self.sidebar_buttons[1].setText(self.tr("sidebar.customers"))
        self.sidebar_buttons[2].setText(self.tr("sidebar.services"))
        self.sidebar_buttons[3].setText(self.tr("sidebar.invoices"))
        
        # Update bottom bar buttons
        self.bottom_bar.findChild(QPushButton, "add_appointment_button").setText(self.tr("appointments.add"))
        self.bottom_bar.findChild(QPushButton, "add_customer_button").setText(self.tr("customers.add"))
        self.bottom_bar.findChild(QPushButton, "create_invoice_button").setText(self.tr("invoices.add"))

    def refresh_ui(self):
        """Refresh the UI to apply any changes"""
        # Re-apply theme
        self.theme_manager.apply_theme()
        
        # Re-translate all text
        self.retranslateUi()
        
        # Update all tabs
        self.appointments_tab.refresh()
        self.customers_tab.refresh()
        self.services_tab.refresh()
        self.invoices_tab.refresh()
        
        # Update calendar and stats
        self.update_appointments_for_date()
        if self.is_admin:
            self.update_financial_stats()
    
    def add_appointment(self):
        self.show_tab(0)  # Switch to appointments tab
        self.appointments_tab.add_appointment()
    
    def add_customer(self):
        self.show_tab(1)  # Switch to customers tab
        self.customers_tab.add_customer()
    
    def create_invoice(self):
        self.show_tab(3)  # Switch to invoices tab
        self.invoices_tab.create_invoice()
