import sys
import os

# Ajouter PyInstaller et ses dépendances au path
sys.path.insert(0, r'D:\EduPaie\pyinstaller-6.22.3')
sys.path.insert(0, r'D:\EduPaie\pefile')
sys.path.insert(0, r'D:\EduPaie\pyinstaller_lib')

# Importer et exécuter PyInstaller
from PyInstaller.__main__ import run

if __name__ == '__main__':
    # Arguments pour PyInstaller sans UPX
    sys.argv = [
        'build_with_noupx.py',
        '--onefile',
        '--windowed',
        '--noupx',  # Désactiver UPX pour éviter les erreurs de décompression
        '--icon=assets/edupaie_favicon.ico',
        '--add-data=assets;assets',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=reportlab',
        '--hidden-import=openpyxl',
        '--hidden-import=PIL',
        '--name=EduPaie',
        'main.py'
    ]
    run()
