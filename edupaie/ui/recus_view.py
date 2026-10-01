"""Registre global des reçus de paiement."""

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from edupaie.ui.recu_export import proposer_export_recu
from edupaie.utils.format import formater_montant


class RecusView(QWidget):
    """Permet de rechercher les paiements et de réexporter leurs reçus PDF."""

    MODES = (
        ("Tous les modes", None),
        ("Espèces", "especes"),
        ("Chèque", "cheque"),
        ("Virement", "virement"),
        ("Mobile Money", "mobile_money"),
    )

    def __init__(self, services):
        super().__init__()
        self.services = services
        self._paiements_par_id = {}
        self._setup_ui()
        self.actualiser()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        heading = QHBoxLayout()
        title_group = QVBoxLayout()
        title_group.setSpacing(5)
        title = QLabel("Registre des reçus")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #5F1015;")
        subtitle = QLabel("Rechercher un paiement et réexporter son reçu PDF")
        subtitle.setStyleSheet("font-size: 12px; color: #657078;")
        title_group.addWidget(title)
        title_group.addWidget(subtitle)
        heading.addLayout(title_group)
        heading.addStretch()
        self.count_label = QLabel("0 reçu")
        self.count_label.setStyleSheet("font-size: 12px; color: #657078;")
        heading.addWidget(self.count_label)
        self.btn_actualiser = QPushButton()
        self.btn_actualiser.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.btn_actualiser.setToolTip("Actualiser le registre")
        self.btn_actualiser.setAccessibleName("Actualiser le registre des reçus")
        self.btn_actualiser.setProperty("secondary", True)
        self.btn_actualiser.clicked.connect(self.actualiser)
        heading.addWidget(self.btn_actualiser)
        layout.addLayout(heading)

        filters = QHBoxLayout()
        filters.setSpacing(10)
        self.recherche_input = QLineEdit()
        self.recherche_input.setPlaceholderText("N° de reçu, élève ou classe…")
        self.recherche_input.setClearButtonEnabled(True)
        self.recherche_input.textChanged.connect(self.actualiser)
        filters.addWidget(self.recherche_input, 1)

        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumWidth(150)
        for label, code in self.MODES:
            self.mode_combo.addItem(label, code)
        self.mode_combo.currentIndexChanged.connect(self.actualiser)
        filters.addWidget(self.mode_combo)
        layout.addLayout(filters)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Date", "N° de reçu", "Élève", "Classe", "Mode", "Montant"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        self.table.cellDoubleClicked.connect(lambda row, _column: self._exporter_selection())
        layout.addWidget(self.table, 1)

        footer = QHBoxLayout()
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #B43B3B;")
        footer.addWidget(self.message_label, 1)
        self.btn_exporter = QPushButton("Exporter le reçu PDF")
        self.btn_exporter.setEnabled(False)
        self.btn_exporter.clicked.connect(self._exporter_selection)
        footer.addWidget(self.btn_exporter)
        layout.addLayout(footer)

    @staticmethod
    def _date_lisible(date_iso: str) -> str:
        try:
            return datetime.strptime(date_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return date_iso

    @staticmethod
    def _mode_libelle(mode: str) -> str:
        return {
            "especes": "Espèces",
            "cheque": "Chèque",
            "virement": "Virement",
            "mobile_money": "Mobile Money",
        }.get(mode, mode)

    def actualiser(self, *_args):
        """Recharge le registre en fonction des critères courants."""
        recherche = self.recherche_input.text().strip() or None
        mode = self.mode_combo.currentData()
        try:
            lignes = self.services["paiement"].lister_tous_paiements(
                recherche=recherche,
                mode=mode,
            )
            devise = self.services["parametre"].lire_parametre("devise") or "FCFA"
        except Exception as erreur:
            self.message_label.setText(f"Impossible de charger les reçus : {erreur}")
            return

        self.message_label.clear()
        self._paiements_par_id = {ligne.paiement.id: ligne for ligne in lignes}
        self.table.setRowCount(len(lignes))
        self.count_label.setText(f"{len(lignes)} reçu" if len(lignes) == 1 else f"{len(lignes)} reçus")

        for row, ligne in enumerate(lignes):
            paiement = ligne.paiement
            valeurs = [
                self._date_lisible(paiement.date_paiement),
                paiement.numero_recu,
                f"{ligne.prenom_eleve} {ligne.nom_eleve}",
                ligne.nom_classe,
                self._mode_libelle(paiement.mode),
                formater_montant(paiement.montant, devise),
            ]
            for column, texte in enumerate(valeurs):
                item = QTableWidgetItem(texte)
                if column == 5:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if column == 1:
                    item.setData(Qt.ItemDataRole.UserRole, paiement.id)
                self.table.setItem(row, column, item)

        self._selection_changed()
        if not lignes:
            self.message_label.setText("Aucun reçu ne correspond à cette recherche.")

    def _selection_changed(self):
        self.btn_exporter.setEnabled(self.table.currentRow() >= 0)

    def _exporter_selection(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 1)
        paiement_id = item.data(Qt.ItemDataRole.UserRole)
        ligne = self._paiements_par_id.get(paiement_id)
        if ligne is None:
            return
        proposer_export_recu(
            self,
            self.services,
            ligne.paiement,
            ligne.paiement.eleve_id,
        )
