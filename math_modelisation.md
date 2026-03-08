# Document 2: Fondements mathématiques

Ce document présente le cadre mathématique nécessaire à la simulation d'un tunnel à vent en deux dimensions et à l'optimisation de formes aérodynamiques. La mathématique agit ici comme le moteur de résolution du modèle physique via la méthode de Lattice Boltzmann (LBM) et comme outil d'exploration stochastique à travers un algorithme génétique (GA). L'objectif est de transformer un problème de dynamique des fluides continu en un système discret optimisable par une intelligence artificielle évolutionnaire.


## 2.1 Application de la physique
### 2.1.1 Matrice de la forme

Le domaine de la simulation est de dimensions $H \times L$. Nous définissons la forme de l'objet par une matrice binaire $M$ (ou champ de phase discret) : 

$$M = (m_{ij}) \in \{0, 1\}^{H \times L}$$


Où chaque élément (ou "segment") $m_{ij}$ détermine l'état de l'index à la position $\mathbf{m}_{ij}$ : 

$$m_{ij} = \begin{cases} 1 & \text{si } \mathbf{x}_{ij} \in \text{Obstacle (Solide)} \\ 0 & \text{si } \mathbf{x}_{ij} \in \text{Fluide} \end{cases}$$

### 2.1.2 Matrice des particules

Cette matrice $N$ de dimension $H \times L$ s'agit d'une matrice composé uniquement d'une valeur fixe (Ex. $n_{ij}$ = 1).

Celle-ci aura comme utilité de simuler la répartition des particules dans l'air à l'état d'équilibre. À l'aide de l'équation de Lattice de Boltzmann, 
qui décrit la position à l'équilibre d'une particule :

$$f_i^{eq}(\mathbf{x}, t) = w_i \rho \left( 1 + \frac{ (\mathbf{e}_i \cdot \mathbf{u})}{c_s^2} + \frac{(\mathbf{e}_i \cdot \mathbf{u})^2}{2c_s^4} - \frac{ \mathbf{u}^2}{2c_s^2} \right)$$

Ainsi que l'équation de BGK qui nous permet de trouver la variation de position (le décalage):

$$\Omega_i = \frac{1}\tau (f_i-f_i^{eq})$$


En combinant ces deux formules, nous obtenons la formule :

$$f_{{i}}(\mathbf{x+e_i \Delta t}, t + \Delta t) = f_I(\mathbf{x}, t) + \Omega_i$$

À partir de cette formule, nous serons en mesure de  déterminer la quantité de particules déplacé ainsi que leur position. 

### 2.1.3 Matrice Heatmap

Cette matrice $D$ de dimension $H \times L$ représente la vitesse moyenne de chaque particule ($\mathbf{n}_ij$). À l'état d'équilibre, celle ci serait une matrice de zéros. Il serait possible de calculer la vitesse moyenne de chaque groupe de particule à l'aide de la formule: 

$$\vec{u} = \frac{1}\rho \sum_{i=0}^8 f_i e_i$$

Afin d'être capable de génerer une heatmap, il faudra d'abord trouver la norme de ce vecteur à partir du théorème de Pythagore: 

$$\|\mathbf{\vec{u}}\| = \sqrt{u_x^2 + u_y^2}$$

