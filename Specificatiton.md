## 5- Partie Individuelle

### 5.1 - Nguyen, Quang-Vinh
#### 5.1.1 - Rôles et responsabilités :

**Conception et Implémentation de l'optimisation et de l'évolution génétique**

Mon rôle principal est de concevoir et d'implémenter l'intelligence artificielle qui va optimiser la forme du solide dans un tunnel de vent. Cela inclut le codage de la structure de l'algorithme génétique (population de matrices binaires, sélection par tournoi, croisement et mutation par segment). Je dois aussi m'assurer que le programme garantit que l'IA respecte les contraintes de données, notamment la conservation de l'aire et le maintien d'un certain niveau de similarité de n% par rapport à l'état initial.

**Limites de la tâche** : 
Mon rôle commence à la réception de la matrice de segments initiale produite à partir de l'interface utilisateur et des paramètres de contraintes associés. Celui-ci se termine lorsque l'algorithme a convergé vers une forme optimale et qu'il transmet la matrice finale au module de visualisation pour la génération de la heatmap. Il n'inclut pas le développement des équations fondamentales du fluide (Lattice Boltzmann), mais nécessite une collaboration avec le responsable de la physique pour l'appel de la fonction de coût.

#### 5.1.2 - Opinions personnelles :

**Quelle partie sera la plus difficile à réaliser (en terme de complexité)?**

La gestion de la mutation avec contraintes de conservation de l'aire. Maintenir une aire constante tout en modifiant aléatoirement des segments de la matrice demande une logique assez précise pour ne pas nuire au modèle de physique à chaque génération.

Dans un algorithme génétique classique, les mutations sont indépendantes et aléatoires. Imposer la conservation de l'aire brise cette indépendance. Si une mutation transforme un segment fluide en solide $(0\to 1)$, une réparation doit être effectuée ailleurs pour transformer un segment solide en fluide $(1 \to 0)$. Coder cette dépendance nécessite une gestion quand même complexe des indices de la matrice avec NumPy pour éviter de créer des formes déconnectées qui feraient échouer la simulation de Lattice Boltzmann.

**Quelle partie sera la plus longue à réaliser (en terme de temps)?**

L’implémentation de validation des contraintes géométriques de la matrice. Dans un algorithme génétique standard, les mutations sont aléatoires. Cependant, chaque mutation doit être validée et corrigée pour respecter les contraintes mathématiques (aire constante, rayon $R_{max}$ et similarité à n%). Le défi technique se trouve dans la création d'un algorithme de compensation capable d'ajouter ou de supprimer un segment à un endroit dès qu'une mutation survient, sans créer de formes physiquement incohérentes pour la simulation fluide.


**Justifiez comment ce projet vous permet d'intégrer les compétemces acquises dans votre formation collégiale**

Ce projet regroupe les compétences vues en calcul intégral (calculer l'aire de la forme), en algèbre linéaire et géométrie vectorielle (manipulation des vecteurs), en physique (application numérique des formules de la mécanique des fluides) et en programmation (l'optimisation d'un problème).

Pour le cours de calcul intégral, la compétence appliquée consiste à calculer l'aire des formes générées. Cette aire devrait rester constante à travers tout le calcul du programme.

Pour le cours d'algèbre linéaire et de géométrie vectorielle, les compétences appliquées seront les matrices qui serviront à définir l'espace, les mutations et la forme de l'objet. Les opérations de mutation et de croisement sont des manipulations algébriques (XOR, masques binaires). Dans le modèle de Lattice Boltzmann (D2Q9), chaque index de la matrice contient un espace vectoriel de 9 directions de vitesses. Gérer les interactions entre ces vecteurs et les parois de la forme optimisée nécessite une bonne connaissance générale des opérations matricielles.

Pour le cours de physique, les compétences impliquées sont la compréhension des formules et la capacité de les adapter selon la situation présentée. La mécanique des fluides n'est pas une matière que l'on voit au cégep, mais être capable de comprendre comment la formule de Lattice Boltzmann fonctionne et être en mesure de l'appliquer à des contextes différents est l'une des compétences acquises à travers le cégep.

Pour le cours d'informatique, les compétences visées consistent en l'optimisation du programme, soit l'efficacité du programme ainsi que l'optimisation d'un problème.