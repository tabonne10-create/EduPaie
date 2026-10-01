"""
Dialogue de gestion des classes.

Ce module définit la QDialog pour lister, ajouter et supprimer des classes.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)


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
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

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
        from PySide6.QtWidgets import QWidget

        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(12)

        # Champ de saisie pour nouveau nom
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de la nouvelle classe...")
        layout.addWidget(self.nom_input)

        # Bouton Ajouter
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_ajouter.clicked.connect(self._on_ajouter)
        layout.addWidget(self.btn_ajouter)

        # Bouton Supprimer
        self.btn_supprimer = QPushButton("Supprimer")
        self.btn_supprimer.clicked.connect(self._on_supprimer)
        self.btn_supprimer.setEnabled(False)
        layout.addWidget(self.btn_supprimer)

        layout.addStretch()

        return toolbar

    def _create_table(self) -> QTableWidget:
        """
        Crée le tableau des classes.

        Returns:
            QTableWidget: Tableau des classes
        """
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["ID", "Nom"])

        # Configuration des colonnes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

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
            self.services['classe'].creer_classe(nom)
            self.nom_input.clear()
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
