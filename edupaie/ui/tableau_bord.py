"""Vue de synthèse financière et des effectifs de l'établissement."""

from datetime import datetime

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from edupaie.utils.format import formater_montant


class TableauBord(QWidget):
    """Affiche les indicateurs globaux et les résultats par classe."""

    def __init__(self, services):
        super().__init__()
        self.services = services
        self._setup_ui()
        self.actualiser()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        title_group = QVBoxLayout()
        title_group.setSpacing(5)
        title = QLabel("Tableau de bord")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #5F1015;")
        subtitle = QLabel("Vue d'ensemble des paiements scolaires")
        subtitle.setStyleSheet("font-size: 12px; color: #657078;")
        title_group.addWidget(title)
        title_group.addWidget(subtitle)
        header_layout.addLayout(title_group)
        header_layout.addStretch()

        self.actualisation_label = QLabel()
        self.actualisation_label.setStyleSheet("font-size: 11px; color: #657078;")
        header_layout.addWidget(self.actualisation_label)

        self.btn_actualiser = QPushButton()
        self.btn_actualiser.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        )
        self.btn_actualiser.setToolTip("Actualiser les statistiques")
        self.btn_actualiser.setAccessibleName("Actualiser les statistiques")
        self.btn_actualiser.setProperty("secondary", True)
        self.btn_actualiser.clicked.connect(self.actualiser)
        header_layout.addWidget(self.btn_actualiser)
        layout.addLayout(header_layout)

        metrics_layout = QGridLayout()
        metrics_layout.setHorizontalSpacing(12)
        metrics_layout.setVerticalSpacing(12)
        self.metric_values = {}
        metrics = [
            ("total_eleves", "Élèves inscrits", "#8B0000"),
            ("total_du", "Total dû", "#556873"),
            ("total_paye", "Total encaissé", "#28734A"),
            ("total_solde", "Reste à encaisser", "#B86A00"),
        ]
        for index, (key, label_text, accent) in enumerate(metrics):
            card = self._create_metric_card(key, label_text, accent)
            metrics_layout.addWidget(card, 0, index)
            self.metric_values[key] = card.findChild(QLabel, f"metric_{key}")
            metrics_layout.setColumnStretch(index, 1)
        layout.addLayout(metrics_layout)

        collection_panel = QFrame()
        collection_panel.setObjectName("collection_panel")
        collection_panel.setStyleSheet(
            "QFrame#collection_panel { background: #F7F8FA; border: 1px solid #E1E5E9; border-radius: 6px; }"
        )
        collection_layout = QVBoxLayout(collection_panel)
        collection_layout.setContentsMargins(16, 13, 16, 14)
        collection_layout.setSpacing(9)
        collection_header = QHBoxLayout()
        collection_title = QLabel("Progression des encaissements")
        collection_title.setStyleSheet("font-weight: 600; color: #303B40; background: transparent;")
        self.collection_percent = QLabel("0 %")
        self.collection_percent.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #28734A; background: transparent;"
        )
        collection_header.addWidget(collection_title)
        collection_header.addStretch()
        collection_header.addWidget(self.collection_percent)
        collection_layout.addLayout(collection_header)
        self.collection_progress = QProgressBar()
        self.collection_progress.setRange(0, 100)
        self.collection_progress.setTextVisible(False)
        self.collection_progress.setFixedHeight(10)
        self.collection_progress.setStyleSheet(
            "QProgressBar { background: #E4E8E9; border: none; border-radius: 5px; }"
            "QProgressBar::chunk { background: #28734A; border-radius: 5px; }"
        )
        collection_layout.addWidget(self.collection_progress)
        layout.addWidget(collection_panel)

        status_panel = QFrame()
        status_panel.setObjectName("status_panel")
        status_panel.setStyleSheet(
            "QFrame#status_panel { background: #FFFFFF; border: 1px solid #E1E5E9; border-radius: 6px; }"
        )
        status_layout = QHBoxLayout(status_panel)
        status_layout.setContentsMargins(16, 10, 16, 10)
        status_layout.setSpacing(0)
        self.status_values = {}
        for key, label_text, color in [
            ("eleves_soldes", "Soldés", "#28734A"),
            ("eleves_partiellement_payes", "Partiellement payés", "#B86A00"),
            ("eleves_non_payes", "Non payés", "#B43B3B"),
        ]:
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(8, 0, 16, 0)
            item_layout.setSpacing(8)
            value = QLabel("0")
            value.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {color};")
            value.setObjectName(f"status_{key}")
            label = QLabel(label_text)
            label.setStyleSheet("color: #4E5A60;")
            item_layout.addWidget(value)
            item_layout.addWidget(label)
            status_layout.addWidget(item)
            self.status_values[key] = value
        layout.addWidget(status_panel)

        section_header = QHBoxLayout()
        section_title = QLabel("Résultats par classe")
        section_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #303B40;")
        section_header.addWidget(section_title)
        section_header.addStretch()
        self.class_count_label = QLabel("0 classe")
        self.class_count_label.setStyleSheet("font-size: 11px; color: #657078;")
        section_header.addWidget(self.class_count_label)
        layout.addLayout(section_header)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Classe", "Élèves", "Total dû", "Encaissé", "Solde restant"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, self.table.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, 1)

        self.empty_classes_label = QLabel("Aucune classe n'est encore enregistrée.")
        self.empty_classes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_classes_label.setStyleSheet(
            "padding: 24px; color: #657078; background: #F7F8FA; border: 1px solid #E1E5E9;"
        )
        self.empty_classes_label.hide()
        layout.addWidget(self.empty_classes_label)

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #C62828;")
        self.message_label.hide()
        layout.addWidget(self.message_label)

    @staticmethod
    def _create_metric_card(key: str, title: str, accent: str) -> QFrame:
        card = QFrame()
        card.setObjectName("metric_card")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(
            "QFrame#metric_card { background-color: #FFFFFF; "
            f"border: 1px solid #E1E5E9; border-left: 4px solid {accent}; border-radius: 6px; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 12, 12)
        layout.setSpacing(9)
        label = QLabel(title)
        label.setStyleSheet("font-size: 11px; color: #657078; background: transparent;")
        value = QLabel("0")
        value.setObjectName(f"metric_{key}")
        value.setMinimumHeight(26)
        value.setStyleSheet(
            f"font-size: 17px; font-weight: 700; color: {accent}; background: transparent;"
        )
        layout.addWidget(label)
        layout.addWidget(value)
        return card

    def actualiser(self):
        """Recharge les totaux globaux et les résultats par classe."""
        try:
            stats = self.services["statistiques"].obtenir_statistiques_globales()
            devise = self.services["parametre"].lire_parametre("devise") or "FCFA"
            classes = self.services["classe"].lister_classes()
            lignes = [
                (classe.nom, self.services["statistiques"].obtenir_statistiques_par_classe(classe.id))
                for classe in classes
            ]
        except Exception as erreur:
            self.message_label.setText(f"Impossible de charger les statistiques : {erreur}")
            self.message_label.show()
            return

        self.message_label.hide()
        self.actualisation_label.setText(
            f"Actualisé à {datetime.now().strftime('%H:%M')}"
        )
        for key, value_label in self.metric_values.items():
            valeur = stats[key]
            texte = str(valeur) if key == "total_eleves" else formater_montant(valeur, devise)
            value_label.setText(texte)
        for key, value_label in self.status_values.items():
            value_label.setText(str(stats[key]))

        total_du = stats["total_du"]
        total_paye = stats["total_paye"]
        progression = min(100, round(total_paye * 100 / total_du)) if total_du else 0
        self.collection_progress.setValue(progression)
        self.collection_percent.setText(f"{progression} %")

        self.table.setRowCount(len(lignes))
        nombre_classes = len(lignes)
        self.class_count_label.setText(
            f"{nombre_classes} classe" if nombre_classes == 1 else f"{nombre_classes} classes"
        )
        self.table.setVisible(bool(lignes))
        self.empty_classes_label.setVisible(not lignes)
        for row, (nom_classe, valeurs) in enumerate(lignes):
            cells = [
                nom_classe,
                str(valeurs["total_eleves"]),
                formater_montant(valeurs["total_du"], devise),
                formater_montant(valeurs["total_paye"], devise),
                formater_montant(valeurs["total_solde"], devise),
            ]
            for column, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if column:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                self.table.setItem(row, column, item)
