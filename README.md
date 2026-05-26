# AeroFlow

> **420-SF4-RE | Projet d'intégration en sciences, informatique et mathématique**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green)](https://doc.qt.io/qtforpython-6/)
[![NumPy](https://img.shields.io/badge/Math-NumPy-orange)](https://numpy.org/)
[![Numba](https://img.shields.io/badge/Performance-Numba-purple)](https://numba.pydata.org/)

---

## Qu'est-ce que AeroFlow ?

**AeroFlow** est une application de bureau interactive qui permet de dessiner des formes en 2D et de simuler leur comportement aérodynamique en temps réel. Elle combine un éditeur vectoriel intuitif, un moteur physique basé sur la méthode de **Lattice Boltzmann (LBM)**, et un **algorithme génétique** pour optimiser automatiquement la géométrie des objets.

Que vous soyez étudiant en sciences, enseignant en physique mécanique, ou simplement curieux de comprendre comment l'air s'écoule autour d'un objet — AeroFlow vous offre une fenêtre visuelle et interactive sur le monde de l'aérodynamique.

---

## Fonctionnalités principales

### Éditeur graphique vectoriel 2D
- **Canevas interactif** : Environnement quadrillé permettant de basculer entre le mode de dessin et le mode libre.
- **Manipulation dynamique** : Ajouter, sélectionner, déplacer et supprimer des sommets et des formes indépendamment les unes des autres.
- **Rastérisation automatique** : Conversion des dessins vectoriels en masque binaire compatible avec le moteur physique.

### Moteur physique — Lattice Boltzmann (LBM)
- **Simulation d'écoulement fluide** : Visualisation en temps réel du mouvement de l'air autour de l'obstacle dessiné.
- **Heatmap de vitesse** : Carte thermique colorée représentant les zones de haute et basse pression.
- **Coefficients aérodynamiques** : Calcul automatique du coefficient de traînée ($C_d$) et de portance ($C_l$) par échange de quantité de mouvement aux bords de l'obstacle.

### Optimisation par algorithme génétique
- **Évolution automatique des formes** : L'IA modifie la géométrie initiale pour minimiser la traînée.
- **Contraintes paramétrables** : Définissez une marge de tolérance (surface ou distance) pour préserver l'identité de votre forme.
- **Graphique de convergence** : Suivez en temps réel l'amélioration du coefficient de traînée à chaque génération.

---

## Installation

### Prérequis
- **Python 3.10** ou ultérieur
- **Git**

### Étapes

```bash
# 1. Créer un environnement virtuel (recommandé)
python -m venv .venv

# Sur Windows
.venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# (Assurez-vous d'utiliser une version adéquate de PySide6.)
# Afin de désinstaller la version courant et réinstaller PySide6 :
pip uninstall PySide6 PySide6-Essentials PySide6-Addons shiboken6
pip install PySide6

# 3. Lancer l'application
python run.py
```

### Dépendances principales
| Bibliothèque | Version | Usage |
|-------------|---------|-------|
| PySide6 | ≥6.0 | Interface graphique (GUI) et rendu 2D |
| NumPy | ≥1.24 | Mathématiques vectorisées et matrices |
| Numba | ≥0.58 | Compilation JIT pour performances du moteur physique |
| SciPy | ≥1.10 | Traitement d'images (zoom, érosion morphologique) |
| OpenCV-Python | ≥4.8 | Génération et manipulation de visualisations |
| h5py | ≥3.8 | Sauvegarde et lecture des étapes de simulation |
| AeroSandbox | ≥4.0 | Outils aérodynamiques et d'optimisation |

---

## Architecture du projet

```
AeroFlow/
├── dev/
│   ├── core/               # Point d'entrée et gestionnaire de projets
│   │   ├── aeroflow.py
│   │   └── project_manager.py
│   ├── physics_engine/     # Moteur LBM et calculs aérodynamiques
│   │   ├── lattice_grid.py
│   │   ├── simulation_engine.py
│   │   ├── vector_obstacle.py
│   │   └── pixmap_gen.py
│   ├── user_interface/     # Composants graphiques PySide6
│   │   ├── canvas/         # Éditeur vectoriel et barre d'outils
│   │   ├── analysis/       # Onglets d'analyse et graphiques
│   │   ├── floating/       # Widgets flottants et paramètres
│   │   ├── management/     # Page d'accueil et fenêtre principale
│   │   └── components/     # Boutons, sliders, séparateurs
│   └── icons/              # Ressources graphiques et polices
├── docs/
│   ├── extrants/conception/  # Spécifications, conception, modélisation
│   └── travail/              # Maquettes et diagrammes UML
├── tmp_files/
├── aeroflow.ini            # Configuration utilisateur
├── run.py                  # Lanceur principal
└── README.md
```

---

## Utilisation rapide

1. **Lancer** l'application avec `python run.py`.
2. **Créer un nouveau projet** depuis la page d'accueil.
3. **Dessiner une forme** en mode dessin : cliquez sur la grille pour placer des sommets.
4. **Lancer la simulation** avec le bouton vert ▶ — observez la heatmap et les coefficients.
5. **Optimiser** via le panneau d'analyse : définissez une tolérance et lancez l'algorithme génétique.
6. **Sauvegarder** votre session (forme initiale, optimisée et résultats) au format JSON.

---

## Documents de conception

| Document | Description |
|----------|-------------|
| [Spécifications fonctionnelles](./docs/extrants/conception/Spécifications.md) | Objectifs, périmètre fonctionnel et stratégie de livraison |
| [Conception logicielle](./docs/extrants/conception/Conception.md) | Choix technologiques, architecture UML et maquettes GUI |
| [Modélisation scientifique](./docs/extrants/conception/Modélisation-Science.md) | Fondements physiques — LBM, BGK, Bounce-Back |
| [Modélisation mathématique](./docs/extrants/conception/Modélisation-Math.md) | Algèbre linéaire, théorème de Green, algorithme génétique |
| [Contrat d'engagement](./docs/extrants/gestion/engagement/Contrat%20d'engagement.pdf) | Engagement de l'équipe et charte de projet |

---

## Équipe

| Membre | Rôle | Contributions |
|--------|------|--------------|
| **Firas Ngazou** [@Firas-Ngazou](https://github.com/Firas-Ngazou) | Architecture principale, UI/UX, éditeur vectoriel | Conception de l'interface, gestion des projets, expérience utilisateur |
| **Mehdi Achouri** [@Mehdiii07](https://github.com/Mehdiii07) | Physique computationnelle | Modèle Lattice Boltzmann, calculs de traînée et portance |
| **Quang-Vinh Nguyen** [@vinh9336](https://github.com/vinh9336) | Intelligence artificielle | Modélisation et implémentation de l'algorithme génétique, contraintes géométriques |

---

## Contexte académique

Ce projet est réalisé dans le cadre du cours **420-SF4-RE — Projet d'intégration en sciences, informatique et mathématique** au Cégep. Il vise à démontrer l'intégration des compétences disciplinaires à travers un projet concret combinant :

- **Sciences** : Mécanique des fluides, aérodynamique
- **Informatique** : Développement d'application desktop, architecture logicielle, gestion de projet Agile/Scrum
- **Mathématiques** : Algèbre linéaire, géométrie vectorielle, optimisation évolutionnaire

---

> **Note** : Ce projet est à but académique. Les simulations sont basées sur des hypothèses simplifiées (écoulement 2D, fluide incompressible, $Ma < 0.3$) et ne remplacent pas des outils de simulation professionnels.