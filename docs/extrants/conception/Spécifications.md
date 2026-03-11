# Spécifications fonctionnelles

> #### 420-SF4-RE | Projet d’intégration en sciences, informatique et mathématique

## Table des matières
* [Spécifications fonctionnelles](#spécifications-fonctionnelles)
  * [1 - Vision du projet](#1---vision-du-projet)
    * [1.1 - Objectif général](#11---objectif-général)
    * [1.2 - Objectif spécifique](#12---objectif-spécifique)
    * [1.3 - Considérations scientifiques](#13---considérations-scientifiques)
    * [1.4 - Considérations mathématiques](#14---considérations-mathématiques)
  * [2 - Périmètre fonctionnel](#2---périmètre-fonctionnel)
    * [2.1 - Acteurs du système](#21---acteurs-du-système)
    * [2.2 - Fonctionnalités principales](#22---fonctionnalités-principales)
    * [2.3 - Intrants et extrants](#23---intrants-et-extrants)
    * [2.4 - Données persistantes](#24---données-persistantes)
  * [3 - Vocabulaire et sémantique du domaine d'application](#3---vocabulaire-et-sémantique-du-domaine-dapplication)
    * [3.1 - Glossaire du domaine](#31---glossaire-du-domaine)
    * [3.2 - Dictionnaire des unités et constantes](#32---dictionnaire-des-unités-et-constantes)
  * [4 - Stratégie de livraison](#4---stratégie-de-livraison)
    * [4.1 - Sprint 3 : Moteur physique et dessin vectoriel](#41---sprint-3--moteur-physique-et-dessin-vectoriel)
      * [4.1.1 - Livrables spécifiques](#411---livrables-spécifiques)
      * [4.1.2 - Intégration scientifique et mathématique](#412---intégration-scientifique-et-mathématique)
    * [4.2 - Sprint 4 : Rendu visuel et extraction des données](#42---sprint-4--rendu-visuel-et-extraction-des-données)
      * [4.2.1 - Livrables spécifiques](#421---livrables-spécifiques)
      * [4.2.2 - Intégration scientifique et mathématique](#422---intégration-scientifique-et-mathématique)
    * [4.3 - Sprint 5 :](#43---sprint-5--)
      * [4.3.1 - Livrables spécifiques](#431---livrables-spécifiques)
      * [4.3.2 - Intégration scientifique et mathématique](#432---intégration-scientifique-et-mathématique)
  * [5 - Partie individuelle](#5---partie-individuelle)
    * [5.1 - Ngazou, Firas](#51---ngazou-firas)
      * [5.1.1 - Rôles et responsabilités :](#511---rôles-et-responsabilités-)
      * [5.1.2 - Opinions personnelles :](#512---opinions-personnelles-)
    * [5.2 - Nguyen, Quang-Vinh](#52---nguyen-quang-vinh)
      * [5.2.1 - Rôles et responsabilités :](#521---rôles-et-responsabilités-)
      * [5.2.2 - Opinions personnelles :](#522---opinions-personnelles-)
    * [5.3 - Achouri Mehdi](#53---mehdi-achouri)
      * [5.3.1 - Rôles et responsabilités :](#531---rôles-et-responsabilités-)
      * [5.3.2 - Opinions personnelles :](#532---opinions-personnelles-)

## 1 - Vision du projet

### 1.1 - Objectif général

L'objectif général du logiciel est de fournir un outil intéractif qui combine la simulation des fluides et 
l'intelligence artificielle pour permettre à ces utilisateurs de concevoir, visualiser et optimiser différentes formes
personnalisées aérodynamiques en deux dimensions.

### 1.2 - Objectif spécifique

- Permettre aux utilisateurs de dessiner une forme personnalisée à l'aide de vecteurs sur une grille.
- Offrir une simulation en temps réel de l'écoulement de l'air autour de l'obstacle vectoriel dessiné.
- Calculer et afficher les performances aérodynamiques de l'objet, notamment l'affichage du coefficient de traînée.
- Proposer un algorithme d'optimisation capable de modifier automatiquement la géométrie initiale de l'objet pour 
optimiser ses performances.
- Offrir une visualisation graphique claire des résultats (_heatmap_ de la vitesse de l'air et graphique de convergence 
de l'algorithme d'optimisation).

### 1.3 - Considérations scientifiques

- **Mécanique des fluides :** Utilisation de la méthode Lattice-Boltzmann (LBM) dans le but de modéliser le comportement 
macroscopique de l'air de manière stable et physiquement juste.
- **Aérodynamique physique :** Application de la méthode d'échange de quantité de mouvement aux bords de l'obstacle pour 
calculer avec assez de précision le coefficient de traînée ($C_d$) ainsi que le coefficient de portance ($C_l$).
- **Optimisation topologique :** Ajustement automatique des contours de l'obstacle pour minimiser la force de traînée, sous 
la contrainte de respecter une marge de modification stricte.

### 1.4 - Considérations mathématiques

- **Algorithme d'évolution :** Implémentation d'un algorithme génétique pour automatiser l'optimisation de la forme qui aura 
été préalablement dessinée (lié à l'optimisation topologique - 1.3).
- **Algèbre linéaire :** Résolution des équations de collision (modèle **BGK**) et de propagation sur une grille en deux 
dimensions à neuf vitesses discrètes (D2Q9) à l'aide de matrices et de tableaux.
- **Géométrie vectorielle :** Calcul de la distance euclidienne et de l'aire des polygones fermés pour contraindre 
mathématiquement les mutations générées par l'algorithme d'optimisation.

## 2 - Périmètre fonctionnel

### 2.1 - Acteurs du système

Le logiciel s'adresse principalement aux étudiants en sciences (physique) ainsi qu'aux professeurs souhaitant démontrer
les principes de l'aérodynamique de manière visuelle et interactive (comme dans le cadre d'un cours de physique 
mécanique, où on fait souvent l'usage de coefficients de traîné connus pour des formes simples).

### 2.2 - Fonctionnalités principales

- **Création de la géométrie :** L'utilisateur ouvre un nouveau projet et choisi d'utiliser sa souris pour cliquer sur
la grille de dessin. Cette action lui permettra de placer des sommets qui se relient automatiquement entre eux pour 
laisser apparaître le dessin d'une forme. Il peut ensuite décider de modifier sa forme en déplaçant n'importe quel 
sommet de son dessin en cliquant dessus et en le faisant glisser à l'endroit où il souhaite.
- **Analyse :** L'utilisateur ajuste la vitesse de vent souhaitée, puis il lance la simulation. Il peut observer de
manière visuelle, l'air frapper sa forme grâce à l'apparition d'une _heatmap_ et peut aussi lire les coefficients de 
traînée et de portance calculés par le logiciel.
- **Optimisation :** L'utilisateur définit une marge de manœuvre stricte (par exemple, l'algorithme ne peut pas modifier la 
forme initiale que de 10%). Après avoir lancé l'optimisation, il peut regarder un graphique de convergence de 
l'algorithme d'optimisation se dessiner en temps réel, montrant le coefficient de traîné diminuer à chaque génération,
jusqu'à ce que le système lui présente le design final optimisé (Il est important de noter que la forme elle-même change
également à chaque itération de l'algorithme pour montrer son évolution).

### 2.3 - Intrants et extrants

- **Intrants :** Les coordonnées vectorielles de la forme dessinée (cliques de la souris), la vitesse du vent (en m/s), la 
résolution de la grille de calcul et les paramètres de configuration de l'algorithme (tolérance (en %), nombre 
d'itérations et méthode de contrainte).
- **Extrants :** L'affichage graphique intéractif des lignes d'écoulement et du dessin personnalisé, l'affichage des 
coefficients ($C_d$ et $C_l$), le pourcentage d'amélioration de la forme optimisée par rapport à la forme initiale, le 
graphique de convergence de l'algorithme génétique et la _heatmap_ finale de la vitesse de l'air.

### 2.4 - Données persistantes

- **Configuration du système :** Sauvegarde des préférences d'interface et des paramètres de calcul par défaut (résolution 
de la grille, méthode de contrainte de l'IA, tolérance de l'IA, vitesse du vent et nombre d'itérations).
- **Données :** Sauvegarde et chargement d'une session de travail de l'utilisateur (coordonnées de la forme initiale, 
coordonnées de la forme optimisée et résultats finaux de la simulation) dans un fichier ``.json``.

## 3 - Vocabulaire et sémantique du domaine d'application

### 3.1 - Glossaire du domaine

- **Lattice-Boltzmann (LBM) :** Méthode de simulation numérique des fluides qui étudie le déplacement et la collision de 
particules virtuelles sur une grille discrète. Elle permet d'éviter de devoir résoudre des équations différentielles 
très complexes pour simuler les fluides.
- **Bounce-Back :** Condition aux limites dans la méthode LBM où les particules rebondissent dans la direction opposée 
lorsqu'elles percutent un obstacle solide, ce qui nous permet de calculer la force de l'impact.
- **Algorithme génétique :** Type d'intelligence artificielle qui s'inspire de l'évolution naturelle (mutation, sélection 
naturelle) pour trouver une solution optimale à un problème donné.
- **Heatmap :** Représentation graphique de données statistiques où chacune des valeurs sont représentées par des couleurs
(rouge pour rapide, jaune pour moyen, vert pour lent, etc.)
- **Itération :** Dans le contexte de l'IA, l'itération représente un cycle complet de création, d'évaluation et de 
sélection de nouvelles solutions.
- **Vertex/Vertices :** En modélisation en deux dimensions, un _vertex_ est un point défini par des coordonnées (x, y) 
dans l'espace : c'est un **sommet**. Dans le logiciel, l'utilisateur place plusieurs _vertices_ sur une grille pour dessiner 
une forme.
- **Modèle BGK (Batnagar-Gross-Krook) :** C'est la formule mathématique utilisée par le moteur physique lors de l'étape de 
collision. Au lieu de calculer les collisions complexes entre chaque particule d'air, ce modèle simplifie le calcul en
forçant toutes les particules d'un pixel à tendre vers un état d'équilibre à une vitesse définie par la viscosité du 
fluide.

### 3.2 - Dictionnaire des unités et constantes

- **Vitesse macroscopique :** Pour l'utilisateur, la vitesse macroscopique est en m/s. Elle est convertie en Unités Lattice
pour le moteur (méthode LBM).
- **Coefficients aérodynamiques ($C_d$ et $C_l$) :** Valeurs qui ne possèdent pas d'unité (ce sont des coefficients).
- **Marge de tolérance :** Pourcentage (%).
- **Constantes D2Q9 :** Poids statistiques ($w_i$) propres à la méthode LBM et vitesse du son au carré pour la méthode LBM 
($c_s^2 = \frac{1}{3}$).

## 4 - Stratégie de livraison

### 4.1 - Sprint 3 : Moteur physique et dessin vectoriel

#### 4.1.1 - Livrables spécifiques

- Interface graphique de base avec un canevas interactif permettant à l'utilisateur de tracer des polygones (sommets)
- Moteur de simulation LBM fonctionnel capable de faire couler un fluide dans un tunnel vide (pas de visualisation, 
juste une matrice).
- Algorithme de rastérisation pour convertir le dessin vectoriel de l'utilisateur en un masque binaire compatible avec 
le moteur de physique.

#### 4.1.2 - Intégration scientifique et mathématique

Implémentation de la grille D2Q9, de l'équation de collision et de la logique _Bounce-Back_ sur le masque binaire.
Intégration de la compilation JIT pour le moteur de physique.

### 4.2 - Sprint 4 : Rendu visuel et extraction des données

#### 4.2.1 - Livrables spécifiques

- Affichage en temps réel des matrices de vitesse sous forme de _heatmap_.
- Mise en place des options de sauvegarde/chargement et lecture des configurations logicielles (le fichier ``.ini``)
- Affichage des valeurs des coefficients aérodynamiques.

#### 4.2.2 - Intégration scientifique et mathématique

Traduction des rebonds de la méthode LBM en un calcul de force physique réelle pour isoler mathématiquement la traînée 
ainsi que la portance.

### 4.3 - Sprint 5 : 

#### 4.3.1 - Livrables spécifiques

- Moteur d'algorithme génétique fonctionnel capable de générer des mutations géométriques du dessin de l'utilisateur.
- Affichage graphique de convergence de l'algorithme d'optimisation.
- Boutons de contrôle de l'algorithme génétique et affichage du gain de performance en pourcentage.

#### 4.3.2 - Intégration scientifique et mathématique

Implémentation des contraintes géométriques (calcul de l'aire et des limites de distances) pour limiter les mutations de
l'IA et garantir la pertinence de la solution optimale.

## 5 - Partie individuelle

### 5.1 - Ngazou, Firas
#### 5.1.1 - Rôles et responsabilités :

**Conception et développement de l'interface graphique (éditeur vectoriel)**

**Description :** 

Je suis responsable de la création de l'interface graphique intéractive (GUI) du logiciel. Afin de remplir ma tâche, je 
ferai usage des modules PySide6 et numba (JIT) et du langage Python. Ma tâche principale consiste à développer le 
canevas de l'éditeur permettant à l'utilisateur de tracer des polygones (sommets), de les modifier et de les manipuler 
via le placement de sommets (vertices) sur une grille. Je suis également responsable de la liaison des données entre la 
facette arrière du logiciel (back-end) et l'interface graphique (front-end). Cela inclut notamment les menus de 
configuration des contraintes de l'IA et l'affichage des résultats de simulation.

**Limites :**

Mon rôle commence à la capture des entrées de l'utilisateur, soit, des clics de souris sur la grille et des 
modifications apportées aux paramètres de simulation. Ensuite, il consiste en l'envoi de toutes les données (géométries
vectorielles et paramètres) au moteur de simulation. Mon rôle s'arrête à la réception des données calculées pour leur
affichage visuel (résultats de la simulation). Par exemple, je suis responsable d'afficher la forme optimisée, de tracer
la graphique de convergence de l'algorithme d'optimisation et de la _heatmap_ de la vitesse de l'air. Cependant, je ne 
suis pas responsable de programmer la logique mathématique des mutations de l'IA, ni de coder les équations de 
Lattice Boltzmann.

#### 5.1.2 - Opinions personnelles :

**Quelle partie sera la plus difficile à réaliser (en termes de complexité) ? Pourquoi ?**

L'agencement de l'algorithme génétique avec le moteur physique sera le défi technique le plus complexe à mon avis. La
génération d'une matrice binaire à une résolution personnalisée à partir d'une simple liste de sommets, tout en 
s'assurant que les mutations générées par l'IA respectent strictement les contraintes mathématiques préalablement 
établies par l'utilisateur représente, selon moi, un défi majeur. Il faudra éviter à tout prix que l'IA ne génère des
topologies (ensemble de plusieurs sommets liés ensemble) qui sont mauvaises et qui feraient planter la simulation 
physique lors de l'étape de collision.

**Quelle partie sera la plus longue à réaliser (en termes de temps) ? Pourquoi ?**

À mon avis, le développement de l'interface sera la partie la plus exigeante en termes de temps de travail. La création
d'un éditeur vectoriel interactif et intuitif à partir de zéro implique la gestion des événements de clics de souris, le 
déplacement des sommets, et de nombreuses autres fonctionnalités qui prennent du temps à implémenter, surtout qu'elles
nécessitent quelques recherches techniques sur les capabilités de PySide6. L'interface graphique doit également 
idéalement être fluide et conviviale pour l'utilisateur, nécessitant donc une attention particulière au niveau de
l'optimisation de code là où c'est possible. De plus, lié de manière efficace l'interface avec le moteur physique, tout 
en mettant à jour l'affichage sans faire figer l'application, demandera de très nombreuses heures de conception, de test
et de débogage.

**Justifiez comment ce projet vous permet d'intégrer les compétences acquises dans le cadre de votre formation 
collégiale.**

Ce projet final marque la fin de notre parcours en science, informatique et mathématiques pour une bonne raison. Il 
exige l'utilisation de plusieurs concepts théoriques et pratiques vues en classe. Les connaissances acquises lors des 
cours de programmation sont utilisés au maximum à travers l'architecture orientée objet de notre logiciel, le 
développement de l'interface utilisateur et la structuration globale du code. L'algèbre linéaire et la géométrie 
vectorielle sont appliquées de manière concrète à chaque fois que nous manipulons les matrices de simulation ou que
nous gérons les coordonnées des sommets de l'obstacle. Le calcul intégral est utile pour notre compréhension de 
certains processus et de la réelle nature de certaines formules mathématiques (notamment avec le théorème de Green). 
Finalement, les notions vues dans le cours de mathématiques discrètes sont essentiels dans la conception de la logique
combinatoire de l'IA. En bref, ce projet permet la liaison entre multiples compétences de différentes disciplines que 
nous avons acquises au cours de notre formation.

### 5.2 - Nguyen, Quang-Vinh
#### 5.2.1 - Rôles et responsabilités :

**Conception et Implémentation de l'optimisation et de l'évolution génétique**

Mon rôle principal est de concevoir et d'implémenter l'intelligence artificielle qui va optimiser la forme du solide 
dans un tunnel de vent. Cela inclut le codage de la structure de l'algorithme génétique (population de matrices 
binaires, sélection par tournoi, croisement et mutation par segment). Je dois aussi m'assurer que le programme garantit 
que l'IA respecte les contraintes de données, notamment la conservation de l'aire et le maintien d'un certain niveau de 
similarité de n% par rapport à l'état initial.

**Limites de la tâche** : 

Mon rôle commence à la réception de la matrice de segments initiale produite à partir de l'interface utilisateur et des 
paramètres de contraintes associés. Celui-ci se termine lorsque l'algorithme a convergé vers une forme optimale et qu'il 
transmet la matrice finale au module de visualisation pour la génération de la heatmap. Il n'inclut pas le développement 
des équations fondamentales du fluide (Lattice Boltzmann), mais nécessite une collaboration avec le responsable de la 
physique pour l'appel de la fonction de coût.

#### 5.2.2 - Opinions personnelles :

**Quelle partie sera la plus difficile à réaliser (en termes de complexité) ? Pourquoi ?**

La gestion de la mutation avec contraintes de conservation de l'aire. Maintenir une aire constante tout en modifiant 
aléatoirement des segments de la matrice demande une logique assez précise pour ne pas nuire au modèle de physique à 
chaque génération. Dans un algorithme génétique classique, les mutations sont indépendantes et aléatoires. Imposer la 
conservation de l'aire brise cette indépendance. Si une mutation transforme un segment fluide en solide $(0\to 1)$, une 
réparation doit être effectuée ailleurs pour transformer un segment solide en fluide $(1 \to 0)$. Coder cette dépendance 
nécessite une gestion quand même complexe des indices de la matrice avec NumPy pour éviter de créer des formes 
déconnectées qui feraient échouer la simulation de Lattice Boltzmann.

**Quelle partie sera la plus longue à réaliser (en termes de temps) ? Pourquoi ?**

L’implémentation de validation des contraintes géométriques de la matrice. Dans un algorithme génétique standard, les 
mutations sont aléatoires. Cependant, chaque mutation doit être validée et corrigée pour respecter les contraintes 
mathématiques (aire constante, rayon $R_{max}$ et similarité à n%). Le défi technique se trouve dans la création d'un 
algorithme de compensation capable d'ajouter ou de supprimer un segment à un endroit dès qu'une mutation survient, sans 
créer de formes physiquement incohérentes pour la simulation fluide.


**Justifiez comment ce projet vous permet d'intégrer les competences acquises dans votre formation collégiale**

Ce projet regroupe les compétences vues en calcul intégral (calculer l'aire de la forme), en algèbre linéaire et 
géométrie vectorielle (manipulation des vecteurs), en physique (application numérique des formules de la mécanique des 
fluides) et en programmation (l'optimisation d'un problème). Pour le cours de calcul intégral, la compétence appliquée 
consiste à calculer l'aire des formes générées. Cette aire devrait rester constante à travers tout le calcul du 
programme. Pour le cours d'algèbre linéaire et de géométrie vectorielle, les compétences appliquées seront les matrices 
qui serviront à définir l'espace, les mutations et la forme de l'objet. Les opérations de mutation et de croisement sont 
des manipulations algébriques (XOR, masques binaires). Dans le modèle de Lattice Boltzmann (D2Q9), chaque index de la 
matrice contient un espace vectoriel de 9 directions de vitesses. Gérer les interactions entre ces vecteurs et les 
parois de la forme optimisée nécessite une bonne connaissance générale des opérations matricielles. Pour le cours de 
physique, les compétences impliquées sont la compréhension des formules et la capacité de les adapter selon la situation 
présentée. La mécanique des fluides n'est pas une matière que l'on voit au cégep, mais être capable de comprendre 
comment la formule de Lattice Boltzmann fonctionne et être en mesure de l'appliquer à différents contextes est l'une 
des compétences acquises à travers le cégep. Pour le cours d'informatique, les compétences visées consistent en 
l'optimisation du programme, soit l'efficacité du programme ainsi que l'optimisation d'un problème.

### 5.3 - Achouri Mehdi
####  5.3.1 - Rôles et responsabilités :

**Conception et implémentation du moteur physique**

Je m'occuperai de concevoir le moteur physique qui simulera le fluide et la forme ainsi que leurs interactions, le tout 
pour trouver des informations clés dans l'aérodynamisme de la forme simulée.

**Limites de la tâche**

Je m'occuperai de créer le code responsable des calculs physiques pour la simulation. Cela inclut la création de 
l'environnement dans lequel se passe la simulation, la gestion de la physique à l'aide de lois et de formules et le 
calcul des différents coefficients liés à l'aérodynamisme. Toutefois, ma tâche individuelle comprend seulement le code 
en Python ; alors, si nous utilisons un autre langage de code ou une autre méthode utilisant la carte graphique en plus, 
je ne considérerai pas cela comme faisant partie de ma tâche individuelle. Je serai quand même là pour aider, si c'était 
le cas, pour guider mes coéquipiers sur la physique. Mon rôle est donc d'utiliser les données prises pour créer l'espace 
et la forme de sorte à mettre en place la simulation avec la physique que je vais gérer avec mon moteur physique. Ainsi, 
je ne suis pas responsable de la prise de données par l'utilisateur ni d'afficher la simulation, mais de fournir les 
données nécessaires.

#### 5.3.2 - Opinions personnelles :

**Quelle partie sera la plus difficile à réaliser (en termes de complexité) ? Pourquoi ?**

Selon moi, la partie la plus difficile techniquement sera le moteur physique et les autres méthodes alternatives de 
calcul. En effet, c'est une chose de comprendre la théorie, mais l'appliquer à notre projet en programmation est d'un 
autre niveau. Les erreurs et le débogage seront difficiles à réaliser vu que l'on devra créer de zéro un moteur 
physique. De plus, la charge de calcul sera énorme et il faudra alors tenter d'optimiser du code déjà complexe. Sans 
oublier les méthodes alternatives de calcul avec la carte graphique ou en utilisant un autre langage qui nous 
demanderont d'explorer des domaines totalement nouveaux.

**Quelle partie sera la plus longue à réaliser (en termes de temps) ? Pourquoi ?**

Selon moi est celle de l'UI. En effet, bien qu'elle puisse paraître simple techniquement, il s'agit là d'une tâche 
longue et répétitive qui présente ses propres défis. De plus, il y a une multitude d'interfaces à créer, ce qui ne fera 
qu'allonger le temps de développement.

**Justifiez comment ce projet vous permet d'intégrer les competences acquises dans votre formation collégiale**

Notre simulation AeroFlow est un excellent moyen de rassembler nos connaissances acquises lors de notre formation. En 
effet, nous voyons des cas similaires à la physique vue dans la classe de Jean-Philippe. D'ailleurs, la formule proposée 
à la base par Jean-Philippe, prof de physique, s'est avérée primordiale pour trouver le $C_d$ que l'on isole dans la 
formule. En plus, nous utilisons les ressources en programmation que nous avons vue et pratiquée tout au long de notre 
cursus comme NumPy, Qt et la programmation orientée objet.