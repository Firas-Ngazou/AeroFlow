# Conception logicielle

> #### 420-SF4-RE | Projet d’intégration en sciences, informatique et mathématique

## Table des matières
* [Conception logicielle](#conception-logicielle)
  * [Choix technologiques](#choix-technologiques)
    * [Technologies imposées](#technologies-imposées)
    * [Bibliothèques utilitaires](#bibliothèques-utilitaires)
  * [Architecture logicielle (UML)](#architecture-logicielle-uml)
  * [Interface utilisateur (GUI)](#interface-utilisateur-gui)
    * [Vues principales de l'éditeur](#vues-principales-de-léditeur)
    * [Paramètres](#paramètres)
    * [Analyse](#analyse)
  * [Gestion des données persistantes](#gestion-des-données-persistantes)
    * [Configuration du logiciel](#configuration-du-logiciel)
    * [Données scientifiques](#données-scientifiques)

## Choix technologiques
### Technologies imposées
- **Langage de programmation** : Python
- **Calcul numérique** : Numpy
- **Interface graphique (GUI)** : PySide6

### Bibliothèques utilitaires
- **Numba (JIT)** : Pour ce projet, nous avons choisi d'utiliser la bibliothèque **Numba**. L'utilisation d'un **JIT** 
nous permettra de gagner beaucoup de temps en calculs complexes. L'utilisation principale sera pour des calculs 
matriciels qui peuvent devenir très lourds lorsque l'on veut obtenir une simulation des plus intéressantes et 
pertinentes possibles.

## Architecture logicielle (UML)

![](docs/extrants/images/Image UML.png)

## Interface utilisateur (GUI)

### Vues principales de l'éditeur

Il s'agit de la vue de base du logiciel. Aucun des panneaux n'est ouvert et il est possible de dessiner sur
le plan de travail une fois avoir sélectionné le mode de dessin dans la barre d'outils en bas au centre. Le bouton 
"commencer" représenté par un cercle vert sert de point de départ pour lancer une nouvelle simulation. Lorsque 
l'utilisateur clique sur le bouton, ce dernier devient rouge foncé et la figure qui s'y trouvait est remplacée par un 
carré signifiant que la prochaine intéraction avec ce bouton fera terminer la simulation. Lorsque la simulation est 
lancée, un bouton pause apparait juste au-dessus qui permet l'interruption ainsi que la reprise de la simulation. Dans 
la bar supérieure, le nom du projet est affiché et est directement modifiable par l'utilisateur lorsqu'il clique dessus.

<img src="docs/extrants/images/Maquette Vue Éditeur 1.png" width="950">
<img src="docs/extrants/images/Maquette Vue Éditeur 2.png" width="950">

### Paramètres

Lorsque l'utilisateur clique sur le bouton "paramètres", le logiciel lui répond en affichant un panneau dans lequel il
pourra trouver deux onglets, soit, un onglet général et un onglet d'optimisation. L'onglet général, comme son nom 
l'indique, permet à l'utilisateur d'apporter des modifications à certains aspects du logiciel et de la simulation. Sous
l'onglet d'optimisation, il pourra modifier tout ce qui est directement relié à l'optimisation de la forme et à 
l'algorithme génétique.

<img src="docs/extrants/images/Maquette Vue Parametres General.png" width="950">
<img src="docs/extrants/images/Maquette Vue Parametres Optimization.png" width="950">
<img src="docs/extrants/images/Maquette Vue Parametres General CU.png" width="950">
<img src="docs/extrants/images/Maquette Vue Parametres Optimization CU.png" width="950">

### Analyse

Un bouton d'analyse, se situant à la droite du nom de projet, permet à l'utilisateur d'afficher les données et 
informations générées par sa simulation. Ce panneau est composé de deux onglets. Le premier est entièrement dédié au 
suivi de l'évolution de l'optimisation ainsi que de ses résultats. Dans ce même onglet se trouvera un graphique de 
l'évolution du coefficient de traîné en fonction de l'itération. Le deuxième onglet sert à l'affichage des résultats 
de la simulation. Une _heatmap_ (carte thermique) du module de la vitesse de l'air autour de la forme sera également 
trouvable sous cet onglet.

<img src="docs/extrants/images/Maquette Vue Analyse Optimization.png" width="950">
<img src="docs/extrants/images/Maquette Vue Analyse Résultats.png" width="950">
<img src="docs/extrants/images/Maquette Vue Analyse Optimization CU.png" width="950">
<img src="docs/extrants/images/Maquette Vue Analyse Résultats CU.png" width="950">

## Gestion des données persistantes

### Configuration du logiciel
Les paramètres de base du logiciel et les préférences de l'utilisateur sont enregistrés de manière persistante à la 
racine du projet dans un fichier au format suivant.
- Format de fichier : **INI**
- Justification : Le format ``.ini`` est, selon nous, un excellent choix de format. En plus du fait qu'il répond aux 
éxigences du fichier ``settings.ini``, il divise également les informations en sections claires, ce qui le rend 
facilement lisible et modifiable par l'utilisateur via un simple éditeur de texte. Il est aussi directement supporté par 
la bibliothèque native ``configparser`` de Python, ce qui nous permet de limiter les dépendances externes.

  
| Nom de la donnée        | Type de donnée | Unités          | Rôle dans le logiciel                                                                                                                                                                                  |
|-------------------------|----------------|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ``grid_resolution``     | ``int``        | Pixels          | Définit la taille du domaine de la <br/> grille et, par conséquent, du <br/> domaine de calcul. (Impacte la <br/> précision visuelle et la charge <br/> de calcul)                                     |
| ``initial_velocity_ms`` | ``float``      | m/s             | Définit la vitesse de l'air soufflée <br/> au début de la simulation.                                                                                                                                  |
| ``constraint_method``   | ``str``        | -               | Définit la méthode utilisée par <br/> l'algorithme génétique pour limiter <br/> la déformation de la forme initiale <br/> lors de l'optimisation.                                                      |
| ``tolerance_margin``    | ``float``      | Pourcentage (%) | Définit la marge de le liberté <br/> accordée à l'IA par rapport à la <br/> forme initiale. (Une marge de 10% <br/> signifie une ressemblance à la <br/> forme initiale exigée d'au <br/> minimum 90%) |
| ``max_iterations``      | ``int``        | -               | Définit le nombre maximal de <br/> générations que l'algorithme génétique <br/> va exécuter avant de s'arrêter.                                                                                        |

### Données scientifiques

Le logiciel permet d'exporter les résultats de l'optimisation de la forme ainsi que les différentes géométries testées
(itérations). L'utilisateur sera invité à choisir l'emplacement de sauvegarde ou de chargement via une boîte de 
dialogue standard du système d'exploitation.
- Format de fichier : **JSON**
- Justification : Les données générées par le logiciel sont des vecteurs géométriques (des listes de sommets pour la 
forme dessinée et la forme optimisée) qui sont joint à des données physiques. Le format ``.json`` est idéal, car il nous 
permet de structurer hiérarchiquement ces données. Contrairement au format de fichier **CSV**, le ``.json`` nous permet
d'enregistrer des listes de coordonnées (x, y) de manière élégante et facilement "deserializable" en dictionnaire ou 
objets Python.

| Nom de la donnée       | Type de donnée            | Unités             |
|------------------------|---------------------------|--------------------|
| ``project_name``       | ``str``                   | -                  |
| ``initial_vertices``   | ``list[tuple[int, int]]`` | Pixels             |
| ``optimized_vertices`` | ``list[tuple[int, int]]`` | Pixels             |
| ``final_area``         | ``float``                 | Pixels<sup>2</sup> |
| ``initial_cd``         | ``float``                 | $C_d$              |
| ``optimized_cd``       | ``float``                 | $C_d$              |
| ``aerodynamic_gain``   | ``float``                 | Pourcentage (%)    |
