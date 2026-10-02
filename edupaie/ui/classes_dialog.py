"""
Dialogue de gestion des classes.

Ce module définit la QDialog pour lister, ajouter et supprimer des classes.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QWidget, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt


class ClassesDialog(QDialog):
    """Dialogue de gestion des classes."""

    def __init__(self, services):
        """
        Initialise le dialogue.

        Args:
            services: Dictionnaire des services métier
        """
        super().__init__()
        self.services = services
        self.setWindowTitle("Gestion des classes")
        self.setMinimumSize(320, 260)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Barre d'outils
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Tableau des classes
        self.table = self._create_table()
        layout.addWidget(self.table)

    def _create_toolbar(self) -> QWidget:
        """
        Crée la barre d'outils.

        Returns:
            QWidget: Barre d'outils
        """
        toolbar = QWidget()
        layout = QVBoxLayout(toolbar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Champ de saisie pour nouveau nom
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de la nouvelle classe...")
        layout.addWidget(self.nom_input)

        self.salle_combo = QComboBox()
        self.salle_combo.addItem("Aucune salle", None)
        if "salle" in self.services:
            for salle in self.services["salle"].lister_salles():
                self.salle_combo.addItem(salle["nom"], salle["id"])
        layout.addWidget(self.salle_combo)

        self.capacite_input = QSpinBox()
        self.capacite_input.setRange(0, 5000)
        self.capacite_input.setSpecialValueText("Capacité non définie")
        self.capacite_input.setValue(0)
        layout.addWidget(self.capacite_input)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        # Bouton Ajouter
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_ajouter.clicked.connect(self._on_ajouter)
        actions_layout.addWidget(self.btn_ajouter)

        # Bouton Supprimer
        self.btn_supprimer = QPushButton("Supprimer")
        self.btn_supprimer.clicked.connect(self._on_supprimer)
        self.btn_supprimer.setEnabled(False)
        actions_layout.addWidget(self.btn_supprimer)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        return toolbar

    def _create_table(self) -> QTableWidget:
        """
        Crée le tableau des classes.

        Returns:
            QTableWidget: Tableau des classes
        """
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "Nom", "Salle", "Capacité"])
        table.setWordWrap(False)
        table.setTextElideMode(Qt.TextElideMode.ElideRight)

        # Configuration des colonnes
        header = table.horizontalHeader()
        header.setMinimumSectionSize(90)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        table.setColumnWidth(0, 70)
        table.setColumnWidth(1, 220)
        table.setColumnWidth(2, 160)
        table.setColumnWidth(3, 100)

        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.itemSelectionChanged.connect(self._on_selection_changed)

        return table

    def _load_data(self):
        """Charge les données des classes dans le tableau."""
        try:
            classes = self.services['classe'].lister_classes()
            self._populate_table(classes)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {str(e)}")

    def _populate_table(self, classes):
        """
        Remplit le tableau avec les données des classes.

        Args:
            classes: Liste des classes
        """
        self.table.setRowCount(len(classes))

        for row, classe in enumerate(classes):
            # ID
            id_item = QTableWidgetItem(str(classe.id))
            id_item.setData(Qt.ItemDataRole.UserRole, classe.id)
            self.table.setItem(row, 0, id_item)

            # Nom
            self.table.setItem(row, 1, QTableWidgetItem(classe.nom))
            salle_nom = "—"
            if getattr(classe, "salle_id", None) is not None and "salle" in self.services:
                salles = self.services["salle"].lister_salles(actives_seulement=False)
                salle = next((salle for salle in salles if salle["id"] == classe.salle_id), None)
                salle_nom = salle["nom"] if salle else "—"
            self.table.setItem(row, 2, QTableWidgetItem(salle_nom))
            self.table.setItem(
                row, 3,
                QTableWidgetItem(str(classe.capacite) if getattr(classe, "capacite", None) else "—"),
            )

    def _on_selection_changed(self):
        """Gère le changement de sélection dans le tableau."""
        has_selection = self.table.currentRow() >= 0
        self.btn_supprimer.setEnabled(has_selection)

    def _on_ajouter(self):
        """Gère le clic sur le bouton Ajouter."""
        nom = self.nom_input.text().strip()
        if not nom:
            QMessageBox.warning(self, "Validation", "Le nom de la classe est obligatoire")
            return

        try:
            capacite = self.capacite_input.value() or None
            self.services['classe'].creer_classe(
                nom,
                self.salle_combo.currentData(),
                capacite,
            )
            self.nom_input.clear()
            self.capacite_input.setValue(0)
            self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _on_supprimer(self):
        """Gère le clic sur le bouton Supprimer."""
        row = self.table.currentRow()
        if row < 0:
            return

        try:
            classe_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            classe_nom = self.table.item(row, 1).text()

            reply = QMessageBox.question(
                self,
                "Confirmation",
                f"Supprimer la classe '{classe_nom}' ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.services['classe'].supprimer_classe(classe_id)
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
