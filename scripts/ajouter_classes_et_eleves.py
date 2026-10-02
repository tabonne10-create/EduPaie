"""
Script pour ajouter les classes de la 6eme au lycee avec 30 eleves chacune.

Classes a creer :
- College : 6eme, 5eme, 4eme, 3eme
- Lycee : Seconde (Moderne, Technique), Premiere (Moderne, Technique), Terminale (Moderne, Technique)
"""

import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edupaie.services.classe_service import ClasseService
from edupaie.services.eleve_service import EleveService
from edupaie.database.repositories.classe_repository import ClasseRepository
from edupaie.database.repositories.eleve_repository import EleveRepository
from edupaie.database.transaction import transaction
from edupaie.database.connection import readonly_connection
import random


# Liste des noms et prénoms africains francophones pour générer des élèves
NOMS = [
    "Kouassi", "Yao", "Koffi", "Konan", "Kouamé", "Adou", "Aka", "Assamoi",
    "Brou", "Coulibaly", "Diomandé", "Djédjé", "Fofana", "Gbakou", "Kouadio",
    "N'Goran", "N'Dri", "Ouattara", "Séri", "Touré", "Yao", "Zouzoua",
    "M'bodji", "Ndiaye", "Diop", "Fall", "Diagne", "Ba", "Sow", "Kane",
    "Diallo", "Sylla", "Camara", "Cissé", "Keita", "Traoré", "Koné", "Diarra",
    "Dembélé", "Sangaré", "Konaté", "Fofana", "Bamba", "Sékou", "Ouedraogo",
    "Kaboré", "Zongo", "Sawadogo", "Yameogo", "Ouatara", "Compaoré", "Sanou"
]

PRENOMS_HOMMES = [
    "Jean", "Pierre", "Paul", "Jacques", "Emmanuel", "Christian", "Eric",
    "Patrick", "David", "Samuel", "Daniel", "Marc", "Philippe", "Michel",
    "Sébastien", "Nicolas", "Alexandre", "Thomas", "Antoine", "Julien",
    "Christophe", "Frédéric", "Guillaume", "Mathieu", "Romain", "Grégoire",
    "Kouamé", "Yao", "Koffi", "Adama", "Ibrahim", "Moussa", "Ousmane",
    "Abdoulaye", "Cheick", "Amadou", "Boubacar", "Ismail", "Souleymane"
]

PRENOMS_FEMMES = [
    "Marie", "Christine", "Sophie", "Julie", "Céline", "Valérie", "Isabelle",
    "Caroline", "Sandrine", "Nathalie", "Catherine", "Elodie", "Aurélie",
    "Camille", "Charlotte", "Claire", "Chloé", "Justine", "Marion", "Pauline",
    "Sarah", "Estelle", "Vanessa", "Adèle", "Josiane", "Aïcha", "Fatoumata",
    "Aminata", "Mariam", "Fatima", "Awa", "Rokiatou", " assetou", "Affoué"
]


def generer_eleve(numero: int, classe_id: int, annee_scolaire: str) -> tuple:
    """
    Génère un élève aléatoire.

    Args:
        numero: Numéro de l'élève dans la classe
        classe_id: ID de la classe
        annee_scolaire: Année scolaire

    Returns:
        tuple (nom, prenom, classe_id, annee_scolaire, total_du)
    """
    nom = random.choice(NOMS)
    sexe = random.choice(['H', 'F'])
    if sexe == 'H':
        prenom = random.choice(PRENOMS_HOMMES)
    else:
        prenom = random.choice(PRENOMS_FEMMES)

    # Total dû aléatoire entre 50000 et 150000 FCFA
    total_du = random.randint(50000, 150000)

    return (nom, prenom, classe_id, annee_scolaire, total_du)


def creer_classes_et_eleves():
    """Crée les classes et les élèves."""

    # Définition des classes à créer
    classes_a_creer = [
        # Collège
        "6ème",
        "5ème",
        "4ème",
        "3ème",
        # Lycée - Seconde
        "Seconde Moderne",
        "Seconde Technique",
        # Lycée - Première
        "Première Moderne",
        "Première Technique",
        # Lycée - Terminale
        "Terminale Moderne",
        "Terminale Technique",
    ]

    annee_scolaire = "2025-2026"
    eleves_par_classe = 30

    print("=== Création des classes et des élèves ===\n")

    # Vérifier les classes existantes
    with readonly_connection() as conn:
        repo = ClasseRepository(conn)
        classes_existantes = repo.lister()
        noms_classes_existantes = {c.nom for c in classes_existantes}

    print(f"Classes existantes : {len(classes_existantes)}")
    for classe in classes_existantes:
        print(f"  - {classe.nom}")

    # Creer les classes
    classe_service = ClasseService()
    eleve_service = EleveService()

    classes_crees = []
    for nom_classe in classes_a_creer:
        if nom_classe in noms_classes_existantes:
            print(f"\n[ATTENTION] La classe '{nom_classe}' existe deja, elle sera ignoree.")
            # Recuperer l'ID de la classe existante
            with readonly_connection() as conn:
                repo = ClasseRepository(conn)
                classe = repo.trouver_par_nom(nom_classe)
                if classe:
                    classes_crees.append((classe.id, nom_classe))
            continue

        try:
            classe = classe_service.creer_classe(nom_classe, capacite=30)
            classes_crees.append((classe.id, nom_classe))
            print(f"[OK] Classe cree : {nom_classe} (ID: {classe.id})")
        except Exception as e:
            print(f"[ERREUR] Erreur lors de la creation de la classe {nom_classe} : {e}")

    # Créer les élèves
    total_eleves_crees = 0
    for classe_id, nom_classe in classes_crees:
        print(f"\n--- Création des élèves pour {nom_classe} ---")

        # Compter les élèves existants dans cette classe
        with readonly_connection() as conn:
            repo = ClasseRepository(conn)
            nb_eleves_existants = repo.compter_eleves(classe_id)

        if nb_eleves_existants >= eleves_par_classe:
            print(f"[ATTENTION] La classe {nom_classe} a deja {nb_eleves_existants} eleves (>= {eleves_par_classe})")
            continue

        eleves_a_creer = eleves_par_classe - nb_eleves_existants
        print(f"Création de {eleves_a_creer} élèves (existant: {nb_eleves_existants})")

        for i in range(eleves_a_creer):
            try:
                nom, prenom, classe_id, annee_scolaire, total_du = generer_eleve(
                    i + nb_eleves_existants + 1, classe_id, annee_scolaire
                )
                eleve = eleve_service.creer_eleve(
                    nom=nom,
                    prenom=prenom,
                    classe_id=classe_id,
                    annee_scolaire=annee_scolaire,
                    total_du=total_du
                )
                total_eleves_crees += 1
                if (i + 1) % 10 == 0:
                    print(f"  {i + 1}/{eleves_a_creer} eleves crees...")
            except Exception as e:
                print(f"[ERREUR] Erreur lors de la creation de l'eleve {i+1} : {e}")

    print(f"\n=== Resume ===")
    print(f"Classes creees : {len(classes_crees)}")
    print(f"Eleves crees : {total_eleves_crees}")

    # Afficher le total des eleves dans la base
    with readonly_connection() as conn:
        repo = EleveRepository(conn)
        total_eleves_db = len(repo.lister_avec_totaux())
        print(f"Total des eleves dans la base : {total_eleves_db}")


if __name__ == "__main__":
    creer_classes_et_eleves()
