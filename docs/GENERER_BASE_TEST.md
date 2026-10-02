# Comment Générer la Base de Données de Test

Ce document explique comment générer la base de données avec les données de test pour EduPaie.

## Méthode 1 : Via l'application (recommandée pour les utilisateurs)

1. **Lancez l'application** :
   ```bash
   python main.py
   ```

2. **Créez le compte directeur** au premier lancement

3. **Fermez l'application**

4. **Exécutez le script de seed** :
   ```bash
   python scripts/seed_donnees_test.py --reset
   ```

5. **Vérifiez** : le message suivant s'affiche :
   ```
   OK : 4 classes, 20 élèves, 23 paiements chargés dans D:\EduPaie\edupaie.db
   ```

## Méthode 2 : Via le script (développeurs)

Depuis la racine du projet :

```bash
# Premier chargement (refuse si des élèves existent déjà)
python scripts/seed_donnees_test.py

# Rechargement complet (vide puis recharge)
python scripts/seed_donnees_test.py --reset

# Avec un chemin de base personnalisé
python scripts/seed_donnees_test.py --db chemin/vers/edupaie.db
```

## Contenu des Données de Test

### Classes (4)
- 6ème A : 150 000 FCFA
- 5ème B : 175 000 FCFA
- 3ème C : 200 000 FCFA
- Terminale D : 250 000 FCFA

### Élèves (20)
- **5 élèves soldés** : ont payé la totalité
- **8 élèves partiellement payés** : paiements en cours
- **7 élèves non payés** : aucun paiement

### Paiements (23)
- Répartis sur différentes dates (2025-2026)
- Modes variés : espèces, chèque, virement, mobile money
- Numéros de reçu séquentiels : REC-2026-000001 à REC-2026-000023

## Structure du Script

Le script `seed_donnees_test.py` respecte les règles métier :
- Montants en entiers (FCFA)
- Jamais de paiement au-dessus du solde
- Solde après figé au moment du paiement
- Numéros de reçu uniques et séquentiels
- Tout dans une transaction (rollback en cas d'erreur)

## Base de Données Pré-remplie

Une base pré-remplie est disponible : `edupaie_test.db`

Pour l'utiliser :
1. Copiez `edupaie_test.db` vers `edupaie.db`
2. Lancez l'application
3. Les données de test sont déjà présentes

## Vérification

Pour vérifier que les données sont chargées :

1. Lancez l'application
2. Connectez-vous
3. Allez dans la liste des élèves
4. Vous devriez voir 20 élèves répartis dans 4 classes

## Réinitialisation

Pour revenir à une base vide :

```bash
# Supprimez le fichier edupaie.db
rm edupaie.db

# Relancez l'application
python main.py

# La base sera recréée vide
```
