"""Données d'un paiement enrichies pour les listes de reçus."""

from dataclasses import dataclass

from edupaie.models.paiement import Paiement


@dataclass
class PaiementListe:
    """Paiement accompagné des informations utiles au registre des reçus."""

    paiement: Paiement
    nom_eleve: str
    prenom_eleve: str
    nom_classe: str