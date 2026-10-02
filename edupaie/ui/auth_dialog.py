"""Création du premier compte directeur et connexion locale."""

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from edupaie.services.exceptions import ValidationError


class AuthDialog(QDialog):
    """Dialogue de connexion ou de configuration initiale du directeur."""

    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.session = None
        self.premiere_installation = auth_service.installation_requise()
        self.setWindowTitle("Configuration du directeur" if self.premiere_installation else "Connexion EduPaie")
        self.setMinimumWidth(380)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(14)

        titre = QLabel("Créer le compte directeur" if self.premiere_installation else "Connexion")
        titre.setStyleSheet("font-size: 19px; font-weight: 700; color: #8B0000;")
        layout.addWidget(titre)

        description = QLabel(
            "Ce compte contrôle les utilisateurs, rôles et paramètres."
            if self.premiere_installation
            else "Connectez-vous avec votre compte EduPaie."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #5E686E;")
        layout.addWidget(description)

        form = QFormLayout()
        form.setSpacing(10)
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom complet du directeur")
        self.identifiant_input = QLineEdit()
        self.identifiant_input.setPlaceholderText("Identifiant")
        self.mot_de_passe_input = QLineEdit()
        self.mot_de_passe_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.mot_de_passe_input.setPlaceholderText("10 caractères minimum")
        form.addRow("Nom complet :", self.nom_input)
        form.addRow("Identifiant :", self.identifiant_input)
        form.addRow("Mot de passe :", self.mot_de_passe_input)
        self.confirmer_input = QLineEdit()
        self.confirmer_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmer_input.setPlaceholderText("Confirmer le mot de passe")
        if self.premiere_installation:
            form.addRow("Confirmation :", self.confirmer_input)
        else:
            self.nom_input.hide()
        layout.addLayout(form)

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #B43B3B;")
        self.message_label.hide()
        layout.addWidget(self.message_label)

        actions = QVBoxLayout()
        self.btn_valider = QPushButton("Créer le compte directeur" if self.premiere_installation else "Se connecter")
        self.btn_valider.clicked.connect(self._valider)
        actions.addWidget(self.btn_valider)
        self.btn_quitter = QPushButton("Quitter")
        self.btn_quitter.setProperty("secondary", True)
        self.btn_quitter.clicked.connect(self.reject)
        actions.addWidget(self.btn_quitter)
        layout.addLayout(actions)

        self.identifiant_input.returnPressed.connect(self.mot_de_passe_input.setFocus)
        self.mot_de_passe_input.returnPressed.connect(self._valider)
        if self.premiere_installation:
            self.confirmer_input.returnPressed.connect(self._valider)
        else:
            self.identifiant_input.setFocus()

    def _valider(self):
        identifiant = self.identifiant_input.text().strip()
        mot_de_passe = self.mot_de_passe_input.text()
        try:
            if self.premiere_installation:
                if mot_de_passe != self.confirmer_input.text():
                    raise ValidationError("Les deux mots de passe ne correspondent pas")
                self.session = self.auth_service.creer_premier_directeur(
                    self.nom_input.text(), identifiant, mot_de_passe
                )
            else:
                self.session = self.auth_service.authentifier(identifiant, mot_de_passe)
        except ValidationError as erreur:
            self.message_label.setText(str(erreur))
            self.message_label.show()
            self.mot_de_passe_input.clear()
            return
        except Exception as erreur:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir la session : {erreur}")
            return
        self.accept()
