"""
Fiche élève avec historique des paiements.

Ce module définit la QDialog affichant la fiche complète d'un élève
et son historique de paiements.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QWidget, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication

from edupaie.ui.styles import (
    COULEUR_SOLDE, COULEUR_NON_PAYE, COULEUR_PARTIEL,
    COULEUR_TEXTE
)
from edupaie.utils.format import formater_montant
from edupaie.ui.recu_export import proposer_export_recu


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

        # Adapter la taille à l'écran disponible
        screen = QGuiApplication.primaryScreen()
        available_geo = screen.availableGeometry()
        initial_width = min(700, available_geo.width() - 50)
        initial_height = min(500, available_geo.height() - 50)
        self.resize(initial_width, initial_height)
        self.setMinimumSize(min(600, available_geo.width() - 100), min(400, available_geo.height() - 100))

        self._fiche_chargee = self._load_data()
        if not self._fiche_chargee:
            self.reject()
            return
        self._setup_ui()

    def exec(self):
        """N'ouvre pas le dialogue si la fiche n'a pas pu être chargée."""
        if not self._fiche_chargee:
            return int(QDialog.DialogCode.Rejected)
        return super().exec()

    def _load_data(self):
        """Charge les données de l'élève."""
        try:
            self.fiche = self.services['eleve'].fiche(self.eleve_id)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement de la fiche : {str(e)}")
            return False

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

        # Largeur minimale pour afficher "Partiellement payé" en entier
        from PySide6.QtGui import QFontMetrics
        font = badge.font()
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.horizontalAdvance("Partiellement payé")
        badge.setMinimumWidth(text_width + 24)  # +24 pour le padding CSS (4px 12px)

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
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Date", "Heure", "Montant", "Mode", "Numéro de reçu", "Payeur", "État"
        ])

        # Configuration des colonnes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for column in range(table.columnCount() - 1):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.itemSelectionChanged.connect(self._on_historique_selection_changed)

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
        self._paiements_par_id = {paiement.id: paiement for paiement in paiements}
        devise = self.services['parametre'].lire_parametre("devise")
        if not devise:
            devise = "FCFA"

        table.setRowCount(len(paiements))

        for row, paiement in enumerate(paiements):
            valeurs = [
                paiement.date_paiement,
                paiement.heure_paiement[:5],
                formater_montant(paiement.montant, devise),
                self._get_mode_libelle(paiement.mode),
                paiement.numero_recu,
                paiement.nom_payeur or "—",
                "Annulé" if paiement.est_annule else "Valide",
            ]
            for column, valeur in enumerate(valeurs):
                item = QTableWidgetItem(valeur)
                if column == 4:
                    item.setData(Qt.ItemDataRole.UserRole, paiement.id)
                if column == 6 and paiement.est_annule:
                    item.setForeground(Qt.GlobalColor.darkRed)
                table.setItem(row, column, item)

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
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addStretch()

        # Bouton Nouveau paiement
        self.btn_nouveau_paiement = QPushButton("Nouveau paiement")
        session = self.services.get("session")
        self.btn_nouveau_paiement.setEnabled(
            session is None or session.autorise("payments.register")
        )
        self.btn_nouveau_paiement.clicked.connect(self._on_nouveau_paiement)
        layout.addWidget(self.btn_nouveau_paiement)

        self.btn_annuler_paiement = QPushButton("Annuler le paiement")
        self.btn_annuler_paiement.setProperty("secondary", True)
        self.btn_annuler_paiement.setEnabled(False)
        self.btn_annuler_paiement.setVisible(
            bool(session and session.autorise("payments.cancel"))
        )
        self.btn_annuler_paiement.clicked.connect(self._on_annuler_paiement)
        layout.addWidget(self.btn_annuler_paiement)

        # Exporter le reçu du paiement sélectionné
        self.btn_voir_recu = QPushButton("Exporter le reçu PDF")
        self.btn_voir_recu.setEnabled(False)
        self.btn_voir_recu.setToolTip("Sélectionnez un paiement dans l'historique")
        self.btn_voir_recu.clicked.connect(self._on_voir_recu)
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
            if not self._load_data():
                return
            self._refresh_ui()
            paiement = dialog.paiement_enregistre
            if paiement:
                for row in range(self.table.rowCount()):
                    recu_item = self.table.item(row, 3)
                    if recu_item.data(Qt.ItemDataRole.UserRole) == paiement.id:
                        self.table.selectRow(row)
                        break

    def _on_historique_selection_changed(self):
        """Active l'export lorsqu'un paiement est sélectionné."""
        row = self.table.currentRow()
        self.btn_voir_recu.setEnabled(row >= 0)
        if self.btn_annuler_paiement.isVisible():
            paiement = self._paiement_selectionne()
            self.btn_annuler_paiement.setEnabled(bool(paiement and not paiement.est_annule))

    def _paiement_selectionne(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        paiement_id = self.table.item(row, 4).data(Qt.ItemDataRole.UserRole)
        return self._paiements_par_id.get(paiement_id)

    def _on_annuler_paiement(self):
        paiement = self._paiement_selectionne()
        session = self.services.get("session")
        if paiement is None or paiement.est_annule or session is None:
            return
        motif, ok = QInputDialog.getMultiLineText(
            self,
            "Annuler le paiement",
            f"Motif obligatoire pour le reçu {paiement.numero_recu} :",
        )
        if not ok:
            return
        if not motif.strip():
            QMessageBox.warning(self, "Motif requis", "Saisis le motif de l'annulation.")
            return
        confirmation = QMessageBox.question(
            self,
            "Confirmer l'annulation",
            "Le paiement restera dans l'historique, marqué comme annulé. Continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return
        try:
            self.services["paiement"].annuler_paiement(paiement.id, session, motif)
            if self._load_data():
                self._refresh_ui()
        except Exception as erreur:
            QMessageBox.critical(self, "Annulation impossible", str(erreur))

    def _on_voir_recu(self):
        """Exporte le reçu du paiement sélectionné."""
        row = self.table.currentRow()
        if row < 0:
            return

        paiement_id = self.table.item(row, 4).data(Qt.ItemDataRole.UserRole)
        paiement = self._paiements_par_id.get(paiement_id)
        if paiement:
            proposer_export_recu(self, self.services, paiement, self.eleve_id)

    def _refresh_ui(self):
        """Rafraîchit l'interface après un paiement."""
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
