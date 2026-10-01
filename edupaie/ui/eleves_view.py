"""
Vue de gestion des élèves.

Ce module définit l'interface pour lister, filtrer et gérer les élèves.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
    QLabel, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt

from edupaie.ui.styles import (
    COULEUR_SOLDE, COULEUR_NON_PAYE, COULEUR_PARTIEL,
    COULEUR_TEXTE
)
from edupaie.utils.format import formater_montant


class ElevesView(QWidget):
    """Vue de gestion des élèves."""

    def __init__(self, services):
        """
        Initialise la vue des élèves.

        Args:
            services: Dictionnaire des services métier
        """
        super().__init__()
        self.services = services
        self.setStyleSheet("""
            QWidget {{
                background-color: #FFFFFF;
            }}
        """)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Barre d'outils (recherche, filtres, boutons)
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Tableau des élèves
        self.table = self._create_table()
        layout.addWidget(self.table)

    def _create_toolbar(self) -> QWidget:
        """
        Crée la barre d'outils.

        Returns:
            QWidget: Barre d'outils
        """
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(12)

        # Recherche
        search_label = QLabel("Recherche:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nom ou prénom...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self._on_search_changed)

        layout.addWidget(search_label)
        layout.addWidget(self.search_input)

        # Filtre par classe
        classe_label = QLabel("Classe:")
        self.classe_combo = QComboBox()
        self.classe_combo.setFixedWidth(150)
        self.classe_combo.addItem("Toutes")
        self.classe_combo.currentIndexChanged.connect(self._on_filter_changed)

        layout.addWidget(classe_label)
        layout.addWidget(self.classe_combo)

        # Filtre par statut
        statut_label = QLabel("Statut:")
        self.statut_combo = QComboBox()
        self.statut_combo.setFixedWidth(150)
        self.statut_combo.addItem("Tous")
        self.statut_combo.addItem("Soldé")
        self.statut_combo.addItem("Partiellement payé")
        self.statut_combo.addItem("Non payé")
        self.statut_combo.currentIndexChanged.connect(self._on_filter_changed)

        layout.addWidget(statut_label)
        layout.addWidget(self.statut_combo)

        layout.addStretch()

        # Boutons d'action
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_ajouter.clicked.connect(self._on_ajouter)

        self.btn_modifier = QPushButton("Modifier")
        self.btn_modifier.clicked.connect(self._on_modifier)
        self.btn_modifier.setEnabled(False)

        self.btn_supprimer = QPushButton("Supprimer")
        self.btn_supprimer.clicked.connect(self._on_supprimer)
        self.btn_supprimer.setEnabled(False)

        layout.addWidget(self.btn_ajouter)
        layout.addWidget(self.btn_modifier)
        layout.addWidget(self.btn_supprimer)

        return toolbar

    def _create_table(self) -> QTableWidget:
        """
        Crée le tableau des élèves.

        Returns:
            QTableWidget: Tableau des élèves
        """
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Nom", "Prénom", "Classe", "Année",
            "Total dû", "Total payé", "Solde", "Statut"
        ])

        # Configuration des colonnes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.itemSelectionChanged.connect(self._on_selection_changed)

        return table

    def _load_data(self):
        """Charge les données des élèves dans le tableau."""
        try:
            # Charger les classes pour le filtre
            classes = self.services['classe'].lister_classes()
            self.classe_combo.clear()
            self.classe_combo.addItem("Toutes")
            for classe in classes:
                self.classe_combo.addItem(classe.nom, classe.id)

            # Charger les élèves
            self._refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {str(e)}")

    def _refresh_table(self):
        """Rafraîchit le tableau avec les filtres actuels."""
        try:
            recherche = self.search_input.text() if self.search_input.text() else None
            classe_id = self.classe_combo.currentData()
            statut = self.statut_combo.currentText()
            if statut == "Tous":
                statut = None

            eleves = self.services['eleve'].lister_eleves(
                classe_id=classe_id,
                recherche=recherche,
                statut=statut
            )

            # Obtenir la devise
            devise = self.services['parametre'].lire_parametre("devise")
            if not devise:
                devise = "FCFA"

            self._populate_table(eleves, devise)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du rafraîchissement : {str(e)}")

    def _populate_table(self, eleves, devise: str):
        """
        Remplit le tableau avec les données des élèves.

        Args:
            eleves: Liste des élèves avec totaux
            devise: Devise pour le formatage
        """
        self.table.setRowCount(len(eleves))

        for row, eleve_avec_totaux in enumerate(eleves):
            eleve = eleve_avec_totaux.eleve

            # Nom (stocke l'ID de l'élève)
            nom_item = QTableWidgetItem(eleve.nom)
            nom_item.setData(Qt.ItemDataRole.UserRole, eleve.id)
            self.table.setItem(row, 0, nom_item)

            # Prénom
            self.table.setItem(row, 1, QTableWidgetItem(eleve.prenom))

            # Classe
            self.table.setItem(row, 2, QTableWidgetItem(eleve_avec_totaux.nom_classe))

            # Année
            self.table.setItem(row, 3, QTableWidgetItem(eleve.annee_scolaire))

            # Total dû
            total_du = formater_montant(eleve.total_du, devise)
            self.table.setItem(row, 4, QTableWidgetItem(total_du))

            # Total payé
            total_paye = formater_montant(eleve_avec_totaux.total_paye, devise)
            self.table.setItem(row, 5, QTableWidgetItem(total_paye))

            # Solde
            solde = eleve.total_du - eleve_avec_totaux.total_paye
            solde_formatted = formater_montant(solde, devise)
            self.table.setItem(row, 6, QTableWidgetItem(solde_formatted))

            # Statut (pastille + texte)
            statut_widget = self._create_statut_badge(eleve.total_du, eleve_avec_totaux.total_paye)
            self.table.setCellWidget(row, 7, statut_widget)

    def _create_statut_badge(self, total_du: int, total_paye: int) -> QLabel:
        """
        Crée une pastille de statut.

        Args:
            total_du: Total dû
            total_paye: Total payé

        Returns:
            QLabel: Pastille de statut
        """
        from edupaie.services.calculs import determiner_statut

        statut = determiner_statut(total_du, total_paye)

        badge = QLabel(statut.value)
        badge.setObjectName("status_badge")

        if statut.value == "Soldé":
            badge.setProperty("solde", True)
        elif statut.value == "Non payé":
            badge.setProperty("non_paye", True)
        else:  # Partiellement payé
            badge.setProperty("partiel", True)

        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return badge

    def _on_search_changed(self):
        """Gère le changement de recherche."""
        self._refresh_table()

    def _on_filter_changed(self):
        """Gère le changement de filtre."""
        self._refresh_table()

    def _on_selection_changed(self):
        """Gère le changement de sélection dans le tableau."""
        has_selection = self.table.currentRow() >= 0
        self.btn_modifier.setEnabled(has_selection)
        self.btn_supprimer.setEnabled(has_selection)

    def _on_ajouter(self):
        """Gère le clic sur le bouton Ajouter."""
        from edupaie.ui.eleve_form import EleveForm
        from edupaie.services.calculs import determiner_statut

        try:
            # Obtenir l'année scolaire courante
            annee_courante = self.services['parametre'].lire_parametre("annee_scolaire_courante")
            if not annee_courante:
                annee_courante = "2025-2026"

            form = EleveForm(self.services, annee_courante)
            if form.exec():
                self._refresh_table()
                QMessageBox.information(self, "Succès", "Élève ajouté avec succès")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout : {str(e)}")

    def _on_modifier(self):
        """Gère le clic sur le bouton Modifier."""
        from edupaie.ui.eleve_form import EleveForm

        row = self.table.currentRow()
        if row < 0:
            return

        try:
            # Récupérer l'ID de l'élève (stocké dans la première colonne)
            eleve_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

            eleve = self.services['eleve'].trouver_eleve(eleve_id)
            if not eleve:
                QMessageBox.warning(self, "Attention", "Élève introuvable")
                return

            form = EleveForm(self.services, None, eleve)
            if form.exec():
                self._refresh_table()
                QMessageBox.information(self, "Succès", "Élève modifié avec succès")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification : {str(e)}")

    def _on_supprimer(self):
        """Gère le clic sur le bouton Supprimer."""
        row = self.table.currentRow()
        if row < 0:
            return

        try:
            # Récupérer l'ID de l'élève
            eleve_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

            eleve = self.services['eleve'].trouver_eleve(eleve_id)
            if not eleve:
                QMessageBox.warning(self, "Attention", "Élève introuvable")
                return

            # Compter les paiements via le service
            paiements = self.services['paiement'].lister_paiements_eleve(eleve_id)
            nb_paiements = len(paiements)

            # Confirmation
            message = f"Supprimer l'élève {eleve.nom} {eleve.prenom} ?"
            if nb_paiements > 0:
                message += f"\n\n{nb_paiements} paiement(s) seront également supprimés."

            reply = QMessageBox.question(
                self,
                "Confirmation",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.services['eleve'].supprimer_eleve(eleve_id)
                self._refresh_table()
                QMessageBox.information(self, "Succès", "Élève supprimé avec succès")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {str(e)}")
