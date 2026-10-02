"""
Styles et thèmes pour l'interface utilisateur.

Ce module définit les constantes de couleurs et la feuille de style QSS
conforme à la charte graphique de l'application.
"""

# Palette originale (rouge/marron)
COULEUR_PRINCIPALE = "#8B0000"       # Rouge foncé principal
COULEUR_ACCENT = "#A52A2A"          # Marron accent
COULEUR_FOND = "#FFFFFF"            # Fond blanc
COULEUR_CARTE = "#FFFFFF"            # Cartes blanches
COULEUR_TEXTE = "#000000"           # Texte principal (noir)
COULEUR_TEXTE_LEGER = "#666666"     # Texte secondaire (gris)
COULEUR_TEXTE_TRES_LEGER = "#999999" # Texte très léger
COULEUR_SOLDE = "#10B981"           # Statut Soldé (vert)
COULEUR_NON_PAYE = "#8B0000"        # Statut Non payé (rouge foncé)
COULEUR_PARTIEL = "#F59E0B"         # Statut Partiellement payé (orange)
COULEUR_SECONDAIRE = "#E0E0E0"      # Gris clair pour boutons secondaires
COULEUR_SIDEBAR_INACTIVE = "#F5F5F5" # Gris très clair pour sidebar inactive


def get_stylesheet() -> str:
    """
    Retourne la feuille de style QSS complète pour l'application.

    Returns:
        str: Feuille de style QSS
    """
    return f"""
    /* === APPLICATION WIDE === */
    QMainWindow {{
        background-color: {COULEUR_FOND};
    }}

    QWidget {{
        background-color: {COULEUR_FOND};
        color: {COULEUR_TEXTE};
        font-family: "Segoe UI", "Arial", sans-serif;
        font-size: 13px;
    }}

    /* === BOUTONS PRINCIPAUX === */
    QPushButton {{
        background-color: {COULEUR_PRINCIPALE};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 600;
        min-width: 80px;
        font-size: 13px;
    }}

    QPushButton:hover {{
        background-color: {COULEUR_ACCENT};
    }}

    QPushButton:pressed {{
        background-color: {COULEUR_PRINCIPALE};
    }}

    QPushButton:disabled {{
        background-color: #E0E0E0;
        color: #999999;
    }}

    /* === BOUTONS SECONDAIRES === */
    QPushButton[secondary="true"] {{
        background-color: {COULEUR_SECONDAIRE};
        color: {COULEUR_TEXTE};
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
    }}

    QPushButton[secondary="true"]:hover {{
        background-color: #D0D0D0;
        border-color: #AAAAAA;
    }}

    /* === BOUTON DÉCONNEXION === */
    QPushButton#btn_deconnexion {{
        background-color: {COULEUR_SECONDAIRE};
        color: {COULEUR_TEXTE};
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
        font-size: 13px;
    }}

    QPushButton#btn_deconnexion:hover {{
        background-color: #D0D0D0;
        border-color: #AAAAAA;
    }}

    /* === BOUTONS DANGEREUX === */
    QPushButton[danger="true"] {{
        background-color: {COULEUR_SECONDAIRE};
        color: {COULEUR_TEXTE};
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
    }}

    QPushButton[danger="true"]:hover {{
        background-color: #D0D0D0;
        border-color: #AAAAAA;
    }}

    /* === TABLEAUX === */
    QTableWidget {{
        background-color: {COULEUR_CARTE};
        border: 1px solid #E0E0E0;
        border-radius: 0px;
        gridline-color: #E0E0E0;
        selection-background-color: {COULEUR_PRINCIPALE};
        selection-color: white;
        alternate-background-color: #FAFAFA;
    }}

    QTableWidget::item {{
        color: {COULEUR_TEXTE};
        padding: 8px 12px;
        border-bottom: 1px solid #E0E0E0;
    }}

    QTableWidget::item:selected {{
        background: {COULEUR_PRINCIPALE};
        color: white;
    }}

    QHeaderView::section {{
        background: {COULEUR_PRINCIPALE};
        color: white;
        padding: 10px 12px;
        border: none;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
        font-weight: 600;
        font-size: 12px;
    }}

    QHeaderView::section:first {{
        border-top-left-radius: 0px;
    }}

    QHeaderView::section:last {{
        border-right: none;
        border-top-right-radius: 0px;
    }}

    /* === BARRE LATÉRALE === */
    QWidget#sidebar {{
        background: {COULEUR_SIDEBAR_INACTIVE};
        border-right: 1px solid #E0E0E0;
    }}

    QPushButton#nav_button {{
        background-color: transparent;
        color: {COULEUR_TEXTE};
        border: none;
        border-radius: 4px;
        padding: 10px 16px;
        text-align: left;
        font-weight: 500;
        font-size: 13px;
    }}

    QPushButton#nav_button:hover {{
        background-color: #E0E0E0;
        color: {COULEUR_TEXTE};
    }}

    QPushButton#nav_button[active="true"] {{
        background: {COULEUR_PRINCIPALE};
        color: white;
        font-weight: 600;
    }}

    /* === BANDEAU SUPÉRIEUR === */
    QWidget#header {{
        background: {COULEUR_PRINCIPALE};
        color: white;
        border-bottom: none;
    }}

    QLabel#app_title {{
        color: white;
        font-size: 18px;
        font-weight: 700;
    }}

    /* === CHAMPS DE SAISIE === */
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QTimeEdit {{
        background-color: {COULEUR_CARTE};
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 8px 12px;
        color: {COULEUR_TEXTE};
        font-size: 13px;
    }}

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QTimeEdit:focus {{
        border: 2px solid {COULEUR_PRINCIPALE};
        background-color: white;
    }}

    QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDateEdit:hover, QTimeEdit:hover {{
        border-color: #AAAAAA;
    }}

    /* === COMBO BOX DROPDOWN === */
    QComboBox QAbstractItemView {{
        background-color: {COULEUR_CARTE};
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        selection-background-color: {COULEUR_PRINCIPALE};
        selection-color: white;
        padding: 8px;
    }}

    /* === LABELS === */
    QLabel {{
        color: {COULEUR_TEXTE};
    }}

    QLabel#section_title {{
        font-size: 16px;
        font-weight: 700;
        color: {COULEUR_PRINCIPALE};
        margin-bottom: 8px;
    }}

    /* === PLACEHOLDERS === */
    QLineEdit::placeholder, QComboBox::placeholder {{
        color: {COULEUR_TEXTE_TRES_LEGER};
    }}

    /* === PASTILLES DE STATUT === */
    QLabel#status_badge {{
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }}

    QLabel#status_badge[solde="true"] {{
        background-color: {COULEUR_SOLDE};
        color: white;
    }}

    QLabel#status_badge[non_paye="true"] {{
        background-color: {COULEUR_NON_PAYE};
        color: white;
    }}

    QLabel#status_badge[partiel="true"] {{
        background-color: {COULEUR_PARTIEL};
        color: white;
    }}

    /* === BADGE NUMÉRO DE LIGNE === */
    QLabel#row_badge {{
        background-color: {COULEUR_PRINCIPALE};
        color: white;
        border-radius: 50%;
        min-width: 24px;
        min-height: 24px;
        font-weight: 600;
        font-size: 12px;
        padding: 0;
    }}

    /* === DIALOGUES === */
    QDialog {{
        background-color: {COULEUR_FOND};
    }}

    QDialogButtonBox QPushButton {{
        min-width: 80px;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 600;
    }}

    /* === ZONES DE CONTENU === */
    QWidget#content_area {{
        background-color: {COULEUR_FOND};
    }}

    QWidget#secondary_area {{
        background-color: {COULEUR_CARTE};
        border-radius: 0px;
        padding: 16px;
        border: 1px solid #E0E0E0;
    }}

    /* === CARTE DE RECHERCHE === */
    QWidget#search_card {{
        background-color: {COULEUR_CARTE};
        border-radius: 0px;
        border: 1px solid #E0E0E0;
        padding: 16px;
    }}

    /* === MESSAGE BOX === */
    QMessageBox {{
        background-color: {COULEUR_CARTE};
    }}

    QMessageBox QPushButton {{
        min-width: 80px;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 600;
    }}

    /* === SCROLLBAR === */
    QScrollBar:vertical {{
        background-color: #F0F0F0;
        width: 12px;
        border-radius: 0px;
    }}

    QScrollBar::handle:vertical {{
        background-color: #CCCCCC;
        border-radius: 0px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: #AAAAAA;
    }}

    QScrollBar:horizontal {{
        background-color: #F0F0F0;
        height: 12px;
        border-radius: 0px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: #CCCCCC;
        border-radius: 0px;
        min-width: 30px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: #AAAAAA;
    }}
    """
