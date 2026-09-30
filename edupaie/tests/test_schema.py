"""
Tests du schéma de la base de données.

Ces tests vérifient que les contraintes du schéma sont correctement appliquées.
"""

import unittest
import sqlite3
import os
import tempfile


class TestSchema(unittest.TestCase):
    """Tests de validation du schéma de la base de données."""
    
    def setUp(self):
        """Crée une base de données temporaire pour chaque test."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.conn = sqlite3.connect(self.db_path, isolation_level="", timeout=10)
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
        self.conn.execute("BEGIN")
        self.conn.executescript(schema_sql)
        self.conn.execute("COMMIT")
    
    def tearDown(self):
        """Ferme la connexion et supprime la base temporaire."""
        self.conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_base_creee(self):
        """Vérifie que la base est créée avec toutes les tables."""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row['name'] for row in cursor.fetchall()]
        
        self.assertIn('parametres', tables)
        self.assertIn('classes', tables)
        self.assertIn('eleves', tables)
        self.assertIn('paiements', tables)
        self.assertIn('compteur_recus', tables)
    
    def test_parametres_par_defaut(self):
        """Vérifie que les paramètres par défaut existent après création."""
        cursor = self.conn.execute("SELECT cle, valeur FROM parametres")
        parametres = {row['cle']: row['valeur'] for row in cursor.fetchall()}
        
        self.assertEqual(parametres['nom_etablissement'], 'Mon Établissement')
        self.assertEqual(parametres['devise'], 'FCFA')
        self.assertEqual(parametres['prefixe_recu'], 'REC')
        self.assertEqual(parametres['annee_scolaire_courante'], '2025-2026')
    
    def test_montant_paiement_positif(self):
        """Vérifie qu'un paiement avec montant <= 0 est refusé (CHECK)."""
        # Créer une classe et un élève
        self.conn.execute("INSERT INTO classes (nom) VALUES ('6ème A')")
        self.conn.execute(
            "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
            "VALUES ('Dupont', 'Jean', 1, '2025-2026', 150000)"
        )
        self.conn.commit()
        
        # Tentative d'insertion avec montant négatif
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO paiements "
                "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
                "VALUES (1, -1000, '2025-09-30', 'especes', 'REC-2025-000001', 149000)"
            )
        
        # Tentative d'insertion avec montant nul
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO paiements "
                "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
                "VALUES (1, 0, '2025-09-30', 'especes', 'REC-2025-000001', 150000)"
            )
    
    def test_mode_paiement_valide(self):
        """Vérifie qu'un mode de paiement invalide est refusé (CHECK)."""
        # Créer une classe et un élève
        self.conn.execute("INSERT INTO classes (nom) VALUES ('6ème A')")
        self.conn.execute(
            "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
            "VALUES ('Dupont', 'Jean', 1, '2025-2026', 150000)"
        )
        self.conn.commit()
        
        # Tentative d'insertion avec mode invalide
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO paiements "
                "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
                "VALUES (1, 50000, '2025-09-30', 'carte', 'REC-2025-000001', 100000)"
            )
    
    def test_numero_recu_unique(self):
        """Vérifie que deux paiements avec le même numéro de reçu sont refusés (UNIQUE)."""
        # Créer une classe et un élève
        self.conn.execute("INSERT INTO classes (nom) VALUES ('6ème A')")
        self.conn.execute(
            "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
            "VALUES ('Dupont', 'Jean', 1, '2025-2026', 150000)"
        )
        self.conn.commit()
        
        # Premier paiement
        self.conn.execute(
            "INSERT INTO paiements "
            "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
            "VALUES (1, 50000, '2025-09-30', 'especes', 'REC-2025-000001', 100000)"
        )
        self.conn.commit()
        
        # Tentative de deuxième paiement avec même numéro
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO paiements "
                "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
                "VALUES (1, 50000, '2025-10-01', 'cheque', 'REC-2025-000001', 50000)"
            )
    
    def test_suppression_eleve_cascade_paiements(self):
        """Vérifie que supprimer un élève supprime ses paiements (CASCADE)."""
        # Créer une classe, un élève et des paiements
        self.conn.execute("INSERT INTO classes (nom) VALUES ('6ème A')")
        self.conn.execute(
            "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
            "VALUES ('Dupont', 'Jean', 1, '2025-2026', 150000)"
        )
        self.conn.execute(
            "INSERT INTO paiements "
            "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
            "VALUES (1, 50000, '2025-09-30', 'especes', 'REC-2025-000001', 100000)"
        )
        self.conn.execute(
            "INSERT INTO paiements "
            "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
            "VALUES (1, 50000, '2025-10-01', 'cheque', 'REC-2025-000002', 50000)"
        )
        self.conn.commit()
        
        # Vérifier qu'il y a 2 paiements
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM paiements")
        self.assertEqual(cursor.fetchone()['count'], 2)
        
        # Supprimer l'élève
        self.conn.execute("DELETE FROM eleves WHERE id = 1")
        self.conn.commit()
        
        # Vérifier que les paiements sont supprimés
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM paiements")
        self.assertEqual(cursor.fetchone()['count'], 0)
    
    def test_total_du_non_negatif(self):
        """Vérifie que total_du ne peut pas être négatif (CHECK)."""
        # Créer une classe
        self.conn.execute("INSERT INTO classes (nom) VALUES ('6ème A')")
        self.conn.commit()
        
        # Tentative d'insertion avec total_du négatif
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
                "VALUES ('Dupont', 'Jean', 1, '2025-2026', -1000)"
            )
    
    def test_date_paiement_valide(self):
        """Vérifie qu'une date invalide est refusée (CHECK)."""
        # Créer une classe et un élève
        self.conn.execute("INSERT INTO classes (nom) VALUES ('6ème A')")
        self.conn.execute(
            "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
            "VALUES ('Dupont', 'Jean', 1, '2025-2026', 150000)"
        )
        self.conn.commit()
        
        # Tentative d'insertion avec date invalide
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO paiements "
                "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
                "VALUES (1, 50000, '30/09/2025', 'especes', 'REC-2025-000001', 100000)"
            )
        
        # Tentative d'insertion avec date vide
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO paiements "
                "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
                "VALUES (1, 50000, '', 'especes', 'REC-2025-000001', 100000)"
            )
    
    def test_nom_non_vide(self):
        """Vérifie qu'un nom vide est refusé (CHECK)."""
        # Tentative d'insertion de classe avec nom vide
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO classes (nom) VALUES ('')")
        
        # Tentative d'insertion de classe avec nom composé d'espaces
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO classes (nom) VALUES ('   ')")
        
        # Créer une classe valide
        self.conn.execute("INSERT INTO classes (nom) VALUES ('6ème A')")
        self.conn.commit()
        
        # Tentative d'insertion d'élève avec nom vide
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
                "VALUES ('', 'Jean', 1, '2025-2026', 150000)"
            )
        
        # Tentative d'insertion d'élève avec prénom vide
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
                "VALUES ('Dupont', '', 1, '2025-2026', 150000)"
            )
    
    def test_solde_apres_non_negatif(self):
        """Vérifie que solde_apres ne peut pas être négatif (CHECK)."""
        # Créer une classe et un élève
        self.conn.execute("INSERT INTO classes (nom) VALUES ('6ème A')")
        self.conn.execute(
            "INSERT INTO eleves (nom, prenom, classe_id, annee_scolaire, total_du) "
            "VALUES ('Dupont', 'Jean', 1, '2025-2026', 150000)"
        )
        self.conn.commit()
        
        # Tentative d'insertion avec solde_apres négatif
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO paiements "
                "(eleve_id, montant, date_paiement, mode, numero_recu, solde_apres) "
                "VALUES (1, 50000, '2025-09-30', 'especes', 'REC-2025-000001', -1000)"
            )


if __name__ == '__main__':
    unittest.main()
