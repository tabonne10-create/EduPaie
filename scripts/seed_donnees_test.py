"""
Jeu de données de test pour EduPaie (20 élèves, 4 classes, paiements variés).

Utilisation (depuis la racine du projet, base déjà créée par un lancement
de l'application) :
    python scripts/seed_donnees_test.py            # refuse si des élèves existent
    python scripts/seed_donnees_test.py --reset    # vide classes/élèves/paiements puis recharge
    python scripts/seed_donnees_test.py --db chemin/vers/edupaie.db

Ce script est un OUTIL de développement, il ne fait pas partie des 3 couches
de l'application. Il écrit directement en SQL et respecte les mêmes règles :
- montants en entiers (FCFA), jamais de paiement au-dessus du solde ;
- solde_apres figé au moment du paiement ;
- numéros de reçu PREFIXE-AAAA-000001 séquentiels (ordre chronologique) ;
- compteur_recus mis à jour ;
- tout dans UNE transaction : en cas d'erreur, rien n'est écrit.
"""
import argparse
import os
import sqlite3
import sys

ANNEE_RECU = 2026          # année civile d'émission des reçus de test
ANNEE_SCOLAIRE = "2025-2026"

# (nom de classe, frais de scolarité en FCFA)
CLASSES = [
    ("6ème A", 150000),
    ("5ème B", 175000),
    ("3ème C", 200000),
    ("Terminale D", 250000),
]

# (nom, prénom, classe, [(montant, date ISO, mode), ...])
# Dates : toutes dans le passé (pas de date future).
ELEVES = [
    # 6ème A : 150 000
    ("Kodjo", "Afi", "6ème A", [(100000, "2025-09-15", "especes"), (50000, "2025-12-10", "mobile_money")]),   # soldé
    ("O'Brien", "Patrick", "6ème A", [(50000, "2025-10-02", "cheque")]),                                      # partiel (apostrophe)
    ("Mensah", "Yawo", "6ème A", []),                                                                         # non payé
    ("Agbodjan", "Esso", "6ème A", [(75000, "2025-09-20", "virement"), (25000, "2026-01-14", "especes")]),    # partiel
    ("Amouzou", "Kossi", "6ème A", [(150000, "2026-01-08", "especes")]),                                      # soldé
    # 5ème B : 175 000
    ("Dossou", "Ama", "5ème B", [(175000, "2025-09-10", "virement")]),                                        # soldé
    ("Lawson", "Komlan", "5ème B", [(60000, "2025-10-11", "mobile_money"), (60000, "2026-02-03", "mobile_money")]),  # partiel
    ("Adjovi", "Mawuli", "5ème B", []),                                                                       # non payé
    ("Aziaha", "Elom", "5ème B", [(100000, "2025-11-05", "especes")]),                                        # partiel
    ("Sanvee", "Dela", "5ème B", [(75000, "2025-09-12", "especes"), (50000, "2025-11-20", "especes"), (50000, "2026-03-05", "cheque")]),  # soldé
    # 3ème C : 200 000
    ("Tsogbe", "Koffi", "3ème C", [(200000, "2025-09-08", "cheque")]),                                        # soldé
    ("Ahlin", "Sena", "3ème C", [(120000, "2025-10-15", "virement")]),                                        # partiel
    ("Quashie", "Edem", "3ème C", []),                                                                        # non payé
    ("Bakoma", "Fiona", "3ème C", [(50000, "2025-12-01", "mobile_money"), (50000, "2026-04-02", "mobile_money"), (50000, "2026-06-10", "especes")]),  # partiel
    ("Kpogo", "Yao", "3ème C", [(150000, "2025-09-25", "especes"), (50000, "2026-01-20", "mobile_money")]),   # soldé
    # Terminale D : 250 000
    ("Houenou", "Mawuena", "Terminale D", [(250000, "2025-09-05", "virement")]),                              # soldé
    ("Attiogbé", "Kafui", "Terminale D", [(125000, "2025-10-30", "especes")]),                                # partiel
    ("Folly", "Dzifa", "Terminale D", []),                                                                    # non payé
    ("Eklou", "Selom", "Terminale D", [(30000, "2026-02-14", "mobile_money")]),                               # partiel
    ("Zotchi", "Agbéko", "Terminale D", []),                                                                  # non payé
]


