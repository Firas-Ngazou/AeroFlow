# Proposition

> #### 420-SF4-RE | Projet d’intégration en sciences, informatique et mathématique

**Table des matières**
- 1 - [**Présentation**](#1---présentation)
  - 1.1 - [**Identification**](#11---identification)
    - 1.11 - [Membres de l'équipe](#111---membres-de-léquipe)
    - 1.12 - [Titre du projet](#112---titre-du-projet--)
    - 1.13 - [Description du projet](#113---description-du-projet)
    - 1.14 - [Date de la rencontre](#114---date-de-la-rencontre--)
  - 1.2 - [**Exigences disciplinaires**](#12---exigences-disciplinaires)
    - 1.21 - [Sciences](#121---sciences)
    - 1.22 - [Mathématiques](#122---mathématiques)
    - 1.23 - [Informatique](#123---informatique)
    - 1.24 - [Organisation](#124---organisation)
- 2 - [**Livrables**](#2---livrables)

## 1 - Présentation
### 1.1 - Identification
#### 1.11 - Membres de l'équipe
- Mehdi Achouri
- Quang-Vinh Nguyen
- Firas Ngazou

#### 1.12 - Titre du projet : 
AeroFlow 3D

#### 1.13 - Description du projet
- L'objectif principal du projet est de développer un simulateur de tunnel à vent virtuel. Le logiciel permettra à 
l'utilisateur d'importer un modèle 3D (comme une voiture ou une forme géométrique), de configurer la vitesse du vent, et 
de visualiser comment l'air s'écoule autour de l'objet. Le logiciel calculera également une approximation de la force de 
traînée (résistance de l'air) pour aider à comprendre quel objet est le plus aérodynamique.

#### 1.14 - Date de la rencontre : 
TBA

### 1.2 - Exigences disciplinaires
### 1.21 - Sciences
#### Responsable : 
Mehdi Achroui

#### Discipline
- La physique mécanique (dynamique des fluides et cinématique) sera la discipline centrale.

#### Concept clé
- Le projet repose sur la compréhension de l'interaction entre un fluide et un solide.
- Le concept clé est la conservation de la quantité de mouvement et la différence de pression. L'air qui frappe 
l'avant de la voiture crée une zone de haute pression (qui pousse l'objet vers l'arrière), alors que l'air qui 
accélère autour crée une dépression. C'est cette différence qui crée la force de traînée.

#### Défi
- La simulation de fluides est complexe (turbulences). Le défi sera de trouver un modèle simplifié acceptable pour notre
niveau. Nous ne pourrons pas simuler chaque molécule parfaitement.
- Nous devrons faire des hypothèses simplificatrices, soit, considérer l'air comme incompressible et ignorer les 
micro-turbulences trop complexes pour ne garder que les grands mouvements de fluides.

#### Simulation
- Nous utiliserons une approche numérique sur grille. L'espace sera divisé en petites cases (voxels). 
Nous appliquerons des règles de collision et de propagation inspirées de la méthode Lattice Boltzmann (ou similaire) 
pour simuler le comportement macroscopique du vent sans avoir à résoudre les équations différentielles complexes de 
Navier-Stokes de manière analytique.

### 1.22 - Mathématiques
#### Responsable : 
Quang-Vinh Nguyen

#### Discipline
- Calcul vectoriel, Algèbre linéaire et Calcul intégral.

#### Concept clé
- L'espace de simulation est un champ vectoriel. Chaque point de la grille possède un vecteur vitesse (direction et 
intensité du vent).
- Pour calculer la force finale exercée sur la voiture, nous devrons effectuer une intégration de surface, soit, 
additionner les forces de pression sur chaque petit polygone qui compose le modèle 3D de la voiture. Cela implique 
l'utilisation de produits scalaires pour déterminer l'angle entre le vent et la surface (vecteur normal).

#### Intégration
- Un exemple : calculer si une particule de vent rebondit sur la voiture demande de calculer le vecteur réfléchi par 
rapport à la normale de la surface à l'impact.

#### Défi
- Le passage du continu (le modèle 3D lisse de la voiture) au discret (notre grille de calcul composée de cubes/pixels). 
Déterminer comment représenter une courbe lisse dans une matrice carrée sans créer des "effets d'escalier" qui 
fausseraient complètement les calculs de frottement.

### 1.23 - Informatique
#### Responsable : 
Firas Ngazou

#### Persistance des données
- **Contexte principal :** Permettre à l'utilisateur de charger des modèles 3D standards (format .OBJ ou .STL). 
Le logiciel devra lire et interpréter ces fichiers pour reconstruire l'objet dans la simulation.
- **Entrées :** Fichiers 3D, paramètres de simulation (vitesse du vent, résolution de la grille).
- **Sorties :** Capture d'écran de la simulation ou exportation des données de performance (Coefficient de traînée) 
dans un fichier texte/CSV.

#### Outils spécifiques
- **NumPy :** Indispensable pour gérer la grille de simulation (matrices géantes représentant l'air). La vectorisation 
sera utilisée pour calculer les changements d'état de milliers de cellules en même temps.
- **PyVista ou Matplotlib 3D :** Contrairement au projet 2D, nous avons besoin d'un moteur de visualisation capable 
d'afficher des volumes et des lignes de courant (_streamlines_) en 3D.
- **PySide6 :** Pour l'interface utilisateur (boutons, sliders pour la vitesse du vent, fenêtres de chargement de 
fichiers).

#### Interactions
- **Forme des interactions :** Visualisation 3D interactive. L'utilisateur pourra tourner autour de l'objet (orbite), 
zoomer et déplacer la caméra pendant que la simulation tourne.
- **Intrants (Actions) :**
  - Importation d'un fichier 3D.
  - Ajustement de la vitesse du flux d'air via un curseur.
  - Choix du type de visualisation (vecteurs, fumée, ou pression).
- **Extrants (Réponses) :**
  - Animation du fluide en temps réel (ou quasi réel).
  - Affichage numérique en direct de la force subie par l'objet (en Newtons).

#### Défi
- Une simulation de fluide en 3D est extrêmement exigeante en ressources. Si le code n'est pas optimisé, 
l'expérience utilisateur sera mauvaise. Le défi sera de trouver l'équilibre entre une simulation physiquement "croyable" 
et une fluidité d'affichage acceptable pour une démonstration.

### 1.24 - Organisation
#### Responsable : 
Firas Ngazou

## 2 - Livrables
### 2.1 - Premier livrable
- Objectif principal : Modél physique de base.
- Fonctionnalité 1 : Simulation fonctionnelle en 2D ou 3D basse résolution d'un flux d'air contournant un obstacle 
simple (cube ou sphère).
- Fonctionnalité 2 : Visualisation de base (code couleur pour la vitesse de l'air).
- Fonctionnalité 3 : Interface utilisateur simple (boutons, scene 3D, etc.).

### 2.2 - Deuxième livrable
- Objectif principal : 3D et importation de models.
- Fonctionnalité 1 : Capacité d'importer un objet 3D complexe (voiture) au format .OBJ.
- Fonctionnalité 2 : Visualisation avancée avec des lignes de courant (_streamlines_) qui montrent le chemin emprunté 
par l'air.

### 2.3 - Troisième livrable
- Objectif principal : Analyse de données et interface finale.
- Fonctionnalité 1 : Calcul et affichage du coefficient de traînée.
- Fonctionnalité 2 : Visualisation de la pression (colorier la voiture en rouge là où l'air frappe fort, et 
en bleu là où il y a dépression).