"""
Formulaire d'ajout/modification d'élève.

Ce module définit la QDialog pour créer ou modifier un élève.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QDialogButtonBox,
    QMessageBox
)
from PySide6.QtCore import Qt


class EleveForm(QDialog):
    """Formulaire d'ajout/modification d'élève."""

    def __init__(self, services, annee_courante: str, eleve=None):
        """
        Initialise le formulaire.

        Args:
            services: Dictionnaire des services métier
            annee_courante: Année scolaire courante
            eleve: Élève à modifier (None pour création)
        """
        super().__init__()
        self.services = services
        self.annee_courante = annee_courante
        self.eleve = eleve
        self.confirmer_baisse = False

        self.setWindowTitle("Ajouter un élève" if eleve is None else "Modifier l'élève")
        self.setMinimumWidth(400)

        self._setup_ui()
        self._load_classes()
        self._populate_fields()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Nom
        nom_layout = QHBoxLayout()
        nom_label = QLabel("Nom *")
        self.nom_input = QLineEdit()
        nom_layout.addWidget(nom_label)
        nom_layout.addWidget(self.nom_input)
        layout.addLayout(nom_layout)

        # Prénom
        prenom_layout = QHBoxLayout()
        prenom_label = QLabel("Prénom *")
        self.prenom_input = QLineEdit()
        prenom_layout.addWidget(prenom_label)
        prenom_layout.addWidget(self.prenom_input)
        layout.addLayout(prenom_layout)

        # Classe
        classe_layout = QHBoxLayout()
        classe_label = QLabel("Classe *")
        self.classe_combo = QComboBox()
        classe_layout.addWidget(classe_label)
        classe_layout.addWidget(self.classe_combo)
        layout.addLayout(classe_layout)

        # Année scolaire
        annee_layout = QHBoxLayout()
        annee_label = QLabel("Année scolaire *")
        self.annee_input = QLineEdit()
        self.annee_input.setText(self.annee_courante)
        annee_layout.addWidget(annee_label)
        annee_layout.addWidget(self.annee_input)
        layout.addLayout(annee_layout)

        # Total dû
        total_layout = QHBoxLayout()
        total_label = QLabel("Total dû (FCFA) *")
        self.total_input = QSpinBox()
        self.total_input.setMinimum(0)
        self.total_input.setMaximum(999999999)
        self.total_input.setSingleStep(1000)
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_input)
        layout.addLayout(total_layout)

        layout.addStretch()

        # Boutons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self._on_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _load_classes(self):
        """Charge les classes dans le combo."""
        try:
            classes = self.services['classe'].lister_classes()
            self.classe_combo.clear()
            for classe in classes:
                self.classe_combo.addItem(classe.nom, classe.id)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des classes : {str(e)}")

    def _populate_fields(self):
        """Remplit les champs si modification."""
        if self.eleve:
            self.nom_input.setText(self.eleve.nom)
            self.prenom_input.setText(self.eleve.prenom)
            self.annee_input.setText(self.eleve.annee_scolaire)
            self.total_input.setValue(self.eleve.total_du)

            # Sélectionner la classe
            for i in range(self.classe_combo.count()):
                if self.classe_combo.itemData(i) == self.eleve.classe_id:
                    self.classe_combo.setCurrentIndex(i)
                    break

    def _on_accept(self):
        """Gère la validation et l'acceptation du formulaire."""
        # Récupérer les valeurs
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        classe_id = self.classe_combo.currentData()
        annee_scolaire = self.annee_input.text().strip()
        total_du = self.total_input.value()

        # Validation basique
        if not nom:
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
        if not prenom:
            QMessageBox.warning(self, "Validation", "Le prénom est obligatoire")
            return
        if classe_id is None:
            QMessageBox.warning(self, "Validation", "La classe est obligatoire")
            return
        if not annee_scolaire:
            QMessageBox.warning(self, "Validation", "L'année scolaire est obligatoire")
            return

        try:
            if self.eleve is None:
                # Création
                self.services['eleve'].creer_eleve(
                    nom, prenom, classe_id, annee_scolaire, total_du
                )
            else:
                # Modification
                self.services['eleve'].modifier_eleve(
                    self.eleve.id,
                    nom, prenom, classe_id, annee_scolaire, total_du,
                    confirmer=self.confirmer_baisse
                )

            self.accept()

        except Exception as e:
            # Gérer ConfirmationRequise
            if "ConfirmationRequise" in type(e).__name__:
                reply = QMessageBox.question(
                    self,
                    "Confirmation requise",
                    str(e),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.confirmer_baisse = True
                    self._on_accept()  # Réessayer avec confirmation
                return

            # Autres erreurs
            QMessageBox.critical(self, "Erreur", str(e))
