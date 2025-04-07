# config/settings.py
import json
import os

class Settings:
    """Manages application settings and preferences."""
    
    def __init__(self):
        self.settings_file = "data/settings.json"
        self._ensure_data_dir()
        self._load_settings()
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
    
    def _load_settings(self):
        """Load settings from the settings file or create default settings."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            # Default settings
            self.settings = {
                "theme": "light",
                "language": "ar",  # Default to Arabic
                "clinic_info": {
                    "name": "مركز جوزيل للتجميل",
                    "phone": "+963956961395",
                    "address": "سوريا - ريف دمشق التل موقف طيبة مقابل امركز الثقافي الجديد",
                    "email": "",
                    "social_media": {}
                },
                "backup": {
                    "auto_backup": True,
                    "backup_interval_days": 1,
                    "backup_location": "backups/"
                },
                "notifications": {
                    "appointment_reminder": True,
                    "reminder_hours_before": 24
                }
            }
            self._save_settings()
    
    def _save_settings(self):
        """Save settings to the settings file."""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)
    
    def get_setting(self, key, default=None):
        """Get a setting value by key."""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_setting(self, key, value):
        """Set a setting value by key."""
        keys = key.split('.')
        settings_dict = self.settings
        
        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in settings_dict:
                settings_dict[k] = {}
            settings_dict = settings_dict[k]
        
        # Set the value
        settings_dict[keys[-1]] = value
        self._save_settings()

