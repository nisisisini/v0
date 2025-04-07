# views\main_view.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QCalendarWidget, 
                           QStackedWidget, QComboBox, QCheckBox, QTextEdit, QMessageBox,
                           QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QTabWidget,
                           QGroupBox, QScrollArea, QSplitter, QMenu, QToolBar, QStatusBar,
                           QAction, QFileDialog, QDateEdit, QTimeEdit, QDateTimeEdit, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QAction, QTextCharFormat
import datetime
import json
import os

from views.clients_view import ClientsView
from views.appointments_view import AppointmentsView
from views.services_view import ServicesView
from views.invoices_view import InvoicesView
from views.settings_view import SettingsView

from controllers.clients_controller import ClientsController
from controllers.appointments_controller import AppointmentsController
from controllers.services_controller import ServicesController
from controllers.invoices_controller import InvoicesController
from controllers.notifications_controller import NotificationsController

from utils.icon_loader import load_icon
from utils.theme_manager import ThemeManager  # Import ThemeManager

class MainView(QMainWindow):
    """Main application window."""
    
    logout_signal = pyqtSignal()
    
    def __init__(self, db_manager, settings, translation_manager, backup_manager, notification_manager, username, is_admin):
        """
        Initialize the main application window.

        Args:
            db_manager: Database manager instance.
            settings: Application settings manager.
            translation_manager: Translation manager for multilingual support.
            backup_manager: Backup manager for handling backups.
            notification_manager: Notification manager for alerts.
            username: Current user's username.
            is_admin: Boolean indicating if the user has admin privileges.
        """
        super().__init__()
        self.db_manager = db_manager
        self.settings = settings
        self.translation_manager = translation_manager
        self.backup_manager = backup_manager
        self.notification_manager = notification_manager
        self.username = username
        self.is_admin = is_admin
        self.tr = self.translation_manager.get_translation

        # Initialize theme manager
        self.theme_manager = ThemeManager(self.settings)

        # Initialize controllers
        self.clients_controller = ClientsController(db_manager)
        self.appointments_controller = AppointmentsController(db_manager)
        self.services_controller = ServicesController(db_manager)
        self.invoices_controller = InvoicesController(db_manager)
        self.notifications_controller = NotificationsController(db_manager, notification_manager)
        
        # Set up the UI and connections
        self.setup_ui()
        self.setup_connections()
        
        # Perform auto backup if needed
        backup_interval = int(self.settings.get_setting("backup.backup_interval_days", 1))
        if self.settings.get_setting("backup.auto_backup", True):
            try:
                self.backup_manager.auto_backup(backup_interval)
            except Exception as e:
                print(f"Auto backup failed: {e}")
    
    def setup_ui(self):
        """
        Set up the main user interface, including the toolbar, sidebar, main content area, and bottom bar.
        """
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
        bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(bottom_bar)  # السطر الصحيح
        
        # Unified button definitions with error handling for icons
        buttons_layout = QHBoxLayout()

        try:
            add_button = QPushButton(self.tr("common.add"))
            add_button.setIcon(QIcon(load_icon("add.png")))
        except FileNotFoundError:
            add_button = QPushButton(self.tr("common.add"))
            add_button.setIcon(QIcon())  # Default empty icon
            print("Warning: Icon 'add.png' not found.")
        add_button.clicked.connect(self.add_appointment)
        buttons_layout.addWidget(add_button)

        try:
            edit_button = QPushButton(self.tr("common.edit"))
            edit_button.setIcon(QIcon(load_icon("edit.png")))
        except FileNotFoundError:
            edit_button = QPushButton(self.tr("common.edit"))
            edit_button.setIcon(QIcon())
            print("Warning: Icon 'edit.png' not found.")
        edit_button.clicked.connect(self.edit_item)
        buttons_layout.addWidget(edit_button)

        try:
            delete_button = QPushButton(self.tr("common.delete"))
            delete_button.setIcon(QIcon(load_icon("delete.png")))
        except FileNotFoundError:
            delete_button = QPushButton(self.tr("common.delete"))
            delete_button.setIcon(QIcon())
            print("Warning: Icon 'delete.png' not found.")
        delete_button.clicked.connect(self.delete_item)
        buttons_layout.addWidget(delete_button)

        try:
            create_invoice_button = QPushButton(self.tr("invoices.add"))
            create_invoice_button.setIcon(QIcon(load_icon("add_invoice.png")))
        except FileNotFoundError:
            create_invoice_button = QPushButton(self.tr("invoices.add"))
            create_invoice_button.setIcon(QIcon())
            print("Warning: Icon 'add_invoice.png' not found.")
        create_invoice_button.clicked.connect(self.create_invoice)
        buttons_layout.addWidget(create_invoice_button)

        # Add buttons layout to main layout
        self.centralWidget().layout().addLayout(buttons_layout)
        
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
        
        try:
            self.language_button = QAction(QIcon(load_icon("language.png")), self.tr("main.languages"), self)
        except FileNotFoundError:
            self.language_button = QAction(QIcon(), self.tr("main.languages"), self)
            print("Warning: Icon 'language.png' not found.")
        self.language_button.triggered.connect(self.toggle_language)
        self.toolbar.addAction(self.language_button)
        
        try:
            self.theme_button = QAction(QIcon(load_icon("theme.png")), self.tr("main.themes"), self)
        except FileNotFoundError:
            self.theme_button = QAction(QIcon(), self.tr("main.themes"), self)
            print("Warning: Icon 'theme.png' not found.")
        self.theme_button.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(self.theme_button)
        
        try:
            self.notifications_button = QAction(QIcon(load_icon("notification.png")), self.tr("main.notifications"), self)
        except FileNotFoundError:
            self.notifications_button = QAction(QIcon(), self.tr("main.notifications"), self)
            print("Warning: Icon 'notification.png' not found.")
        self.notifications_button.triggered.connect(self.show_notifications)
        self.toolbar.addAction(self.notifications_button)
        
        try:
            self.settings_button = QAction(QIcon(load_icon("settings.png")), self.tr("main.settings"), self)
        except FileNotFoundError:
            self.settings_button = QAction(QIcon(), self.tr("main.settings"), self)
            print("Warning: Icon 'settings.png' not found.")
        self.settings_button.triggered.connect(self.show_settings)
        self.toolbar.addAction(self.settings_button)
        
        try:
            self.logout_button = QAction(QIcon(load_icon("logout.png")), self.tr("main.logout"), self)
        except FileNotFoundError:
            self.logout_button = QAction(QIcon(), self.tr("main.logout"), self)
            print("Warning: Icon 'logout.png' not found.")
        self.logout_button.triggered.connect(self.logout)
        self.toolbar.addAction(self.logout_button)
    
    def create_sidebar(self):
        """
        Initialize the sidebar with navigation buttons for different tabs.
        """
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(250)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Create sidebar buttons
        self.sidebar_buttons = []
        
        try:
            appointments_button = QPushButton(self.tr("sidebar.appointments"))
            appointments_button.setIcon(QIcon(load_icon("calendar.png")))
        except FileNotFoundError:
            appointments_button = QPushButton(self.tr("sidebar.appointments"))
            appointments_button.setIcon(QIcon())
            print("Warning: Icon 'calendar.png' not found.")
        appointments_button.setCheckable(True)
        appointments_button.clicked.connect(lambda: self.show_tab(0))
        sidebar_layout.addWidget(appointments_button)
        self.sidebar_buttons.append(appointments_button)
        
        try:
            customers_button = QPushButton(self.tr("sidebar.customers"))
            customers_button.setIcon(QIcon(load_icon("customers.png")))
        except FileNotFoundError:
            customers_button = QPushButton(self.tr("sidebar.customers"))
            customers_button.setIcon(QIcon())
            print("Warning: Icon 'customers.png' not found.")
        customers_button.setCheckable(True)
        customers_button.clicked.connect(lambda: self.show_tab(1))
        sidebar_layout.addWidget(customers_button)
        self.sidebar_buttons.append(customers_button)
        
        try:
            services_button = QPushButton(self.tr("sidebar.services"))
            services_button.setIcon(QIcon(load_icon("services.png")))
        except FileNotFoundError:
            services_button = QPushButton(self.tr("sidebar.services"))
            services_button.setIcon(QIcon())
            print("Warning: Icon 'services.png' not found.")
        services_button.setCheckable(True)
        services_button.clicked.connect(lambda: self.show_tab(2))
        sidebar_layout.addWidget(services_button)
        self.sidebar_buttons.append(services_button)
        
        try:
            invoices_button = QPushButton(self.tr("sidebar.invoices"))
            invoices_button.setIcon(QIcon(load_icon("invoice.png")))
        except FileNotFoundError:
            invoices_button = QPushButton(self.tr("sidebar.invoices"))
            invoices_button.setIcon(QIcon())
            print("Warning: Icon 'invoice.png' not found.")
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
        self.appointments_view = AppointmentsView(
            self.db_manager, 
            self.translation_manager, 
            self.appointments_controller,
            self.clients_controller,
            self.services_controller,
            self.is_admin
        )
        
        self.clients_view = ClientsView(
            self.db_manager, 
            self.translation_manager, 
            self.clients_controller,
            self.is_admin
        )
        
        self.services_view = ServicesView(
            self.db_manager, 
            self.translation_manager, 
            self.services_controller,
            self.is_admin
        )
        
        self.invoices_view = InvoicesView(
            self.db_manager, 
            self.translation_manager, 
            self.invoices_controller,
            self.clients_controller,
            self.appointments_controller,
            self.services_controller,
            self.is_admin
        )
        
        # Add tabs to stack
        self.content_stack.addWidget(self.appointments_view)
        self.content_stack.addWidget(self.clients_view)
        self.content_stack.addWidget(self.services_view)
        self.content_stack.addWidget(self.invoices_view)
        
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
        
        try:
            add_appointment_button = QPushButton(self.tr("appointments.add"))
            add_appointment_button.setIcon(QIcon(load_icon("add_appointment.png")))
        except FileNotFoundError:
            add_appointment_button = QPushButton(self.tr("appointments.add"))
            add_appointment_button.setIcon(QIcon())
            print("Warning: Icon 'add_appointment.png' not found.")
        add_appointment_button.setObjectName("add_appointment_button")  # Assign object name
        add_appointment_button.setIconSize(QSize(24, 24))
        add_appointment_button.setStyleSheet("QPushButton { padding: 5px; }")
        add_appointment_button.clicked.connect(self.add_appointment)
        bottom_layout.addWidget(add_appointment_button)
        
        try:
            add_customer_button = QPushButton(self.tr("customers.add"))
            add_customer_button.setIcon(QIcon(load_icon("add_customer.png")))
        except FileNotFoundError:
            add_customer_button = QPushButton(self.tr("customers.add"))
            add_customer_button.setIcon(QIcon())
            print("Warning: Icon 'add_customer.png' not found.")
        add_customer_button.setObjectName("add_customer_button")  # Assign object name
        add_customer_button.setIconSize(QSize(24, 24))
        add_customer_button.setStyleSheet("QPushButton { padding: 5px; }")
        add_customer_button.clicked.connect(self.add_customer)
        bottom_layout.addWidget(add_customer_button)
        
        try:
            create_invoice_button = QPushButton(self.tr("invoices.add"))
            create_invoice_button.setIcon(QIcon(load_icon("add_invoice.png")))
        except FileNotFoundError:
            create_invoice_button = QPushButton(self.tr("invoices.add"))
            create_invoice_button.setIcon(QIcon())
            print("Warning: Icon 'add_invoice.png' not found.")
        create_invoice_button.setObjectName("create_invoice_button")  # Assign object name
        create_invoice_button.setIconSize(QSize(24, 24))
        create_invoice_button.setStyleSheet("QPushButton { padding: 5px; }")
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
            self.appointments_view.search(text)
        elif current_tab == 1:
            self.clients_view.search(text)
        elif current_tab == 2:
            self.services_view.search(text)
        elif current_tab == 3:
            self.invoices_view.search(text)
    
    def calendar_date_clicked(self, date):
        # Show appointments for the selected date
        appointments = self.appointments_controller.get_appointments_by_date(date.toPyDate())
        
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
        appointments = self.appointments_controller.get_appointments_by_date(selected_date)
        
        if not appointments:
            # Show a message indicating no appointments
            self.upcoming_appointments.setRowCount(1)
            self.upcoming_appointments.setItem(0, 0, QTableWidgetItem(self.tr("appointments.no_appointments")))
            self.upcoming_appointments.setItem(0, 1, QTableWidgetItem(""))
        else:
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
        # Get appointments for the currently displayed month
        try:
            appointments = self.appointments_controller.get_appointments_by_month(
                self.calendar.yearShown(), self.calendar.monthShown()
            )
        except AttributeError:
            # Fallback if get_appointments_by_month is not implemented
            appointments = [
                appt for appt in self.appointments_controller.get_all_appointments()
                if QDateTime.fromString(appt["date_time"], Qt.DateFormat.ISODate).date().month() == self.calendar.monthShown()
                and QDateTime.fromString(appt["date_time"], Qt.DateFormat.ISODate).date().year() == self.calendar.yearShown()
            ]
        
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
        daily_revenue = self.invoices_controller.get_daily_revenue(today)
        self.daily_revenue.setText(f"{daily_revenue:,.0f} {self.tr('services.price_currency')}")
        
        # Calculate weekly revenue (starting from Monday)
        monday = today - datetime.timedelta(days=today.weekday())
        weekly_revenue = self.invoices_controller.get_weekly_revenue(monday)
        self.weekly_revenue.setText(f"{weekly_revenue:,.0f} {self.tr('services.price_currency')}")
        
        # Calculate monthly revenue
        monthly_revenue = self.invoices_controller.get_monthly_revenue(today.year, today.month)
        self.monthly_revenue.setText(f"{monthly_revenue:,.0f} {self.tr('services.price_currency')}")
    
    def toggle_language(self):
        # تبديل اللغة بين العربية والإنجليزية
        current_language = self.translation_manager.get_current_language()
        new_language = "en" if current_language == "ar" else "ar"
        self.change_language(new_language)

    def toggle_theme(self):
        # تبديل الثيم بين الفاتح والغامق
        current_theme = self.settings.get_setting("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.change_theme(new_theme)

    def change_language(self, language_code):
        # تغيير اللغة مباشرة
        self.translation_manager.set_language(language_code)
        self.refresh_ui()

    def change_theme(self, theme_name):
        # تغيير الثيم مباشرة
        self.settings.set_setting("theme", theme_name)
        self.refresh_ui()

    def retranslate_ui(self):
        """Retranslate all UI elements"""
        self.setWindowTitle(self.tr("app_title"))
        self.search_box.setPlaceholderText(self.tr("main.search"))
        self.language_button.setText(self.tr("main.languages"))
        self.theme_button.setText(self.tr("main.themes"))
        self.notifications_button.setText(self.tr("main.notifications"))
        self.settings_button.setText(self.tr("main.settings"))
        self.logout_button.setText(self.tr("main.logout"))
        
        # Update sidebar buttons
        for i, button in enumerate(self.sidebar_buttons):
            button.setText(self.tr(f"sidebar.{['appointments', 'customers', 'services', 'invoices'][i]}"))
        
        # Update bottom bar buttons
        button = self.bottom_bar.findChild(QPushButton, "add_appointment_button")
        if button:
            button.setText(self.tr("appointments.add"))

        button = self.bottom_bar.findChild(QPushButton, "add_customer_button")
        if button:
            button.setText(self.tr("customers.add"))

        button = self.bottom_bar.findChild(QPushButton, "create_invoice_button")
        if button:
            button.setText(self.tr("invoices.add"))

        self.update_financial_stats()

    def refresh_ui(self):
        """
        Refresh the UI to apply any changes, such as theme or language updates.
        """
        # Re-apply theme
        self.theme_manager.apply_theme()
        
        # Re-translate all text
        self.retranslate_ui()
        
        # Update all views
        self.appointments_view.refresh()
        self.clients_view.refresh()
        self.services_view.refresh()
        self.invoices_view.refresh()
        
        # Update calendar and stats
        self.update_appointments_for_date()
        if self.is_admin:
            self.update_financial_stats()
    
    def show_notifications(self):
        # Check for upcoming appointments
        reminder_hours = self.settings.get_setting("notifications.reminder_hours_before", 24)
        count = self.notifications_controller.check_upcoming_appointments(reminder_hours)
        
        if count > 0:
            QMessageBox.information(self, self.tr("main.notifications"), 
                                   self.tr("upcoming_appointments_count").format(count=count))
        else:
            QMessageBox.information(self, self.tr("main.notifications"), self.tr("no_notifications"))
    
    def show_settings(self):
        # Show settings dialog
        settings_view = SettingsView(
            self.db_manager, 
            self.settings, 
            self.translation_manager, 
            self.backup_manager, 
            self.is_admin
        )
        settings_view.exec()
    
    def logout(self):
        # Confirm logout
        reply = QMessageBox.question(self, self.tr("main.logout"), 
                                    self.tr("confirm_logout"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()
    
    def add_appointment(self):
        self.show_tab(0)  # Switch to appointments tab
        self.appointments_view.add_appointment()
    
    def add_customer(self):
        self.show_tab(1)  # Switch to customers tab
        self.clients_view.add_customer()
    
    def create_invoice(self):
        self.show_tab(3)  # Switch to invoices tab
        self.invoices_view.create_invoice()
    
    def edit_item(self):
        # Placeholder for edit functionality
        print("Edit item functionality not implemented.")
    
    def delete_item(self):
        # Placeholder for delete functionality
        print("Delete item functionality not implemented.")

