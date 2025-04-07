# build_exe.py
import os
import sys
import shutil
import subprocess

def build_executable():
    """Build the executable using PyInstaller."""
    try:
        # Check if PyInstaller is installed
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # Create spec file
        spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('icons', 'icons'),
        ('backups', 'backups')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GuzelBeautyClinic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/settings.png',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GuzelBeautyClinic',
)
        """
        
        with open("guzel_clinic.spec", "w") as f:
            f.write(spec_content)
        
        # Run PyInstaller
        subprocess.run(["pyinstaller", "guzel_clinic.spec", "--clean"], check=True)
        
        print("Executable built successfully!")
        print(f"You can find it in the {os.path.join(os.getcwd(), 'dist', 'GuzelBeautyClinic')} directory.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    build_executable()

