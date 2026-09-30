"""
Point d'entrée de l'application EduPaie.

Ce module lance l'application desktop de gestion des paiements scolaires.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow


def main():
    """
    Fonction principale de l'application.

    Initialise l'application Qt et affiche la fenêtre principale.
    """
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("EduPaie")
    window.resize(800, 600)
    
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
