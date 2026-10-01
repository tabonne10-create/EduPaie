"""
Fiche élève avec historique des paiements.

Ce module définit la QDialog affichant la fiche complète d'un élève
et son historique de paiements.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

from edupaie.ui.styles import (
    COULEUR_SOLDE, COULEUR_NON_PAYE, COULEUR_PARTIEL,
    COULEUR_TEXTE
)
from edupaie.utils.format import formater_montant


class FicheEleveDialog(QDialog):
    """Dialogue de fiche élève."""

    def __init__(self, services, eleve_id, parent=None):
        """
        Initialise la fiche élève.

        Args:
            services: Dictionnaire des services métier
            eleve_id: ID de l'élève
            parent: Widget parent
        """
        super().__init__(parent)
        self.services = services
        self.eleve_id = eleve_id
        self.setWindowTitle("Fiche élève")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self._load_data()
        self._setup_ui()

    def _load_data(self):
        """Charge les données de l'élève."""
        try:
            self.fiche = self.services['eleve'].fiche(self.eleve_id)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement de la fiche : {str(e)}")
            self.reject()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Section identité
        identite_layout = self._create_identite_section()
        layout.addWidget(identite_layout)

        # Section montants
        montants_layout = self._create_montants_section()
        layout.addWidget(montants_layout)

        # Section historique
        historique_label = QLabel("Historique des paiements")
        historique_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #8B0000;")
        layout.addWidget(historique_label)

        self.table = self._create_historique_table()
        layout.addWidget(self.table)

        # Boutons d'action
        buttons_layout = self._create_buttons()
        layout.addWidget(buttons_layout)

    def _create_identite_section(self) -> QWidget:
        """
        Crée la section d'identité de l'élève.

        Returns:
            QWidget: Section identité
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)

        # Nom et prénom
        nom_label = QLabel(f"{self.fiche['eleve'].nom} {self.fiche['eleve'].prenom}")
        nom_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #8B0000;")
        layout.addWidget(nom_label)

        # Classe et année
        info_label = QLabel(f"{self.fiche['nom_classe']} - {self.fiche['eleve'].annee_scolaire}")
        info_label.setStyleSheet("color: #666666;")
        layout.addWidget(info_label)

        return widget

    def _create_montants_section(self) -> QWidget:
        """
        Crée la section des montants.

        Returns:
            QWidget: Section montants
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        widget.setObjectName("secondary_area")
        layout = QHBoxLayout(widget)
        layout.setSpacing(24)

        devise = self.services['parametre'].lire_parametre("devise")
        if not devise:
            devise = "FCFA"

        # Total dû
        total_du_label = QLabel(f"Total dû : {formater_montant(self.fiche['total_du'], devise)}")
        total_du_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(total_du_label)

        # Total payé
        total_paye_label = QLabel(f"Total payé : {formater_montant(self.fiche['total_paye'], devise)}")
        total_paye_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(total_paye_label)

        # Solde
        solde_label = QLabel(f"Solde : {formater_montant(self.fiche['solde'], devise)}")
        solde_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(solde_label)

        # Statut (pastille + texte)
        statut_widget = self._create_statut_badge()
        layout.addWidget(statut_widget)

        # Trop-perçu si applicable
        if self.fiche['trop_percu'] > 0:
            trop_percu_label = QLabel(f"(Trop-perçu : {formater_montant(self.fiche['trop_percu'], devise)})")
            trop_percu_label.setStyleSheet("color: #F57C00; font-style: italic;")
            layout.addWidget(trop_percu_label)

        layout.addStretch()

        return widget

    def _create_statut_badge(self) -> QLabel:
        """
        Crée une pastille de statut.

        Returns:
            QLabel: Pastille de statut
        """
        badge = QLabel(self.fiche['statut'])
        badge.setObjectName("status_badge")

        if self.fiche['statut'] == "Soldé":
            badge.setProperty("solde", True)
        elif self.fiche['statut'] == "Non payé":
            badge.setProperty("non_paye", True)
        else:  # Partiellement payé
            badge.setProperty("partiel", True)

        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return badge

    def _create_historique_table(self) -> QTableWidget:
        """
        Crée le tableau d'historique des paiements.

        Returns:
            QTableWidget: Tableau d'historique
        """
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Date", "Montant", "Mode", "Numéro de reçu", "Solde après"
        ])

        # Configuration des colonnes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Remplir avec les paiements
        self._populate_historique_table(table)

        return table

    def _populate_historique_table(self, table):
        """
        Remplit le tableau avec l'historique des paiements.

        Args:
            table: TableWidget à remplir
        """
        paiements = self.fiche['paiements']
        devise = self.services['parametre'].lire_parametre("devise")
        if not devise:
            devise = "FCFA"

        table.setRowCount(len(paiements))

        for row, paiement in enumerate(paiements):
            # Date
            date_item = QTableWidgetItem(paiement.date_paiement)
            table.setItem(row, 0, date_item)

            # Montant
            montant_item = QTableWidgetItem(formater_montant(paiement.montant, devise))
            table.setItem(row, 1, montant_item)

            # Mode (avec libellé accentué)
            mode_libelle = self._get_mode_libelle(paiement.mode)
            mode_item = QTableWidgetItem(mode_libelle)
            table.setItem(row, 2, mode_item)

            # Numéro de reçu
            recu_item = QTableWidgetItem(paiement.numero_recu)
            table.setItem(row, 3, recu_item)

            # Solde après
            solde_item = QTableWidgetItem(formater_montant(paiement.solde_apres, devise))
            table.setItem(row, 4, solde_item)

    def _get_mode_libelle(self, mode: str) -> str:
        """
        Retourne le libellé accentué du mode de paiement.

        Args:
            mode: Code du mode (especes, cheque, virement, mobile_money)

        Returns:
            Libellé accentué
        """
        libelles = {
            "especes": "Espèces",
            "cheque": "Chèque",
            "virement": "Virement",
            "mobile_money": "Mobile Money"
        }
        return libelles.get(mode, mode)

    def _create_buttons(self) -> QWidget:
        """
        Crée les boutons d'action.

        Returns:
            QWidget: Widget contenant les boutons
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addStretch()

        # Bouton Nouveau paiement
        self.btn_nouveau_paiement = QPushButton("Nouveau paiement")
        self.btn_nouveau_paiement.clicked.connect(self._on_nouveau_paiement)
        layout.addWidget(self.btn_nouveau_paiement)

        # Bouton Voir le reçu (désactivé pour l'étape 6)
        self.btn_voir_recu = QPushButton("Voir le reçu")
        self.btn_voir_recu.setEnabled(False)
        self.btn_voir_recu.setToolTip("Disponible à l'étape 6")
        layout.addWidget(self.btn_voir_recu)

        # Bouton Fermer
        btn_fermer = QPushButton("Fermer")
        btn_fermer.clicked.connect(self.accept)
        layout.addWidget(btn_fermer)

        return widget

    def _on_nouveau_paiement(self):
        """Gère le clic sur le bouton Nouveau paiement."""
        from edupaie.ui.paiement_dialog import PaiementDialog

        dialog = PaiementDialog(self.services, self.eleve_id, self)
        if dialog.exec():
            # Paiement enregistré, recharger les données
            self._load_data()
            self._refresh_ui()

    def _refresh_ui(self):
        """Rafraîchit l'interface après un paiement."""
        # Recréer l'interface
        from PySide6.QtWidgets import QWidget

        # Vider le layout actuel
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Recréer les sections
        identite_layout = self._create_identite_section()
        layout.addWidget(identite_layout)

        montants_layout = self._create_montants_section()
        layout.addWidget(montants_layout)

        historique_label = QLabel("Historique des paiements")
        historique_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #8B0000;")
        layout.addWidget(historique_label)

        self.table = self._create_historique_table()
        layout.addWidget(self.table)

        buttons_layout = self._create_buttons()
        layout.addWidget(buttons_layout)
