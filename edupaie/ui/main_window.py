"""
Fenêtre principale de l'application EduPaie.

Ce module définit la QMainWindow avec le bandeau supérieur,
la barre latérale de navigation et le conteneur de pages.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget
)
from PySide6.QtCore import Qt

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
        self.resize(1000, 700)
        self.setStyleSheet(get_stylesheet())

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

        title_label = QLabel("EduPaie")
        title_label.setObjectName("app_title")
        layout.addWidget(title_label)

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
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(4)

        # Boutons de navigation
        self.btn_eleves = self._create_nav_button("Élèves", active=True)
        self.btn_paiements = self._create_nav_button("Paiements")
        self.btn_tableau_bord = self._create_nav_button("Tableau de bord")
        self.btn_recus = self._create_nav_button("Reçus")

        layout.addWidget(self.btn_eleves)
        layout.addWidget(self.btn_paiements)
        layout.addWidget(self.btn_tableau_bord)
        layout.addWidget(self.btn_recus)

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

        # Pages "à venir" (placeholders)
        self.paiements_page = self._create_placeholder_page("Paiements")
        self.stack.addWidget(self.paiements_page)

        self.tableau_bord_page = self._create_placeholder_page("Tableau de bord")
        self.stack.addWidget(self.tableau_bord_page)

        self.recus_page = self._create_placeholder_page("Reçus")
        self.stack.addWidget(self.recus_page)

        # Connexion des boutons de navigation
        self.btn_eleves.clicked.connect(lambda: self._show_page(0))
        self.btn_paiements.clicked.connect(lambda: self._show_page(1))
        self.btn_tableau_bord.clicked.connect(lambda: self._show_page(2))
        self.btn_recus.clicked.connect(lambda: self._show_page(3))

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

    def _show_page(self, index: int):
        """
        Affiche la page spécifiée.

        Args:
            index: Index de la page à afficher
        """
        self.stack.setCurrentIndex(index)

        # Mettre à jour l'état actif des boutons
        buttons = [self.btn_eleves, self.btn_paiements, self.btn_tableau_bord, self.btn_recus]
        for i, button in enumerate(buttons):
            if i == index:
                button.setProperty("active", True)
            else:
                button.setProperty("active", False)
            button.style().unpolish(button)
            button.style().polish(button)

    def _load_etablissement_name(self):
        """Charge le nom de l'établissement depuis les paramètres."""
        try:
            nom = self.services['parametre'].lire("nom_etablissement")
            if nom:
                title_label = self.header.findChild(QLabel, "app_title")
                title_label.setText(nom)
        except Exception:
            # En cas d'erreur, garder le titre par défaut
            pass
