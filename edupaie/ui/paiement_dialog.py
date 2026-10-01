"""
Dialogue d'enregistrement de paiement.

Ce module définit la QDialog pour enregistrer un paiement pour un élève.
"""

from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDateEdit, QDialogButtonBox,
    QMessageBox
)
from PySide6.QtCore import Qt, QDate

from edupaie.services.exceptions import ValidationError, RegleMetierError
from edupaie.utils.format import formater_montant


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
        self.setWindowTitle("Enregistrer un paiement")
        self.setMinimumWidth(400)

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
        layout.setSpacing(16)

        # Informations de l'élève
        info_layout = self._create_eleve_info()
        layout.addWidget(info_layout)

        # Solde restant
        devise = self.services['parametre'].lire_parametre("devise")
        if not devise:
            devise = "FCFA"
        solde_label = QLabel(f"Solde restant : {formater_montant(self.solde, devise)}")
        solde_label.setStyleSheet("font-weight: 600; color: #8B0000;")
        layout.addWidget(solde_label)

        # Champ montant
        montant_layout = QHBoxLayout()
        montant_label = QLabel("Montant :")
        self.montant_input = QLineEdit()
        self.montant_input.setPlaceholderText("Ex: 50000")
        montant_layout.addWidget(montant_label)
        montant_layout.addWidget(self.montant_input)
        layout.addLayout(montant_layout)

        # Champ date
        date_layout = QHBoxLayout()
        date_label = QLabel("Date :")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Champ mode de paiement
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode :")
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Espèces", "especes")
        self.mode_combo.addItem("Chèque", "cheque")
        self.mode_combo.addItem("Virement", "virement")
        self.mode_combo.addItem("Mobile Money", "mobile_money")
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        layout.addStretch()

        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _create_eleve_info(self) -> QLabel:
        """
        Crée le label d'information de l'élève.

        Returns:
            QLabel: Label avec les informations de l'élève
        """
        info_text = f"{self.eleve.nom} {self.eleve.prenom} - {self.nom_classe}"
        label = QLabel(info_text)
        label.setStyleSheet("font-weight: 600; font-size: 14px;")
        return label

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
        mode = self.mode_combo.currentData()

        # Enregistrer le paiement
        try:
            paiement = self.services['paiement'].enregistrer_paiement(
                self.eleve_id,
                montant,
                date_paiement,
                mode
            )

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
