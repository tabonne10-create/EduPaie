"""
Styles et thèmes pour l'interface utilisateur.

Ce module définit les constantes de couleurs et la feuille de style QSS
conforme à la charte graphique de l'application.
"""

# Couleurs de la charte graphique
COULEUR_BORDEAU = "#8B0000"        # Couleur principale (boutons, en-têtes)
COULEUR_DORE = "#D4AF37"          # Couleur d'accent (doré)
COULEUR_FOND = "#FFFFFF"           # Fond principal (blanc)
COULEUR_ZONE_SECONDAIRE = "#F5F6F8"  # Zones secondaires (gris clair)
COULEUR_TEXTE = "#2B2B2B"          # Texte principal (gris foncé)
COULEUR_SOLDE = "#2E7D32"          # Statut Soldé (vert)
COULEUR_NON_PAYE = "#C62828"       # Statut Non payé (rouge)
COULEUR_PARTIEL = "#F57C00"        # Statut Partiellement payé (orange)


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
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 12px;
    }}

    /* === BOUTONS PRINCIPAUX === */
    QPushButton {{
        background-color: {COULEUR_BORDEAU};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        min-width: 80px;
    }}

    QPushButton:hover {{
        background-color: #6B0000;
    }}

    QPushButton:pressed {{
        background-color: #4B0000;
    }}

    QPushButton:disabled {{
        background-color: #B0B0B0;
        color: #606060;
    }}

    /* === BOUTONS SECONDAIRES === */
    QPushButton[secondary="true"] {{
        background-color: {COULEUR_ZONE_SECONDAIRE};
        color: {COULEUR_TEXTE};
        border: 1px solid #D0D0D0;
    }}

    QPushButton[secondary="true"]:hover {{
        background-color: #E5E6E8;
    }}

    /* === TABLEAUX === */
    QTableWidget {{
        background-color: {COULEUR_FOND};
        border: 1px solid #D0D0D0;
        gridline-color: #E0E0E0;
        selection-background-color: {COULEUR_BORDEAU};
        selection-color: white;
    }}

    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid #E0E0E0;
    }}

    QTableWidget::item:selected {{
        background-color: {COULEUR_BORDEAU};
        color: white;
    }}

    QHeaderView::section {{
        background-color: {COULEUR_BORDEAU};
        color: white;
        padding: 10px;
        border: none;
        border-right: 1px solid #6B0000;
        font-weight: 600;
    }}

    QHeaderView::section:first {{
        border-top-left-radius: 4px;
    }}

    QHeaderView::section:last {{
        border-right: none;
        border-top-right-radius: 4px;
    }}

    /* === BARRE LATÉRALE === */
    QWidget#sidebar {{
        background-color: {COULEUR_ZONE_SECONDAIRE};
        border-right: 1px solid #D0D0D0;
    }}

    QPushButton#nav_button {{
        background-color: transparent;
        color: {COULEUR_TEXTE};
        border: none;
        border-radius: 4px;
        padding: 12px 16px;
        text-align: left;
        font-weight: 500;
    }}

    QPushButton#nav_button:hover {{
        background-color: #E5E6E8;
    }}

    QPushButton#nav_button[active="true"] {{
        background-color: {COULEUR_BORDEAU};
        color: white;
        border-bottom: 3px solid {COULEUR_DORE};
    }}

    /* === BANDEAU SUPÉRIEUR === */
    QWidget#header {{
        background-color: {COULEUR_BORDEAU};
        color: white;
        border-bottom: 3px solid {COULEUR_DORE};
    }}

    QLabel#app_title {{
        color: white;
        font-size: 18px;
        font-weight: 700;
    }}

    /* === CHAMPS DE SAISIE === */
    QLineEdit, QComboBox, QSpinBox, QDateEdit {{
        background-color: white;
        border: 1px solid #D0D0D0;
        border-radius: 4px;
        padding: 6px 8px;
    }}

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {{
        border: 2px solid {COULEUR_BORDEAU};
    }}

    /* === LABELS === */
    QLabel {{
        color: {COULEUR_TEXTE};
    }}

    QLabel#section_title {{
        font-size: 16px;
        font-weight: 600;
        color: {COULEUR_BORDEAU};
        margin-bottom: 8px;
    }}

    /* === PASTILLES DE STATUT === */
    QLabel#status_badge {{
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 11px;
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

    /* === DIALOGUES === */
    QDialog {{
        background-color: {COULEUR_FOND};
    }}

    QDialogButtonBox QPushButton {{
        min-width: 80px;
    }}

    /* === ZONES DE CONTENU === */
    QWidget#content_area {{
        background-color: {COULEUR_FOND};
    }}

    QWidget#secondary_area {{
        background-color: {COULEUR_ZONE_SECONDAIRE};
        border-radius: 8px;
        padding: 16px;
    }}

    /* === MESSAGE BOX === */
    QMessageBox {{
        background-color: {COULEUR_FOND};
    }}

    QMessageBox QPushButton {{
        min-width: 80px;
    }}
    """
