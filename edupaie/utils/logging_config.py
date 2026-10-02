"""
Configuration du système de logging pour EduPaie.

Ce module configure un système de logging centralisé pour l'application.
"""

import logging
import os
from pathlib import Path


def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Configure le système de logging pour l'application.

    Args:
        log_level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Chemin du fichier de log (optionnel)
    """
    # Créer le dossier logs s'il n'existe pas
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configuration du logger racine
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),  # Console
        ]
    )

    # Ajouter un handler de fichier si spécifié
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logging.getLogger().addHandler(file_handler)

    # Configuration spécifique pour les bibliothèques externes
    logging.getLogger('PySide6').setLevel(logging.WARNING)
    logging.getLogger('reportlab').setLevel(logging.WARNING)


def get_logger(name):
    """
    Obtient un logger pour un module donné.

    Args:
        name: Nom du module (généralement __name__)

    Returns:
        Logger configuré
    """
    return logging.getLogger(name)


# Configuration par défaut au chargement du module
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_FILE = LOG_DIR / "edupaie.log"

# Ne configurer que si ce n'est pas déjà fait
if not logging.getLogger().handlers:
    setup_logging(log_file=str(LOG_FILE))
