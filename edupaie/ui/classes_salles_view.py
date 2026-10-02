"""Gestion des classes et des salles."""

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ClassesSallesView(QWidget):
    def __init__(self, services):
        super().__init__()
        self.services = services
        self._setup_ui()
        self.actualiser()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(14)

        title = QLabel("Classes et salles")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #5F1015;")
        subtitle = QLabel("Organiser les classes et la capacité d'accueil de l'établissement")
        subtitle.setStyleSheet("color: #657078;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        class_actions = QHBoxLayout()
        description = QLabel("Créer, renommer ou supprimer les classes enregistrées.")
        description.setStyleSheet("color: #4E5A60;")
        class_actions.addWidget(description, 1)
        self.btn_gerer_classes = QPushButton("Gérer les classes")
        self.btn_gerer_classes.clicked.connect(self._gerer_classes)
        class_actions.addWidget(self.btn_gerer_classes)
        layout.addLayout(class_actions)

        room_title = QLabel("Salles")
        room_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #303B40;")
        layout.addWidget(room_title)

        form = QFormLayout()
        self.nom_salle_input = QLineEdit()
        self.nom_salle_input.setPlaceholderText("Ex. Salle 12")
        self.capacite_input = QSpinBox()
        self.capacite_input.setRange(0, 5000)
        self.capacite_input.setSpecialValueText("Non définie")
        self.capacite_input.setValue(0)
        form.addRow("Nom de la salle", self.nom_salle_input)
        form.addRow("Capacité", self.capacite_input)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.btn_ajouter_salle = QPushButton("Ajouter la salle")
        self.btn_ajouter_salle.clicked.connect(self._ajouter_salle)
        actions.addWidget(self.btn_ajouter_salle)
        self.message_label = QLabel()
        self.message_label.setStyleSheet("color: #B43B3B;")
        actions.addWidget(self.message_label, 1)
        layout.addLayout(actions)

        self.salles_table = QTableWidget(0, 3)
        self.salles_table.setHorizontalHeaderLabels(["Salle", "Capacité", "Classes affectées"])
        self.salles_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.salles_table.setAlternatingRowColors(True)
        self.salles_table.verticalHeader().setVisible(False)
        self.salles_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.salles_table, 1)

    def actualiser(self):
        try:
            salles = self.services["salle"].lister_salles(actives_seulement=False)
            classes = self.services["classe"].lister_classes()
        except Exception as erreur:
            self.message_label.setText(str(erreur))
            return
        self.salles_table.setRowCount(len(salles))
        for row, salle in enumerate(salles):
            count = sum(1 for classe in classes if getattr(classe, "salle_id", None) == salle["id"])
            values = [salle["nom"], salle["capacite"] or "—", count]
            for column, value in enumerate(values):
                self.salles_table.setItem(row, column, QTableWidgetItem(str(value)))

    def _ajouter_salle(self):
        capacite = self.capacite_input.value() or None
        try:
            self.services["salle"].creer_salle(self.nom_salle_input.text(), capacite)
            self.nom_salle_input.clear()
            self.capacite_input.setValue(0)
            self.message_label.clear()
            self.actualiser()
        except Exception as erreur:
            self.message_label.setText(str(erreur))

    def _gerer_classes(self):
        from edupaie.ui.classes_dialog import ClassesDialog

        dialog = ClassesDialog(self.services, self)
        if dialog.exec():
            self.actualiser()
