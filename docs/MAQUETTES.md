# Maquettes et Wireframes - EduPaie

Ce document présente les maquettes des écrans principaux de l'application EduPaie.

---

## 1. Écran de Connexion

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      [LOGO EduPaie]                         │
│                                                             │
│              Gestion des Paiements Scolaires                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                                                     │  │
│  │  Identifiant                                       │  │
│  │  [_______________________________]                  │  │
│  │                                                     │  │
│  │  Mot de passe                                      │  │
│  │  [_______________________________]                  │  │
│  │                                                     │  │
│  │           [Se connecter]                           │  │
│  │                                                     │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│                Premier lancement ? Créer un compte          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Éléments** :
- Logo EduPaie (centré)
- Titre de l'application
- Formulaire de connexion (identifiant, mot de passe)
- Bouton "Se connecter"
- Lien pour créer le compte (premier lancement)

---

## 2. Fenêtre Principale

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Bandeau supérieur                                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ [LOGO]  Mon Établissement           [Date/Heure]  [Admin] [Déconnexion] │ │
│ │         Gestion des élèves de votre établissement                        │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├──────────┬───────────────────────────────────────────────────────────────────┤
│ Barre    │ Zone de contenu                                                   │
│ latérale │                                                                   │
│          │ ┌─────────────────────────────────────────────────────────────┐ │
│ [LOGO]   │ │                                                             │ │
│          │ │                   [Contenu de la page]                     │ │
│ Élèves   │ │                                                             │ │
│ ◄─────── │ │                                                             │ │
│          │ │                                                             │ │
│ Paiements│ │                                                             │ │
│          │ │                                                             │ │
│ Tableau  │ │                                                             │ │
│ de bord  │ │                                                             │ │
│          │ │                                                             │ │
│ Reçus    │ │                                                             │ │
│          │ │                                                             │ │
│ Admin    │ │                                                             │ │
│          │ │                                                             │ │
│ Parents  │ │                                                             │ │
│          │ │                                                             │ │
│ Classes  │ │                                                             │ │
│          │ │                                                             │ │
│          │ └─────────────────────────────────────────────────────────────┘ │
└──────────┴───────────────────────────────────────────────────────────────────┘
```

**Éléments** :
- **Bandeau supérieur** : Logo, nom établissement, date/heure, info utilisateur, déconnexion
- **Barre latérale** : Navigation avec boutons (Élèves, Paiements, Tableau de bord, Reçus, Admin, Parents, Classes)
- **Zone de contenu** : Page active (liste élèves, fiche, tableau de bord, etc.)

---

## 3. Page Liste des Élèves

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Bandeau supérieur (identique fenêtre principale)                            │
├──────────┬───────────────────────────────────────────────────────────────────┤
│ Barre    │ ┌─────────────────────────────────────────────────────────────┐ │
│ latérale │ │ Barre de recherche et filtres                              │ │
│          │ │ ┌───────────────────────────────────────────────────────┐ │ │
│ Élèves   │ │ │ Rechercher un élève (Nom, Prénom...)                  │ │ │
│ ◄─────── │ │ │ [Saisir nom ou prénom...]                           │ │ │
│ Paiements│ │ │                                                       │ │ │
│ Tableau  │ │ │ Classe : [Toutes ▼]  Statut : [Tous ▼]              │ │ │
│ de bord  │ │ └───────────────────────────────────────────────────────┘ │ │
│ Reçus    │ │                                                         │ │ │
│ Admin    │ │ [+ Ajouter] [Modifier] [Supprimer] [Fiche/Paiements]    │ │ │
│ Parents  │ │                                                     [Exporter] │ │
│ Classes  │ │                                                         │ │ │
│          │ │ ┌─────────────────────────────────────────────────────┐ │ │
│          │ │ │ # │ Nom    │ Prénom │ Classe │ Année │ Total │ Payé │ │ │
│          │ │ │───┼────────┼────────┼────────┼───────┼───────┼──────│ │ │
│          │ │ │ 1 │ Diallo │ Aminata│ 6ème A │2025-26│150000│150000│ │ │
│          │ │ │ 2 │ Mensah │ Yawo   │ 6ème A │2025-26│150000│ 50000│ │ │
│          │ │ │ 3 │ Kodjo  │ Afi    │ 5ème B │2025-26│175000│175000│ │ │
│          │ │ │ 4 │ ...    │ ...    │ ...    │ ...   │ ...   │ ...  │ │ │
│          │ │ │   │        │        │        │       │       │      │ │ │
│          │ │ └─────────────────────────────────────────────────────┘ │ │
│          │ │                                                          │ │
│          │ └───────────────────────────────────────────────────────────┘ │
└──────────┴───────────────────────────────────────────────────────────────┘
```

