# II - Fondements mathématiques

> #### 420-SF4-RE | Projet d'intégration en sciences, informatique et mathématique

## Table des matières

* [II - Fondements mathématiques](#ii---fondements-mathématiques)
  * [1 - Introduction](#1---introduction)
  * [2 - Structures mathématiques](#2---structures-mathématiques)
    * [2.1 - L'espace même de la simulation (grille d'édition) :](#21---lespace-même-de-la-simulation-grille-dédition-)
    * [2.2 - L'espace vectoriel de l'IA :](#22---lespace-vectoriel-de-lia-)
  * [3 - Démonstrations formelles](#3---démonstrations-formelles)
    * [3.1 - Démonstration de la restriction d'aire (théorème de Green) :](#31---démonstration-de-la-restriction-daire-théorème-de-green-)
    * [3.2 - Démonstration de la restriction de mobilité :](#32---démonstration-de-la-restriction-de-mobilité-)
  * [4 - Transition du modèle mathématique continu à sa résolution numérique](#4---transition-du-modèle-mathématique-continu-à-sa-résolution-numérique)
    * [4.1 - La collision (modèle BGK) :](#41---la-collision-modèle-bgk-)
    * [4.2 - La propagation :](#42---la-propagation-)
    * [4.3 - Justification de la méthode :](#43---justification-de-la-méthode-)
  * [5 - Modélisation mathématique de la visualisation (heatmap)](#5---modélisation-mathématique-de-la-visualisation-heatmap)
    * [5.1 - Calcul de la vitesse macroscopique :](#51---calcul-de-la-vitesse-macroscopique-)
    * [5.2 - Calcul de la force du vent (théorème de Pythagore) :](#52---calcul-de-la-force-du-vent-théorème-de-pythagore-)
    * [5.3 - Normalisation et coloration :](#53---normalisation-et-coloration-)
  * [6 - Modélisation mathématique de l'intelligence artificielle](#6---modélisation-mathématique-de-lintelligence-artificielle)
    * [6.1 - La fitness :](#61---la-fitness-)
    * [6.2 - La mutation :](#62---la-mutation-)
    * [6.3 - Application de la méthode de contrainte :](#63---application-de-la-méthode-de-contrainte-)
    * [6.4 - La ressemblance finale (distance de Hamming) :](#64---la-ressemblance-finale-distance-de-hamming-)
  * [7 - Lexique mathématique](#7---lexique-mathématique)
  * [8 - Bibliographie](#8---bibliographie)

## 1 - Introduction

Ce document consiste en l'explication des mathématiques qui se cachent derrière notre projet. Comme il l'a déjà été 
spécifié, notre projet consiste en une simulation de tunnel à vent en deux dimensions dans laquelle sera intégré un 
algorithme génétique.
Afin de permettre au système de comprendre tout ce qui se passe, nous devons traduire le vent et les objets de la 
simulation en chiffres, en matrices et en vecteurs. Les mathématiques jouent deux rôles très importants dans ce projet :
elles agissent comme moteur de résolution pour calculer le mouvement du vent (grâce à la méthode de Lattice Boltzmann),
et elles servent d'outil pour contraindre les agissements de l'intelligence artificielle. L'objectif est donc de rendre 
un problème complexe de dynamique des fluides facilement calculable et optimisable par notre programme.

## 2 - Structures mathématiques

Afin de représenter le monde virtuel de notre logiciel, nous utiliserons deux espaces mathématiques distincts :

---
**2.1 - L'espace même de la simulation (grille d'édition) :**

Le domaine de la simulation consiste en une grande grille cartésienne de dimensions $H \times L$ (hauteur fois largeur).
Le système voit le dessin de l'utilisateur sous la forme d'une matrice binaire $M$ (ou champ de phase discret) :

$$M = (m_{ij}) \in \{0, 1\}^{H \times L}$$

Où chaque élément détermine l'état à la position donnée. 1 pour un élément solide (obstacle) et 0 pour un segment vide
(fluide/air).
---
**2.2 - L'espace vectoriel de l'IA :**

Pour l'algorithme chargé d'améliorer la forme initiale de l'objet, la simple utilisation d'une matrice de pixels serait
trop inefficace. Chaque solution candidate (individu) est plutôt représentée par les coordonnées de ses sommets dans un
espace vectoriel en deux dimensions. Un dessin ($V$) contenant $K$ sommets (vertexes) peut être défini comme suit :

$$V = \begin{bmatrix} \mathbf{v}_1 \\ \mathbf{v}_2 \\ \vdots \\ \mathbf{v}_K \end{bmatrix} \quad \text{où} \quad 
\mathbf{v}_k = (x_k, y_k) \in \mathbb{R}^2$$

## 3 - Démonstrations formelles

**3.1 - Démonstration de la restriction d'aire (théorème de Green) :**

Afin d'éviter que l'IA ne triche dans sa recherche d'une solution optimale (par exemple, en effaçant complètement la 
forme préalablement dessinée par l'utilisateur pour réduire la résistance de l'air à zéro), on utilise des restrictions 
mathématiques. L'utilisateur aura le choix entre deux méthodes de contrainte et celle d'aire en est une. Ce qu'elle 
propose, c'est que la forme se doit de conserver la même surface que le dessin original de l'utilisateur à chaque 
génération d'individu. Nous devons donc démontrer que l'aire d'un polygone peut être calculée algébriquement à partir 
des sommets $\mathbf{v}_k$.

Par le théorème de Green, l'aire $A$ d'un domaine délimité par une courbe fermée simple $C$ est donnée par l'intégrale
curviligne :

$$A = \oint_C xdy = -\oint_C ydx = \frac{1}{2}\oint_C(-ydx + xdy)$$

Comme cette intégrale a besoin d'avancer pas à pas pour calculer la surface, mais que nous n'avons que des points fixes
sur le dessin, on doit pouvoir exprimer la position de chaque morceau entre deux points fixes en fonction du 
pourcentage de la distance entre ces deux points.
Puisque notre forme est justement constituée de simples segments de droites reliant nos sommets, cela devient très 
simple. Pour un segment entre $(x_k, y_k)$ et $(x_{k+1}, y_{k+1})$ où $t \in [0, 1]$, $t$ étant le pourcentage de la 
distance entre les deux points :

$$x(t) = x_k + t(x_{k+1} - x_k)$$
$$y(t) = y_k + t(y_{k+1} - y_k)$$

En dérivant ces deux dernières équations, on obtient :

$$dx = (x_{k+1} - x_k)dt$$
$$dy = (y_{k+1} - y_k)dt$$

$x_{k+1} - x_k$ noté $\Delta x$ et $y_{k+1} - y_k$, $\Delta y$, lorsque l'on substitue cela dans notre intégrale pour un
seul segment $S_k$ :

$$\int_{S_k} (xdy - ydx) = \int_{t=0}^{t=1} ((x_k + t\Delta x)\Delta y - (y_k + t\Delta y)\Delta x)dt$$

En développant et en simplifiant :

$$\int_0^1 (x_k\Delta y - y_k\Delta x)dt = x_k(y_{k+1} - y_k) - y_k(x_{k+1} - x_k) = x_ky_{k+1}-y_kx_{k+1}$$

En utilisant cette relation sur tous les $K$ segments de la forme, nous obtenons la formule des lacets :

$$A(V) = \frac{1}{2} |\sum_{k=1}^{K} (x_ky_{k+1}-y_kx_{k+1})|$$

**3.2 - Démonstration de la restriction de mobilité :**

Si cette méthode est choisie plutôt que la précédente, l'aire de la figure peut changer, mais aucun sommet ne peut trop
s'éloigner de sa position initiale. Afin de vérifier cela, on calcule la distance en ligne droite entre un sommet et sa 
position initiale (la norme euclidienne basée sur le théorème de Pythagore).
Pour chaque somme $\mathbf{v}_k^{initial}$, le logiciel trace mathématiquement un cercle de rayon $R_{max}$ autour du 
point d'origine. Cette méthode de validation consiste à s'assurer que le nouveau sommet n'est pas sorti de ce cercle.
Un individu $V$ est géométriquement valide seulement si tous ses nouveaux sommets respectent l'inéquation de 
distance :

$$\forall k \in \{1, ..., K\}, \sqrt{(x_k^{nouveau} - x_k^{initial})^2 + (y_k^{nouveau} - y_k^{initial})^2} \leq R_{max}
$$

## 4 - Transition du modèle mathématique continu à sa résolution numérique

Dans la réalité, l'air est un fluide complexe dont le mouvement peut être décrit par les équations différentielles de 
Navier-Stokes. Résoudre ces équations directement demande des calculs extrêmement lourds et complexes, faisant de cette
tâche un vrai cauchemar, même pour les plus grands experts.
Pour notre projet, nous effectuerons une transition vers le numérique en décidant qu'au lieu de considérer le vent comme
un seul gros bloc d'air, on le considère plutôt comme des millions de petites particules sur notre grille. Il s'agit là
de la méthode de Lattice Boltzmann (LBM).

Nous passons donc à un modèle D2Q9 (2 dimensions, 9 directions possibles $e_i$). L'équation de calcul du fluide peut 
donc facilement se résumer à deux principales étapes :

**La collision (modèle BGK) :**

L'air est un fluide visqueux, donc, les particules qui le composent se rentrent constamment dedans. On calcule ce 
décalage de position causé par une collision vers un état d'équilibre $f^{eq}$ avec un paramètre de relaxation $\tau$ :

$$\tilde{f}_i(x, t) = f_i(x, t) - \frac{1}{\tau}(f_i(x,t) - f^{eq}(x, t))$$

**La propagation :**

Les particules ont une envie naturelle d'avancer vers la cellule voisine :

$$f_i(x + e_i\Delta t, t + \Delta t) = \tilde{f}_i(x, t)$$

**Justification de la méthode :**

En combinant ces deux étapes cruciales, nous sommes en mesure de déterminer la nouvelle position des particules avec des
calculs beaucoup plus simples que ceux nécessaires à la résolution d'équations différentielles complexes de 
Navier-Stokes. Le choix de la méthode LBM sert donc à minimiser la charge de calcul, rendant la réalisation de ce projet
tout en nous permettant de créer un écoulement d'air réaliste capable de rebondir facilement sur les surfaces définies 
dans notre matrice binaire $M$.

## 5 - Modélisation mathématique de la visualisation (heatmap)

Pour que l'utilisateur puisse comprendre le comportement du vent, le logiciel doit transformer des millions de données
(particules de la LBM) en une carte de chaleur (heatmap). Ce processus repose sur trois principales étapes 
mathématiques :

**Calcul de la vitesse macroscopique :**

Le logiciel commence donc par calculer la vitesse du vent $\mathbf{u}$ sur chaque cellule de la grille. Pour cela, il 
fait simplement la moyenne de toutes les directions $e_i$ des particules présentent sur la cellule :

$$\mathbf{u} = \frac{1}{\rho} \sum_{i=0}^{8} f_ie_i$$

Où $\rho$ est la densité locale de la cellule.

**Calcul de la force du vent (théorème de Pythagore) :**

Le vecteur vitesse $\mathbf{u}$ possède une composante horizontale $u_x$ et une composante verticale $u_y$. Pour 
connaître la force du vent sur une cellule, on calcule, à l'aide du théorème de Pythagore, la norme de ce vecteur :

$$||\mathbf{u}|| = \sqrt{u_x^2 + u_y^2}$$

**Normalisation et coloration :**

Pour choisir la bonne couleur de chaque cellule, on transforme cette norme en un pourcentage $v_{norm}$ (entre 1 et 0). 
S'il n'y a pas de mouvement de vent sur la cellule, alors $v_{norm} = 0$ tandis que si le vent souffle à la vitesse 
maximale enregistrée, $v_{norm} = 1$ :

$$v_{norm} = \frac{||\mathbf{u}||}{||\mathbf{u}||_{max}}$$

Pour finir, on utilise ce pourcentage pour choisir la couleur de la cellule. On procède ici par interpolation linéaire.
En d'autres termes, on mélange mathématiquement deux couleurs de base (du bleu pour du vent calme et du rouge pour du 
vent fort, par exemple) pour obtenir une couleur finale :

$$Couleur = (1 - v_{norm}) \times RGB_{bleu} + v_{norm} \times RGB_{rouge}$$

## 6 - Modélisation mathématique de l'intelligence artificielle

Pour que notre algorithme génétique puisse trouver la forme la plus aérodynamique possible, il s'appuie sur des 
processus mathématiques et statistiques précis.

**La fitness :**

Pour chaque individu $V$, le moteur calcule le coefficient de traînée $C_d(V)$. Puisqu'on souhaite minimiser cette 
valeur, la fonction de fitness $F(V)$ attribue un score élevé aux faibles valeurs de $C_d$ :

$$F(V) = \frac{1}{C_d(V) + \epsilon}$$

**La mutation :**

Pour éviter de créer des formes trop chaotiques, la modification d'un sommet $\Delta \mathbf{v}$ n'est pas uniforme, 
mais suit plutôt une distribution normale. Chaque sommet a une probabilité de se déplacer selon la formule :

$$\mathbf{v}_k^{nouveau} = \mathbf{v}_k + \alpha \times \mathcal{N}(0, \sigma^2)$$

Où $\mathcal{N}(0, \sigma^2)$ est une valeur générée aléatoirement favorisant les petits déplacements (proches de 0).

**Application de la méthode de contrainte :**

Tout dépendamment du choix de l'utilisateur dans l'interface graphique, l'algorithme génétique appliquera soit la 
méthode de validation par la formule des lacets pour s'assurer que l'aire $A(V)$ reste constante, soit celle de la 
validation par la distance pour s'assurer qu'aucun sommet ne sort de la zone délimitée par le rayon $R_{max}$. Si le 
mutant échoue le test de la méthode sélectionnée, sa fitness sera mauvaise.

**La ressemblance finale (distance de Hamming) :**

Une fois la forme reconvertie en matrice binaire $M$, l'algorithme vérifie qu'elle ressemble toujours au dessin original
$M_{user}$. Nous utiliserons un calcul de distance mathématique pixel par pixel :

$$\gamma = 1 - \frac{1}{H \times L} \sum_{i, j} |m_{ij} - m_{ij}^{user}| \ge \Gamma_{seuil}$$

Si $\gamma$ descend en dessous du seuil autorisé (ex : 90%), la forme est rejetée.

## 7 - Lexique mathématique

- $\mathbb{R}^2$ : Espace vectoriel réel à deux dimensions.
- $\mathcal{M}_{H \times L}$ : Ensemble des matrices de dimensions $H \times L$. 
- $\mathbf{v}_k$ : Vecteur spatial représentant un sommet géométrique du dessin.
- $\sum$ : Opérateur de sommation discrète.
- $\oint$ : Intégrale curviligne sur un contour fermé.
- $\Delta t$ : Pas de discrétisation temporelle.
- $f_i$ : Fonction de distribution (probabilité de présence d'une particule dans la direction $i$). 
- $\tau$ : Temps de relaxation, un paramètre lié à la viscosité du fluide.
- $\mathcal{N}(0, \sigma^2)$ : Distribution normale (Gaussienne) de moyenne 0 et variance $\sigma^2$.
- $\gamma$ : Taux de similarité global entre deux matrices.
- $\Gamma_{seuil}$ : Seuil minimal de ressemblance exigé par l'utilisateur.

## 8 - Bibliographie

[1] Geeksforgeeks. (2026). _Genetic Algorithms_. 
https://www.geeksforgeeks.org/genetic-algorithms/

[2] Wikipédia. (2026). _Green's theorem_.
https://en.wikipedia.org/wiki/Green%27s_theorem

[3] MathWorks. (2026). What is the genetic algorithm? 
https://www.mathworks.com/help/gads/what-is-the-genetic-algorithm.html

[4] Paul's Online Math Notes. (2026). _Calculus III - Line Integrals - Section 16.7: Green's Theorem_.
https://tutorial.math.lamar.edu/classes/calciii/GreensTheorem.aspx

[5] Wikipedia. (2025). _Distance de Hamming_. 
https://fr.wikipedia.org/wiki/Distance_de_Hamming

[6] Wikipedia. (2026). _Shoelace formula_. 
https://en.wikipedia.org/wiki/Shoelace_formula

[7] Medium. (2025). _The Lattice Boltzmann Method_.
https://medium.com/@ethan_beddard/the-lattice-boltzmann-method-lbm-fluid-simulation-43a4fa248614

[8] Google Gemini (3.1 Pro). _Explication de la méthode LBM et de l'algorithme génétique, aide à la recherche de 
formules et de solutions mathématiques_. Consulté le 2 mars 2026. 