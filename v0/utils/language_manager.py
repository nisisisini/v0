# utils/language_manager.py
import json
import os
from PyQt6.QtCore import pyqtSignal, QObject

class LanguageManager(QObject):
    language_changed = pyqtSignal()  # Signal emitted when language changes

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.translations_dir = "data/translations"
        self.ensure_translations_dir()
        self.load_translations()
    
    def ensure_translations_dir(self):
        os.makedirs(self.translations_dir, exist_ok=True)
    
    def load_translations(self):
        self.translations = {}
        
        # Load Arabic translations
        ar_file = os.path.join(self.translations_dir, "ar.json")
        if not os.path.exists(ar_file):
            self.create_default_arabic_translations(ar_file)
        
        with open(ar_file, 'r', encoding='utf-8') as f:
            self.translations["ar"] = json.load(f)
        
        # Load English translations
        en_file = os.path.join(self.translations_dir, "en.json")
        if not os.path.exists(en_file):
            self.create_default_english_translations(en_file)
        
        with open(en_file, 'r', encoding='utf-8') as f:
            self.translations["en"] = json.load(f)
    
    def create_default_arabic_translations(self, file_path):
        translations = {
            "app_title": "مركز جوزيل للتجميل",
            "login": {
                "title": "تسجيل الدخول",
                "username": "اسم المستخدم",
                "password": "كلمة المرور",
                "remember_me": "تذكرني",
                "login_button": "تسجيل الدخول",
                "error": "اسم المستخدم أو كلمة المرور غير صحيحة"
            },
            "main": {
                "search": "بحث",
                "languages": "اللغات",
                "themes": "السمات",
                "notifications": "الإشعارات",
                "settings": "الإعدادات",
                "logout": "تسجيل الخروج"
            },
            "sidebar": {
                "appointments": "المواعيد",
                "customers": "الزبائن",
                "services": "الخدمات والأسعار",
                "invoices": "الفواتير"
            },
            "calendar": {
                "upcoming_appointments": "المواعيد القادمة",
                "today": "اليوم",
                "no_appointments": "لا توجد مواعيد"
            },
            "appointments": {
                "title": "المواعيد",
                "id": "الرقم",
                "customer_name": "اسم الزبون/ة",
                "phone": "رقم الهاتف",
                "email": "البريد الإلكتروني",
                "date_time": "التاريخ والوقت",
                "services": "الخدمات",
                "service_provider": "مقدم الخدمة",
                "notes": "ملاحظات",
                "status": "الحالة",
                "remaining_payments": "الدفعات المتبقية",
                "add": "إضافة موعد",
                "edit": "تعديل",
                "delete": "حذف",
                "confirmed": "مؤكد",
                "unconfirmed": "غير مؤكد",
                "select_customer": "اختر الزبون",
                "select_service": "اختر الخدمة",
                "select_provider": "اختر مقدم الخدمة",
                "appointment_details": "تفاصيل الموعد"
            },
            "customers": {
                "title": "الزبائن",
                "id": "الرقم",
                "name": "الاسم",
                "phone": "رقم الهاتف",
                "email": "البريد الإلكتروني",
                "hair_type": "نوع الشعر",
                "hair_color": "لون الشعر",
                "skin_type": "نوع البشرة",
                "allergies": "الحساسية",
                "current_sessions": "عدد الجلسات الحالية",
                "remaining_sessions": "عدد الجلسات المتبقية",
                "most_requested_services": "الخدمات الأكثر طلباً",
                "remaining_payments": "الدفعات المتبقية",
                "notes": "ملاحظات",
                "add": "إضافة زبون",
                "edit": "تعديل",
                "delete": "حذف",
                "customer_details": "تفاصيل الزبون"
            },
            "services": {
                "title": "الخدمات والأسعار",
                "id": "الرقم",
                "name": "اسم الخدمة",
                "price": "السعر",
                "add": "إضافة خدمة",
                "edit": "تعديل",
                "delete": "حذف",
                "service_details": "تفاصيل الخدمة",
                "price_currency": "ل.س"
            },
            "invoices": {
                "title": "الفواتير",
                "id": "الرقم",
                "customer_name": "اسم الزبون/ة",
                "phone": "رقم الهاتف",
                "date": "التاريخ",
                "services": "الخدمات",
                "payment_method": "طريقة الدفع",
                "amount_paid": "المبلغ المدفوع",
                "amount_remaining": "المبلغ المتبقي",
                "invoice_creator": "محرر الفاتورة",
                "service_provider": "مقدم الخدمة",
                "total_amount": "المبلغ الإجمالي",
                "add": "إنشاء فاتورة",
                "edit": "تعديل",
                "delete": "حذف",
                "cash": "كاش",
                "installment": "تقسيط",
                "select_customer": "اختر الزبون",
                "select_appointment": "اختر الموعد",
                "select_service": "اختر الخدمة",
                "invoice_details": "تفاصيل الفاتورة",
                "print": "طباعة",
                "price_currency": "ل.س"
            },
            "settings": {
                "title": "الإعدادات",
                "general": "عام",
                "clinic_info": "معلومات المركز",
                "clinic_name": "اسم المركز",
                "clinic_phone": "رقم الهاتف",
                "clinic_address": "العنوان",
                "clinic_email": "البريد الإلكتروني",
                "social_media": "وسائل التواصل الاجتماعي",
                "backup": "النسخ الاحتياطي",
                "auto_backup": "نسخ احتياطي تلقائي",
                "backup_interval": "فترة النسخ الاحتياطي (أيام)",
                "backup_location": "موقع النسخ الاحتياطي",
                "backup_now": "نسخ احتياطي الآن",
                "restore_backup": "استعادة من نسخة احتياطية",
                "notifications": "الإشعارات",
                "appointment_reminder": "تذكير بالمواعيد",
                "reminder_hours": "ساعات التذكير قبل الموعد",
                "users": "المستخدمين",
                "add_user": "إضافة مستخدم",
                "edit_user": "تعديل مستخدم",
                "delete_user": "حذف مستخدم",
                "username": "اسم المستخدم",
                "password": "كلمة المرور",
                "is_admin": "مدير",
                "save": "حفظ",
                "cancel": "إلغاء",
                "about": "حول البرنامج",
                "version": "الإصدار",
                "developer": "المطور"
            },
            "common": {
                "save": "حفظ",
                "cancel": "إلغاء",
                "delete": "حذف",
                "edit": "تعديل",
                "add": "إضافة",
                "search": "بحث",
                "confirm": "تأكيد",
                "yes": "نعم",
                "no": "لا",
                "error": "خطأ",
                "success": "نجاح",
                "warning": "تحذير",
                "info": "معلومات",
                "confirm_delete": "هل أنت متأكد من الحذف؟",
                "operation_success": "تمت العملية بنجاح",
                "operation_failed": "فشلت العملية",
                "required_field": "هذا الحقل مطلوب",
                "invalid_input": "إدخال غير صالح"
            }
        }
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)
    
    def create_default_english_translations(self, file_path):
        translations = {
            "app_title": "Guzel Beauty Clinic",
            "login": {
                "title": "Login",
                "username": "Username",
                "password": "Password",
                "remember_me": "Remember me",
                "login_button": "Login",
                "error": "Invalid username or password"
            },
            "main": {
                "search": "Search",
                "languages": "Languages",
                "themes": "Themes",
                "notifications": "Notifications",
                "settings": "Settings",
                "logout": "Logout"
            },
            "sidebar": {
                "appointments": "Appointments",
                "customers": "Customers",
                "services": "Services & Prices",
                "invoices": "Invoices"
            },
            "calendar": {
                "upcoming_appointments": "Upcoming Appointments",
                "today": "Today",
                "no_appointments": "No appointments"
            },
            "appointments": {
                "title": "Appointments",
                "id": "ID",
                "customer_name": "Customer Name",
                "phone": "Phone",
                "email": "Email",
                "date_time": "Date & Time",
                "services": "Services",
                "service_provider": "Service Provider",
                "notes": "Notes",
                "status": "Status",
                "remaining_payments": "Remaining Payments",
                "add": "Add Appointment",
                "edit": "Edit",
                "delete": "Delete",
                "confirmed": "Confirmed",
                "unconfirmed": "Unconfirmed",
                "select_customer": "Select Customer",
                "select_service": "Select Service",
                "select_provider": "Select Provider",
                "appointment_details": "Appointment Details"
            },
            "customers": {
                "title": "Customers",
                "id": "ID",
                "name": "Name",
                "phone": "Phone",
                "email": "Email",
                "hair_type": "Hair Type",
                "hair_color": "Hair Color",
                "skin_type": "Skin Type",
                "allergies": "Allergies",
                "current_sessions": "Current Sessions",
                "remaining_sessions": "Remaining Sessions",
                "most_requested_services": "Most Requested Services",
                "remaining_payments": "Remaining Payments",
                "notes": "Notes",
                "add": "Add Customer",
                "edit": "Edit",
                "delete": "Delete",
                "customer_details": "Customer Details"
            },
            "services": {
                "title": "Services & Prices",
                "id": "ID",
                "name": "Service Name",
                "price": "Price",
                "add": "Add Service",
                "edit": "Edit",
                "delete": "Delete",
                "service_details": "Service Details",
                "price_currency": "SYP"
            },
            "invoices": {
                "title": "Invoices",
                "id": "ID",
                "customer_name": "Customer Name",
                "phone": "Phone",
                "date": "Date",
                "services": "Services",
                "payment_method": "Payment Method",
                "amount_paid": "Amount Paid",
                "amount_remaining": "Amount Remaining",
                "invoice_creator": "Invoice Creator",
                "service_provider": "Service Provider",
                "total_amount": "Total Amount",
                "add": "Create Invoice",
                "edit": "Edit",
                "delete": "Delete",
                "cash": "Cash",
                "installment": "Installment",
                "select_customer": "Select Customer",
                "select_appointment": "Select Appointment",
                "select_service": "Select Service",
                "invoice_details": "Invoice Details",
                "print": "Print",
                "price_currency": "SYP"
            },
            "settings": {
                "title": "Settings",
                "general": "General",
                "clinic_info": "Clinic Information",
                "clinic_name": "Clinic Name",
                "clinic_phone": "Phone",
                "clinic_address": "Address",
                "clinic_email": "Email",
                "social_media": "Social Media",
                "backup": "Backup",
                "auto_backup": "Auto Backup",
                "backup_interval": "Backup Interval (days)",
                "backup_location": "Backup Location",
                "backup_now": "Backup Now",
                "restore_backup": "Restore Backup",
                "notifications": "Notifications",
                "appointment_reminder": "Appointment Reminder",
                "reminder_hours": "Reminder Hours Before",
                "users": "Users",
                "add_user": "Add User",
                "edit_user": "Edit User",
                "delete_user": "Delete User",
                "username": "Username",
                "password": "Password",
                "is_admin": "Admin",
                "save": "Save",
                "cancel": "Cancel",
                "about": "About",
                "version": "Version",
                "developer": "Developer"
            },
            "common": {
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "add": "Add",
                "search": "Search",
                "confirm": "Confirm",
                "yes": "Yes",
                "no": "No",
                "error": "Error",
                "success": "Success",
                "warning": "Warning",
                "info": "Info",
                "confirm_delete": "Are you sure you want to delete?",
                "operation_success": "Operation completed successfully",
                "operation_failed": "Operation failed",
                "required_field": "This field is required",
                "invalid_input": "Invalid input"
            }
        }
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)
    
    def get_current_language(self):
        return self.settings.get_setting("language", "ar")
    
    def set_language(self, language_code, force_refresh=False):
        if language_code in self.translations:
            self.settings.set_setting("language", language_code)
            self.apply_language()
            self.language_changed.emit()  # Notify listeners of language change
            if force_refresh:
                from PyQt6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    app.processEvents()  # Force immediate UI update
    
    def apply_language(self):
        import locale
        
        language = self.get_current_language()
        
        # Set the application locale
        if language == "ar":
            locale.setlocale(locale.LC_ALL, 'ar_SY.UTF-8')
        else:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    
    def get_translation(self, key, default=None, return_icon=False):
        """Get translation for the given key in the current language.
        
        Args:
            key: Translation key (e.g. 'common.save')
            default: Default value if key not found
            return_icon: If True, returns icon path instead of text
        """
        language = self.get_current_language()
        translations = self.translations.get(language, {})
        
        keys = key.split('.')
        value = translations
        
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default if default is not None else key

        # Handle new icon format
        if isinstance(value, dict) and 'text' in value:
            return value['icon'] if return_icon else value['text']
        
        return value
