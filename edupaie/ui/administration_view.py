"""Gestion des comptes, permissions et fonctionnalités par le directeur."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from edupaie.database.connection import readonly_connection


class AdministrationView(QWidget):
    """Interface locale d'administration réservée au directeur."""

    def __init__(self, services):
        super().__init__()
        self.services = services
        self.auth = services["auth"]
        self._setup_ui()
        self.actualiser()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Administration")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #5F1015;")
        subtitle = QLabel("Comptes, permissions, affectations et options EduPaie")
        subtitle.setStyleSheet("color: #657078;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._creer_onglet_utilisateurs(), "Utilisateurs")
        self.tabs.addTab(self._creer_onglet_permissions(), "Rôles et permissions")
        self.tabs.addTab(self._creer_onglet_fonctionnalites(), "Fonctionnalités")
        layout.addWidget(self.tabs, 1)

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #B43B3B;")
        layout.addWidget(self.message_label)

    def _creer_onglet_utilisateurs(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        form = QFormLayout()
        self.nom_input = QLineEdit()
        self.identifiant_input = QLineEdit()
        self.mot_de_passe_input = QLineEdit()
        self.mot_de_passe_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.mot_de_passe_input.setPlaceholderText("10 caractères minimum")
        self.role_combo = QComboBox()
        self.classes_list = QListWidget()
        self.classes_list.setMaximumHeight(100)
        form.addRow("Nom complet", self.nom_input)
        form.addRow("Identifiant", self.identifiant_input)
        form.addRow("Mot de passe provisoire", self.mot_de_passe_input)
        form.addRow("Rôle initial", self.role_combo)
        form.addRow("Classes (enseignants)", self.classes_list)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.btn_creer_utilisateur = QPushButton("Créer l'utilisateur")
        self.btn_creer_utilisateur.clicked.connect(self._creer_utilisateur)
        actions.addWidget(self.btn_creer_utilisateur)
        self.utilisateur_role_combo = QComboBox()
        actions.addWidget(self.utilisateur_role_combo)
        self.btn_affecter_role = QPushButton("Attribuer au sélectionné")
        self.btn_affecter_role.clicked.connect(self._affecter_role)
        actions.addWidget(self.btn_affecter_role)
        self.btn_affecter_classes = QPushButton("Enregistrer les classes cochées")
        self.btn_affecter_classes.clicked.connect(self._affecter_classes)
        actions.addWidget(self.btn_affecter_classes)
        self.btn_activer_utilisateur = QPushButton("Activer / désactiver")
        self.btn_activer_utilisateur.clicked.connect(self._basculer_utilisateur)
        actions.addWidget(self.btn_activer_utilisateur)
        layout.addLayout(actions)

        self.utilisateurs_table = QTableWidget(0, 4)
        self.utilisateurs_table.setHorizontalHeaderLabels(
            ["Nom", "Identifiant", "Rôle(s)", "État"]
        )
        self.utilisateurs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.utilisateurs_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.utilisateurs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.utilisateurs_table.itemSelectionChanged.connect(self._charger_selection_utilisateur)
        self.utilisateurs_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.utilisateurs_table, 1)
        return page

    def _creer_onglet_permissions(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QHBoxLayout()
        self.role_permission_combo = QComboBox()
        self.role_permission_combo.currentIndexChanged.connect(self._charger_permissions)
        header.addWidget(QLabel("Modifier le rôle :"))
        header.addWidget(self.role_permission_combo, 1)
        self.btn_nouveau_role = QPushButton("Créer un rôle")
        self.btn_nouveau_role.clicked.connect(self._creer_role)
        header.addWidget(self.btn_nouveau_role)
        layout.addLayout(header)

        aide = QLabel("Les modifications s'appliquent aux utilisateurs de ce rôle à leur prochaine connexion.")
        aide.setWordWrap(True)
        aide.setStyleSheet("color: #657078;")
        layout.addWidget(aide)

        self.permissions_table = QTableWidget(0, 2)
        self.permissions_table.setHorizontalHeaderLabels(["Permission", "Accordée"])
        self.permissions_table.horizontalHeader().setStretchLastSection(True)
        self.permissions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.permissions_table.itemChanged.connect(self._permission_modifiee)
        layout.addWidget(self.permissions_table, 1)
        return page

    def _creer_onglet_fonctionnalites(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        aide = QLabel("Désactive temporairement une section sans supprimer ses données.")
        aide.setWordWrap(True)
        aide.setStyleSheet("color: #657078;")
        layout.addWidget(aide)
        self.features_layout = QVBoxLayout()
        layout.addLayout(self.features_layout)
        layout.addStretch()
        return page

    def actualiser(self):
        """Recharge les listes depuis les services d'administration."""
        try:
            roles = self.auth.lister_roles()
            self._roles = list(roles)
            for combo in (self.role_combo, self.utilisateur_role_combo, self.role_permission_combo):
                combo.blockSignals(True)
                combo.clear()
                for role in self._roles:
                    combo.addItem(role["nom"], role["code"])
                combo.blockSignals(False)

            classes = self.services["classe"].lister_classes()
            self.classes_list.clear()
            for classe in classes:
                item = QListWidgetItem(classe.nom)
                item.setData(Qt.ItemDataRole.UserRole, classe.id)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.classes_list.addItem(item)

            utilisateurs = self.auth.lister_utilisateurs()
            self.utilisateurs_table.setRowCount(len(utilisateurs))
            self._utilisateurs = {row["id"]: row for row in utilisateurs}
            for index, utilisateur in enumerate(utilisateurs):
                values = [
                    utilisateur["nom_complet"],
                    utilisateur["identifiant"],
                    utilisateur["roles"] or "Aucun rôle",
                    "Actif" if utilisateur["actif"] else "Désactivé",
                ]
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if column == 0:
                        item.setData(Qt.ItemDataRole.UserRole, utilisateur["id"])
                    self.utilisateurs_table.setItem(index, column, item)

            self.role_permission_combo.setCurrentIndex(0)
            self._charger_fonctionnalites()
            self.message_label.clear()
        except Exception as erreur:
            self.message_label.setText(f"Impossible de charger l'administration : {erreur}")

    def _creer_utilisateur(self):
        classes = [
            self.classes_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.classes_list.count())
            if self.classes_list.item(i).checkState() == Qt.CheckState.Checked
        ]
        try:
            self.auth.creer_utilisateur(
                self.nom_input.text(),
                self.identifiant_input.text(),
                self.mot_de_passe_input.text(),
                self.role_combo.currentData(),
                classes,
            )
            self.nom_input.clear()
            self.identifiant_input.clear()
            self.mot_de_passe_input.clear()
            self.actualiser()
        except Exception as erreur:
            self.message_label.setText(str(erreur))

    def _affecter_role(self):
        utilisateur_id = self._utilisateur_selectionne()
        role_code = self.utilisateur_role_combo.currentData()
        if utilisateur_id is None or role_code is None:
            return
        try:
            row = self._utilisateurs[utilisateur_id]
            roles_courants = [role["code"] for role in self._roles if role["nom"] in (row["roles"] or "").split(", ")]
            if role_code not in roles_courants:
                roles_courants.append(role_code)
            self.auth.modifier_roles_utilisateur(utilisateur_id, roles_courants)
            self.actualiser()
        except Exception as erreur:
            self.message_label.setText(str(erreur))

    def _basculer_utilisateur(self):
        utilisateur_id = self._utilisateur_selectionne()
        if utilisateur_id is None:
            return
        try:
            actif = not bool(self._utilisateurs[utilisateur_id]["actif"])
            self.auth.definir_role_actif(utilisateur_id, actif)
            self.actualiser()
        except Exception as erreur:
            self.message_label.setText(str(erreur))

    def _affecter_classes(self):
        utilisateur_id = self._utilisateur_selectionne()
        if utilisateur_id is None:
            return
        classe_ids = [
            self.classes_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.classes_list.count())
            if self.classes_list.item(i).checkState() == Qt.CheckState.Checked
        ]
        try:
            self.auth.definir_classes_utilisateur(utilisateur_id, classe_ids)
            self.message_label.setText("Affectations de classes enregistrées.")
        except Exception as erreur:
            self.message_label.setText(str(erreur))

    def _charger_selection_utilisateur(self):
        utilisateur_id = self._utilisateur_selectionne()
        if utilisateur_id is None:
            return
        with readonly_connection() as conn:
            affectations = {
                row[0] for row in conn.execute(
                    "SELECT classe_id FROM utilisateur_classes WHERE utilisateur_id = ?",
                    (utilisateur_id,),
                )
            }
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            item.setCheckState(
                Qt.CheckState.Checked
                if item.data(Qt.ItemDataRole.UserRole) in affectations
                else Qt.CheckState.Unchecked
            )

    def _utilisateur_selectionne(self):
        row = self.utilisateurs_table.currentRow()
        if row < 0:
            return None
        return self.utilisateurs_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _charger_permissions(self, _index=None):
        role_code = self.role_permission_combo.currentData()
        if not role_code:
            return
        self.permissions_table.blockSignals(True)
        permissions = self.auth.lister_permissions(role_code)
        self.permissions_table.setRowCount(len(permissions))
        for row, permission in enumerate(permissions):
            label = QTableWidgetItem(permission["libelle"])
            label.setData(Qt.ItemDataRole.UserRole, permission["code"])
            self.permissions_table.setItem(row, 0, label)
            checkbox = QTableWidgetItem()
            checkbox.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
            )
            checkbox.setCheckState(
                Qt.CheckState.Checked if permission["active"] else Qt.CheckState.Unchecked
            )
            if role_code == "directeur":
                checkbox.setFlags(checkbox.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.permissions_table.setItem(row, 1, checkbox)
        self.permissions_table.blockSignals(False)

    def _permission_modifiee(self, item):
        if item.column() != 1:
            return
        role_code = self.role_permission_combo.currentData()
        permission_code = self.permissions_table.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
        try:
            self.auth.definir_permission_role(
                role_code,
                permission_code,
                item.checkState() == Qt.CheckState.Checked,
            )
        except Exception as erreur:
            self.message_label.setText(str(erreur))
            self._charger_permissions()

    def _creer_role(self):
        nom, ok = QInputDialog.getText(self, "Nouveau rôle", "Nom du rôle :")
        if not ok or not nom.strip():
            return
        try:
            code = self.auth.creer_role(nom)
            self.actualiser()
            index = self.role_permission_combo.findData(code)
            self.role_permission_combo.setCurrentIndex(index)
        except Exception as erreur:
            self.message_label.setText(str(erreur))

    def _charger_fonctionnalites(self):
        while self.features_layout.count():
            item = self.features_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for feature in self.auth.lister_fonctionnalites():
            checkbox = QCheckBox(feature["nom"])
            checkbox.setChecked(bool(feature["active"]))
            checkbox.stateChanged.connect(
                lambda state, code=feature["code"]: self.auth.definir_fonctionnalite(
                    code, state == int(Qt.CheckState.Checked)
                )
            )
            self.features_layout.addWidget(checkbox)
