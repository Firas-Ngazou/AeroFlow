# I - Fondements scientifiques

> #### 420-SF4-RE | Projet d'intégration en sciences, informatique et mathématique

## Table des matières
* [I - Fondements scientifiques](#fondements-scientifiques)
  * [1. Introduction et contexte scientifique](#1-introduction-et-contexte-scientifique)
  * [2. Hypothèses initiales](#2-hypothèses-initiales)
  * [3. Équations fondamentales et relations mathématiques](#3-équations-fondamentales-et-relations-mathématiques)
    * [L'équation de Boltzmann et l'approximation BGK](#léquation-de-boltzmann-et-lapproximation-bgk)
    * [Le lien avec Navier-Stokes (Chapman-Enskog)](#le-lien-avec-navier-stokes-chapman-enskog)
    * [Calcul des variables macroscopiques et forces](#calcul-des-variables-macroscopiques-et-forces)
  * [4. Résolution numérique](#4-résolution-numérique)
    * [Streaming](#streaming)
    * [Implémentation des limites (Bounce-Back)](#implémentation-des-limites-bounce-back)
  * [5. Lexique scientifique](#5-lexique-scientifique)
  * [6. Bibliographie](#6-bibliographie)

## 1. Introduction et contexte scientifique

L'objectif de notre projet est de créer un logiciel qui simule l'aérodynamisme d'une forme dans un tunnel à vent. Dans 
cette optique, nous avons contacté l'enseignant de physique mécanique Jean-Philipe Cournoyer. Suite à notre rencontre, 
nous avions déterminé que le meilleur moyen de calculer l'aérodynamisme d'une forme serait d'agencer une série de 
plusieurs plaques pour former la carrosserie d'un objet en 2D, en calculant le frottement de l'air sur chacune de ces 
plaques. Cela aurait été fait avec la formule de la force de traînée vue lors du cours de physique mécanique : 

$$F_d = \frac{1}{2} \rho v^2 C_d A$$

Issues des équations de Navier-Stokes, ces équations permettent de décrire le mouvement des fluides tels que l'air. De 
nos jours, les scientifiques et mathématiciens savent utiliser ces équations, mais n'en maîtrisent pas toutes les 
facettes (les défis que représentent ces équations ont d'ailleurs été inscrits dans les problèmes mathématiques du 
siècle). 

Malheureusement, cette formule s'est avérée obsolète pour notre cas. En effet, cette formule ne s'applique que quand 
l'objet dont on calcule la force de traînée est seul dans l'air. En d'autres mots, il devient impossible de calculer le 
frottement de l'air de deux plaques à la suite vu que l'écoulement de l'air affecterait les autres plaques, ce qui 
augmenterait considérablement la difficulté sans apporter de valeur significative pour le projet.

Pour les raisons précédemment citées, nous avons décidé d'utiliser la méthode de Lattice-Boltzmann (LBM). 
Cette méthode nous permettra de trouver un résultat plus intéressant visuellement, de mieux s'adapter à notre vision du 
projet et de faciliter l'intégration d'un modèle physique à la hauteur de nos capacités.

Grâce à cette technique, nous pouvons voir en temps réel l'évolution de la traînée et des turbulences. Les turbulences 
sont dues au phénomène de décollement qui arrive quand l'air suit une surface, mais qu'il y a un angle trop élevé pour 
que le flux d'air suive la forme de l'objet. Dans notre cas, cela arrive quand le flux d'air arrive à l'arrière de 
l'objet et que celui-ci n'a plus assez d'énergie pour suivre la forme, et s'en décolle (d'où son nom). Ainsi, une zone 
de basse pression est créée et des tourbillons s'y forment. Dans ce contexte, cette méthode sera parfaite pour voir 
comment les masses d'air se comportent avec une forme à pleine vitesse et pour trouver la constante de traînée pour les 
différents véhicules que nous allons tester.

## 2. Hypothèses initiales

La modélisation d'un fluide complexe comme l'air nécessite des simplifications fondamentales pour que le calcul soit 
réalisable par notre moteur en temps réel. Voici les hypothèses de travail adoptées et justifiées :

- **1. Écoulement bidimensionnel (2D) :** Nous supposons que le fluide s'écoule uniquement sur les axes X et Y, 
négligeant la profondeur (Z). L'objet simulé est donc considéré comme un cylindre infini. Bien que cette hypothèse 
réduise la précision du modèle concernant les turbulences réelles (qui sont tridimensionnelles dans la nature), elle 
divise drastiquement la complexité algorithmique, permettant une résolution fluide sur des ordinateurs standards.


- **2. Fluide incompressible :** Nous considérons que la densité $\rho$ de l'air reste globalement constante et que sa 
température ne varie pas (pas de transfert de chaleur). Le modèle LBM est valide sous cette hypothèse tant que le nombre 
de Mach reste faible ($Ma < 0.3$). L'impact de ce choix est que notre simulation n'est valide que pour des écoulements 
subsoniques lents (comme des véhicules de route), et ne pourrait pas modéliser l'aérodynamisme d'un avion de chasse 
dépassant le mur du son.

## 3. Équations fondamentales et relations mathématiques

### L'équation de Boltzmann et l'approximation BGK

Les fondements physiques de notre simulation reposent sur l'équation de Boltzmann, qui permet de représenter les 
collisions pour un fluide. Dans ce cas, $f_i$ représente la valeur théorique de la densité de molécules qui se déplacent 
vers la direction $i$, et $f_i^{eq}$ représente l'état d'équilibre local. Plus la différence entre $f_i$ et $f_i^{eq}$ 
est grande, plus le fluide est perturbé. 

Lors de la simulation, les particules du fluide vont faire deux choses principales : se propager et collisionner. Ces 
comportements sont simulés en utilisant l'approximation de BGK qui stipule : 

$$(\partial_t + \mathbf{v} \cdot \nabla) f = -\frac{f - f^{eq}}{\tau}$$

Ici, $\tau$ est le taux de relaxation qui représente l'échelle de temps caractéristique pour que le système retrouve son 
équilibre. Bien que cela ne soit pas utile dans notre cas direct, il est intéressant de notifier qu'il existe une 
relation stricte entre $\tau$ et la viscosité cinématique $\nu$ du fluide.



### Le lien avec Navier-Stokes (Chapman-Enskog)
Cette formule a un lien direct avec les équations de Navier-Stokes sur les fluides incompressibles. L'analyse de 
Chapman-Enskog est le pont qui permet de prouver que simuler le comportement d'un fluide avec la méthode de 
Lattice-Boltzmann revient à simuler un fluide réel régi par les équations de Navier-Stokes :

$$f = f^{(0)} + \epsilon f^{(1)} + \epsilon^2 f^{(2)} + \dots$$

L'analyse permet de rectifier le comportement réel d'un fluide en utilisant les séries de Taylor. Analysons cette 
formule : d'abord, $f^{(0)}$ représente la fonction qui décrit le comportement théorique du fluide. Ensuite, on commence 
à ajouter des corrections, comme $\epsilon f^{(1)}$ qui représente le comportement du fluide par rapport à sa viscosité. 
Dans ce cas-là, le paramètre $\epsilon$ (nombre de Knudsen) représente l'écart par rapport à l'équilibre. Ainsi de 
suite, le comportement du fluide va être corrigé pour simuler le vrai comportement de l'air.

### Calcul des variables macroscopiques et forces
Pour trouver $\rho$, qui représente la masse volumique du fluide qui se déplace, on doit faire la somme du déplacement 
du fluide $f$ dans toutes les directions $i$ : 

$$\rho = \sum_i f_i$$

Avec cette équation comme base, on peut trouver la quantité de mouvement $\rho \mathbf{u}$ où l'on trouve le produit de 
la densité et de la vitesse macroscopique : 

$$\rho \mathbf{u} = \sum_{i=0}^{8} f_i \mathbf{v}_i$$

Pour évaluer les performances de notre forme aérodynamique, nous devons trouver le coefficient de traînée ($C_d$) et de 
portance ($C_l$). Cela est possible car on peut trouver les forces qui sont en contact avec la forme en isolant ces 
coefficients dans nos formules : 

$$C_d = \frac{2F_d}{\rho u^2 A} \quad \text{et} \quad C_l = \frac{2 F_l}{\rho u^2 A}$$

La force totale sur l'objet est un vecteur possédant deux composantes ($X$ pour la traînée $F_d$ et $Y$ pour la portance 
$F_l$). On trouve cette force $\vec{F}_{total}$ via l'échange de quantité de mouvement :

$$\vec{F} = \sum_{\vec{x}_b} \sum_{i} \left[ f_i(\vec{x}_b, t) + f_{\bar{i}}(\vec{x}_b, t^*) \right] \mathbf{c}_i$$

Dans cette formule, $\vec{x}_b$ représente les points de la forme, $i$ le sens dans lequel le fluide se déplace, et 
$\bar{i}$ le sens opposé. La composante $\mathbf{c}_i$ représente le vecteur vitesse (la direction initiale du fluide). 
Pour finir, $f_i + f_{\bar{i}}$ représente l'aller-retour de la particule qui crée le frottement.

## 4. Résolution numérique

Maintenant que nous avons la formule qui décrit le comportement du fluide, on doit rendre la formule compatible avec une 
grille en la discrétisant. Cette méthode consiste à créer une grille de l'espace en 2D de taille $N_x \times N_y$ pour 
calculer l'écoulement de l'air. Cela est possible en calculant l'effet de l'écoulement d'un point sur les 9 points qui 
l'entourent. On utilise la géométrie du réseau D2Q9, qui nous impose de discrétiser pour travailler en 2 dimensions avec 
9 vecteurs de vitesse $\mathbf{v}_i$.

La variable de poids $w_i$ sert à compenser les différences de longueur (diagonales vs orthogonales) pour garder une 
isotropie du fluide. En d'autres mots, on assigne des poids scalaires aux différentes directions pour que les propriétés 
du fluide restent les mêmes dans tous les cas.

### Streaming

Maintenant que l'on a nos variables, on peut calculer $f_i^{eq}$ pour connaître le comportement du fluide à la prochaine 
itération : 
$$F_i^{eq} = w_i \rho \left( 1 + 3(\mathbf{v}_i \cdot \mathbf{u}) + \frac{9}{2}(\mathbf{v}_i \cdot \mathbf{u})^2 - 
\frac{3}{2}(\mathbf{u} \cdot \mathbf{u}) \right)$$

Les coefficients sont propres au réseau D2Q9 et sont liés à la vitesse à laquelle les particules se déplacent (vitesse 
du son du réseau) : $c_s = \frac{1}{\sqrt{3}}$. Cette valeur assure que le comportement du fluide respecte 
Navier-Stokes.

L'équation de Boltzmann discrétisée sépare le problème en deux étapes (Collision et Streaming) :
$$F_i(\mathbf{x}_i + \mathbf{v}_i\Delta t, t + \Delta t) - F_i(\mathbf{x}_i, t) = -\frac{F_i(\mathbf{x}_i, t) - 
F_i^{eq}(\mathbf{x}_i, t)}{\tau}$$

- **L'étape de collision (Côté droit) :** $-\frac{F_i - F_i^{eq}}{\tau}$. Représente la différence de densité due aux 
chocs entre particules.

- **L'étape de streaming (Côté gauche isolé) :** $f_i(\mathbf{x} + \mathbf{v}_i \Delta t, t + \Delta t) = 
f_i^*(\mathbf{x}, t)$. Représente le fluide après la collision ($f_i^*$) qui se propage vers sa destination au temps 
$\Delta t$.

### Implémentation des limites (Bounce-Back)

Pour implémenter la forme souhaitée, on utilise le concept de rebond (*Bounce-Back*). Quand le fluide rentre 
en contact avec un point de la grille qui fait partie de la forme, $f_i$ ne traverse pas l'objet, mais est renvoyé dans 
la direction opposée d'arrivée ($f_{\bar{i}}$). Cette condition fait en sorte que la vitesse du fluide devient nulle 
directement sur la paroi de la forme. Le frottement se crée alors via la collision entre le fluide immobile sur la 
surface et le fluide qui circule à pleine vitesse juste au-dessus.

## 5. Lexique scientifique

- $\rho$ **(Masse volumique)** : Représente la densité du fluide, exprimée en kilogrammes par mètre cube ($kg/m^3$). 
Dans le réseau LBM discret, elle est souvent normalisée autour de 1.
- $u$ ou $\mathbf{v}$ **(Vitesse macroscopique)** : Vitesse de déplacement du flux d'air, exprimée en mètres par seconde 
($m/s$).
- $F_d$ **(Force de traînée)** : Résistance aérodynamique opposée au mouvement par le fluide, exprimée en Newtons ($N$), 
soit $kg \cdot m/s^2$.
- $F_l$ **(Force de portance)** : Force perpendiculaire au flux d'air, exprimée en Newtons ($N$).
- $C_d$ et $C_l$ **(Coefficients aérodynamiques)** : Grandeurs adimensionnelles (sans unité) représentant l'efficacité 
de la forme face à la résistance et à la portance.
- $A$ **(Aire de référence)** : Surface de contact de l'obstacle, exprimée en mètres carrés ($m^2$).
- $\tau$ **(Temps de relaxation)** : Paramètre de l'approximation BGK contrôlant le retour à l'équilibre, exprimé en 
secondes ($s$).
- $\nu$ **(Viscosité cinématique)** : Résistance à l'écoulement du fluide, liée proportionnellement à $\tau$. 
Elle s'exprime en mètres carrés par seconde ($m^2/s$).
- $c_s$ **(Vitesse du son du réseau)** : Vitesse de propagation au réseau D2Q9, exprimée en mètres par 
seconde ($m/s$).

## 6. Bibliographie

[1] Mocz, P. (2020). _Create Your Own Lattice Boltzmann Simulation (With Python)_. Medium. 
https://medium.com/swlh/create-your-own-lattice-boltzmann-simulation-with-python-8759e8b53b1c

[2] Wikipédia. (2026). _Équations de Navier-Stokes_. 
https://fr.wikipedia.org/wiki/%C3%89quations_de_Navier-Stokes

[3] Google Gemini (3.1 Pro). _Comprendre l'équation de Boltzmann et les hypothèses de fluides, aide à la compréhension 
de l'approximation BGK, du phénomène de décollement et intégration du formalisme des contraintes de l'analyse de 
Chapman-Enskog_. Consulté le 10 mars 2026.
