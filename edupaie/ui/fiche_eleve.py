"""
Fiche élève avec historique des paiements.

Ce module définit la QDialog affichant la fiche complète d'un élève.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)
from PySide6.QtCore import Qt

from edupaie.ui.styles import (
    COULEUR_SOLDE, COULEUR_NON_PAYE, COULEUR_PARTIEL
)
from edupaie.utils.format import formater_montant


class FicheEleveDialog(QDialog):
    """Dialogue de fiche élève."""

    def __init__(self, services, eleve_id: int, parent_view=None):
        """
        Initialise la fiche élève.

        Args:
            services: Dictionnaire des services métier
            eleve_id: ID de l'élève
            parent_view: Vue parente (optionnel, pour rafraîchissement)
        """
        super().__init__()
        self.services = services
        self.eleve_id = eleve_id
        self.parent_view = parent_view

        self.setWindowTitle("Fiche élève")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self._load_fiche()
        self._setup_ui()

    def _load_fiche(self):
        """Charge les données de la fiche."""
        try:
            self.fiche = self.services['eleve'].fiche(self.eleve_id)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {str(e)}")
            self.reject()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Identité
        identite = self._create_identite()
        layout.addWidget(identite)

        # Informations financières
        financements = self._create_financements()
        layout.addWidget(financements)

        # Historique des paiements
        historique = self._create_historique()
        layout.addWidget(historique)

        # Boutons d'action
        actions = self._create_actions()
        layout.addWidget(actions)

    def _create_identite(self) -> QWidget:
        """
        Crée le widget d'identité.

        Returns:
            QWidget: Widget d'identité
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        widget.setStyleSheet("background-color: #F5F6F8; border-radius: 8px; padding: 16px;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)

        eleve = self.fiche["eleve"]

        nom_label = QLabel(f"{eleve.nom} {eleve.prenom}")
        nom_label.setStyleSheet("font-weight: 600; font-size: 18px;")
        layout.addWidget(nom_label)

        classe_label = QLabel(f"Classe : {self.fiche['nom_classe']}")
        layout.addWidget(classe_label)

        annee_label = QLabel(f"Année scolaire : {eleve.annee_scolaire}")
        layout.addWidget(annee_label)

        return widget

    def _create_financements(self) -> QWidget:
        """
        Crée le widget des informations financières.

        Returns:
            QWidget: Widget financier
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(24)

        devise = self.services['parametre'].lire_parametre("devise") or "FCFA"

        # Total dû
        total_du_layout = QVBoxLayout()
        total_du_label = QLabel("Total dû")
        total_du_value = QLabel(formater_montant(self.fiche["total_du"], devise))
        total_du_value.setStyleSheet("font-weight: 600; font-size: 16px;")
        total_du_layout.addWidget(total_du_label)
        total_du_layout.addWidget(total_du_value)
        layout.addLayout(total_du_layout)

        # Total payé
        total_paye_layout = QVBoxLayout()
        total_paye_label = QLabel("Total payé")
        total_paye_value = QLabel(formater_montant(self.fiche["total_paye"], devise))
        total_paye_value.setStyleSheet("font-weight: 600; font-size: 16px;")
        total_paye_layout.addWidget(total_paye_label)
        total_paye_layout.addWidget(total_paye_value)
        layout.addLayout(total_paye_layout)

        # Solde
        solde_layout = QVBoxLayout()
        solde_label = QLabel("Solde")
        solde_value = QLabel(formater_montant(self.fiche["solde"], devise))
        solde_value.setStyleSheet("font-weight: 600; font-size: 16px;")
        solde_layout.addWidget(solde_label)
        solde_layout.addWidget(solde_value)
        layout.addLayout(solde_layout)

        # Statut (pastille + texte)
        statut_layout = QVBoxLayout()
        statut_label = QLabel("Statut")
        statut_widget = self._create_statut_badge()
        statut_layout.addWidget(statut_label)
        statut_layout.addWidget(statut_widget)
        layout.addLayout(statut_layout)

        layout.addStretch()

        # Trop-perçu si applicable
        if self.fiche["trop_percu"] > 0:
            trop_percu_label = QLabel(f"Trop-perçu : {formater_montant(self.fiche['trop_percu'], devise)}")
            trop_percu_label.setStyleSheet("color: #2E7D32; font-weight: 600;")
            layout.addWidget(trop_percu_label)

        return widget

    def _create_statut_badge(self) -> QLabel:
        """
        Crée une pastille de statut.

        Returns:
            QLabel: Pastille de statut
        """
        badge = QLabel(self.fiche["statut"])
        badge.setObjectName("status_badge")

        if self.fiche["statut"] == "Soldé":
            badge.setProperty("solde", True)
        elif self.fiche["statut"] == "Non payé":
            badge.setProperty("non_paye", True)
        else:  # Partiellement payé
            badge.setProperty("partiel", True)

        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return badge

    def _create_historique(self) -> QWidget:
        """
        Crée le tableau d'historique des paiements.

        Returns:
            QWidget: Tableau d'historique
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        titre = QLabel("Historique des paiements")
        titre.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(titre)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Date", "Montant", "Mode", "N° reçu", "Solde après"
        ])

        # Configuration des colonnes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        devise = self.services['parametre'].lire_parametre("devise") or "FCFA"

        table.setRowCount(len(self.fiche["paiements"]))

        for row, paiement in enumerate(self.fiche["paiements"]):
            # Date
            table.setItem(row, 0, QTableWidgetItem(paiement.date_paiement))

            # Montant
            montant = formater_montant(paiement.montant, devise)
            table.setItem(row, 1, QTableWidgetItem(montant))

            # Mode
            mode_label = QTableWidgetItem(paiement.mode)
            table.setItem(row, 2, mode_label)

            # Numéro de reçu
            table.setItem(row, 3, QTableWidgetItem(paiement.numero_recu))

            # Solde après
            solde_apres = formater_montant(paiement.solde_apres, devise)
            table.setItem(row, 4, QTableWidgetItem(solde_apres))

        layout.addWidget(table)

        return widget

    def _create_actions(self) -> QWidget:
        """
        Crée les boutons d'action.

        Returns:
            QWidget: Boutons d'action
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(12)

        # Bouton Nouveau paiement
        self.btn_nouveau_paiement = QPushButton("Nouveau paiement")
        self.btn_nouveau_paiement.clicked.connect(self._on_nouveau_paiement)
        layout.addWidget(self.btn_nouveau_paiement)

        # Bouton Voir le reçu (désactivé pour l'étape 5)
        self.btn_voir_recu = QPushButton("Voir le reçu")
        self.btn_voir_recu.setEnabled(False)
        self.btn_voir_recu.setToolTip("Disponible à l'étape 6")
        layout.addWidget(self.btn_voir_recu)

        layout.addStretch()

        return widget

    def _on_nouveau_paiement(self):
        """Gère le clic sur le bouton Nouveau paiement."""
        from edupaie.ui.paiement_dialog import PaiementDialog

        try:
            dialog = PaiementDialog(self.services, self.fiche)
            if dialog.exec():
                # Paiement enregistré, recharger la fiche
                self._load_fiche()
                # Rafraîchir l'interface
                self._setup_ui()
                # Rafraîchir la vue parente si elle existe
                if self.parent_view:
                    self.parent_view._refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement : {str(e)}")
