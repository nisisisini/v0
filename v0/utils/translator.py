import os
import json
from PyQt6.QtCore import QTranslator, QLocale, QCoreApplication, Qt

class TranslationManager:
    """Manages translations for the application."""
    
    def __init__(self, settings=None):
        self.settings = settings
        self.translator = QTranslator()
        self.translations = {}
        self.current_language = "ar"  # Default to Arabic
        
        # Load translations
        self.load_translations()
        
        # Apply initial language
        if self.settings:
            self.current_language = self.settings.get_setting("language", "ar")
        
        self.apply_language()
    
    def load_translations(self):
        """Load translations from JSON files."""
        translations_dir = "resources/translations"
        
        # Ensure the directory exists
        os.makedirs(translations_dir, exist_ok=True)
        
        # Load Arabic translations
        ar_path = os.path.join(translations_dir, "ar.json")
        if not os.path.exists(ar_path):
            self.create_default_arabic_translations(ar_path)
        
        with open(ar_path, "r", encoding="utf-8") as f:
            self.translations["ar"] = json.load(f)
        
        # Load English translations
        en_path = os.path.join(translations_dir, "en.json")
        if not os.path.exists(en_path):
            self.create_default_english_translations(en_path)
        
        with open(en_path, "r", encoding="utf-8") as f:
            self.translations["en"] = json.load(f)
    
    def create_default_arabic_translations(self, path):
        """Create default Arabic translations."""
        translations = {
            "app_title": "مركز جوزيل للتجميل",
            
            # Common
            "common.success": "نجاح",
            "common.error": "خطأ",
            "common.warning": "تحذير",
            "common.info": "معلومات",
            "common.confirm": "تأكيد",
            "common.cancel": "إلغاء",
            "common.save": "حفظ",
            "common.delete": "حذف",
            "common.edit": "تعديل",
            "common.add": "إضافة",
            "common.close": "إغلاق",
            "common.actions": "إجراءات",
            "common.confirm_delete": "هل أنت متأكد من أنك تريد الحذف؟",
            "common.operation_success": "تمت العملية بنجاح",
            "common.operation_failed": "فشلت العملية",
            
            # Login
            "login.title": "تسجيل الدخول",
            "login.username": "اسم المستخدم",
            "login.password": "كلمة المرور",
            "login.remember_me": "تذكرني",
            "login.login_button": "تسجيل الدخول",
            "login.error": "اسم المستخدم أو كلمة المرور غير صحيحة",
            
            # Main
            "main.search": "بحث...",
            "main.languages": "اللغات",
            "main.themes": "السمات",
            "main.notifications": "الإشعارات",
            "main.settings": "الإعدادات",
            "main.logout": "تسجيل الخروج",
            
            # Sidebar
            "sidebar.appointments": "المواعيد",
            "sidebar.customers": "العملاء",
            "sidebar.services": "الخدمات",
            "sidebar.invoices": "الفواتير",
            
            # Appointments
            "appointments.title": "المواعيد",
            "appointments.id": "الرقم",
            "appointments.customer_name": "اسم العميل",
            "appointments.phone": "الهاتف",
            "appointments.date_time": "التاريخ والوقت",
            "appointments.services": "الخدمات",
            "appointments.service_provider": "مقدم الخدمة",
            "appointments.notes": "ملاحظات",
            "appointments.status": "الحالة",
            "appointments.remaining_payments": "المدفوعات المتبقية",
            "appointments.add": "إضافة موعد",
            "appointments.edit": "تعديل موعد",
            "appointments.delete": "حذف موعد",
            "appointments.appointment_details": "تفاصيل الموعد",
            "appointments.confirmed": "مؤكد",
            "appointments.unconfirmed": "غير مؤكد",
            "appointments.time": "الوقت",
            "appointments.search": "بحث في المواعيد...",
            
            # Customers
            "customers.title": "العملاء",
            "customers.id": "الرقم",
            "customers.name": "الاسم",
            "customers.phone": "الهاتف",
            "customers.email": "البريد الإلكتروني",
            "customers.hair_type": "نوع الشعر",
            "customers.hair_color": "لون الشعر",
            "customers.skin_type": "نوع البشرة",
            "customers.allergies": "الحساسية",
            "customers.current_sessions": "الجلسات الحالية",
            "customers.remaining_sessions": "الجلسات المتبقية",
            "customers.most_requested_services": "الخدمات الأكثر طلبًا",
            "customers.remaining_payments": "المدفوعات المتبقية",
            "customers.notes": "ملاحظات",
            "customers.add": "إضافة عميل",
            "customers.edit": "تعديل عميل",
            "customers.delete": "حذف عميل",
            "customers.customer_details": "تفاصيل العميل",
            "customers.search": "بحث في العملاء...",
            
            # Services
            "services.title": "الخدمات",
            "services.id": "الرقم",
            "services.name": "الاسم",
            "services.price": "السعر",
            "services.price_currency": "ل.س",
            "services.add": "إضافة خدمة",
            "services.edit": "تعديل خدمة",
            "services.delete": "حذف خدمة",
            "services.service_details": "تفاصيل الخدمة",
            "services.search": "بحث في الخدمات...",
            
            # Invoices
            "invoices.title": "الفواتير",
            "invoices.id": "الرقم",
            "invoices.customer_name": "اسم العميل",
            "invoices.phone": "الهاتف",
            "invoices.date": "التاريخ",
            "invoices.services": "الخدمات",
            "invoices.payment_method": "طريقة الدفع",
            "invoices.amount_paid": "المبلغ المدفوع",
            "invoices.amount_remaining": "المبلغ المتبقي",
            "invoices.total_amount": "المبلغ الإجمالي",
            "invoices.add": "إنشاء فاتورة",
            "invoices.edit": "تعديل فاتورة",
            "invoices.delete": "حذف فاتورة",
            "invoices.print": "طباعة فاتورة",
            "invoices.invoice_details": "تفاصيل الفاتورة",
            "invoices.cash": "نقدي",
            "invoices.installment": "تقسيط",
            "invoices.price_currency": "ل.س",
            "invoices.select_customer": "اختر العميل",
            "invoices.select_appointment": "اختر الموعد (اختياري)",
            "invoices.appointment_id": "رقم الموعد",
            "invoices.select_service": "اختر الخدمة",
            "invoices.invoice_creator": "منشئ الفاتورة",
            "invoices.service_provider": "مقدم الخدمة",
            "invoices.search": "بحث في الفواتير...",
            
            # Settings
            "settings.title": "الإعدادات",
            "settings.general": "عام",
            "settings.backup": "النسخ الاحتياطي",
            "settings.users": "المستخدمين",
            "settings.about": "حول",
            "settings.clinic_info": "معلومات العيادة",
            "settings.clinic_name": "اسم العيادة",
            "settings.clinic_phone": "هاتف العيادة",
            "settings.clinic_address": "عنوان العيادة",
            "settings.clinic_email": "البريد الإلكتروني للعيادة",
            "settings.notifications": "الإشعارات",
            "settings.appointment_reminder": "تذكير بالمواعيد",
            "settings.reminder_hours": "ساعات التذكير قبل الموعد",
            "settings.auto_backup": "نسخ احتياطي تلقائي",
            "settings.backup_interval": "فترة النسخ الاحتياطي (أيام)",
            "settings.backup_location": "موقع النسخ الاحتياطي",
            "settings.backup_now": "نسخ احتياطي الآن",
            "settings.restore_backup": "استعادة من نسخة احتياطية",
            "settings.username": "اسم المستخدم",
            "settings.password": "كلمة المرور",
            "settings.is_admin": "مدير",
            "settings.add_user": "إضافة مستخدم",
            "settings.edit_user": "تعديل مستخدم",
            "settings.version": "الإصدار",
            "settings.developer": "المطور",
            
            # Other
            "admin_only": "هذه العملية متاحة للمدير فقط",
            "select_appointment_to_edit": "الرجاء اختيار موعد للتعديل",
            "select_appointment_to_delete": "الرجاء اختيار موعد للحذف",
            "select_customer_to_edit": "الرجاء اختيار عميل للتعديل",
            "select_customer_to_delete": "الرجاء اختيار عميل للحذف",
            "select_service_to_edit": "الرجاء اختيار خدمة للتعديل",
            "select_service_to_delete": "الرجاء اختيار خدمة للحذف",
            "select_invoice_to_edit": "الرجاء اختيار فاتورة للتعديل",
            "select_invoice_to_delete": "الرجاء اختيار فاتورة للحذف",
            "select_invoice_to_print": "الرجاء اختيار فاتورة للطباعة",
            "select_customer": "الرجاء اختيار عميل",
            "enter_valid_date": "الرجاء إدخال تاريخ صحيح",
            "select_at_least_one_service": "الرجاء اختيار خدمة واحدة على الأقل",
            "enter_invoice_creator": "الرجاء إدخال اسم منشئ الفاتورة",
            "enter_service_provider": "الرجاء إدخال اسم مقدم الخدمة",
            "enter_customer_name": "الرجاء إدخال اسم العميل",
            "enter_customer_phone": "الرجاء إدخال رقم هاتف العميل",
            "enter_service_name": "الرجاء إدخال اسم الخدمة",
            "quantity": "الكمية",
            "calendar.upcoming_appointments": "المواعيد القادمة",
            "financial_stats": "الإحصائيات المالية",
            "daily_revenue": "الإيرادات اليومية",
            "weekly_revenue": "الإيرادات الأسبوعية",
            "monthly_revenue": "الإيرادات الشهرية",
            "confirm_logout": "هل أنت متأكد من أنك تريد تسجيل الخروج؟",
            "light_theme": "سمة فاتحة",
            "dark_theme": "سمة داكنة",
            "language_change_restart": "يجب إعادة تشغيل التطبيق لتطبيق تغيير اللغة",
            "theme_change_restart": "يجب إعادة تشغيل التطبيق لتطبيق تغيير السمة",
            "upcoming_appointments_count": "لديك {count} مواعيد قادمة",
            "no_notifications": "لا توجد إشعارات",
            "available_backups": "النسخ الاحتياطية المتاحة",
            "filename": "اسم الملف",
            "date": "التاريخ",
            "size": "الحجم",
            "delete_backup": "حذف النسخة الاحتياطية",
            "select_backup_to_restore": "الرجاء اختيار نسخة احتياطية للاستعادة",
            "confirm_restore_backup": "هل أنت متأكد من أنك تريد استعادة هذه النسخة الاحتياطية؟ سيتم استبدال جميع البيانات الحالية.",
            "backup_created": "تم إنشاء النسخة الاحتياطية",
            "backup_restored": "تم استعادة النسخة الاحتياطية",
            "backup_deleted": "تم حذف النسخة الاحتياطية",
            "backup_failed": "فشل إنشاء النسخة الاحتياطية",
            "restore_failed": "فشل استعادة النسخة الاحتياطية",
            "delete_failed": "فشل حذف النسخة الاحتياطية",
            "restart_required": "يجب إعادة تشغيل التطبيق لتطبيق التغييرات",
            "select_backup_location": "اختر موقع النسخ الاحتياطي",
            "select_backup_to_delete": "الرجاء اختيار نسخة احتياطية للحذف",
            "enter_username": "الرجاء إدخال اسم المستخدم",
            "enter_password": "الرجاء إدخال كلمة المرور",
            "confirm_delete_user": "هل أنت متأكد من أنك تريد حذف المستخدم {username}؟",
            "user_deleted": "تم حذف المستخدم",
            "user_saved": "تم حفظ المستخدم"
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)
    
    def create_default_english_translations(self, path):
        """Create default English translations."""
        translations = {
            "app_title": "Guzel Beauty Clinic",
            
            # Common
            "common.success": "Success",
            "common.error": "Error",
            "common.warning": "Warning",
            "common.info": "Information",
            "common.confirm": "Confirm",
            "common.cancel": "Cancel",
            "common.save": "Save",
            "common.delete": "Delete",
            "common.edit": "Edit",
            "common.add": "Add",
            "common.close": "Close",
            "common.actions": "Actions",
            "common.confirm_delete": "Are you sure you want to delete?",
            "common.operation_success": "Operation completed successfully",
            "common.operation_failed": "Operation failed",
            
            # Login
            "login.title": "Login",
            "login.username": "Username",
            "login.password": "Password",
            "login.remember_me": "Remember me",
            "login.login_button": "Login",
            "login.error": "Invalid username or password",
            
            # Main
            "main.search": "Search...",
            "main.languages": "Languages",
            "main.themes": "Themes",
            "main.notifications": "Notifications",
            "main.settings": "Settings",
            "main.logout": "Logout",
            
            # Sidebar
            "sidebar.appointments": "Appointments",
            "sidebar.customers": "Customers",
            "sidebar.services": "Services",
            "sidebar.invoices": "Invoices",
            
            # Appointments
            "appointments.title": "Appointments",
            "appointments.id": "ID",
            "appointments.customer_name": "Customer Name",
            "appointments.phone": "Phone",
            "appointments.date_time": "Date & Time",
            "appointments.services": "Services",
            "appointments.service_provider": "Service Provider",
            "appointments.notes": "Notes",
            "appointments.status": "Status",
            "appointments.remaining_payments": "Remaining Payments",
            "appointments.add": "Add Appointment",
            "appointments.edit": "Edit Appointment",
            "appointments.delete": "Delete Appointment",
            "appointments.appointment_details": "Appointment Details",
            "appointments.confirmed": "Confirmed",
            "appointments.unconfirmed": "Unconfirmed",
            "appointments.time": "Time",
            "appointments.search": "Search appointments...",
            
            # Customers
            "customers.title": "Customers",
            "customers.id": "ID",
            "customers.name": "Name",
            "customers.phone": "Phone",
            "customers.email": "Email",
            "customers.hair_type": "Hair Type",
            "customers.hair_color": "Hair Color",
            "customers.skin_type": "Skin Type",
            "customers.allergies": "Allergies",
            "customers.current_sessions": "Current Sessions",
            "customers.remaining_sessions": "Remaining Sessions",
            "customers.most_requested_services": "Most Requested Services",
            "customers.remaining_payments": "Remaining Payments",
            "customers.notes": "Notes",
            "customers.add": "Add Customer",
            "customers.edit": "Edit Customer",
            "customers.delete": "Delete Customer",
            "customers.customer_details": "Customer Details",
            "customers.search": "Search customers...",
            
            # Services
            "services.title": "Services",
            "services.id": "ID",
            "services.name": "Name",
            "services.price": "Price",
            "services.price_currency": "SYP",
            "services.add": "Add Service",
            "services.edit": "Edit Service",
            "services.delete": "Delete Service",
            "services.service_details": "Service Details",
            "services.search": "Search services...",
            
            # Invoices
            "invoices.title": "Invoices",
            "invoices.id": "ID",
            "invoices.customer_name": "Customer Name",
            "invoices.phone": "Phone",
            "invoices.date": "Date",
            "invoices.services": "Services",
            "invoices.payment_method": "Payment Method",
            "invoices.amount_paid": "Amount Paid",
            "invoices.amount_remaining": "Amount Remaining",
            "invoices.total_amount": "Total Amount",
            "invoices.add": "Create Invoice",
            "invoices.edit": "Edit Invoice",
            "invoices.delete": "Delete Invoice",
            "invoices.print": "Print Invoice",
            "invoices.invoice_details": "Invoice Details",
            "invoices.cash": "Cash",
            "invoices.installment": "Installment",
            "invoices.price_currency": "SYP",
            "invoices.select_customer": "Select Customer",
            "invoices.select_appointment": "Select Appointment (Optional)",
            "invoices.appointment_id": "Appointment ID",
            "invoices.select_service": "Select Service",
            "invoices.invoice_creator": "Invoice Creator",
            "invoices.service_provider": "Service Provider",
            "invoices.search": "Search invoices...",
            
            # Settings
            "settings.title": "Settings",
            "settings.general": "General",
            "settings.backup": "Backup",
            "settings.users": "Users",
            "settings.about": "About",
            "settings.clinic_info": "Clinic Information",
            "settings.clinic_name": "Clinic Name",
            "settings.clinic_phone": "Clinic Phone",
            "settings.clinic_address": "Clinic Address",
            "settings.clinic_email": "Clinic Email",
            "settings.notifications": "Notifications",
            "settings.appointment_reminder": "Appointment Reminder",
            "settings.reminder_hours": "Reminder Hours Before Appointment",
            "settings.auto_backup": "Automatic Backup",
            "settings.backup_interval": "Backup Interval (Days)",
            "settings.backup_location": "Backup Location",
            "settings.backup_now": "Backup Now",
            "settings.restore_backup": "Restore Backup",
            "settings.username": "Username",
            "settings.password": "Password",
            "settings.is_admin": "Administrator",
            "settings.add_user": "Add User",
            "settings.edit_user": "Edit User",
            "settings.version": "Version",
            "settings.developer": "Developer",
            
            # Other
            "admin_only": "This operation is only available for administrators",
            "select_appointment_to_edit": "Please select an appointment to edit",
            "select_appointment_to_delete": "Please select an appointment to delete",
            "select_customer_to_edit": "Please select a customer to edit",
            "select_customer_to_delete": "Please select a customer to delete",
            "select_service_to_edit": "Please select a service to edit",
            "select_service_to_delete": "Please select a service to delete",
            "select_invoice_to_edit": "Please select an invoice to edit",
            "select_invoice_to_delete": "Please select an invoice to delete",
            "select_invoice_to_print": "Please select an invoice to print",
            "select_customer": "Please select a customer",
            "enter_valid_date": "Please enter a valid date",
            "select_at_least_one_service": "Please select at least one service",
            "enter_invoice_creator": "Please enter the invoice creator's name",
            "enter_service_provider": "Please enter the service provider's name",
            "enter_customer_name": "Please enter the customer's name",
            "enter_customer_phone": "Please enter the customer's phone number",
            "enter_service_name": "Please enter the service name",
            "quantity": "Quantity",
            "calendar.upcoming_appointments": "Upcoming Appointments",
            "financial_stats": "Financial Statistics",
            "daily_revenue": "Daily Revenue",
            "weekly_revenue": "Weekly Revenue",
            "monthly_revenue": "Monthly Revenue",
            "confirm_logout": "Are you sure you want to logout?",
            "light_theme": "Light Theme",
            "dark_theme": "Dark Theme",
            "language_change_restart": "You need to restart the application to apply the language change",
            "theme_change_restart": "You need to restart the application to apply the theme change",
            "upcoming_appointments_count": "You have {count} upcoming appointments",
            "no_notifications": "No notifications",
            "available  upcoming appointments": "Available upcoming appointments",
            "no_notifications": "No notifications",
            "available_backups": "Available Backups",
            "filename": "Filename",
            "date": "Date",
            "size": "Size",
            "delete_backup": "Delete Backup",
            "select_backup_to_restore": "Please select a backup to restore",
            "confirm_restore_backup": "Are you sure you want to restore this backup? All current data will be replaced.",
            "backup_created": "Backup created",
            "backup_restored": "Backup restored",
            "backup_deleted": "Backup deleted",
            "backup_failed": "Backup creation failed",
            "restore_failed": "Backup restoration failed",
            "delete_failed": "Backup deletion failed",
            "restart_required": "You need to restart the application to apply the changes",
            "select_backup_location": "Select backup location",
            "select_backup_to_delete": "Please select a backup to delete",
            "enter_username": "Please enter a username",
            "enter_password": "Please enter a password",
            "confirm_delete_user": "Are you sure you want to delete the user {username}?",
            "user_deleted": "User deleted",
            "user_saved": "User saved"
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)
    
    def get_translation(self, key):
        """Get a translation for a key."""
        if self.current_language in self.translations and key in self.translations[self.current_language]:
            return self.translations[self.current_language][key]
        
        # Fallback to Arabic
        if "ar" in self.translations and key in self.translations["ar"]:
            return self.translations["ar"][key]
        
        # Return the key if no translation is found
        return key
    
    def set_language(self, language_code):
        """Set the current language."""
        if language_code in self.translations:
            self.current_language = language_code
            
            if self.settings:
                self.settings.set_setting("language", language_code)
            
            self.apply_language()
            return True
        
        return False
    
    def apply_language(self):
        """Apply the current language to the application."""
        # Set the application layout direction
        if self.current_language == "ar":
            QApplication = QCoreApplication.instance()
            if QApplication:
                QApplication.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            QApplication = QCoreApplication.instance()
            if QApplication:
                QApplication.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        # Load the QTranslator (for future use with .qm files)
        # self.translator.load(f"resources/translations/{self.current_language}.qm")
        # QCoreApplication.instance().installTranslator(self.translator)

