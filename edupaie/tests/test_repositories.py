"""
Tests des repositories.
"""

import unittest
import sqlite3
import os
import tempfile
from edupaie.database.connection import get_connection
from edupaie.database.repositories.classe_repository import ClasseRepository
from edupaie.database.repositories.eleve_repository import EleveRepository
from edupaie.database.repositories.paiement_repository import PaiementRepository
from edupaie.database.repositories.compteur_recus_repository import CompteurRecusRepository
from edupaie.database.repositories.parametre_repository import ParametreRepository
from edupaie.database.repositories.statistiques_repository import StatistiquesRepository
from edupaie.database.errors import (
    ClasseRepositoryError, EleveRepositoryError, PaiementRepositoryError
)


class TestRepositories(unittest.TestCase):
    """Tests de validation des repositories."""
    
    def setUp(self):
        """Crée une base de données temporaire pour chaque test."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

        # Exécuter le schéma
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'database',
            'schema.sql'
        )
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        self.conn.executescript(schema_sql)
        self.conn.commit()

    def tearDown(self):
        """Ferme la connexion et supprime la base temporaire."""
        self.conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_classe_crud(self):
        """Teste CRUD complet sur une classe."""
        repo = ClasseRepository(self.conn)
        
        # Créer
        classe = repo.creer("6ème A")
        self.conn.commit()
        self.assertIsNotNone(classe.id)
        self.assertEqual(classe.nom, "6ème A")
        
        # Lire
        trouvee = repo.trouver_par_id(classe.id)
        self.assertEqual(trouvee.nom, "6ème A")
        
        # Modifier
        repo.modifier(classe.id, "6ème B")
        self.conn.commit()
        modifiee = repo.trouver_par_id(classe.id)
        self.assertEqual(modifiee.nom, "6ème B")
        
        # Supprimer
        repo.supprimer(classe.id)
        self.conn.commit()
        self.assertIsNone(repo.trouver_par_id(classe.id))
    
    def test_eleve_crud(self):
        """Teste CRUD complet sur un élève."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        
        # Créer une classe
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        
        # Créer un élève
        eleve = eleve_repo.creer(
            "Dupont", "Jean", classe.id, "2025-2026", 150000
        )
        self.conn.commit()
        self.assertIsNotNone(eleve.id)
        self.assertEqual(eleve.nom, "Dupont")
        
        # Lire
        trouve = eleve_repo.trouver_par_id(eleve.id)
        self.assertEqual(trouve.nom, "Dupont")
        
        # Modifier
        eleve_repo.modifier(
            eleve.id, "Martin", "Paul", classe.id, "2025-2026", 200000
        )
        self.conn.commit()
        modifie = eleve_repo.trouver_par_id(eleve.id)
        self.assertEqual(modifie.nom, "Martin")
        self.assertEqual(modifie.total_du, 200000)
        
        # Supprimer
        eleve_repo.supprimer(eleve.id)
        self.conn.commit()
        self.assertIsNone(eleve_repo.trouver_par_id(eleve.id))
    
    def test_lister_avec_totaux_sans_paiement(self):
        """Teste qu'un élève sans paiement a total_paye = 0."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        eleve = eleve_repo.creer(
            "Dupont", "Jean", classe.id, "2025-2026", 150000
        )
        self.conn.commit()
        
        liste = eleve_repo.lister_avec_totaux()
        self.assertEqual(len(liste), 1)
        self.assertEqual(liste[0].total_paye, 0)
        self.assertEqual(liste[0].nom_classe, "6ème A")
    
    def test_lister_avec_totaux_avec_paiement(self):
        """Teste le calcul de total_paye avec des paiements."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        paiement_repo = PaiementRepository(self.conn)
        
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        eleve = eleve_repo.creer(
            "Dupont", "Jean", classe.id, "2025-2026", 150000
        )
        self.conn.commit()
        
        # Ajouter des paiements
        paiement_repo.inserer(
            eleve.id, 50000, "2025-09-30", "especes", "REC-2025-000001", 100000
        )
        self.conn.commit()
        paiement_repo.inserer(
            eleve.id, 30000, "2025-10-01", "cheque", "REC-2025-000002", 70000
        )
        self.conn.commit()
        
        liste = eleve_repo.lister_avec_totaux()
        self.assertEqual(len(liste), 1)
        self.assertEqual(liste[0].total_paye, 80000)
    
    def test_lister_avec_totaux_recherche(self):
        """Teste le filtrage par recherche (nom/prénom)."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        eleve_repo.creer("Dupont", "Jean", classe.id, "2025-2026", 150000)
        eleve_repo.creer("Martin", "Paul", classe.id, "2025-2026", 150000)
        eleve_repo.creer("Dupont", "Marie", classe.id, "2025-2026", 150000)
        self.conn.commit()
        
        # Recherche par nom
        resultats = eleve_repo.lister_avec_totaux(recherche="Dupont")
        self.assertEqual(len(resultats), 2)
        
        # Recherche par prénom
        resultats = eleve_repo.lister_avec_totaux(recherche="Paul")
        self.assertEqual(len(resultats), 1)
    
    def test_lister_avec_totaux_filtre_classe(self):
        """Teste le filtrage par classe."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        
        classe1 = classe_repo.creer("6ème A")
        classe2 = classe_repo.creer("6ème B")
        self.conn.commit()
        
        eleve_repo.creer("Dupont", "Jean", classe1.id, "2025-2026", 150000)
        eleve_repo.creer("Martin", "Paul", classe1.id, "2025-2026", 150000)
        eleve_repo.creer("Durand", "Marie", classe2.id, "2025-2026", 150000)
        self.conn.commit()
        
        resultats = eleve_repo.lister_avec_totaux(classe_id=classe1.id)
        self.assertEqual(len(resultats), 2)
        
        resultats = eleve_repo.lister_avec_totaux(classe_id=classe2.id)
        self.assertEqual(len(resultats), 1)
    
    def test_supprimer_eleve_supprime_paiements(self):
        """Teste que supprimer un élève supprime ses paiements."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        paiement_repo = PaiementRepository(self.conn)
        
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        eleve = eleve_repo.creer(
            "Dupont", "Jean", classe.id, "2025-2026", 150000
        )
        self.conn.commit()
        
        # Ajouter des paiements
        paiement_repo.inserer(
            eleve.id, 50000, "2025-09-30", "especes", "REC-2025-000001", 100000
        )
        self.conn.commit()
        paiement_repo.inserer(
            eleve.id, 30000, "2025-10-01", "cheque", "REC-2025-000002", 70000
        )
        self.conn.commit()
        
        # Vérifier que les paiements existent
        self.assertEqual(len(paiement_repo.lister_par_eleve(eleve.id)), 2)
        
        # Supprimer l'élève
        eleve_repo.supprimer(eleve.id)
        self.conn.commit()
        
        # Vérifier que les paiements sont supprimés
        self.assertEqual(len(paiement_repo.lister_par_eleve(eleve.id)), 0)
    
    def test_supprimer_classe_avec_eleves_leve_erreur(self):
        """Teste que supprimer une classe avec des élèves lève une erreur."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        eleve_repo.creer("Dupont", "Jean", classe.id, "2025-2026", 150000)
        self.conn.commit()
        
        with self.assertRaises(ClasseRepositoryError) as context:
            classe_repo.supprimer(classe.id)
        
        self.assertIn("élèves", str(context.exception).lower())
    
    def test_paiement_meme_numero_recu(self):
        """Teste que deux paiements avec le même numéro de reçu échouent."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        paiement_repo = PaiementRepository(self.conn)
        
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        eleve = eleve_repo.creer(
            "Dupont", "Jean", classe.id, "2025-2026", 150000
        )
        self.conn.commit()
        
        # Premier paiement
        paiement_repo.inserer(
            eleve.id, 50000, "2025-09-30", "especes", "REC-2025-000001", 100000
        )
        self.conn.commit()
        
        # Deuxième paiement avec même numéro
        with self.assertRaises(PaiementRepositoryError):
            paiement_repo.inserer(
                eleve.id, 30000, "2025-10-01", "cheque", "REC-2025-000001", 70000
            )
    
    def test_lister_par_eleve_ordre_chronologique(self):
        """Teste que lister_par_eleve respecte l'ordre chronologique."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        paiement_repo = PaiementRepository(self.conn)
        
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        eleve = eleve_repo.creer(
            "Dupont", "Jean", classe.id, "2025-2026", 150000
        )
        self.conn.commit()
        
        # Ajouter des paiements dans le désordre
        paiement_repo.inserer(
            eleve.id, 30000, "2025-10-01", "cheque", "REC-2025-000002", 70000
        )
        self.conn.commit()
        paiement_repo.inserer(
            eleve.id, 50000, "2025-09-30", "especes", "REC-2025-000001", 100000
        )
        self.conn.commit()
        
        paiements = paiement_repo.lister_par_eleve(eleve.id)
        self.assertEqual(len(paiements), 2)
        self.assertEqual(paiements[0].date_paiement, "2025-09-30")
        self.assertEqual(paiements[1].date_paiement, "2025-10-01")
    
    def test_parametres_lire_ecrire(self):
        """Teste la lecture et écriture des paramètres."""
        repo = ParametreRepository(self.conn)
        
        # Lire un paramètre existant
        nom = repo.lire("nom_etablissement")
        self.assertEqual(nom, "Mon Établissement")
        
        # Modifier un paramètre
        repo.ecrire("nom_etablissement", "Nouveau Nom")
        self.conn.commit()
        nom = repo.lire("nom_etablissement")
        self.assertEqual(nom, "Nouveau Nom")
        
        # Créer un nouveau paramètre
        repo.ecrire("nouveau_param", "valeur")
        self.conn.commit()
        valeur = repo.lire("nouveau_param")
        self.assertEqual(valeur, "valeur")
        
        # Lire tous
        tous = repo.lire_tous()
        self.assertIn("nom_etablissement", tous)
        self.assertIn("nouveau_param", tous)
    
    def test_requete_avec_apostrophe(self):
        """Teste qu'une requête avec une apostrophe dans le nom ne casse rien."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        eleve = eleve_repo.creer(
            "O'Brien", "Jean", classe.id, "2025-2026", 150000
        )
        self.conn.commit()
        
        # Vérifier que l'élève est créé
        trouve = eleve_repo.trouver_par_id(eleve.id)
        self.assertEqual(trouve.nom, "O'Brien")
        
        # Vérifier que la recherche fonctionne
        resultats = eleve_repo.lister_avec_totaux(recherche="O'Brien")
        self.assertEqual(len(resultats), 1)
    
    def test_compteur_recus(self):
        """Teste le compteur de reçus."""
        repo = CompteurRecusRepository(self.conn)
        
        # Première année
        num1 = repo.incrementer(2025)
        self.conn.commit()
        self.assertEqual(num1, 1)
        
        num2 = repo.incrementer(2025)
        self.conn.commit()
        self.assertEqual(num2, 2)
        
        # Nouvelle année
        num3 = repo.incrementer(2026)
        self.conn.commit()
        self.assertEqual(num3, 1)
        
        # Lecture
        dernier = repo.lire_dernier(2025)
        self.assertEqual(dernier, 2)
    
    def test_statistiques_globales(self):
        """Teste le calcul des statistiques globales."""
        classe_repo = ClasseRepository(self.conn)
        eleve_repo = EleveRepository(self.conn)
        paiement_repo = PaiementRepository(self.conn)
        stats_repo = StatistiquesRepository(self.conn)
        
        classe = classe_repo.creer("6ème A")
        self.conn.commit()
        eleve1 = eleve_repo.creer(
            "Dupont", "Jean", classe.id, "2025-2026", 150000
        )
        eleve2 = eleve_repo.creer(
            "Martin", "Paul", classe.id, "2025-2026", 200000
        )
        self.conn.commit()
        
        paiement_repo.inserer(
            eleve1.id, 50000, "2025-09-30", "especes", "REC-2025-000001", 100000
        )
        self.conn.commit()
        paiement_repo.inserer(
            eleve2.id, 100000, "2025-10-01", "cheque", "REC-2025-000002", 100000
        )
        self.conn.commit()
        
        stats = stats_repo.totaux_globaux()
        self.assertEqual(stats['nombre_eleves'], 2)
        self.assertEqual(stats['total_du'], 350000)
        self.assertEqual(stats['total_encaisse'], 150000)


if __name__ == '__main__':
    unittest.main()
