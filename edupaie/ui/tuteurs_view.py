"""Gestion des parents et tuteurs liés aux élèves."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TuteursView(QWidget):
    def __init__(self, services):
        super().__init__()
        self.services = services
        self._setup_ui()
        self.actualiser()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(14)

        title = QLabel("Parents et tuteurs")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #5F1015;")
        subtitle = QLabel("Coordonnées des responsables liées aux élèves")
        subtitle.setStyleSheet("color: #657078;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        filters = QHBoxLayout()
        self.recherche_input = QLineEdit()
        self.recherche_input.setPlaceholderText("Rechercher un nom ou téléphone…")
        self.recherche_input.setClearButtonEnabled(True)
        self.recherche_input.textChanged.connect(self.actualiser)
        filters.addWidget(self.recherche_input, 1)
        self.eleve_combo = QComboBox()
        self.eleve_combo.setMinimumWidth(220)
        filters.addWidget(self.eleve_combo)
        layout.addLayout(filters)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Nom", "Téléphone", "Fonction", "Lien", "Élèves", "Responsable principal"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, 6):
            self.table.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )
        layout.addWidget(self.table, 1)

        self.message_label = QLabel()
        self.message_label.setStyleSheet("color: #B43B3B;")
        layout.addWidget(self.message_label)

        form = QFormLayout()
        self.nom_input = QLineEdit()
        self.prenom_input = QLineEdit()
        self.telephone_input = QLineEdit()
        self.telephone_input.setPlaceholderText("Téléphone, facultatif")
        self.fonction_input = QLineEdit()
        self.fonction_input.setPlaceholderText("Ex. commerçant, enseignant…")
        self.lien_input = QLineEdit()
        self.lien_input.setPlaceholderText("Ex. mère, tuteur légal…")
        form.addRow("Nom *", self.nom_input)
        form.addRow("Prénom", self.prenom_input)
        form.addRow("Téléphone", self.telephone_input)
        form.addRow("Fonction", self.fonction_input)
        form.addRow("Lien avec l'élève", self.lien_input)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.btn_ajouter = QPushButton("Ajouter et associer à l'élève")
        self.btn_ajouter.clicked.connect(self._ajouter)
        actions.addWidget(self.btn_ajouter)
        actions.addStretch()
        layout.addLayout(actions)

    def actualiser(self, *_args):
        session = self.services.get("session")
        try:
            eleves = self.services["eleve"].lister_eleves()
            selection = self.eleve_combo.currentData()
            self.eleve_combo.blockSignals(True)
            self.eleve_combo.clear()
            for eleve in eleves:
                self.eleve_combo.addItem(
                    f"{eleve.eleve.prenom} {eleve.eleve.nom} — {eleve.nom_classe}",
                    eleve.eleve.id,
                )
            index = self.eleve_combo.findData(selection)
            if index >= 0:
                self.eleve_combo.setCurrentIndex(index)
            self.eleve_combo.blockSignals(False)
            lignes = self.services["tuteur"].lister_tous(
                self.recherche_input.text(), session
            )
        except Exception as erreur:
            self.message_label.setText(str(erreur))
            return

        self.message_label.clear()
        self.table.setRowCount(len(lignes))
        for row, tuteur in enumerate(lignes):
            values = [
                f"{tuteur['prenom']} {tuteur['nom']}".strip(),
                tuteur["telephone"] or "—",
                tuteur["fonction"] or "—",
                "—",
                str(tuteur["nombre_eleves"]),
                "—",
            ]
            for column, text in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(text))

    def _ajouter(self):
        eleve_id = self.eleve_combo.currentData()
        if eleve_id is None:
            self.message_label.setText("Crée d'abord un élève pour lui associer un tuteur.")
            return
        try:
            self.services["tuteur"].creer_et_associer(
                eleve_id=eleve_id,
                nom=self.nom_input.text(),
                prenom=self.prenom_input.text(),
                telephone=self.telephone_input.text(),
                fonction=self.fonction_input.text(),
                lien=self.lien_input.text(),
                session=self.services.get("session"),
            )
            self.nom_input.clear()
            self.prenom_input.clear()
            self.telephone_input.clear()
            self.fonction_input.clear()
            self.lien_input.clear()
            self.actualiser()
        except Exception as erreur:
            self.message_label.setText(str(erreur))
