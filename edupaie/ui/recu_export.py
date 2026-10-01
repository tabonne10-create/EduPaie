"""Actions d'export et d'ouverture des reçus PDF."""

import re
from pathlib import Path

from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QMessageBox

from edupaie.receipts.pdf_generator import generer_recu_pdf


def proposer_export_recu(parent, services, paiement, eleve_id: int) -> bool:
    """Demande où enregistrer un reçu, le génère et l'ouvre."""
    numero_securise = re.sub(r"[^A-Za-z0-9_-]", "_", paiement.numero_recu)
    nom_fichier = f"Recu_{numero_securise}.pdf"
    dossier = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
    chemin_initial = str(Path(dossier) / nom_fichier) if dossier else nom_fichier

    chemin, _ = QFileDialog.getSaveFileName(
        parent,
        "Enregistrer le reçu PDF",
        chemin_initial,
        "Fichier PDF (*.pdf)",
    )
    if not chemin:
        return False

    destination = Path(chemin)
    if destination.suffix.lower() != ".pdf":
        destination = destination.with_suffix(".pdf")

    try:
        fiche = services["eleve"].fiche(eleve_id)
        parametres = services["parametre"].lire_tous_les_parametres()
        generer_recu_pdf(paiement, fiche, parametres, destination)
    except Exception as erreur:
        QMessageBox.critical(
            parent,
            "Erreur de reçu",
            f"Le paiement est enregistré, mais le reçu PDF n'a pas pu être créé :\n{erreur}",
        )
        return False

    if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(destination.resolve()))):
        QMessageBox.information(
            parent,
            "Reçu enregistré",
            f"Le reçu a été enregistré ici :\n{destination.resolve()}",
        )
    return True
