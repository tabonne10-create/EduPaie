# Comment Générer l'Exécutable Windows

Ce document explique comment générer l'exécutable EduPaie.exe avec PyInstaller.

## Prérequis

1. **Python 3.10+** installé
2. **PyInstaller** installé :
   ```bash
   pip install pyinstaller
   ```

## Procédure

### Étape 1 : Installer PyInstaller

```bash
pip install pyinstaller
```

Si l'installation échoue avec une erreur "fichier utilisé par un autre processus" :
- Fermez toutes les applications Python
- Réessayez l'installation
- Ou redémarrez votre ordinateur

### Étape 2 : Générer la base de données de test

```bash
# Lancer l'application une première fois pour créer la base
python main.py

# Créer le compte directeur, puis fermez l'application

# Charger les données de test
python scripts/seed_donnees_test.py --reset
```

### Étape 3 : Générer l'exécutable

Depuis la racine du projet :

```bash
pyinstaller edupaie.spec
```

Cela créera :
- Un dossier `build/` (fichiers temporaires, peut être supprimé)
- Un dossier `dist/` contenant `EduPaie.exe`

### Étape 4 : Préparer le package de distribution

1. Créez un dossier `EduPaie_Package/`
2. Copiez les fichiers suivants dans ce dossier :
   ```
   EduPaie_Package/
   ├── EduPaie.exe           (depuis dist/)
   ├── edupaie.db            (base de données avec données de test)
   └── docs/                 (documentation)
       ├── MANUEL_UTILISATEUR.md
       ├── GUIDE_INSTALLATION.md
       ├── SCHEMA_BASE_DONNEES.md
       └── GENERER_BASE_TEST.md
   ```

3. Compressez le dossier `EduPaie_Package/` en ZIP

### Étape 5 : Tester l'exécutable

Sur une machine Windows propre (sans Python installé) :

1. Extrayez le ZIP
2. Double-cliquez sur `EduPaie.exe`
3. Vérifiez que l'application se lance correctement
4. Testez les fonctionnalités principales :
   - Création d'un élève
   - Enregistrement d'un paiement
   - Génération d'un reçu PDF

## Configuration PyInstaller (.spec)

Le fichier `edupaie.spec` contient la configuration :

- **Mode GUI** : pas de console (`console=False`)
- **Icône** : `assets/edupaie_favicon.ico`
- **Données incluses** :
  - `edupaie/database/schema.sql`
  - `assets/` (images)
- **Modules cachés** : PySide6, ReportLab, etc.
- **Exclusions** : tkinter, matplotlib, numpy (pour réduire la taille)

## Taille de l'exécutable

L'exécutable pèsera environ **150-200 Mo** car :
- PySide6 est une bibliothèque complète
- ReportLab inclut les polices et moteurs PDF
- Python runtime est inclus

## Problèmes Courants

### Erreur "ModuleNotFoundError"

**Cause** : Module manquant dans les hiddenimports

**Solution** : Ajoutez le module dans `edupaie.spec` :
```python
hiddenimports=[
    'module_manquant',
    # ...
]
```

### Erreur "Fichier non trouvé"

**Cause** : Chemin relatif incorrect dans les datas

**Solution** : Vérifiez les chemins dans `edupaie.spec` :
```python
datas=[
    (str(root_dir / 'chemin/vers/fichier'), 'destination'),
]
```

### Exécutable bloqué par l'antivirus

**Cause** : Faux positif de l'antivirus

**Solution** :
- Ajoutez `EduPaie.exe` aux exceptions
- Signez l'exécutable (optionnel, certificat requis)

## Alternative : Commande simple

Si vous préférez une commande simple (sans fichier .spec) :

```bash
pyinstaller --onefile --windowed --add-data "edupaie/database/schema.sql;." --add-data "assets;assets" --icon=assets/edupaie_favicon.ico --name=EduPaie main.py
```

Cependant, le fichier `.spec` est recommandé pour :
- Une configuration réutilisable
- Un meilleur contrôle des options
- Une maintenance plus facile

## Nettoyage

Après génération, vous pouvez supprimer le dossier `build/` :

```bash
# Windows
rmdir /s /q build

# Linux/Mac
rm -rf build
```

Ne supprimez pas le dossier `dist/` car il contient l'exécutable final.

## Notes de Version

- **PyInstaller** : 6.22.3
- **Python** : 3.10+
- **Système** : Windows 10/11