def chemin_base_par_defaut():
    """Utilise le même chemin que l'application (utils/paths.py)."""
    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, racine)
    from edupaie.utils.paths import get_database_path
    return get_database_path()


def verifier(conn):
    """Contrôles de cohérence avant d'écrire quoi que ce soit."""
    frais = dict(CLASSES)
    for nom, prenom, classe, paiements in ELEVES:
        if classe not in frais:
            raise ValueError(f"Classe inconnue pour {nom} : {classe}")
        total = sum(m for m, _, _ in paiements)
        if total > frais[classe]:
            raise ValueError(f"{nom} {prenom} : paiements ({total}) > total dû ({frais[classe]})")
        for m, d, mode in paiements:
            if m <= 0:
                raise ValueError(f"{nom} : montant invalide {m}")
            if d > "2026-09-30":
                raise ValueError(f"{nom} : date dans le futur {d}")
            if mode not in ("especes", "cheque", "virement", "mobile_money"):
                raise ValueError(f"{nom} : mode invalide {mode}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="chemin de la base SQLite")
    parser.add_argument("--reset", action="store_true", help="vide les données avant de recharger")
    args = parser.parse_args()

    db_path = args.db or chemin_base_par_defaut()
    if not os.path.exists(db_path):
        sys.exit(f"Base introuvable : {db_path}\nLance d'abord l'application une fois (python main.py).")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        verifier(conn)
        existe = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='classes'"
        ).fetchone()
        if not existe:
            sys.exit("La base n'a pas de tables : lance d'abord python main.py.")

        nb = conn.execute("SELECT COUNT(*) FROM eleves").fetchone()[0]
        if nb > 0 and not args.reset:
            sys.exit(f"{nb} élève(s) déjà présents. Utilise --reset pour tout remplacer.")

        conn.execute("BEGIN")
        if args.reset:
            conn.execute("DELETE FROM paiements")
            conn.execute("DELETE FROM eleves")
            conn.execute("DELETE FROM classes")
            conn.execute("DELETE FROM compteur_recus")

        # Préfixe de reçu lu dans les paramètres (rien d'établissement en dur)
        ligne = conn.execute("SELECT valeur FROM parametres WHERE cle = 'prefixe_recu'").fetchone()
        prefixe = ligne[0] if ligne and ligne[0] else "REC"

        # Classes
        ids_classes = {}
        frais = dict(CLASSES)
        for nom_classe, _ in CLASSES:
            cur = conn.execute("INSERT INTO classes (nom) VALUES (?)", (nom_classe,))
            ids_classes[nom_classe] = cur.lastrowid

        # Élèves
        eleves_ids = []
        for nom, prenom, classe, paiements in ELEVES:
            cur = conn.execute(
                "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
                "VALUES (?, ?, ?, ?, ?)",
                (nom, prenom, ids_classes[classe], ANNEE_SCOLAIRE, frais[classe]),
            )
            eleves_ids.append((cur.lastrowid, frais[classe], paiements))

        # Paiements, dans l'ordre chronologique global pour des numéros de reçu cohérents
        a_inserer = []
        for eleve_id, total_du, paiements in eleves_ids:
            for montant, date_p, mode in paiements:
                a_inserer.append((date_p, eleve_id, total_du, montant, mode))
        a_inserer.sort(key=lambda p: (p[0], p[1]))

        deja_paye = {}
        numero = 0
        for date_p, eleve_id, total_du, montant, mode in a_inserer:
            numero += 1
            paye = deja_paye.get(eleve_id, 0) + montant
            deja_paye[eleve_id] = paye
            solde_apres = total_du - paye          # jamais négatif (vérifié plus haut)
            numero_recu = f"{prefixe}-{ANNEE_RECU}-{numero:06d}"
            conn.execute(
                "INSERT INTO paiements (eleve_id, montant, date_paiement, mode, "
                "numero_recu, solde_apres, cree_le) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (eleve_id, montant, date_p, mode, numero_recu, solde_apres, f"{date_p} 09:00:00"),
            )

        conn.execute(
            "INSERT OR REPLACE INTO compteur_recus (annee, dernier_numero) VALUES (?, ?)",
            (ANNEE_RECU, numero),
        )
        conn.execute("COMMIT")
        print(f"OK : {len(CLASSES)} classes, {len(ELEVES)} élèves, {numero} paiements chargés dans {db_path}")
    except Exception as e:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        sys.exit(f"Échec, rien n'a été écrit : {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