**Éléments** :
- **Barre de recherche** : Champ de texte pour filtrer par nom/prénom
- **Filtres** : Liste déroulante Classe (Toutes, 6ème A, 5ème B, etc.), Statut (Tous, Soldé, Partiel, Non payé)
- **Boutons d'action** : Ajouter, Modifier, Supprimer, Fiche/Paiements, Exporter
- **Tableau** : Colonnes #, Nom, Prénom, Classe, Année, Total dû, Total payé, Solde, Statut
- **Statut** : Pastille de couleur (vert=soldé, orange=partiel, rouge=non payé)

---

## 4. Fiche Élève

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Bandeau supérieur (identique fenêtre principale)                            │
├──────────┬───────────────────────────────────────────────────────────────────┤
│ Barre    │ ┌─────────────────────────────────────────────────────────────┐ │
│ latérale │ │ [Fermer]                                                    │ │
│ Élèves   │ │                                                             │ │
│ Paiements│ │ ┌─────────────────────────────────────────────────────┐    │ │
│ Tableau  │ │ │ DIALLO Aminata                                      │    │ │
│ de bord  │ │ │ Classe : 6ème A                                       │    │ │
│ Reçus    │ │ │ Année scolaire : 2025-2026                            │    │ │
│ Admin    │ │ └─────────────────────────────────────────────────────┘    │ │
│ Parents  │ │                                                             │ │
│ Classes  │ │ ┌─────────────────────────────────────────────────────┐    │ │
│          │ │ │ Total dû : 150 000 FCFA  │ Total payé : 150 000 FCFA│    │ │
│          │ │ │ Solde : 0 FCFA            │ Statut : [Soldé 🟢]     │    │ │
│          │ │ └─────────────────────────────────────────────────────┘    │ │
│          │ │                                                             │ │
│          │ │ ┌─────────────────────────────────────────────────────┐    │ │
│          │ │ │ Historique des paiements                            │    │ │
│          │ │ │ ┌───────────────────────────────────────────────┐ │    │ │
│          │ │ │ │ Date  │ Montant │ Mode      │ N° reçu │ Solde │ │    │ │
│          │ │ │ │───────┼─────────┼───────────┼─────────┼───────│ │    │ │
│          │ │ │ │15/09/25│100 000 │ Espèces   │REC-0001 │ 50 000│ │    │ │
│          │ │ │ │10/12/25│ 50 000 │ Mobile M. │REC-0002 │     0 │ │    │ │
│          │ │ │ └───────────────────────────────────────────────┘ │    │ │
│          │ │ └─────────────────────────────────────────────────────┘    │ │
│          │ │                                                             │ │
│          │ │ [Nouveau paiement] [Voir le reçu]                           │ │
│          │ │                                                             │ │
│          │ └───────────────────────────────────────────────────────────┘ │
└──────────┴───────────────────────────────────────────────────────────────┘
```

**Éléments** :
- **Identité** : Nom, prénom, classe, année scolaire
- **Informations financières** : Total dû, Total payé, Solde, Statut (pastille)
- **Historique des paiements** : Tableau avec Date, Montant, Mode, N° reçu, Solde après
- **Boutons d'action** : Nouveau paiement, Voir le reçu

---

## 5. Dialogue d'Enregistrement de Paiement

```
┌─────────────────────────────────────────────────────────────┐
│ Enregistrer un paiement                                [X] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ DIALLO Aminata                                        │    │
│ │ Classe : 6ème A                                       │    │
│ │ Total dû : 150 000 FCFA                              │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
│ Solde restant : 0 FCFA                                     │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ Montant à payer *                                    │    │
│ │ [________________] FCFA                              │    │
│ │                                                     │    │
│ │ Date *                                              │    │
│ │ [📅 02/10/2026]                                     │    │
│ │                                                     │    │
│ │ Mode de paiement *                                   │    │
│ │ [Espèces ▼]                                         │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
│                                          [Annuler] [OK]    │
└─────────────────────────────────────────────────────────────┘
```

**Éléments** :
- **Informations élève** : Nom, prénom, classe, total dû
- **Solde restant** : Montant encore à payer
- **Formulaire** :
  - Montant à payer (spinbox, max = solde)
  - Date (sélecteur de date, par défaut aujourd'hui)
  - Mode de paiement (liste déroulante : Espèces, Chèque, Virement, Mobile Money)
- **Boutons** : Annuler, OK

---

## 6. Tableau de Bord

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Bandeau supérieur (identique fenêtre principale)                            │
├──────────┬───────────────────────────────────────────────────────────────────┤
│ Barre    │ ┌─────────────────────────────────────────────────────────────┐ │
│ latérale │ │ Tableau de bord                                             │ │
│ Élèves   │ │ Vue d'ensemble des paiements scolaires                      │ │
│ Paiements│ │                                                             │ │
│ ◄─────── │ │ ┌─────────────────────────────────────────────────────┐    │ │
│ Tableau  │ │ │ 📊 Statistiques globales                              │    │ │
│ de bord  │ │ │                                                       │    │ │
│ Reçus    │ │ │ • Nombre d'élèves : 20                                │    │ │
│ Admin    │ │ │ • Total encaissé : 2 750 000 FCFA                     │    │ │
│ Parents  │ │ │ • Total restant dû : 425 000 FCFA                     │    │ │
│ Classes  │ │ │ • Élèves non soldés : 7                               │    │ │
│          │ │ └─────────────────────────────────────────────────────┘    │ │
│          │ │                                                             │ │
│          │ │ ┌─────────────────────────────────────────────────────┐    │ │
│          │ │ │ Répartition par statut                                │    │ │
│          │ │ │                                                       │    │ │
│          │ │ │ Soldé (5)          [████████████████░░░░] 25%        │    │ │
│          │ │ │ Partiel (8)        [██████████████████████] 40%       │    │ │
│          │ │ │ Non payé (7)       [████████████░░░░░░░░░░] 35%       │    │ │
│          │ │ └─────────────────────────────────────────────────────┘    │ │
│          │ │                                                             │ │
│          │ │ ┌─────────────────────────────────────────────────────┐    │ │
│          │ │ │ Élèves à surveiller (solde élevé)                    │    │ │
│          │ │ │ ┌───────────────────────────────────────────────┐   │    │ │
│          │ │ │ │ Élève          │ Classe │ Solde    │ Statut  │   │    │ │
│          │ │ │ │────────────────┼────────┼──────────┼─────────│   │    │ │
│          │ │ │ │ Folly Dzifa    │ Term D │ 250 000  │ Non payé│   │    │ │
│          │ │ │ │ Zotchi Agbéko  │ Term D │ 250 000  │ Non payé│   │    │ │
│          │ │ │ │ Eklou Selom    │ Term D │ 220 000  │ Partiel │   │    │ │
│          │ │ │ └───────────────────────────────────────────────┘   │    │ │
│          │ │ └─────────────────────────────────────────────────────┘    │ │
│          │ │                                                             │ │
│          │ └───────────────────────────────────────────────────────────┘ │
└──────────┴───────────────────────────────────────────────────────────────┘
```