Pour convertir cette magnitude brute en une valeur unitaire $v_{norm}$ comprise entre 0 et 1 (qui servira d'indice pour la palette de couleurs), on applique la formule de normalisation Min-Max :

$$v_{norm} = \frac{\|\mathbf{\vec{u}}\| - \|\mathbf{\vec{u}}\|_{min}}{\|\mathbf{\vec{u}}\|_{max} - \|\mathbf{\vec{u}}\|_{min}}$$

Puisque la vitesse minimale ne peut pas atteindre une valeur inférieure à zéro, cette équation se simplifie donc en: 

$$v_{norm} = \frac{\|\mathbf{\vec{u}}\|}{\|\mathbf{\vec{u}}\|_{max}}$$

Donc, avec ceci, il est maintenant possible de convertir cette matrice en une heatmap avec la fonction suivante : 

$$Couleur(t) = (1 - t) \cdot RGB_{min} + t \cdot RGB_{max}$$

Où t représente la valeur unitaire $v_{norm}$ calculée comprise entre 0 et 1.



## 2.2 IA

### __2.2.1 Modèle__

Pour le modèle de l'IA, nous allons utiliser le Genetic Algorithm (GA). 
<!-- Nous avons choisi le GA plutot que le GSA parce que l'Algorithme Génétique est beaucoup plus liés au mathématiques comparé au GSA. -->

Le fonctionnement d'un algorithme génétique repose sur une boucle itérative composée de cinq étapes fondamentales appliqués à une population de solutions candidates.



### __2.2.2 Population__

Chaque solution candidate (individu) est représentée par une matrice binaire $M \in \{0, 1\}^{H \times L}$.

- $m_{ij} = 1$ représente un segment solide (obstacle).
- $m_{ij} = 0$ représente un segment fluide (tunnel).

La population à une génération $g$ est un ensemble de $N$ matrices : $P^{(g)} = \{M_1, M_2, \dots, M_N\}$. L'état initial $P^{(0)}$ est généré à partir de la matrice $M_{user}$ fournie par l'utilisateur, à laquelle on applique des perturbations stochastiques légères.



### __2.2.3 Évolution__

__1. Fitness :__

Pour chaque matrice, on calcule le coefficient de traînée $J(M)$ via la simulation Lattice Boltzmann. Puisqu'on souhaite avoir un coefficient de traînée minimale, la fitness sera définie comme : 

$$F(M) = \frac{1}{J(M) + \epsilon}$$

__2. Sélection :__  Les matrices ayant la meilleure fitness seront sélectionnées pour la reproduction. Les matrices qui ne respectent pas les restrictions ou qui ont un coefficient de traînée élevé seront suprimées.

__3. Croisement :__ Deux matrices parentes échangent des segments afin de créer plusieurs enfants, préservant ainsi les structures géométriques importantes

__4. Mutation par segment :__ Chaque élément $m_{ij}$ de la matrice a une probabilité $p_m$ de basculer d'état ($0 \to 1$ ou $1 \to 0$). C'est ici que l'IA test si l'ajout ou le retrait d'un segment spécifique améliore l'aérodynamisme.



### __2.2.4 Restrictions et Contraintes Mathématiques__

__1. Conservation de l'aire :__

La forme doit conserver la même surface que l'état initial pour éviter que l'IA ne minimise la traînée en supprimant simplement tous les segments solides.

Soit $A_0 = \sum m_{ij}^{user}$ l'aire initiale. La contrainte impose :

<!-- formule de l'aire -->
<!-- faire l'intégration à la place (?) -->
$$\sum_{i,j} m_{ij}^{(g)} = A_0$$

Mécanisme : Si une mutation ajoute un segment solide, l'algorithme doit simultanément en supprimer un autre à un endroit moins critique pour maintenir l'équilibre.

__2. Restriction de mobilité :__

Afin d'éviter que les segments ne s'éparpillent sur toute la grille, chaque point solide de la nouvelle forme doit rester à proximité de la structure originale.

Soit $\mathcal{S}_0$ l'ensemble des indices $(i, j)$ où $m_{ij}^{user} = 1$. On impose :

<!-- revérifier la formule -->
$$\forall (i,j) \text{ t.q. } m_{ij} = 1, \quad \min_{(i',j') \in \mathcal{S}_0} \sqrt{(i-i')^2 + (j-j')^2} \le R_{max}$$


Où $R_{max}$ est la distance maximale autorisée pour le déplacement d'un segment.`


__3. Pourcentage de similarité par rapport à la forme originale :__

La forme finale doit ressembler à l'état initial selon un seuil $\Gamma_{seuil}$ (ex: 90%). On utilise la distance de Hamming normalisée pour mesurer cette ressemblance $\gamma$ :

$$\gamma = 1 - \frac{\sum_{i,j} |m_{ij} - m_{ij}^{user}|}{H \times L} \ge \Gamma_{seuil}$$

Si $\gamma$ descend en dessous du seuil, l'individu est considéré comme non-viable (fitness nulle), forçant l'IA à n'explorer que des variations proches du dessin original.

