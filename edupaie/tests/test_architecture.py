"""
Tests d'architecture du projet.

Ce module vérifie les règles d'architecture, notamment que la couche UI
n'importe pas directement sqlite3 ni les repositories.
"""

import ast
import os


def test_ui_nimporte_pas_sqlite3():
    """Vérifie que le module ui n'importe pas sqlite3."""
    ui_dir = os.path.join(os.path.dirname(__file__), '..', 'ui')

    for filename in os.listdir(ui_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(ui_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parser le fichier
            tree = ast.parse(content)

            # Vérifier les imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert 'sqlite3' not in alias.name, f"{filename} importe sqlite3 directement"
                elif isinstance(node, ast.ImportFrom):
                    if node.module and 'sqlite3' in node.module:
                        assert False, f"{filename} importe depuis sqlite3"


def test_ui_nimporte_pas_repositories():
    """Vérifie que le module ui n'importe pas depuis database.repositories."""
    ui_dir = os.path.join(os.path.dirname(__file__), '..', 'ui')

    for filename in os.listdir(ui_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(ui_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parser le fichier
            tree = ast.parse(content)

            # Vérifier les imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and 'database.repositories' in node.module:
                        assert False, f"{filename} importe depuis database.repositories"
