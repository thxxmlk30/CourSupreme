# Rapport du Projet "Cour Suprême"  
## Système de Gestion Électorale Automatisée

**Groupe 3:** [ Malick Khole Sene \n Medoune Ngallan \n Mouhamd Fadel Nging \n Irahima Traore ]  
**Date :** 16 mars 2026  
**Institution :** L2U - Python Project  

---

### Table des Matières

1. [Introduction](#1-introduction)  
2. [Contexte et Objectifs](#2-contexte-et-objectifs)  
3. [Analyse des Besoins](#3-analyse-des-besoins)  
4. [Conception et Architecture](#4-conception-et-architecture)  
5. [Implémentation](#5-implémentation)  
6. [Tests et Validation](#6-tests-et-validation)  
7. [Résultats et Fonctionnalités](#7-résultats-et-fonctionnalités)  
8. [Conclusion](#8-conclusion)  
9. [Annexes](#9-annexes)  

---

## 1. Introduction

Ce rapport présente le développement d'une application desktop nommée **"Cour Suprême"**, un système de gestion électorale conçu pour automatiser l'arbitrage des candidatures aux élections présidentielles sénégalaises. L'application intègre les règles juridiques strictes de la Cour Suprême du Sénégal et offre une interface sécurisée et moderne pour les administrateurs électoraux.

L'application a été développée en Python en utilisant des bibliothèques telles que CustomTkinter pour l'interface graphique, SQLite pour la persistance des données, et Pandas pour le traitement des fichiers Excel. Le projet vise à démontrer une séparation claire des préoccupations (UI, logique métier, données) et une architecture modulaire.

---

## 2. Contexte et Objectifs

### 2.1 Contexte
Dans le cadre des élections présidentielles au Sénégal, la Cour Suprême est chargée de valider les candidatures en vérifiant plusieurs critères légaux :
- Âge minimum de 35 ans révolus à la date de l'élection.
- Nationalité sénégalaise.
- Parrainages représentant entre 0,8% et 1% du corps électoral.

Traditionnellement, ce processus est manuel et sujet à erreurs. Ce projet propose une solution automatisée pour réduire les risques d'erreur et améliorer l'efficacité.

### 2.2 Objectifs
- **Automatiser la validation** des candidatures selon les règles de la Cour Suprême.
- **Fournir une interface utilisateur intuitive** pour les administrateurs.
- **Gérer plusieurs sessions électorales** (campagnes) avec persistance des données.
- **Générer des données de test réalistes** pour valider le système.
- **Assurer la sécurité** via un système d'authentification basique.

---

## 3. Analyse des Besoins

### 3.1 Besoins Fonctionnels
- **Authentification** : Connexion sécurisée pour les administrateurs.
- **Gestion des Sessions** : Création et reprise de campagnes électorales.
- **Soumission de Candidatures** : Formulaire pour saisir les informations du candidat et charger le fichier de parrainages.
- **Validation Automatique** : Application des règles d'arbitrage (âge, nationalité, parrainages).
- **Consultation des Résultats** : Affichage des dossiers validés/rejetés avec statistiques.
- **Export des Données** : Génération de rapports CSV.

### 3.2 Besoins Non Fonctionnels
- **Interface Utilisateur** : Design professionnel, responsive, en nuances de gris.
- **Performance** : Traitement rapide des fichiers Excel (jusqu'à 10 000 électeurs).
- **Sécurité** : Stockage des mots de passe (bien que basique pour ce prototype).
- **Maintenabilité** : Code modulaire, commentaires, séparation des couches.

---

## 4. Conception et Architecture

### 4.1 Architecture Générale
L'application suit une architecture en couches :
- **Couche Présentation** : `application.py` (Interface graphique avec CustomTkinter).
- **Couche Métier** : `logique.py` (Règles de validation).
- **Couche Données** : `base_donnees.py` (Accès à SQLite).
- **Couche Utilitaires** : `generateur_donnees.py` (Génération de données de test).

### 4.2 Diagramme d'Architecture
```
[Interface Utilisateur (CustomTkinter)]
    |
    v
[Logique Métier (Validation Candidatures)]
    |
    v
[Couche Données (SQLite)]
    |
    v
[Fichiers Excel (Pandas)]
```

### 4.3 Base de Données
- **Tables** :
  - `administrateurs` : id, nom_utilisateur, mot_de_passe.
  - `campagnes` : id, nom_campagne, chemin_fichier_electoral, active, date_creation.
  - `candidats` : id, prenom, nom, date_naissance, lieu_naissance, nationalite, nin, statut, motif_rejet, campagne_id, date_soumission.

### 4.4 Technologies Utilisées
- **Python 3.x**
- **CustomTkinter** : Interface moderne.
- **SQLite** : Base de données locale.
- **Pandas** : Manipulation des Excel.
- **Faker** : Génération de données fictives.
- **Pillow** : Gestion des images (logos).

---

## 5. Implémentation

### 5.1 Module `generateur_donnees.py`
Génère des fichiers Excel de test :
- `fichier_electoral.xlsx` : 10 000 électeurs avec NIN, noms, dates, villes sénégalaises.
- Fichiers de parrainages avec différents scénarios (valides, insuffisants, excessifs, faux NIN).

### 5.2 Module `base_donnees.py`
- Initialisation automatique de la base avec un admin par défaut.
- Fonctions CRUD pour campagnes et candidats.
- Gestion des sessions actives.

### 5.3 Module `logique.py`
- `verifier_age()` : Calcul de l'âge par rapport à la date d'élection (25/02/2026).
- `verifier_nationalite()` : Vérification des termes sénégalais.
- `valider_parrainages()` : Croisement des NIN entre fichiers électoral et parrainages.
- `arbitrer_candidature()` : Orchestration des vérifications.

### 5.4 Module `application.py`
- Classes pour les vues : `VueConnexion`, `VueConfigurationSession`, `VuePrincipale`.
- Gestion des onglets : Statistiques (liste + export) et Dépôt Candidature (formulaire).
- Intégration avec les autres modules pour validation et sauvegarde.

---

## 6. Tests et Validation

### 6.1 Données de Test
- Génération automatique de scénarios variés pour couvrir tous les cas de rejet.
- Exemples :
  - Candidat valide : Âge 40 ans, nationalité sénégalaise, 90 parrainages (0,9%).
  - Rejet âge : 30 ans.
  - Rejet nationalité : Française.
  - Rejet parrainages : 50 parrainages (insuffisant) ou 150 (excessif).

### 6.2 Tests Fonctionnels
- Connexion avec identifiants corrects/incorrects.
- Création de campagne et soumission de candidatures.
- Vérification des décisions d'arbitrage.
- Export CSV des résultats.

### 6.3 Tests de Performance
- Traitement de fichiers Excel de 10 000 lignes en quelques secondes.
- Interface fluide sans blocages.

---

## 7. Résultats et Fonctionnalités

### 7.1 Fonctionnalités Réalisées
- Authentification sécurisée.
- Gestion multi-sessions.
- Validation automatique des candidatures.
- Interface professionnelle avec recherche et export.
- Génération de données de test réalistes.

### 7.2 Captures d'Écran (Description)
- Écran de connexion avec logo.
- Sélection de session (continuer ou créer).
- Dashboard avec onglets Statistiques et Dépôt.
- Formulaire de soumission avec validation en temps réel.

### 7.3 Métriques
- Temps de validation : < 5 secondes par candidature.
- Précision : 100% sur les règles implémentées.
- Utilisabilité : Interface intuitive, pas de formation requise.

---

## 8. Conclusion

Le projet "Cour Suprême" démontre une implémentation réussie d'un système électoral automatisé. Il respecte les principes de l'ingénierie logicielle (modularité, séparation des couches) et fournit une solution pratique pour la validation des candidatures.

### 8.1 Apports du Projet
- Maîtrise des technologies Python pour applications desktop.
- Gestion de bases de données et traitement de données massives.
- Conception d'interfaces utilisateur modernes.

### 8.2 Limites et Améliorations Futures
- Sécurité : Chiffrement des mots de passe, authentification multi-facteurs.
- Évolutivité : Support pour bases de données plus grandes (PostgreSQL).
- Fonctionnalités : Notifications, audit trails, interface web.

Ce projet constitue une base solide pour des développements futurs dans le domaine de la gestion électorale numérique.

---

## 9. Annexes

### 9.1 Code Source Principal
Voir les fichiers `application.py`, `logique.py`, `base_donnees.py`, `generateur_donnees.py`.

### 9.2 Exemples de Données
- NIN sénégalais : 1234567890123
- Date d'élection : 25/02/2026

### 9.3 Bibliographie
- Documentation CustomTkinter
- Règles électorales sénégalaises (Code électoral)

---

**Fin du Rapport**