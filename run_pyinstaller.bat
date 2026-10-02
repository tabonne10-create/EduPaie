@echo off
set PYTHONPATH=D:\EduPaie\pyinstaller_lib
set TEMP=D:\EduPaie\temp
set TMP=D:\EduPaie\temp
C:\Python314\python.exe -m PyInstaller --onefile --windowed --noupx --icon=assets/edupaie_favicon.ico --add-data="assets;assets" --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets --hidden-import=reportlab --hidden-import=openpyxl --hidden-import=PIL --name=EduPaie main.py
