# Guide d'Installation - EduPaie

**Version 1.0 - Application Windows autonome**

---

## Prérequis

- **Système** : Windows 10 ou Windows 11
- **Espace disque** : ~200 Mo pour l'application
- **Droits** : Aucun droit administrateur requis

---

## Installation

### Étape 1 : Télécharger les fichiers

Téléchargez le dossier compressé contenant :
- `EduPaie.exe` (exécutable principal)
- `edupaie.db` (base de données pré-remplie avec données de test)
- `docs/` (documentation optionnelle)

### Étape 2 : Extraire les fichiers

1. Créez un dossier sur votre ordinateur (ex: `C:\Programmes\EduPaie\` ou `C:\EduPaie\`)
2. Extrayez le contenu du dossier compressé dans ce dossier
3. Vérifiez que vous avez les fichiers suivants :
   ```
   EduPaie/
   ├── EduPaie.exe
   ├── edupaie.db
   └── docs/ (optionnel)
       ├── MANUEL_UTILISATEUR.md
       └── GUIDE_INSTALLATION.md
   ```

### Étape 3 : Lancer l'application

Double-cliquez sur `EduPaie.exe`

**Au premier lancement** :
- L'application créera automatiquement la base de données si elle n'existe pas
- Un assistant de création de compte directeur s'affichera

---

## Premier Démarrage

### Création du compte directeur

1. Remplissez le formulaire :
   - **Nom complet** : votre nom complet
   - **Identifiant** : votre identifiant de connexion (minimum 3 caractères)
   - **Mot de passe** : votre mot de passe (minimum 10 caractères)

2. Cliquez sur **"Créer le compte"**

⚠️ **Important** : Conservez ces identifiants en lieu sûr. Ils serviront pour toutes les connexions futures.

### Connexion

1. Saisissez votre identifiant
2. Saisissez votre mot de passe
3. Cliquez sur **"Se connecter"**

---

## Chargement des Données de Test (Optionnel)

Si vous souhaitez utiliser le jeu de données de test (20 élèves, paiements variés) :

### Méthode 1 : Via la base pré-remplie
- Si vous avez reçu le fichier `edupaie.db` pré-rempli, aucune action n'est requise
- Les données de test sont déjà présentes

### Méthode 2 : Via le script (développeurs uniquement)
- Ouvrez une invite de commande dans le dossier d'installation
- Exécutez : `python scripts/seed_donnees_test.py --reset`
- Cela chargera 20 élèves avec des paiements variés

---

## Structure des Dossiers

Après installation, la structure sera :

```
EduPaie/
├── EduPaie.exe          # Exécutable principal
├── edupaie.db           # Base de données (créée au premier lancement)
├── edupaie.db-journal   # Fichier temporaire SQLite (normal)
└── docs/                # Documentation (optionnel)
    ├── MANUEL_UTILISATEUR.md
    ├── GUIDE_INSTALLATION.md
    └── SCHEMA_BASE_DONNEES.md
```

---

## Mise à Jour

Pour mettre à jour l'application :

1. **Sauvegardez votre base de données** :
   - Copiez `edupaie.db` dans un dossier de sauvegarde
   - Cela préserve vos données (élèves, paiements, utilisateurs)

2. **Remplacez l'exécutable** :
   - Supprimez l'ancien `EduPaie.exe`
   - Copiez le nouveau `EduPaie.exe`

3. **Relancez l'application** :
   - La base de données sera automatiquement migrée si nécessaire

---

## Désinstallation

Pour désinstaller EduPaie :

1. **Sauvegardez vos données** (si nécessaire) :
   - Copiez `edupaie.db` dans un dossier de sauvegarde

2. **Supprimez le dossier d'installation** :
   - Supprimez le dossier `EduPaie/` et tout son contenu

3. **Nettoyage optionnel** :
   - Supprimez le raccourci du Bureau (si créé)
   - Aucune entrée dans le Registre Windows n'est créée

---

## Dépannage

### L'application ne se lance pas

**Cause possible** : Antivirus bloquant l'exécutable
- **Solution** : Ajoutez `EduPaie.exe` aux exceptions de votre antivirus

**Cause possible** : Windows Defender SmartScreen
- **Solution** : Cliquez sur "Plus d'informations" → "Exécuter quand même"

### Erreur "Base de données introuvable"

**Cause possible** : Fichier `edupaie.db` manquant
- **Solution** : Lancez l'application une première fois pour créer la base automatiquement

### Erreur "Permission refusée"

**Cause possible** : Dossier en lecture seule
- **Solution** : Vérifiez les permissions du dossier d'installation

### L'application est lente

**Cause possible** : Base de données volumineuse
- **Solution** : Archivez les anciennes années scolaires (fonctionnalité future)

---

## Sauvegarde des Données

### Sauvegarde manuelle

1. Fermez l'application EduPaie
2. Copiez le fichier `edupaie.db` dans un dossier de sauvegarde
3. Conservez plusieurs versions (quotidiennes, hebdomadaires)

### Restauration

1. Fermez l'application EduPaie
2. Copiez le fichier `edupaie.db` sauvegardé dans le dossier d'installation
3. Remplacez le fichier existant
4. Relancez l'application

---

## Support Technique

Pour toute question ou problème :

1. Consultez le **Manuel Utilisateur** (`docs/MANUEL_UTILISATEUR.md`)
2. Consultez la **Documentation Technique** (`docs/DOCUMENTATION_TECHNIQUE.md`)
3. Contactez votre administrateur système

---

## Informations Complémentaires

- **Version** : 1.0
- **Développeur** : Abdou-Akim GBADAMASSI
- **Langage** : Python 3.10+
- **Interface** : PySide6 (Qt for Python)
- **Base de données** : SQLite
- **Licence** : Usage éducatif uniquement

---

## Notes de Version

### Version 1.0 (2026)
- Première version stable
- Gestion complète des élèves et paiements
- Génération de reçus PDF
- Tableau de bord
- Système d'authentification et permissions
- 20 élèves de test pré-chargés