**Éléments** :
- **Statistiques globales** : Nombre d'élèves, total encaissé, total restant dû, élèves non soldés
- **Répartition par statut** : Barres de progression visuelles (Soldé, Partiel, Non payé)
- **Élèves à surveiller** : Liste des élèves avec solde élevé (triée par solde décroissant)

---

## 7. Page Reçus

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Bandeau supérieur (identique fenêtre principal)                             │
├──────────┬───────────────────────────────────────────────────────────────────┤
│ Barre    │ ┌─────────────────────────────────────────────────────────────┐ │
│ latérale │ │ Registre des reçus                                          │ │
│ Élèves   │ │                                                             │ │
│ Paiements│ │ ┌───────────────────────────────────────────────────────┐   │ │
│ Tableau  │ │ │ Rechercher un reçu (N°, élève, classe...)             │   │ │
│ de bord  │ │ │ [Saisir numéro ou nom...]                            │   │ │
│ Reçus    │ │ │                                                       │   │ │
│ ◄─────── │ │ │ Mode : [Tous ▼]                                      │   │ │
│ Admin    │ │ └───────────────────────────────────────────────────────┘   │ │
│ Parents  │ │                                                         │   │ │
│ Classes  │ │ ┌─────────────────────────────────────────────────────┐   │ │
│          │ │ │ N° reçu      │ Date   │ Élève         │ Montant │   │ │
│          │ │ │─────────────┼────────┼───────────────┼─────────│   │ │
│          │ │ │ REC-2026-001│15/09/25│ Diallo Aminata │100 000 │   │ │
│          │ │ │ REC-2026-002│10/12/25│ Diallo Aminata │ 50 000 │   │ │
│          │ │ │ REC-2026-003│10/09/25│ Kodjo Afi     │150 000 │   │ │
│          │ │ │ ...         │ ...    │ ...           │ ...    │   │ │
│          │ │ └─────────────────────────────────────────────────────┘   │ │
│          │ │                                                             │ │
│          │ │ [Voir le reçu] [Exporter]                                   │ │
│          │ │                                                             │ │
│          │ └───────────────────────────────────────────────────────────┘ │
└──────────┴───────────────────────────────────────────────────────────────┘
```

**Éléments** :
- **Recherche** : Champ pour filtrer par numéro de reçu, nom élève, classe
- **Filtre mode** : Liste déroulante (Tous, Espèces, Chèque, Virement, Mobile Money)
- **Tableau** : N° reçu, Date, Élève, Montant, Mode, Solde après
- **Boutons** : Voir le reçu (génère PDF), Exporter

---

## 8. Dialogue de Visualisation de Reçu (Génération PDF)

```
┌─────────────────────────────────────────────────────────────┐
│ Enregistrer le reçu                                  [X] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Nom du fichier :                                           │
│ [Recu_REC-2026-000001.pdf                                 │
│                                                             │
│ Fichiers PDF (*.pdf)                                       │
│                                                             │
│                                             [Enregistrer]  │
│                                            [Annuler]       │
└─────────────────────────────────────────────────────────────┘
```

**Éléments** :
- **Nom du fichier** : Pré-rempli avec le numéro de reçu
- **Type de fichier** : PDF uniquement
- **Boutons** : Enregistrer, Annuler

Après enregistrement, le PDF s'ouvre automatiquement avec le visualiseur par défaut du système.

---

## 9. Écran de Création de Compte (Premier Lancement)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      [LOGO EduPaie]                         │
│                                                             │
│              Création du compte directeur                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                                                     │  │
│  │  Nom complet                                       │  │
│  │  [_______________________________]                  │  │
│  │                                                     │  │
│  │  Identifiant (min. 3 caractères)                   │  │
│  │  [_______________________________]                  │  │
│  │                                                     │  │
│  │  Mot de passe (min. 10 caractères)                 │  │
│  │  [_______________________________]                  │  │
│  │                                                     │  │
│  │  Confirmer le mot de passe                         │  │
│  │  [_______________________________]                  │  │
│  │                                                     │  │
│  │           [Créer le compte]                         │  │
│  │                                                     │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Éléments** :
- **Nom complet** : Nom du directeur
- **Identifiant** : Login (minimum 3 caractères)
- **Mot de passe** : Minimum 10 caractères
- **Confirmation** : Vérification du mot de passe
- **Bouton** : Créer le compte

---

## Notes de Design

### Couleurs
- **Bordeau** (#8B0000) : Couleur principale (logo, titres, boutons actifs)
- **Gris clair** (#F5F6F8) : Arrière-plan des sections
- **Vert** (#2E7D32) : Statut "Soldé"
- **Orange** (#F59E0B) : Statut "Partiellement payé"
- **Rouge** (#EF4444) : Statut "Non payé"

### Typographie
- **Titres** : 18-20px, gras
- **Sous-titres** : 14-16px, semi-gras
- **Corps** : 12-14px, normal
- **Petit** : 10-11px, normal

### Comportements
- **Double-clic** sur un élève → Ouvre la fiche élève
- **Clic sur bouton** → Action correspondante
- **Filtres** → Mise à jour automatique de la liste
- **Recherche** → Mise à jour en temps réel

### Responsive
- **Taille minimale** : 900x600 px
- **Taille recommandée** : 1100x700 px
- **Adaptation** : Colonnes du tableau redimensionnables
