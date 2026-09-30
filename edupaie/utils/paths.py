"""
Gestion des chemins de l'application.

Ce module fournit des fonctions pour obtenir les chemins de l'application
et de la base de données, en tenant compte du mode d'exécution
(normal ou packagé avec PyInstaller).
"""

import sys
import os


def get_app_directory():
    """
    Retourne le dossier de l'application.

    - En exécution normale : le dossier du projet (où se trouve main.py)
    - En exécution packagée PyInstaller (sys.frozen) : le dossier contenant l'exe

    Returns:
        str: Chemin absolu du dossier de l'application
    """
    if getattr(sys, 'frozen', False):
        # Application packagée avec PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Exécution normale (développement)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_database_path():
    """
    Retourne le chemin vers la base de données edupaie.db.

    La base se trouve à côté de l'exécutable (ou du dossier du projet en dev),
    jamais dans un dossier temporaire.

    Returns:
        str: Chemin absolu vers edupaie.db
    """
    app_dir = get_app_directory()
    return os.path.join(app_dir, 'edupaie.db')
