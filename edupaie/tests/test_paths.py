"""
Tests des chemins de l'application.

Ce module vérifie que les chemins retournés par utils/paths.py
sont corrects en mode développement.
"""

import os
from edupaie.utils.paths import get_app_directory, get_database_path


def test_get_app_directory_dev_mode():
    """Vérifie qu'en mode développement, get_app_directory retourne la racine du projet."""
    # En mode développement, le dossier de l'application doit contenir main.py
    app_dir = get_app_directory()
    main_py_path = os.path.join(app_dir, 'main.py')

    assert os.path.exists(main_py_path), f"main.py doit exister dans {app_dir}"


def test_get_database_path_dev_mode():
    """Vérifie qu'en mode développement, la base est à la racine du projet."""
    db_path = get_database_path()
    app_dir = get_app_directory()

    # La base doit être dans le même dossier que main.py
    assert db_path.startswith(app_dir), "La base doit être dans le dossier de l'application"
    assert db_path.endswith('edupaie.db'), "Le fichier doit s'appeler edupaie.db"

    # Le parent de la base doit être le dossier de l'application
    db_parent = os.path.dirname(db_path)
    assert db_parent == app_dir, f"La base doit être directement dans {app_dir}"
