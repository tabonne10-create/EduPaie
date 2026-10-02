"""
Vue de gestion des élèves.

Ce module définit l'interface pour lister, filtrer et gérer les élèves.
"""

from datetime import date
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
    QLabel, QMessageBox, QHeaderView, QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics

from edupaie.ui.styles import (
    COULEUR_SOLDE, COULEUR_NON_PAYE, COULEUR_PARTIEL,
    COULEUR_TEXTE
)
from edupaie.utils.format import formater_montant
from edupaie.utils.export import exporter_eleves_csv, exporter_eleves_excel


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
        session = self.services.get("session")
        if (
            session and "enseignant" in session.roles
            and not session.autorise("payments.view")
        ):
            for column in range(5, 9):
                self.table.setColumnHidden(column, True)

    def _create_toolbar(self) -> QWidget:
        """
        Crée la barre d'outils.

        Returns:
            QWidget: Barre d'outils
        """
        toolbar = QWidget()
        toolbar.setObjectName("search_card")
        layout = QVBoxLayout(toolbar)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(12)

        # Recherche
        search_label = QLabel("Rechercher un élève (Nom, Prénom...)")
        search_label.setStyleSheet("font-weight: 500; color: #64748B; font-size: 13px;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Saisir nom ou prénom...")
        self.search_input.setMinimumWidth(200)
        self.search_input.textChanged.connect(self._on_search_changed)

        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.search_input, 1)

        # Filtre par classe
        classe_label = QLabel("Classe :")
        classe_label.setStyleSheet("font-weight: 500; color: #64748B; font-size: 13px;")
        self.classe_combo = QComboBox()
        self.classe_combo.setMinimumWidth(120)
        self.classe_combo.addItem("Toutes")
        self.classe_combo.currentIndexChanged.connect(self._on_filter_changed)

        filters_layout.addWidget(classe_label)
        filters_layout.addWidget(self.classe_combo)

        # Filtre par statut
        statut_label = QLabel("Statut :")
        statut_label.setStyleSheet("font-weight: 500; color: #64748B; font-size: 13px;")
        self.statut_combo = QComboBox()
        self.statut_combo.setMinimumWidth(120)
        self.statut_combo.addItem("Tous")
        self.statut_combo.addItem("Soldé")
        self.statut_combo.addItem("Partiellement payé")
        self.statut_combo.addItem("Non payé")
        self.statut_combo.currentIndexChanged.connect(self._on_filter_changed)

        filters_layout.addWidget(statut_label)
        filters_layout.addWidget(self.statut_combo)

        layout.addLayout(filters_layout)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        actions_layout.addStretch()

        # Boutons d'action
        self.btn_ajouter = QPushButton("+ Ajouter")
        self.btn_ajouter.setMinimumWidth(0)
        self.btn_ajouter.clicked.connect(self._on_ajouter)

        self.btn_modifier = QPushButton("Modifier")
        self.btn_modifier.setMinimumWidth(0)
        self.btn_modifier.clicked.connect(self._on_modifier)
        self.btn_modifier.setEnabled(False)
        self.btn_modifier.setProperty("secondary", True)

        self.btn_supprimer = QPushButton("Supprimer")
        self.btn_supprimer.setMinimumWidth(0)
        self.btn_supprimer.clicked.connect(self._on_supprimer)
        self.btn_supprimer.setEnabled(False)
        self.btn_supprimer.setProperty("danger", True)

        self.btn_fiche = QPushButton("Fiche / Paiements")
        self.btn_fiche.setMinimumWidth(0)
        self.btn_fiche.clicked.connect(self._on_fiche)
        self.btn_fiche.setEnabled(False)
        self.btn_fiche.setProperty("secondary", True)

        self.btn_exporter = QPushButton("Exporter")
        self.btn_exporter.setMinimumWidth(0)
        self.btn_exporter.clicked.connect(self._on_exporter)
        self.btn_exporter.setProperty("secondary", True)

        session = self.services.get("session")
        if session is not None:
            peut_gérer_eleves = session.autorise("students.manage")
            self.btn_ajouter.setVisible(peut_gérer_eleves)
            self.btn_modifier.setVisible(peut_gérer_eleves)
            self.btn_supprimer.setVisible(peut_gérer_eleves)
            self.btn_fiche.setVisible(session.autorise("payments.view"))
            self.statut_combo.setVisible(session.autorise("payments.view"))

        actions_layout.addWidget(self.btn_ajouter)
        actions_layout.addWidget(self.btn_modifier)
        actions_layout.addWidget(self.btn_supprimer)
        actions_layout.addWidget(self.btn_fiche)
        actions_layout.addWidget(self.btn_exporter)
        layout.addLayout(actions_layout)

        return toolbar

    def _create_table(self) -> QTableWidget:
        """
        Crée le tableau des élèves.

        Returns:
            QTableWidget: Tableau des élèves
        """
        table = QTableWidget()
        table.setColumnCount(9)  # +1 pour le numéro de ligne
        table.setHorizontalHeaderLabels([
            "#", "Nom", "Prénom", "Classe", "Année",
            "Total dû", "Total payé", "Solde", "Statut"
        ])
        table.setWordWrap(False)
        table.setTextElideMode(Qt.TextElideMode.ElideRight)
        table.setStyleSheet("QTableWidget::item { padding: 2px 0; }")

        # Configuration des colonnes
        header = table.horizontalHeader()
        header.setMinimumSectionSize(50)

        # Colonne # : Fixe
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 50)

        # Colonnes Nom et Prénom : Stretch avec largeur initiale plus généreuse
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(1, 150)  # Nom
        header.resizeSection(2, 120)  # Prénom

        # Colonnes fixes : ResizeToContents
        for column in range(3, table.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)

        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.itemSelectionChanged.connect(self._on_selection_changed)
        table.doubleClicked.connect(self._on_fiche)

        # Activer le scrollbar horizontal si nécessaire
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

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

            # Numéro de ligne (badge circulaire)
            row_badge = QLabel(str(row + 1))
            row_badge.setObjectName("row_badge")
            row_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row, 0, row_badge)

            # Nom (stocke l'ID de l'élève)
            nom_item = QTableWidgetItem(eleve.nom)
            nom_item.setData(Qt.ItemDataRole.UserRole, eleve.id)
            self.table.setItem(row, 1, nom_item)

            # Prénom
            self.table.setItem(row, 2, QTableWidgetItem(eleve.prenom))

            # Classe
            self.table.setItem(row, 3, QTableWidgetItem(eleve_avec_totaux.nom_classe))

            # Année
            self.table.setItem(row, 4, QTableWidgetItem(eleve.annee_scolaire))

            # Total dû
            total_du = formater_montant(eleve.total_du, devise)
            self.table.setItem(row, 5, QTableWidgetItem(total_du))

            # Total payé
            total_paye = formater_montant(eleve_avec_totaux.total_paye, devise)
            self.table.setItem(row, 6, QTableWidgetItem(total_paye))

            # Solde
            solde = max(0, eleve.total_du - eleve_avec_totaux.total_paye)
            solde_formatted = formater_montant(solde, devise)
            self.table.setItem(row, 7, QTableWidgetItem(solde_formatted))

            # Statut (pastille + texte)
            statut_widget = self._create_statut_badge(eleve.total_du, eleve_avec_totaux.total_paye)
            self.table.setCellWidget(row, 8, statut_widget)

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
        badge.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        badge.setWordWrap(False)
        badge.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        # Largeur minimale pour afficher "Partiellement payé" en entier
        font_metrics = QFontMetrics(badge.font())
        text_width = font_metrics.horizontalAdvance("Partiellement payé")
        badge.setMinimumWidth(text_width + 24)  # +24 pour le padding CSS (4px 12px)

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
        self.btn_fiche.setEnabled(has_selection)

    def _on_double_click(self):
        """Gère le double-clic sur un élève."""
        self._on_fiche()

    def _on_fiche(self):
        """Gère le clic sur le bouton Fiche / Paiements."""
        session = self.services.get("session")
        if session is not None and not session.autorise("payments.view"):
            return
        from edupaie.ui.fiche_eleve import FicheEleveDialog

        row = self.table.currentRow()
        if row < 0:
            return

        try:
            # Récupérer l'ID de l'élève (maintenant dans la colonne 1 après ajout de #)
            eleve_id = self.table.item(row, 1).data(Qt.ItemDataRole.UserRole)

            dialog = FicheEleveDialog(self.services, eleve_id, self)
            if dialog.exec():
                # Rafraîchir la liste après un paiement
                self._refresh_table()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ouverture de la fiche : {str(e)}")

    def _on_ajouter(self):
        """Gère le clic sur le bouton Ajouter."""
        from edupaie.ui.eleve_form import EleveForm
        from edupaie.services.calculs import determiner_statut

        try:
            # Obtenir l'année scolaire courante
            annee_courante = self.services['parametre'].lire_parametre("annee_scolaire_courante")
            if not annee_courante:
                annee_debut = date.today().year if date.today().month >= 9 else date.today().year - 1
                annee_courante = f"{annee_debut}-{annee_debut + 1}"

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
            # Récupérer l'ID de l'élève (maintenant dans la colonne 1 après ajout de #)
            eleve_id = self.table.item(row, 1).data(Qt.ItemDataRole.UserRole)

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
            # Récupérer l'ID de l'élève (maintenant dans la colonne 1 après ajout de #)
            eleve_id = self.table.item(row, 1).data(Qt.ItemDataRole.UserRole)

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

    def _on_exporter(self):
        """Gère l'export de la liste des élèves."""
        try:
            # Récupérer les données actuelles
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

            if not eleves:
                QMessageBox.warning(self, "Attention", "Aucun élève à exporter")
                return

            # Demander le format et le fichier
            devise = self.services['parametre'].lire_parametre("devise")
            if not devise:
                devise = "FCFA"

            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilter("Fichier Excel (*.xlsx);;Fichier CSV (*.csv)")
            file_dialog.setDefaultSuffix("xlsx")
            file_dialog.setWindowTitle("Exporter la liste des élèves")

            if file_dialog.exec():
                chemin_fichier = file_dialog.selectedFiles()[0]
                suffix = Path(chemin_fichier).suffix.lower()

                if suffix == '.xlsx':
                    exporter_eleves_excel(eleves, chemin_fichier, devise)
                    QMessageBox.information(self, "Succès", f"Export réussi : {chemin_fichier}")
                elif suffix == '.csv':
                    exporter_eleves_csv(eleves, chemin_fichier, devise)
                    QMessageBox.information(self, "Succès", f"Export réussi : {chemin_fichier}")
                else:
                    QMessageBox.warning(self, "Erreur", "Format de fichier non supporté")

        except ImportError:
            QMessageBox.warning(
                self,
                "Module manquant",
                "Pour exporter en Excel, installez openpyxl :\npip install openpyxl"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export : {str(e)}")
