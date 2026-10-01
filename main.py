"""
Point d'entrée de l'application EduPaie.

Ce module lance l'application desktop de gestion des paiements scolaires.
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from edupaie.database.connection import init_database
from edupaie.database.repositories.classe_repository import ClasseRepository
from edupaie.database.repositories.eleve_repository import EleveRepository
from edupaie.database.repositories.paiement_repository import PaiementRepository
from edupaie.database.repositories.parametre_repository import ParametreRepository
from edupaie.database.repositories.compteur_recus_repository import CompteurRecusRepository
from edupaie.database.repositories.statistiques_repository import StatistiquesRepository
from edupaie.services.classe_service import ClasseService
from edupaie.services.eleve_service import EleveService
from edupaie.services.paiement_service import PaiementService
from edupaie.services.parametre_service import ParametreService
from edupaie.services.statistiques_service import StatistiquesService
from edupaie.ui.main_window import MainWindow


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Gestionnaire global des exceptions non interceptées.

    Affiche une QMessageBox avec les détails de l'erreur.

    Args:
        exc_type: Type de l'exception
        exc_value: Valeur de l'exception
        exc_traceback: Traceback de l'exception
    """
    import traceback
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    QMessageBox.critical(None, "Erreur inattendue", f"Une erreur s'est produite :\n\n{error_msg}")


def main():
    """
    Fonction principale de l'application.

    Initialise la base de données, les services et l'interface Qt.
    """
    # Configurer le gestionnaire global d'exceptions
    sys.excepthook = handle_exception

    # Initialiser la base de données si elle n'existe pas
    try:
        init_database()
    except Exception as e:
        QMessageBox.critical(None, "Erreur", f"Erreur lors de l'initialisation de la base de données :\n{str(e)}")
        sys.exit(1)

    # Créer les services (une seule fois)
    services = {
        'classe': ClasseService(),
        'eleve': EleveService(),
        'paiement': PaiementService(),
        'parametre': ParametreService(),
        'statistiques': StatistiquesService()
    }

    # Initialiser l'application Qt
    app = QApplication(sys.argv)

    # Créer et afficher la fenêtre principale
    window = MainWindow(services)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
