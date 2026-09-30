# EduPaie

Application desktop de gestion des paiements scolaires.

## Installation

### Prérequis
- Python 3.10 ou supérieur

### Étapes d'installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
- Windows : `venv\Scripts\activate`
- Linux/Mac : `source venv/bin/activate`

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

## Structure du projet

```
edupaie/
├── main.py              # Point d'entrée
├── requirements.txt    # Dépendances Python
├── README.md           # Ce fichier
├── edupaie/
│   ├── database/       # Connexion, schéma SQL, repositories
│   ├── models/         # Dataclasses (Eleve, Paiement)
│   ├── services/       # Logique métier
│   ├── ui/             # Fenêtres PySide6
│   ├── receipts/       # Génération des reçus PDF
│   └── utils/          # Utilitaires (chemins, etc.)
├── tests/              # Tests unitaires
└── docs/               # Documentation
```

## Technologies

- **Python 3.10+**
- **PySide6** : Framework GUI
- **SQLite3** : Base de données (bibliothèque standard)
- **ReportLab** : Génération de PDF

## Packaging

Pour créer l'exécutable Windows :

```bash
pyinstaller --onefile --windowed main.py
```

L'exécutable se trouvera dans le dossier `dist/`.

## Licence

Projet scolaire - Usage éducatif uniquement.
