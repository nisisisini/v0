import os
import shutil
import datetime
import sqlite3
import json
import zipfile
import glob

class BackupManager:
    """يدير عمليات النسخ الاحتياطي والاستعادة للقاعدة البيانات والإعدادات والترجمات"""
    
    def __init__(self, db_manager):
        """
        تهيئة مدير النسخ الاحتياطي
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        self.db_manager = db_manager
        self.backup_dir = "backups"
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """يتأكد من وجود مجلد النسخ الاحتياطي"""
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        """
        إنشاء نسخة احتياطية كاملة تشمل:
        - قاعدة البيانات
        - الإعدادات
        - ملفات الترجمة
        """
        # إنشاء طابع زمني لاسم الملف
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"guzel_clinic_backup_{timestamp}.zip"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # مجلد مؤقت للنسخ الاحتياطي
        temp_dir = os.path.join(self.backup_dir, "temp_backup")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # نسخ ملف قاعدة البيانات
            db_backup_path = os.path.join(temp_dir, "guzel_clinic.db")
            shutil.copy2(self.db_manager.db_path, db_backup_path)
            
            # نسخ ملف الإعدادات إذا كان موجوداً
            settings_path = "data/settings.json"
            if os.path.exists(settings_path):
                settings_backup_path = os.path.join(temp_dir, "settings.json")
                shutil.copy2(settings_path, settings_backup_path)
            
            # نسخ مجلد الترجمات إذا كان موجوداً
            translations_dir = "data/translations"
            if os.path.exists(translations_dir):
                translations_backup_dir = os.path.join(temp_dir, "translations")
                os.makedirs(translations_backup_dir, exist_ok=True)
                
                for file in os.listdir(translations_dir):
                    if file.endswith(".json"):
                        src_file = os.path.join(translations_dir, file)
                        dst_file = os.path.join(translations_backup_dir, file)
                        shutil.copy2(src_file, dst_file)
            
            # إنشاء ملف وصف للنسخة الاحتياطية
            metadata = {
                "backup_date": datetime.datetime.now().isoformat(),
                "version": "1.0.0",
                "description": "Guzel Beauty Clinic Backup"
            }
            
            with open(os.path.join(temp_dir, "backup_metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)
            
            # ضغط جميع الملفات في ملف zip واحد
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # تنظيف المجلد المؤقت
            shutil.rmtree(temp_dir)
            
            return backup_path
        
        except Exception as e:
            # تنظيف المجلد المؤقت في حالة الخطأ
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            # حذف ملف النسخة الاحتياطية غير المكتملة إذا كان موجوداً
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            raise e
    
    def create_simple_backup(self):
        """
        إنشاء نسخة احتياطية بسيطة لقاعدة البيانات فقط
        (وظيفة من backup_tool.py)
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"guzel_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        shutil.copy2(self.db_manager.db_path, backup_path)
        
        return backup_path
    
    def restore_backup(self, backup_path):
        """
        استعادة نسخة احتياطية
        
        Args:
            backup_path: مسار ملف النسخة الاحتياطية (.zip أو .db)
        """
        if backup_path.endswith('.zip'):
            return self._restore_full_backup(backup_path)
        elif backup_path.endswith('.db'):
            return self._restore_simple_backup(backup_path)
        else:
            raise ValueError("نوع ملف النسخة الاحتياطية غير معروف")
    
    def _restore_full_backup(self, backup_path):
        """استعادة نسخة احتياطية كاملة (ملف zip)"""
        temp_dir = os.path.join(self.backup_dir, "temp_restore")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # استخراج محتويات ملف zip
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # التحقق من ملف الوصف
            metadata_path = os.path.join(temp_dir, "backup_metadata.json")
            if not os.path.exists(metadata_path):
                raise Exception("ملف النسخة الاحتياطية غير صالح: لا يوجد ملف وصف")
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # إغلاق اتصال قاعدة البيانات قبل الاستعادة
            conn = self.db_manager.get_connection()
            conn.close()
            
            # استعادة قاعدة البيانات
            db_backup_path = os.path.join(temp_dir, "guzel_clinic.db")
            if not os.path.exists(db_backup_path):
                raise Exception("ملف النسخة الاحتياطية غير صالح: لا يوجد ملف قاعدة بيانات")
            
            shutil.copy2(db_backup_path, self.db_manager.db_path)
            
            # استعادة الإعدادات إذا كانت موجودة
            settings_backup_path = os.path.join(temp_dir, "settings.json")
            if os.path.exists(settings_backup_path):
                settings_path = "data/settings.json"
                os.makedirs(os.path.dirname(settings_path), exist_ok=True)
                shutil.copy2(settings_backup_path, settings_path)
            
            # استعادة الترجمات إذا كانت موجودة
            translations_backup_dir = os.path.join(temp_dir, "translations")
            if os.path.exists(translations_backup_dir):
                translations_dir = "data/translations"
                
                if os.path.exists(translations_dir):
                    shutil.rmtree(translations_dir)
                
                os.makedirs(translations_dir, exist_ok=True)
                
                for file in os.listdir(translations_backup_dir):
                    if file.endswith(".json"):
                        src_file = os.path.join(translations_backup_dir, file)
                        dst_file = os.path.join(translations_dir, file)
                        shutil.copy2(src_file, dst_file)
            
            # تنظيف المجلد المؤقت
            shutil.rmtree(temp_dir)
            
            return True
        
        except Exception as e:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise e
    
    def _restore_simple_backup(self, backup_path):
        """استعادة نسخة احتياطية بسيطة (ملف .db فقط)"""
        # إغلاق أي اتصالات مفتوحة
        if hasattr(self.db_manager, 'connection') and self.db_manager.connection:
            self.db_manager.connection.close()
        
        # استعادة النسخة الاحتياطية
        shutil.copy2(backup_path, self.db_manager.db_path)
        
        return True
    
    def get_available_backups(self):
        """الحصول على قائمة بالنسخ الاحتياطية المتاحة"""
        backups = []
        
        # البحث عن جميع ملفات النسخ الاحتياطية
        zip_backups = glob.glob(os.path.join(self.backup_dir, "guzel_clinic_backup_*.zip"))
        db_backups = glob.glob(os.path.join(self.backup_dir, "guzel_backup_*.db"))
        all_backups = zip_backups + db_backups
        
        for backup_path in all_backups:
            filename = os.path.basename(backup_path)
            
            try:
                # استخراج الطابع الزمني من اسم الملف
                if filename.startswith("guzel_clinic_backup_"):
                    timestamp_str = filename.replace("guzel_clinic_backup_", "").replace(".zip", "")
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                else:
                    timestamp_str = filename.replace("guzel_backup_", "").replace(".db", "")
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
                
                # الحصول على حجم الملف
                size = os.path.getsize(backup_path)
                
                backups.append({
                    "filename": filename,
                    "path": backup_path,
                    "timestamp": timestamp,
                    "size": size,
                    "type": "full" if filename.endswith(".zip") else "simple"
                })
            except:
                continue
        
        # ترتيب النسخ الاحتياطية حسب التاريخ (الأحدث أولاً)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return backups
    
    def delete_backup(self, backup_path):
        """حذف نسخة احتياطية"""
        if os.path.exists(backup_path):
            os.remove(backup_path)
            return True
        return False
    
    def auto_backup(self, interval_days=1, backup_type="full"):
        """
        إنشاء نسخة احتياطية تلقائية إذا مرت الفترة المحددة
        
        Args:
            interval_days: عدد الأيام بين النسخ الاحتياطية
            backup_type: نوع النسخة الاحتياطية ("full" أو "simple")
        """
        # التحقق من الحاجة لنسخة احتياطية
        last_backup = None
        backups = self.get_available_backups()
        
        if backups:
            last_backup = backups[0]["timestamp"]
        
        now = datetime.datetime.now()
        
        # إذا لم يكن هناك نسخ احتياطية سابقة أو انقضت الفترة
        if last_backup is None or (now - last_backup).days >= interval_days:
            if backup_type == "full":
                return self.create_backup()
            else:
                return self.create_simple_backup()
        
        return None
