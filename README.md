# AeroFlow

> **420-SF4-RE | Projet d'intégration en sciences, informatique et mathématique**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green)](https://doc.qt.io/qtforpython-6/)
[![NumPy](https://img.shields.io/badge/Math-NumPy-orange)](https://numpy.org/)
[![OpenCV](https://img.shields.io/badge/Visual-OpenCV-red)](https://opencv.org/)

---

## Qu'est-ce que AeroFlow ?

**AeroFlow** est une application de bureau interactive qui permet de dessiner des formes en 2D et de simuler leur comportement aérodynamique en temps réel. Elle combine un éditeur vectoriel intuitif, un moteur physique basé sur la méthode de **Lattice Boltzmann (LBM)**, et un **algorithme génétique** pour optimiser automatiquement la géométrie des objets.

Que vous soyez étudiant en sciences, enseignant en physique mécanique, ou simplement curieux de comprendre comment l'air s'écoule autour d'un objet — AeroFlow vous offre une fenêtre visuelle et interactive sur le monde de l'aérodynamique.

---

## Fonctionnalités principales

### Éditeur graphique vectoriel 2D
- **Canevas interactif** : Environnement quadrillé permettant de basculer entre le mode de dessin et le mode libre.
- **Manipulation dynamique** : Ajouter, sélectionner, déplacer, faire pivoter, mettre à l'échelle et supprimer des sommets et des formes indépendamment les unes des autres.
- **Rastérisation automatique** : Conversion des dessins vectoriels en masque binaire compatible avec le moteur physique.
- **Prefabs** : Sauvegarde et réutilisation de formes personnalisées via le navigateur de préfabriqués.

### Moteur physique — Lattice Boltzmann (LBM)
- **Simulation d'écoulement fluide** : Visualisation en temps réel du mouvement de l'air autour de l'obstacle dessiné.
- **Heatmap de vitesse et de densité** : Cartes thermiques colorées représentant les zones de haute et basse pression.
- **Visualisations avancées** : Lignes d'écoulement (streamlines), carte de tourbillons (curl), et modes combinés.
- **Édition en temps réel** : Modification de la forme pendant la simulation avec mise à jour dynamique du fluide.

### Optimisation par algorithme génétique
- **Évolution automatique des formes** : L'IA modifie la géométrie initiale pour minimiser la traînée ou maximiser la portance.
- **Contraintes paramétrables** : Définissez une marge de tolérance (surface ou distance) pour préserver l'identité de votre forme.
- **Évaluation externe** : Les coefficients aérodynamiques ($C_d$, $C_l$) de l'algorithme génétique sont calculés via la bibliothèque **AeroSandbox**.
- **Graphique de convergence** : Suivez en temps réel l'amélioration du coefficient cible à chaque génération.

### Gestion de projet
- **Sauvegarde et chargement** de session au format JSON (dessin et certains paramètres de simulation).
- **Configuration persistante** des paramètres utilisateur au format INI.

---

## Installation

### Prérequis
- **Python 3.11** ou ultérieur
- **Git**

### Étapes

```bash
# 1. Créer un environnement virtuel (recommandé)
python -m venv .venv

# Sur Windows
.venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 2.1. Dans le cas où vous auriez une erreur en lien avec `q_wrapper`, les actions suivantes devraient régler le problème :

# Désinstallation des paquets existants :
pip uninstall PySide6 PySide6-Essentials PySide6-Addons shiboken6
# Réinstallation de PySide6 :
pip install PySide6

# 3. Lancer l'application
python run.py
```

### Dépendances principales
| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| PySide6 | ≥6.0 | Interface graphique (GUI) et rendu 2D |
| NumPy | ≥1.24 | Mathématiques vectorisées et matrices |
| Numba | ≥0.58 | Compilation JIT pour la génération des heatmaps (pixmap_gen) |
| SciPy | ≥1.10 | Traitement d'images (érosion morphologique) |
| OpenCV-Python | ≥4.8 | Upscaling des visualisations de simulation |
| h5py | ≥3.8 | Cache disque des frames de simulation (HDF5) |
| AeroSandbox | ≥4.0 | Calcul des coefficients aérodynamiques pour l'algorithme génétique |

---

## Architecture du projet

```
AeroFlow/
├── dev/
│   ├── core/               # Point d'entrée et gestionnaire de projets
│   │   ├── aeroflow.py
│   │   └── project_manager.py
│   ├── physics_engine/     # Moteur LBM, génération de visualisations et calculs aérodynamiques
│   │   ├── lattice_grid.py
│   │   ├── simulation_engine.py
│   │   ├── vector_obstacle.py
│   │   └── pixmap_gen.py
│   ├── genetic_algorithm/  # Algorithme génétique et optimisation de formes
│   │   └── genetic_algorithm.py
│   ├── user_interface/     # Composants graphiques PySide6
│   │   ├── canvas/         # Éditeur vectoriel, barre d'outils et contrôleur d'animation
│   │   ├── analysis/       # Onglets d'analyse et graphiques
│   │   ├── floating/       # Widgets flottants et paramètres
│   │   ├── management/     # Page d'accueil et fenêtre principale
│   │   ├── components/     # Boutons, sliders, séparateurs
│   │   └── groups/         # Groupes de contrôles (checkboxes, combos)
│   └── icons/              # Ressources graphiques et polices
├── docs/
│   ├── extrants/conception/  # Spécifications, conception, modélisation
│   ├── extrants/final/       # Rapport final du projet
│   └── travail/              # Maquettes et diagrammes UML
├── tmp_files/              # Fichiers temporaires (cache HDF5)
├── aeroflow.ini            # Configuration utilisateur
├── run.py                  # Lanceur principal
├── README.md               # Ce fichier
└── Manuel.md               # Manuel d'utilisation complet
```

---

## Utilisation rapide

1. **Lancer** l'application avec `python run.py`.
2. **Créer un nouveau projet** depuis la page d'accueil.
3. **Dessiner une forme** en mode dessin : cliquez sur la grille pour placer des sommets.
4. **Lancer la simulation** avec le bouton vert ▶ — observez la heatmap et les coefficients.
5. **Optimiser** via le panneau d'analyse : définissez une tolérance et lancez l'algorithme génétique.
6. **Sauvegarder** votre session au format JSON.

Pour un guide détaillé de toutes les fonctionnalités, consultez le [**Manuel d'utilisation**](./Manuel.md).

---

## Documents du projet

| Document | Description |
|----------|-------------|
| [Spécifications fonctionnelles](./docs/extrants/conception/Spécifications.md) | Objectifs, périmètre fonctionnel et stratégie de livraison |
| [Conception logicielle](./docs/extrants/conception/Conception.md) | Choix technologiques, architecture UML et maquettes GUI |
| [Modélisation scientifique](./docs/extrants/conception/Modélisation-Science.md) | Fondements physiques — LBM, BGK, Bounce-Back |
| [Modélisation mathématique](./docs/extrants/conception/Modélisation-Math.md) | Algèbre linéaire, théorème de Green, algorithme génétique |
| [Rapport final](./docs/extrants/final/Rapport.md) | Rapport final du projet d'intégration |
| [Manuel d'utilisation](./Manuel.md) | Guide complet pour tester et utiliser l'application |
| [Contrat d'engagement](./docs/extrants/gestion/engagement/Contrat%20d'engagement.pdf) | Engagement de l'équipe et charte de projet |

---

## Équipe

| Membre | Rôle | Contributions |
|--------|------|--------------|
| **Firas Ngazou** [@Firas-Ngazou](https://github.com/Firas-Ngazou) | Architecture principale, UI/UX, éditeur vectoriel | Conception de l'interface, gestion des projets, expérience utilisateur, système d'animation |
| **Mehdi Achouri** [@Mehdiii07](https://github.com/Mehdiii07) | Physique computationnelle | Modèle Lattice Boltzmann, calculs de traînée et portance, visualisations scientifiques |
| **Quang-Vinh Nguyen** [@vinh9336](https://github.com/vinh9336) | Intelligence artificielle | Modélisation et implémentation de l'algorithme génétique, contraintes géométriques, intégration AeroSandbox |

---

## Contexte académique

Ce projet est réalisé dans le cadre du cours **420-SF4-RE — Projet d'intégration en sciences, informatique et mathématique** au Cégep. Il vise à démontrer l'intégration des compétences disciplinaires à travers un projet concret combinant :

- **Sciences** : Mécanique des fluides, aérodynamique
- **Informatique** : Développement d'application desktop, architecture logicielle, gestion de projet Agile/Scrum
- **Mathématiques** : Algèbre linéaire, géométrie vectorielle, optimisation évolutionnaire

---

> **Note** : Ce projet est à but académique. Les simulations sont basées sur des hypothèses simplifiées (écoulement 2D, fluide incompressible, $Ma < 0.3$) et ne remplacent pas des outils de simulation professionnels.

> **Note** : Comme la cible de 'traîné' est codée en français, il se peut que les caractères spéciaux de cette méthode causent des problèmes internes. Nous en sommes désolé, nous n'avions pas tout à fait eu le temps nécessaire pour tester ce projet comme il se doit.
