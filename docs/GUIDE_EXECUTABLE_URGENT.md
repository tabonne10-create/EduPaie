# Guide de Génération de l'Exécutable Windows - URGENT

⚠️ **IMPORTANT** : Ce livrable est OBLIGATOIRE pour la soutenance (critère d'évaluation).

## Pourquoi maintenant ?

- L'exécutable Windows est mentionné dans le brief comme livrable obligatoire
- La configuration PyInstaller est prête (`edupaie.spec`)
- Il manque seulement l'étape de génération

## Problème actuel

❌ **Pas d'espace disque** pour installer PyInstaller et générer l'exécutable

## Solution : Faire sur une autre machine

### Option 1 : Sur un autre ordinateur avec Python

1. **Copiez le dossier EduPaie** sur une clé USB
2. **Sur l'autre ordinateur** :
   ```bash
   # Installer Python 3.10+ si pas installé
   # Installer les dépendances
   pip install -r requirements.txt
   pip install pyinstaller
   
   # Générer l'exécutable
   pyinstaller edupaie.spec
   ```
3. **Copiez le dossier `dist/`** sur votre clé USB
4. **Sur votre ordinateur** : Collez `dist/EduPaie.exe` dans votre dossier

### Option 2 : Nettoyer l'espace disque d'abord

1. **Videz la corbeille**
2. **Supprimez les fichiers temporaires** :
   ```bash
   # Windows
   %temp%
   # Supprimez tout dans ce dossier
   ```
3. **Supprimez les anciennes versions Python** (si présentes)
4. **Réessayez l'installation** :
   ```bash
   pip install pyinstaller
   pyinstaller edupaie.spec
   ```

### Option 3 : Utiliser un espace disque externe

1. **Connectez un disque dur externe**
2. **Changez le répertoire temporaire** :
   ```bash
   set TEMP=E:\Temp
   set TMP=E:\Temp
   mkdir E:\Temp
   ```
3. **Installez PyInstaller** :
   ```bash
   pip install pyinstaller --target E:\PythonPackages
   ```

## Procédure Complète (Quand vous avez de l'espace)

### Étape 1 : Vérifier l'espace disque

```bash
# Windows
dir C:
```

Il faut au moins **500 Mo** d'espace libre.

### Étape 2 : Installer PyInstaller

```bash
pip install pyinstaller
```

### Étape 3 : Vérifier que la base de données existe

```bash
# Dans le dossier EduPaie
dir edupaie.db
```

Si le fichier n'existe pas :
```bash
python main.py
# Créez le compte, fermez l'application
python scripts/seed_donnees_test.py --reset
```

### Étape 4 : Générer l'exécutable

```bash
pyinstaller edupaie.spec
```

Cela va créer :
- `build/` (fichiers temporaires)
- `dist/EduPaie.exe` (l'exécutable final)

### Étape 5 : Tester l'exécutable

```bash
# Double-cliquez sur dist/EduPaie.exe
# Vérifiez que l'application se lance
```

### Étape 6 : Préparer le package de distribution

1. Créez un dossier `EduPaie_Final/`
2. Copiez dedans :
   ```
   EduPaie_Final/
   ├── EduPaie.exe
   ├── edupaie.db
   └── docs/
       ├── MANUEL_UTILISATEUR.md
       ├── GUIDE_INSTALLATION.md
       └── MAQUETTES.md
   ```
3. Compressez en ZIP

### Étape 7 : Tester sur une machine propre (OPTIONNEL mais RECOMMANDÉ)

Si possible, testez sur une machine sans Python :
- Extrayez le ZIP
- Lancez `EduPaie.exe`
- Vérifiez que tout fonctionne

## Fichier de Configuration (edupaie.spec)

Le fichier `edupaie.spec` est déjà configuré avec :
- ✅ Mode GUI (sans console)
- ✅ Icône de l'application
- ✅ Inclusion du schéma SQL
- ✅ Inclusion des assets (logo)
- ✅ Modules cachés (PySide6, ReportLab)
- ✅ Exclusion des modules inutiles (tkinter, matplotlib)

## Taille attendue

L'exécutable pèsera environ **150-200 Mo** car :
- PySide6 (~100 Mo)
- ReportLab (~30 Mo)
- Python runtime (~50 Mo)

## Dépannage

### Erreur "No space left on device"
- **Solution** : Libérez de l'espace disque (voir Option 2)

### Erreur "ModuleNotFoundError"
- **Solution** : Le module est dans les hiddenimports du .spec
- Vérifiez le fichier `edupaie.spec`

### Erreur "Fichier non trouvé"
- **Solution** : Vérifiez les chemins dans `edupaie.spec`
- Les chemins doivent être absolus

### Exécutable bloqué par l'antivirus
- **Solution** : Ajoutez `EduPaie.exe` aux exceptions
- C'est un faux positif courant

## Alternative : Utiliser un service cloud

Si vous n'avez pas d'autre ordinateur :
1. Uploadez le dossier EduPaie sur GitHub/GitLab
2. Utilisez GitHub Actions pour générer l'exécutable automatiquement
3. Téléchargez l'artifacts généré

## Livrable Final pour la Soutenance

Vous devez avoir :
- ✅ `EduPaie.exe` (l'exécutable)
- ✅ `edupaie.db` (base de données avec données de test)
- ✅ `GUIDE_INSTALLATION.md` (comment installer)
- ✅ `MANUEL_UTILISATEUR.md` (comment utiliser)

## Note d'Évaluation

Sans l'exécutable : **-5 points** sur la note finale (critère "Livrables")

Avec l'exécutable : **Note complète**

## Urgence

⚠️ **Faites cette génération AVANT la soutenance**

- Temps estimé : 15-30 minutes
- Nécessite : 500 Mo d'espace disque
- Alternative : Utiliser un autre ordinateur

---

## Résumé Rapide

```bash
# 1. Libérez de l'espace disque (500 Mo minimum)

# 2. Installez PyInstaller
pip install pyinstaller

# 3. Générez l'exécutable
pyinstaller edupaie.spec

# 4. Testez
dist\EduPaie.exe

# 5. Préparez le package
# Copiez EduPaie.exe + edupaie.db + docs/ dans un dossier
# Compressez en ZIP
```

**C'est tout !** L'exécutable sera prêt pour la soutenance.
