"""
Fenêtre principale de l'application EduPaie.

Ce module définit la QMainWindow avec le bandeau supérieur,
la barre latérale de navigation et le conteneur de pages.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QComboBox,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication

from edupaie.ui.styles import get_stylesheet


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""

    def __init__(self, services):
        """
        Initialise la fenêtre principale.

        Args:
            services: Dictionnaire des services métier
        """
        super().__init__()
        self.services = services
        self.setWindowTitle("EduPaie")
        self.setStyleSheet(get_stylesheet())

        # Adapter la taille à l'écran disponible
        screen = QGuiApplication.primaryScreen()
        available_geo = screen.availableGeometry()
        initial_width = min(1100, available_geo.width())
        initial_height = min(700, available_geo.height())
        self.resize(initial_width, initial_height)

        # Taille minimale adaptée à l'écran (pour petits écrans)
        min_width = min(900, available_geo.width() - 50)
        min_height = min(600, available_geo.height() - 50)
        self.setMinimumSize(min_width, min_height)

        self._setup_ui()
        self._load_etablissement_name()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Barre latérale
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Zone de contenu
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Bandeau supérieur
        self.header = self._create_header()
        content_layout.addWidget(self.header)

        # Conteneur de pages
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        main_layout.addWidget(content_area, stretch=1)

        # Pages
        self._create_pages()

    def _create_header(self) -> QWidget:
        """
        Crée le bandeau supérieur avec le nom de l'établissement.

        Returns:
            QWidget: Bandeau supérieur
        """
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(60)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        self.title_label = QLabel("EduPaie")
        self.title_label.setObjectName("app_title")
        self.title_label.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.title_label)

        layout.addStretch()

        return header

    def _create_sidebar(self) -> QWidget:
        """
        Crée la barre latérale de navigation.

        Returns:
            QWidget: Barre latérale
        """
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(120)
        sidebar.setMaximumWidth(180)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(4)

        # Boutons de navigation
        self.btn_eleves = self._create_nav_button("Élèves", active=True)
        self.btn_paiements = self._create_nav_button("Paiements")
        self.btn_tableau_bord = self._create_nav_button("Tableau de bord")
        self.btn_recus = self._create_nav_button("Reçus")
        self.btn_administration = self._create_nav_button("Administration")
        self.btn_tuteurs = self._create_nav_button("Parents / tuteurs")
        self.btn_classes = self._create_nav_button("Classes et salles")

        layout.addWidget(self.btn_eleves)
        layout.addWidget(self.btn_paiements)
        layout.addWidget(self.btn_tableau_bord)
        layout.addWidget(self.btn_recus)
        layout.addWidget(self.btn_administration)
        layout.addWidget(self.btn_tuteurs)
        layout.addWidget(self.btn_classes)

        layout.addStretch()

        return sidebar

    def _create_nav_button(self, text: str, active: bool = False) -> QPushButton:
        """
        Crée un bouton de navigation.

        Args:
            text: Texte du bouton
            active: Si le bouton est actif

        Returns:
            QPushButton: Bouton de navigation
        """
        button = QPushButton(text)
        button.setObjectName("nav_button")
        if active:
            button.setProperty("active", True)
        return button

    def _create_pages(self):
        """Crée les différentes pages de l'application."""
        # Page Élèves (réelle)
        from edupaie.ui.eleves_view import ElevesView
        self.eleves_page = ElevesView(self.services)
        self.stack.addWidget(self.eleves_page)

        # Page Paiements (choix d'un élève puis dialogue de paiement)
        self.paiements_page = self._create_paiements_page()
        self.stack.addWidget(self.paiements_page)

        # Page de synthèse des paiements et effectifs
        from edupaie.ui.tableau_bord import TableauBord
        self.tableau_bord_page = TableauBord(self.services)
        self.stack.addWidget(self.tableau_bord_page)

        from edupaie.ui.recus_view import RecusView
        self.recus_page = RecusView(self.services)
        self.stack.addWidget(self.recus_page)

        session = self.services.get("session")
        if session and session.autorise("classes.manage"):
            from edupaie.ui.classes_salles_view import ClassesSallesView
            self.classes_salles_page = ClassesSallesView(self.services)
        else:
            self.classes_salles_page = QWidget()
        self.stack.addWidget(self.classes_salles_page)

        if session and session.est_directeur and session.autorise("users.manage"):
            from edupaie.ui.administration_view import AdministrationView
            self.administration_page = AdministrationView(self.services)
        else:
            self.administration_page = QWidget()
        self.stack.addWidget(self.administration_page)

        from edupaie.ui.tuteurs_view import TuteursView
        self.tuteurs_page = TuteursView(self.services)
        self.stack.addWidget(self.tuteurs_page)

        # Connexion des boutons de navigation
        self.navigation = [
            (self.btn_eleves, 0, "students.view", "students"),
            (self.btn_paiements, 1, "payments.view", "payments"),
            (self.btn_tableau_bord, 2, "dashboard.view", "dashboard"),
            (self.btn_recus, 3, "receipts.view", "receipts"),
            (self.btn_classes, 4, "classes.manage", "classes"),
            (self.btn_administration, 5, "users.manage", None),
            (self.btn_tuteurs, 6, "guardians.manage", "guardians"),
        ]
        for button, index, _permission, _feature in self.navigation:
            button.clicked.connect(lambda checked=False, page=index: self._show_page(page))
        self._configurer_navigation()

    def _configurer_navigation(self):
        """Masque les pages non autorisées ou désactivées par le directeur."""
        session = self.services.get("session")
        visible_pages = []
        for button, index, permission, feature in self.navigation:
            autorise = session is not None and session.autorise(permission)
            active = feature is None or self.services["auth"].fonctionnalite_active(feature)
            button.setVisible(autorise and active)
            if autorise and active:
                visible_pages.append(index)
        page_initiale = visible_pages[0] if visible_pages else 0
        self._show_page(page_initiale)

    def _create_placeholder_page(self, title: str) -> QWidget:
        """
        Crée une page placeholder pour les fonctionnalités à venir.

        Args:
            title: Titre de la page

        Returns:
            QWidget: Page placeholder
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(f"{title}\n\nFonctionnalité à venir")
        label.setStyleSheet("font-size: 18px; color: #808080;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        return page

    def _create_paiements_page(self) -> QWidget:
        """
        Crée la page Paiements.

        Cette page permet de choisir un élève puis d'enregistrer un paiement.
        C'est une solution simple : on utilise la liste des élèves existante
        et on ouvre directement le dialogue de paiement.

        Returns:
            QWidget: Page Paiements
        """
        from edupaie.ui.eleves_view import ElevesView

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Titre
        title_label = QLabel("Enregistrer un paiement")
        title_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #8B0000;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Sélectionnez un élève dans la liste ci-dessous, puis cliquez sur \"Fiche / Paiements\" ou double-cliquez pour enregistrer un paiement.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666666;")
        layout.addWidget(desc_label)

        # Réutiliser la vue des élèves
        self.eleves_view_for_paiements = ElevesView(self.services)
        layout.addWidget(self.eleves_view_for_paiements)

        return page

    def _show_page(self, index: int):
        """
        Affiche la page spécifiée.

        Args:
            index: Index de la page à afficher
        """
        # Mettre à jour l'état actif des boutons
        if hasattr(self, "navigation") and not any(
            page == index and not button.isHidden()
            for button, page, _permission, _feature in self.navigation
        ):
            return
        self.stack.setCurrentIndex(index)

        if hasattr(self, "navigation"):
            for button, page, _permission, _feature in self.navigation:
                button.setProperty("active", page == index)
                button.style().unpolish(button)
                button.style().polish(button)

    def _load_etablissement_name(self):
        """Charge le nom de l'établissement depuis les paramètres."""
        try:
            nom = self.services['parametre'].lire_parametre("nom_etablissement")
            if nom:
                self.title_label.setText(nom)
        except Exception:
            # En cas d'erreur, garder le titre par défaut
            pass
