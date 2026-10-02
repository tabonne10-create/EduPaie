# Manuel Utilisateur - EduPaie

**Application de gestion des paiements scolaires**

---

## Installation

1. **Prérequis** : Windows 10 ou supérieur
2. **Copier les fichiers** :
   - `EduPaie.exe` (exécutable)
   - `edupaie.db` (base de données)
   - Placer les deux fichiers dans un dossier (ex: `C:\EduPaie\`)
3. **Lancer l'application** : Double-cliquer sur `EduPaie.exe`

---

## Première Connexion

Au premier lancement, créez le compte directeur :

1. **Nom complet** : votre nom (ex: "Jean Dupont")
2. **Identifiant** : votre login (ex: "admin")
3. **Mot de passe** : minimum 10 caractères (ex: "MonMotDePasse123!")

⚠️ **Conservez ces identifiants** : ils serviront pour toutes les connexions futures.

---

## Enregistrer un Élève

1. Cliquez sur **"Élèves"** dans la barre latérale
2. Cliquez sur **"+ Ajouter"**
3. Remplissez le formulaire :
   - **Nom** : nom de famille de l'élève
   - **Prénom** : prénom de l'élève
   - **Classe** : sélectionnez dans la liste
   - **Année scolaire** : pré-remplie automatiquement
   - **Total dû** : montant des frais de scolarité (en FCFA)
4. Cliquez sur **"Enregistrer"**

---

## Enregistrer un Paiement

### Méthode 1 : Via la fiche élève
1. Dans la liste des élèves, double-cliquez sur un élève
2. Cliquez sur **"Nouveau paiement"**
3. Remplissez le formulaire :
   - **Montant à payer** : saisissez le montant (ne peut pas dépasser le solde)
   - **Date** : date du paiement (par défaut : aujourd'hui)
   - **Mode de paiement** : Espèces, Chèque, Virement ou Mobile Money
4. Cliquez sur **"OK"**
5. Un message de succès affiche le **numéro de reçu**

### Méthode 2 : Via le bouton Paiements
1. Cliquez sur **"Paiements"** dans la barre latérale
2. Sélectionnez un élève dans la liste
3. Cliquez sur **"Fiche / Paiements"**
4. Suivez les étapes de la Méthode 1

---

## Imprimer un Reçu

1. Ouvrez la fiche d'un élève (double-clic dans la liste)
2. Cliquez sur **"Voir le reçu"**
3. Le reçu s'ouvre automatiquement en PDF
4. Imprimez-le depuis votre lecteur PDF

**Le reçu contient** :
- Numéro de reçu unique
- Nom et prénom de l'élève
- Classe et année scolaire
- Montant payé
- Date et mode de paiement
- Solde restant après paiement

---

## Consulter le Solde d'un Élève

**Dans la liste des élèves** :
- Colonne **"Solde"** : montant restant à payer
- Colonne **"Statut"** : pastille de couleur
  - 🟢 **Soldé** : tout est payé
  - 🟡 **Partiellement payé** : paiement en cours
  - 🔴 **Non payé** : aucun paiement

**Dans la fiche élève** :
- Section **"Informations financières"** : total dû, total payé, solde
- Tableau **"Historique des paiements"** : tous les paiements chronologiques

---

## Rechercher et Filtrer

**Recherche** :
- Dans la barre "Rechercher un élève", saisissez un nom ou prénom
- La liste se met à jour automatiquement

**Filtre par classe** :
- Sélectionnez une classe dans le menu déroulant
- Seuls les élèves de cette classe s'affichent

**Filtre par statut** :
- Sélectionnez un statut (Soldé, Partiellement payé, Non payé)
- Seuls les élèves correspondants s'affichent

---

## Tableau de Bord

Cliquez sur **"Tableau de bord"** pour voir :
- Nombre total d'élèves
- Total encaissé
- Total restant dû
- Nombre d'élèves non soldés

---

## Déconnexion

Cliquez sur **"Déconnexion"** en haut à droite.

---

## En Cas de Problème

- **Erreur de paiement** : vérifiez que le montant ne dépasse pas le solde
- **Élève introuvable** : vérifiez l'orthographe du nom dans la recherche
- **Base de données corrompue** : contactez l'administrateur système

---

## Support

Pour toute question technique, contactez votre administrateur système ou consultez la documentation technique dans le dossier `docs/`.
