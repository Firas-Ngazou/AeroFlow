# III. Modélisation.md

## 1. Introduction et synthèse du projet

L'objectif de notre projet, PyTunnel, est de créer un logiciel interactif qui simule l'aérodynamisme d'une forme dans un tunnel à vent et qui l'optimise de façon autonome. Dans cette optique, nous avons dû concevoir un système capable de comprendre la mécanique des fluides tout en appliquant des règles strictes d'évolution géométrique. 

Ce document représente la synthèse de notre travail de modélisation. Il montre comment nous avons réussi à atteindre nos objectifs en fusionnant la physique de l'air avec les mathématiques discrètes et l'intelligence artificielle. Plutôt que de voir la physique et les mathématiques comme deux choses séparées, ce document explique le pont qui relie le comportement de notre vent virtuel (Lattice-Boltzmann) aux mutations de notre algorithme génétique.

## 2. Résultats finaux de la modélisation

Suite à nos recherches et à la conception théorique, nous avons obtenu deux résultats finaux majeurs qui forment la base de notre logiciel, sans avoir à refaire les démonstrations complexes des documents précédents.

**Du côté scientifique (Document I) :**
Nous avons réussi à modéliser le comportement de l'air de manière très performante sans utiliser directement les lourdes équations de Navier-Stokes. Le résultat final est l'utilisation de la méthode LBM avec l'approximation de collision BGK. Cela nous donne une formule de mise à jour simple où le fluide se propage et rebondit sur notre objet :
$$f_i(\mathbf{x} + \mathbf{v}_i \Delta t, t + \Delta t) = f_i(\mathbf{x}, t) - \frac{1}{\tau} [f_i(\mathbf{x}, t) - f_i^{eq}(\mathbf{x}, t)]$$
C'est grâce à cette technique que l'on peut calculer la force de traînée totale ($F_d$) et obtenir le coefficient de traînée ($C_d$) de n'importe quelle forme de façon numérique.

**Du côté mathématique (Document II) :**
Nous avons obtenu un cadre mathématique strict pour encadrer notre intelligence artificielle. Le résultat final est notre fonction de survie (Fitness) qui évalue les formes :
$$F(V) = \frac{1}{C_d(V) + \epsilon}$$
Et pour s'assurer que l'IA ne triche pas en effaçant la forme, nous avons mis en place deux restrictions mathématiques finales : la conservation de l'aire avec le théorème de Green discret, et la restriction de mobilité avec la distance euclidienne.

## 3. Articulation entre les sciences et les mathématiques

Maintenant, analysons comment ces éléments s'articulent pour répondre à la problématique du projet. Le défi principal était de faire communiquer un espace vectoriel (le dessin de l'IA) avec une grille discrète de fluide (la physique).



Le processus de notre programme s'imbrique de la façon suivante :
1. **Génération mathématique :** L'algorithme génétique (Mathématiques) crée une population de vecteurs qui représentent plusieurs variations de la voiture.
2. **Traduction :** Ces vecteurs sont transformés en une matrice binaire de zéros et de uns pour que la physique puisse la lire.
3. **Simulation physique :** Le moteur Lattice-Boltzmann (Sciences) prend cette matrice binaire, fait souffler le vent virtuel dessus, calcule les turbulences, et nous retourne la valeur de la force de traînée ($F_d$).
4. **Sélection et évolution :** La mathématique reprend le relais. Elle utilise ce $F_d$ calculé par la science pour donner une note à la forme. Ensuite, avec des formules de probabilités (distribution normale), elle fait muter les meilleurs dessins pour la prochaine génération.

Ainsi, la physique sert de guide, tandis que les mathématiques sont les outils pour arriverau bon déroulement  à résoudre le tout. Finalement, on comprend qu'il s'agit des deux cotès d'une même pièce qui sont indissociable de la simulation

## 4. Compromis et impacts sur le modèle final

Lors de la conception, certaines idées se sont avérées obsolètes ou trop lourdes pour notre cas. Pour que la simulation reste fluide sur un ordinateur normal, nous avons dû faire certains compromis :

- **L'abandon de la 3D :** Comme spécifié dans les hypothèses du _Document I_, nous avons réduit l'espace à deux dimensions (D2Q9). L'impact est que les turbulences générées derrière l'objet ne reflètent pas parfaitement la réalité (qui est toujours en 3D), mais cela divise le temps de calcul par un facteur énorme, ce qui apporte une valeur significative pour les performances du projet.
- **Le fluide incompressible :** Le modèle considère que l'air ne se compresse pas et ne change pas de température. L'impact direct est que notre logiciel ne peut simuler que des objets allant à des vitesses subsonique (vitesse inférieure à la vitesse du son).

- **L'absence d'animation en temps réel pour l'IA :** Générer une simulation visuelle de l'air pour chaque mutant de l'IA prenait trop de ressources. Le compromis a été de faire calculer l'IA de manière invisible en arrière-plan, et de ne générer qu'une seule carte de chaleur (Heatmap) statique à la toute fin. L'impact est une perte de dynamisme visuel pendant le chargement, mais c'est le seul moyen d'éviter que le programme ne fige.


## 5. Conclusion et perspectives

Pour conclure, la modélisation de notre projet PyTunnel prouve qu'il est possible de lier l'évolution artificielle à la mécanique des fluides. En combinant la méthode des lattices de Boltzmann pour la physique et un algorithme génétique contraint par des lois géométriques strictes, nous avons créé une base théorique solide, claire et actionnable pour notre phase de programmation.

Dans le futur, plusieurs perspectives d'amélioration pourraient être explorées pour ce projet. Il serait par exemple intéressant d'adapter notre modèle LBM pour intégrer un réseau en trois dimensions (comme le D3Q19). De plus, l'intégration de calculs thermiques permettrait d'observer comment la chaleur d'un moteur affecte la traînée de l'air autour de la carrosserie, repoussant ainsi les limites de notre simulation actuelle.