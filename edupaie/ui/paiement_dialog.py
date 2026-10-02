"""
Dialogue d'enregistrement de paiement.

Ce module définit la QDialog pour enregistrer un paiement pour un élève.
"""

from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QDialogButtonBox,
    QMessageBox
)
from PySide6.QtCore import Qt

from edupaie.utils.format import formater_montant


class PaiementDialog(QDialog):
    """Dialogue d'enregistrement de paiement."""

    def __init__(self, services, eleve_fiche: dict):
        """
        Initialise le dialogue.

        Args:
            services: Dictionnaire des services métier
            eleve_fiche: Dictionnaire retourné par EleveService.fiche()
        """
        super().__init__()
        self.services = services
        self.eleve_fiche = eleve_fiche

        self.setWindowTitle("Enregistrer un paiement")
        self.setMinimumWidth(450)

        self._setup_ui()
        self._populate_fields()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Informations de l'élève
        eleve_info = self._create_eleve_info()
        layout.addWidget(eleve_info)

        # Solde restant
        solde_layout = self._create_solde_info()
        layout.addWidget(solde_layout)

        # Formulaire de paiement
        form_layout = self._create_payment_form()
        layout.addWidget(form_layout)

        layout.addStretch()

        # Boutons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self._on_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _create_eleve_info(self) -> QWidget:
        """
        Crée le widget d'information de l'élève.

        Returns:
            QWidget: Widget d'information
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        widget.setStyleSheet("background-color: #F5F6F8; border-radius: 8px; padding: 12px;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)

        eleve = self.eleve_fiche["eleve"]
        nom_label = QLabel(f"{eleve.nom} {eleve.prenom}")
        nom_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(nom_label)

        classe_label = QLabel(f"Classe : {self.eleve_fiche['nom_classe']}")
        layout.addWidget(classe_label)

        total_label = QLabel(f"Total dû : {formater_montant(self.eleve_fiche['total_du'])}")
        layout.addWidget(total_label)

        return widget

    def _create_solde_info(self) -> QWidget:
        """
        Crée le widget d'information du solde.

        Returns:
            QWidget: Widget d'information
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(8)

        devise = self.services['parametre'].lire_parametre("devise") or "FCFA"

        solde_label = QLabel("Solde restant :")
        layout.addWidget(solde_label)

        solde_value = QLabel(formater_montant(self.eleve_fiche["solde"], devise))
        solde_value.setStyleSheet("font-weight: 600; font-size: 16px;")
        layout.addWidget(solde_value)

        layout.addStretch()

        return widget

    def _create_payment_form(self) -> QWidget:
        """
        Crée le formulaire de paiement.

        Returns:
            QWidget: Formulaire de paiement
        """
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        # Montant
        montant_layout = QHBoxLayout()
        montant_label = QLabel("Montant à payer *")
        self.montant_input = QSpinBox()
        self.montant_input.setMinimum(1)
        self.montant_input.setMaximum(999999999)
        self.montant_input.setSingleStep(1000)
        montant_layout.addWidget(montant_label)
        montant_layout.addWidget(self.montant_input)
        layout.addLayout(montant_layout)

        # Date
        date_layout = QHBoxLayout()
        date_label = QLabel("Date *")
        from PySide6.QtWidgets import QDateEdit
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(date.today())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Mode de paiement
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode de paiement *")
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Espèces", "especes")
        self.mode_combo.addItem("Chèque", "cheque")
        self.mode_combo.addItem("Virement", "virement")
        self.mode_combo.addItem("Mobile Money", "mobile_money")
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        return widget

    def _populate_fields(self):
        """Remplit les champs avec les valeurs par défaut."""
        # Le montant max ne peut pas dépasser le solde
        self.montant_input.setMaximum(self.eleve_fiche["solde"])

    def _on_accept(self):
        """Gère la validation et l'acceptation du formulaire."""
        devise = self.services['parametre'].lire_parametre("devise") or "FCFA"

        # Récupérer les valeurs
        montant = self.montant_input.value()
        date_paiement = self.date_input.date().toString("yyyy-MM-dd")
        mode = self.mode_combo.currentData()

        try:
            paiement = self.services['paiement'].enregistrer_paiement(
                self.eleve_fiche["eleve"].id,
                montant,
                date_paiement,
                mode
            )

            # Message de succès avec numéro de reçu
            QMessageBox.information(
                self,
                "Succès",
                f"Paiement enregistré avec succès\n\n"
                f"Numéro de reçu : {paiement.numero_recu}\n"
                f"Montant : {formater_montant(montant, devise)}\n"
                f"Solde après : {formater_montant(paiement.solde_apres, devise)}"
            )

            self.accept()

        except Exception as e:
            # RegleMetierError : paiement supérieur au solde
            if "RegleMetierError" in type(e).__name__:
                QMessageBox.warning(
                    self,
                    "Paiement refusé",
                    f"Le montant dépasse le solde restant.\n\n"
                    f"Solde restant : {formater_montant(self.eleve_fiche['solde'], devise)}\n"
                    f"Montant saisi : {formater_montant(montant, devise)}"
                )
                return

            # ValidationError
            QMessageBox.critical(self, "Erreur", str(e))
