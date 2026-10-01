"""
Test de vérification des appels de services dans l'UI.

Ce module parcourt le code de l'UI et vérifie que chaque appel
à une méthode de service correspond à une méthode existante.
"""

import ast
import os
import re
from edupaie.services.classe_service import ClasseService
from edupaie.services.eleve_service import EleveService
from edupaie.services.paiement_service import PaiementService
from edupaie.services.parametre_service import ParametreService
from edupaie.services.statistiques_service import StatistiquesService


def extract_service_calls_from_file(filepath):
    """
    Extrait les appels de services d'un fichier Python.

    Args:
        filepath: Chemin du fichier

    Returns:
        list: Liste de tuples (service_name, method_name)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    calls = []
    # Pattern: services['xxx'].yyy(...)
    pattern = r"services\['(\w+)'\]\.(\w+)\("
    matches = re.finditer(pattern, content)

    for match in matches:
        service_name = match.group(1)
        method_name = match.group(2)
        calls.append((service_name, method_name))

    return calls


def test_ui_service_calls_exist():
    """Vérifie que tous les appels de services dans l'UI sont valides."""
    ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui')

    # Mapping des noms de services vers les classes
    service_classes = {
        'classe': ClasseService,
        'eleve': EleveService,
        'paiement': PaiementService,
        'parametre': ParametreService,
        'statistiques': StatistiquesService
    }

    all_calls = []

    # Parcourir tous les fichiers Python de l'UI
    for filename in os.listdir(ui_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(ui_dir, filename)
            calls = extract_service_calls_from_file(filepath)
            all_calls.extend([(filename, service, method) for service, method in calls])

    # Vérifier chaque appel
    errors = []
    for filename, service_name, method_name in all_calls:
        if service_name not in service_classes:
            errors.append(f"{filename}: Service '{service_name}' inconnu")
            continue

        service_class = service_classes[service_name]

        # Vérifier que la méthode existe
        if not hasattr(service_class, method_name):
            errors.append(
                f"{filename}: Service '{service_name}' n'a pas de méthode '{method_name}'"
            )

    if errors:
        error_msg = "\n".join(errors)
        assert False, f"Appels de services invalides détectés :\n{error_msg}"
