"""
Script pour générer le logo EduPaie avec Pillow.

Ce script crée un logo professionnel avec un icône éducatif
et le texte stylisé "EduPaie".
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_logo(output_path="edupaie_logo.png", size=(400, 120)):
    """
    Crée le logo EduPaie.

    Args:
        output_path: Chemin de sortie du logo
        size: Taille du logo (largeur, hauteur)
    """
    width, height = size

    # Créer une image avec fond transparent
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Couleurs
    primary_red = (139, 0, 0)  # #8B0000
    dark_red = (100, 0, 0)
    accent_gold = (255, 193, 7)
    white = (255, 255, 255)

    # Créer l'icône (livre ouvert stylisé)
    icon_x = 20
    icon_y = 25
    icon_size = 70

    # Fond du livre (couverture gauche)
    draw.polygon([
        (icon_x, icon_y + icon_size // 2),
        (icon_x + icon_size // 2, icon_y + icon_size),
        (icon_x + icon_size // 2, icon_y + icon_size // 2),
        (icon_x, icon_y)
    ], fill=primary_red)

    # Fond du livre (couverture droite)
    draw.polygon([
        (icon_x + icon_size // 2, icon_y + icon_size // 2),
        (icon_x + icon_size, icon_y),
        (icon_x + icon_size, icon_y + icon_size // 2),
        (icon_x + icon_size // 2, icon_y + icon_size)
    ], fill=dark_red)

    # Pages du livre (intérieur)
    draw.polygon([
        (icon_x + 5, icon_y + icon_size // 2),
        (icon_x + icon_size // 2 - 5, icon_y + icon_size - 5),
        (icon_x + icon_size // 2 - 5, icon_y + icon_size // 2 + 5),
        (icon_x + 5, icon_y + 5)
    ], fill=white)

    draw.polygon([
        (icon_x + icon_size // 2 + 5, icon_y + icon_size // 2 + 5),
        (icon_x + icon_size - 5, icon_y + 5),
        (icon_x + icon_size - 5, icon_y + icon_size // 2),
        (icon_x + icon_size // 2 + 5, icon_y + icon_size - 5)
    ], fill=(245, 245, 245))

    # Ligne centrale du livre
    draw.line([
        (icon_x + icon_size // 2, icon_y + icon_size // 2),
        (icon_x + icon_size // 2, icon_y + icon_size)
    ], fill=dark_red, width=2)

    # Petit détail sur le livre (symbole éducation)
    draw.ellipse([
        icon_x + icon_size // 2 - 12,
        icon_y + icon_size // 2 + 15,
        icon_x + icon_size // 2 + 12,
        icon_y + icon_size // 2 + 35
    ], fill=accent_gold)

    # Texte "EduPaie"
    try:
        # Essayer d'utiliser une police système
        font_large = ImageFont.truetype("arial.ttf", 52)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback sur la police par défaut
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    text_x = icon_x + icon_size + 15
    text_y = 35

    # Ombre du texte
    draw.text((text_x + 2, text_y + 2), "EduPaie", font=font_large, fill=(50, 50, 50, 100))

    # Texte principal
    draw.text((text_x, text_y), "EduPaie", font=font_large, fill=primary_red)

    # Tagline
    draw.text((text_x, text_y + 60), "Gestion scolaire", font=font_small, fill=(100, 100, 100))

    # Sauvegarder
    img.save(output_path, "PNG")
    print(f"Logo créé : {output_path}")
    return output_path


def create_logo_square(output_path="edupaie_logo_square.png", size=(128, 128)):
    """
    Crée une version carrée du logo pour les icônes.

    Args:
        output_path: Chemin de sortie
        size: Taille du logo carré
    """
    width, height = size

    # Créer une image avec fond
    img = Image.new("RGBA", (width, height), primary_red := (139, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dessiner un "E" stylisé
    margin = 20
    e_width = width - 2 * margin
    e_height = height - 2 * margin

    # Barre verticale du E
    draw.rectangle([margin, margin, margin + 15, margin + e_height], fill=(255, 255, 255))

    # Barres horizontales du E
    draw.rectangle([margin, margin, margin + e_width, margin + 15], fill=(255, 255, 255))
    draw.rectangle([margin, margin + e_height // 2 - 7, margin + e_width, margin + e_height // 2 + 7], fill=(255, 255, 255))
    draw.rectangle([margin, margin + e_height - 15, margin + e_width, margin + e_height], fill=(255, 255, 255))

    # Sauvegarder
    img.save(output_path, "PNG")
    print(f"Logo carré créé : {output_path}")
    return output_path


def create_logo_favicon(output_path="edupaie_favicon.ico", size=(32, 32)):
    """
    Crée un favicon pour le navigateur.

    Args:
        output_path: Chemin de sortie
        size: Taille du favicon
    """
    width, height = size

    # Créer une image
    img = Image.new("RGBA", (width, height), (139, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dessiner un "E" simplifié
    margin = 4
    e_width = width - 2 * margin
    e_height = height - 2 * margin

    # Barre verticale
    draw.rectangle([margin, margin, margin + 4, margin + e_height], fill=(255, 255, 255))

    # Barres horizontales
    draw.rectangle([margin, margin, margin + e_width, margin + 4], fill=(255, 255, 255))
    draw.rectangle([margin, margin + e_height // 2 - 2, margin + e_width, margin + e_height // 2 + 2], fill=(255, 255, 255))
    draw.rectangle([margin, margin + e_height - 4, margin + e_width, margin + e_height], fill=(255, 255, 255))

    # Sauvegarder en ICO
    img.save(output_path, "ICO")
    print(f"Favicon créé : {output_path}")
    return output_path


if __name__ == "__main__":
    # Créer le dossier assets s'il n'existe pas
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Générer les différents formats
    print("Génération du logo EduPaie...")
    create_logo(os.path.join(assets_dir, "edupaie_logo.png"))
    create_logo_square(os.path.join(assets_dir, "edupaie_logo_square.png"))
    create_logo_favicon(os.path.join(assets_dir, "edupaie_favicon.ico"))

    print("\nTous les logos ont été créés dans le dossier 'assets/'")
