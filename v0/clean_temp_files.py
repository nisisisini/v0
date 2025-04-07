import os
import shutil

def delete_temp_files():
    # قائمة بأنماط الملفات المؤقتة
    temp_patterns = ["*.log", "*.tmp"]
    temp_folders = [".vscode", "__pycache__"]
    deleted_any = False  # متغير لتتبع ما إذا تم حذف أي شيء

    # البحث في جميع المجلدات الفرعية
    for root, dirs, files in os.walk(".", topdown=False):
        # حذف الملفات المؤقتة
        for file in files:
            if any(file.endswith(pattern) for pattern in temp_patterns):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                    deleted_any = True
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

        # حذف المجلدات المؤقتة
        for folder in dirs:
            if folder in temp_folders:
                folder_path = os.path.join(root, folder)
                try:
                    shutil.rmtree(folder_path)
                    print(f"Deleted folder: {folder_path}")
                    deleted_any = True
                except Exception as e:
                    print(f"Error deleting folder {folder_path}: {e}")

    if not deleted_any:
        print("No temporary files or folders found to delete.")

if __name__ == "__main__":
    delete_temp_files()
