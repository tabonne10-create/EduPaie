"""
Dialogue d'enregistrement de paiement.

Ce module définit la QDialog pour enregistrer un paiement pour un élève.
"""

from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDateEdit, QDialogButtonBox,
    QMessageBox, QTimeEdit
)
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QGuiApplication

from edupaie.services.exceptions import ValidationError, RegleMetierError
from edupaie.utils.format import formater_montant
from edupaie.ui.recu_export import proposer_export_recu


class PaiementDialog(QDialog):
    """Dialogue d'enregistrement de paiement."""

    def __init__(self, services, eleve_id, parent=None):
        """
        Initialise le dialogue de paiement.

        Args:
            services: Dictionnaire des services métier
            eleve_id: ID de l'élève
            parent: Widget parent
        """
        super().__init__(parent)
        self.services = services
        self.eleve_id = eleve_id
        self.paiement_enregistre = None
        self.setWindowTitle("Enregistrer un paiement")

        # Adapter la taille à l'écran disponible
        screen = QGuiApplication.primaryScreen()
        available_geo = screen.availableGeometry()
        initial_width = min(400, available_geo.width() - 50)
        self.resize(initial_width, 300)
        self.setMinimumSize(min(350, available_geo.width() - 100), 250)

        # Charger les données de l'élève
        self._load_eleve_data()

        self._setup_ui()

    def _load_eleve_data(self):
        """Charge les données de l'élève."""
        try:
            fiche = self.services['eleve'].fiche(self.eleve_id)
            self.eleve = fiche['eleve']
            self.nom_classe = fiche['nom_classe']
            self.total_du = fiche['total_du']
            self.total_paye = fiche['total_paye']
            self.solde = fiche['solde']
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement de l'élève : {str(e)}")
            self.reject()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Informations de l'élève
        info_layout = self._create_eleve_info()
        layout.addWidget(info_layout)

        # Solde restant
        devise = self.services['parametre'].lire_parametre("devise")
        if not devise:
            devise = "FCFA"
        solde_label = QLabel(f"Solde restant : {formater_montant(self.solde, devise)}")
        solde_label.setStyleSheet("font-weight: 600; color: #8B0000; font-size: 13px;")
        layout.addWidget(solde_label)

        # Champ montant
        montant_layout = QHBoxLayout()
        montant_layout.setSpacing(8)
        montant_label = QLabel("Montant :")
        self.montant_input = QLineEdit()
        self.montant_input.setPlaceholderText("Ex: 50000")
        montant_layout.addWidget(montant_label)
        montant_layout.addWidget(self.montant_input)
        layout.addLayout(montant_layout)

        # Champ date
        date_layout = QHBoxLayout()
        date_layout.setSpacing(8)
        date_label = QLabel("Date :")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        heure_layout = QHBoxLayout()
        heure_layout.setSpacing(8)
        heure_label = QLabel("Heure :")
        self.heure_input = QTimeEdit()
        self.heure_input.setTime(QTime.currentTime())
        self.heure_input.setDisplayFormat("HH:mm")
        heure_layout.addWidget(heure_label)
        heure_layout.addWidget(self.heure_input)
        layout.addLayout(heure_layout)

        # Champ mode de paiement
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(8)
        mode_label = QLabel("Mode :")
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Espèces", "especes")
        self.mode_combo.addItem("Chèque", "cheque")
        self.mode_combo.addItem("Virement", "virement")
        self.mode_combo.addItem("Mobile Money", "mobile_money")
        self.mode_combo.currentIndexChanged.connect(self._mettre_a_jour_payeur)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        payeur_layout = QHBoxLayout()
        payeur_layout.setSpacing(8)
        self.payeur_label = QLabel("Nom de l'envoyeur :")
        self.payeur_input = QLineEdit()
        self.payeur_input.setPlaceholderText("Facultatif, si différent de l'élève")
        payeur_layout.addWidget(self.payeur_label)
        payeur_layout.addWidget(self.payeur_input)
        layout.addLayout(payeur_layout)
        self._mettre_a_jour_payeur()

        layout.addStretch()

        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _create_eleve_info(self) -> QWidget:
        """
        Crée le widget d'information de l'élève.

        Returns:
            QWidget: Widget avec les informations de l'élève
        """
        widget = QWidget()
        widget.setObjectName("secondary_area")
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)

        info_text = f"{self.eleve.nom} {self.eleve.prenom} - {self.nom_classe}"
        label = QLabel(info_text)
        label.setStyleSheet("font-weight: 600; font-size: 16px; color: #1E293B;")
        layout.addWidget(label)

        return widget

    def _mettre_a_jour_payeur(self):
        """Met en évidence le payeur pour les paiements non espèces."""
        visible = self.mode_combo.currentData() != "especes"
        self.payeur_label.setVisible(visible)
        self.payeur_input.setVisible(visible)

    def _on_accept(self):
        """Gère la validation du dialogue."""
        # Récupérer les valeurs
        montant_text = self.montant_input.text().strip()
        if not montant_text:
            QMessageBox.warning(self, "Attention", "Veuillez saisir un montant.")
            return

        try:
            montant = int(montant_text.replace(" ", ""))
        except ValueError:
            QMessageBox.warning(self, "Attention", "Le montant doit être un nombre entier.")
            return

        date_paiement = self.date_input.date().toString("yyyy-MM-dd")
        heure_paiement = self.heure_input.time().toString("HH:mm:ss")
        nom_payeur = self.payeur_input.text().strip()
        mode = self.mode_combo.currentData()

        # Enregistrer le paiement
        try:
            paiement = self.services['paiement'].enregistrer_paiement(
                self.eleve_id,
                montant,
                date_paiement,
                mode,
                heure_paiement,
                nom_payeur,
            )
            self.paiement_enregistre = paiement

            devise = self.services['parametre'].lire_parametre("devise")
            if not devise:
                devise = "FCFA"

            QMessageBox.information(
                self,
                "Succès",
                f"Paiement enregistré avec succès.\n\n"
                f"Numéro de reçu : {paiement.numero_recu}\n"
                f"Montant : {formater_montant(montant, devise)}"
            )
            proposer_export_recu(self, self.services, paiement, self.eleve_id)
            self.accept()

        except RegleMetierError as e:
            # Erreur de règle métier (paiement supérieur au solde)
            devise = self.services['parametre'].lire_parametre("devise")
            if not devise:
                devise = "FCFA"
            QMessageBox.warning(
                self,
                "Paiement refusé",
                str(e)
            )
        except ValidationError as e:
            QMessageBox.warning(self, "Erreur de validation", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement : {str(e)}")
