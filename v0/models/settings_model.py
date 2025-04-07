# models\settings_model.py
import json
import os
from config.settings import Settings

class SettingsModel:
    """Model for settings-related operations."""
    
    def __init__(self, settings=None):
        self.settings = settings or Settings()
    
    def get_all_settings(self):
        """Get all settings."""
        return self.settings.settings
    
    def get_setting(self, key, default=None):
        """Get a setting value by key."""
        return self.settings.get_setting(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value by key."""
        self.settings.set_setting(key, value)
        return True
    
    def get_clinic_info(self):
        """Get clinic information."""
        return {
            "name": self.settings.get_setting("clinic_info.name", "مركز جوزيل للتجميل"),
            "phone": self.settings.get_setting("clinic_info.phone", "+963956961395"),
            "address": self.settings.get_setting("clinic_info.address", "سوريا - ريف دمشق التل موقف طيبة مقابل امركز الثقافي الجديد"),
            "email": self.settings.get_setting("clinic_info.email", ""),
            "social_media": self.settings.get_setting("clinic_info.social_media", {})
        }
    
    def set_clinic_info(self, clinic_info):
        """Set clinic information."""
        self.settings.set_setting("clinic_info.name", clinic_info.get("name", "مركز جوزيل للتجميل"))
        self.settings.set_setting("clinic_info.phone", clinic_info.get("phone", "+963956961395"))
        self.settings.set_setting("clinic_info.address", clinic_info.get("address", "سوريا - ريف دمشق التل موقف طيبة مقابل امركز الثقافي الجديد"))
        self.settings.set_setting("clinic_info.email", clinic_info.get("email", ""))
        self.settings.set_setting("clinic_info.social_media", clinic_info.get("social_media", {}))
        return True
    
    def get_backup_settings(self):
        """Get backup settings."""
        return {
            "auto_backup": self.settings.get_setting("backup.auto_backup", True),
            "backup_interval_days": self.settings.get_setting("backup.backup_interval_days", 1),
            "backup_location": self.settings.get_setting("backup.backup_location", "backups/")
        }
    
    def set_backup_settings(self, backup_settings):
        """Set backup settings."""
        self.settings.set_setting("backup.auto_backup", backup_settings.get("auto_backup", True))
        self.settings.set_setting("backup.backup_interval_days", backup_settings.get("backup_interval_days", 1))
        self.settings.set_setting("backup.backup_location", backup_settings.get("backup_location", "backups/"))
        return True
    
    def get_notification_settings(self):
        """Get notification settings."""
        return {
            "appointment_reminder": self.settings.get_setting("notifications.appointment_reminder", True),
            "reminder_hours_before": self.settings.get_setting("notifications.reminder_hours_before", 24)
        }
    
    def set_notification_settings(self, notification_settings):
        """Set notification settings."""
        self.settings.set_setting("notifications.appointment_reminder", notification_settings.get("appointment_reminder", True))
        self.settings.set_setting("notifications.reminder_hours_before", notification_settings.get("reminder_hours_before", 24))
        return True

