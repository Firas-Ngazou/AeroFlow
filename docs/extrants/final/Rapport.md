# Rapport final
> #### 420-SF4-RE | Projet d'intégration en sciences, informatique et mathématiques

## Partie 1 - Résultats et analyses d'équipe

### 1. Validation et analyse

#### Méthodes de validation et fidélité de la simulation

Pour vérifier que notre simulation reste fidèle à la réalité physique, nous avons adopté une démarche simple et intuitive.

D'abord, nous avons testé des formes connues pour lesquelles on peut prédire le comportement aérodynamique. Une goutte d'eau allongée doit produire un coefficient de traînée ($C_d$) faible, tandis qu'un rectangle plat perpendiculaire au flux doit donner un $C_d$ élevé. Nos simulations respectent cela. Enfin, une forme symétrique par rapport à l'axe horizontal du flux produit une portance presque nulle, ce qui est attendu.

La visualisation par heatmap a aussi servi de validation visuelle. Les zones de haute pression apparaissent à l'avant de l'obstacle, et les tourbillons se forment à l'arrière, là où le décollement se produit, ce qui correspond à ce qui est attendu.

#### Évolution de l'architecture (Prévue vs Finale)

L'architecture prévue lors de la conception reposait sur une séparation claire entre trois modules : l'interface utilisateur (PySide6), le moteur physique (LBM), et l'algorithme génétique. Chaque module devait communiquer par des interfaces simples. Cette séparation a globalement été respectée dans la version finale.

Cependant, deux changements majeurs ont été nécessaires :

1. **Intégration du contrôleur de simulation et du stockage intermédiaire.** L'architecture initiale ne prévoyait pas de stockage temporaire pour les frames de simulation. En pratique, générer une heatmap à chaque itération en temps réel surchargait le rendu. Nous avons ajouté un `VideoController` qui enregistre les états de la grille dans un fichier temporaire au format HDF5 (via `h5py`). Cela a permis de séparer le calcul physique de l'affichage visuel.

2. **Passage du GA en thread séparé.** L'algorithme génétique devait, dans la conception initiale, s'exécuter de manière synchronisée. En fait, comme l'évaluation d'un individu bloquerait l'interface pendant plusieurs secondes et que nous souhaitions plutôt voir l'algorithme en action, nous avons repenser l'architecture pour intégrer un `QThread` dédié au GA.

Ces changements ont eu pour conséquence l'ajout d'une grande charge de travail qui nous a ralentie, mais ils ont permis aussi de conserver une interface fluide et réactive.

#### Problèmes techniques les plus difficiles à résoudre

##### Mathématiques

Le problème mathématique le plus difficile a été l'implémentation des contraintes géométriques sur l'algorithme génétique. En effet, la première version du GA tentait de muter des pixels individuels sur une matrice binaire. Il n'est pas difficile de voir le problème dans cette manière de faire, puisque l'application d'un décalage aléatoire aux sommets d'une matrice **binaire** aux milliers d'éléments est assez complexe et largement inefficace.

Au final, le GA a été retravaillé pour fonctionner avec de simples matrices de sommets. Les contraintes d'aire et de distance étaient devenues beaucoup plus gérables, étant donné la simplicité de la mutation de simples coordonnées lorsque comparées à des booléens.

##### Sciences

Le problème scientifique le plus difficile a été la stabilisation du moteur Lattice-Boltzmann lorsque le mode d'édition en temps réel était activé. Dans les premières versions, le fluide devenait instable dès que des formes étaient rétrécies ou supprimées. Des valeurs aberrantes apparaissaient dans la grille, provoquant des "explosions numériques" où la densité locale devenait négative ou infinie.

Pour remédier à ce problème, lorsque le moteur détecte que des pixels solides passent à l'état fluide pendant la simulation, il initialise ces nouvelles cellules en leur attribuant les caractéristiques moyennes du milieu environnant. Pour illustrer ce principe, imaginons un bloc d'acier plongé dans une flaque d'eau. Au lieu de faire disparaître le bloc instantanément (ce qui serait physiquement irréaliste), on simule un retrait progressif en le soulevant lentement.

##### Informatique

Le problème informatique le plus difficile a été la gestion des animations et de la mémoire. Au début du projet, le moteur physique calculait l'écoulement à très haute résolution et chaque frame était convertie en image puis enregistrée dans une liste Python en RAM. Une simulation de quelques secondes occupait plusieurs gigaoctets et faisait planter l'ordinateur. Nous avons même envisagé de faire tourner les calculs pendant la nuit pour générer automatiquement un fichier MP4 à la fin, mais cette solution aurait été trop lente et peu interactive.

Nous avons exploré plusieurs pistes : 
1. Réduire la résolution des calculs physiques, mais cela donnait des images pixelisées et moches.
2. Ne stocker que les données brutes NumPy en RAM, mais cela restait trop lourd pour de longues simulations.
3. Écrire chaque image sur le disque sous forme d'image PNG, mais le projet aurait été trop peu interactif.

Finalement, nous avons choisi de :
- Réduire la résolution de la grille de calcul physique tout en utilisant OpenCV (`cv2.resize`) pour upscaler bilinéairement les heatmaps à la résolution de l'écran. Cela donne des visuels lisses sans coût de calcul physique.
- Enregistrer les données brutes de la simulation (tableaux NumPy 3D) dans un fichier temporaire HDF5 compressé (LZF), géré par un `VideoController` avec deux threads d'I/O en arrière-plan (lecture et écriture).
- Maintenir en RAM uniquement une fenêtre glissante d'images proches de la position actuelle du lecteur, ce qui limite la consommation mémoire.

#### Synergie entre les disciplines

Le moment où les trois disciplines se sont le plus renforcées mutuellement a été l'optimisation et l'intégration du moteur de simulation. Pour obtenir une simulation (science) en temps réel, nous avons dû vectoriser l'ensemble des opérations avec NumPy.

Cette vectorisation est un exemple concret de synergie entre les mathématiques et l'informatique : les équations discrètes du modèle LBM (mathématiques) ont été écrites sous forme d'opérations matricielles avec NumPy, ce qui a réduit le temps de calcul de manière considérable. Ensuite, il a fallu intégrer ce moteur optimisé dans l'interface PySide6 (informatique) via des signaux et des slots, pour que l'utilisateur puisse lancer la simulation, la mettre en pause, et voir les résultats s'afficher en direct sans que l'application ne gèle.

Ainsi, les mathématiques ont rendu la simulation rapide, les sciences ont fourni le modèle à simuler, et l'informatique a rendu le tout accessible et interactif pour l'utilisateur.

---

### 2. Réalisation technique

#### Résultats les plus significatifs du projet (Maximum 3)

1. **Un éditeur vectoriel 2D interactif intégré à un moteur physique.** L'utilisateur peut dessiner, modifier, sauvegarder et charger des formes personnalisées. Ces formes sont automatiquement converties en masque binaire et injectées dans la simulation sans interruption.

2. **Une simulation de mécanique des fluides en temps réel basée sur la méthode LBM.** Le moteur calcule l'écoulement de l'air, génère une heatmap de vitesse, et extrait les coefficients aérodynamiques ($C_d$, $C_l$) par échange de quantité de mouvement.

3. **Un algorithme génétique fonctionnel optimisant la géométrie pour minimiser la traînée.** L'IA respecte les contraintes géométriques choisies par l'utilisateur (aire constante ou distance limitée) et présente ses résultats via un graphique de convergence interactif.

#### Consolidation des concepts et liens avec les cours (3 liens par discipline)

##### Mathématiques

1. **Algèbre linéaire et géométrie vectorielle :** La méthode LBM repose sur un espace vectoriel à neuf dimensions (D2Q9) en chaque cellule de la grille. La manipulation de ces vecteurs de distribution $f_i$, ainsi que la représentation des sommets du dessin dans $\mathbb{R}^2$, sont des applications directes des concepts d'espaces vectoriels et de matrices vus en algèbre linéaire.

2. **Calcul intégral :** La démonstration et l'implémentation de la formule des lacets pour le calcul de l'aire d'un polygone sont une application directe du théorème de Green. Ce théorème permet de transformer une intégrale de surface en une intégrale curviligne sur le contour.

3. **Probabilités et statistiques :** L'opérateur de mutation de l'algorithme génétique utilise une distribution normale $\mathcal{N}(0, \sigma^2)$ pour générer des déplacements aléatoires. Comprendre la densité de probabilité et l'effet de l'écart-type sur l'amplitude des mutations est essentiel pour calibrer l'exploration de l'espace de solutions.

##### Sciences

1. **Physique mécanique — Coefficients de frottement :** Dans le cours de physique mécanique, nous avons appris les bases du calcul des forces de résistance et des coefficients de traînée ($C_d$) et de portance ($C_l$). Notre projet applique directement ces concepts en calculant numériquement ces coefficients à partir des forces exercées par le fluide sur l'obstacle dessiné.

2. **Physique mécanique — Simulations avec VPython :** Le cours utilisait VPython pour visualiser des phénomènes physiques. Cette expérience nous a préparés à concevoir notre propre simulation interactive.

3. **Physique mécanique — Analyse des forces :** Les travaux pratiques du cours de mécanique portaient sur l'analyse vectorielle des forces (somme des forces, équilibre, frottement). Le moteur LBM repose sur le même principe d'analyse vectorielle, mais appliqué à des millions de particules virtuelles sur une grille discrète.

##### Informatique

1. **Programmation orientée objet :** L'architecture du logiciel repose sur l'héritage et le polymorphisme. Par exemple, les widgets PySide6 (`QEditor`, `QAnalysisTabs`) héritent de classes de base Qt, et le moteur de simulation expose une interface standardisée indépendamment de son implémentation interne.

2. **Développement d'interfaces graphiques avec PySide6 :** Le cours de SF3 nous a appris à utiliser PySide6 pour créer des applications de bureau. Ces compétences ont été directement appliquées dans notre projet pour construire l'éditeur vectoriel, les panneaux de paramètres et les widgets d'analyse. Sans cette base, le développement de l'interface aurait été beaucoup plus long.

3. **Structures de données et choix d'implémentation :** Le projet a nécessité de choisir correctement entre différentes structures selon les besoins : NumPy pour les calculs matriciels rapides, fichiers HDF5 pour le stockage séquentiel des images de simulation, et JSON (vu dans le cours SF2 de programmation orientée objet) pour la persistance des projets.

---

### 3. Gestion du travail

#### Valeur et pertinence de la conception initiale (~5 semaines)

Quand nous avons commencé à imaginer le projet et à établir les échéanciers, nous nous sommes dit d'abord que nous allions commencer à coder avant la fin du sprint 2, et nous avions ainsi mis dans nos tâches du sprint 2 de faire des tests de code. Toutefois, nous nous sommes rapidement rendu compte de l'importance de bien faire nos documents de conception et que le temps alloué était déjà assez restreint pour imaginer et décrire tout ce que nous voulions faire, de manière à avoir une vraie base sur laquelle travailler quand nous allions programmer. De cette manière, nous avons pu directement enchaîner avec la programmation en ayant une très bonne idée de ce que nous voulions faire, quand et comment.

#### Valeur et pertinence des rencontres hebdomadaires Scrum

À la différence de nos projets précédents, nous avons fait de notre mieux pour tenir des rencontres Scrum efficaces. Ainsi, chaque semaine, on savait quoi faire sans le stress d'être pris de cours par manque d'information sur ce qui se passait. En effet, nous avons pu être mis à jour sur chacun des avancements des autres et sur les tâches à venir, tout en s'entraidant.

#### Valeur et pertinence de l'utilisation de GitHub pour la gestion des documents

Nous utilisions déjà GitHub auparavant, mais il n'en demeure pas moins crucial pour notre projet. Effectivement, la gestion des tâches et la manière de travailler requièrent d'avoir une version propre et des moyens de réalisation efficaces, tout en ayant accès au projet en tout temps et à n'importe quel endroit.

---

### 4. Éléments fonctionnels

#### Spécifications fonctionnelles réussies (Environ 10 éléments ordonnés)

1. **Éditeur vectoriel 2D interactif** permettant de placer, déplacer, sélectionner et supprimer des sommets pour dessiner des polygones fermés.
2. **Rastérisation automatique** des formes vectorielles en masque binaire compatible avec la grille du moteur physique.
3. **Simulation d'écoulement fluide en temps réel** par méthode LBM avec conditions aux limites bounce-back sur les obstacles.
4. **Heatmap de vitesse** générée par interpolation linéaire des normes de vecteurs vitesse sur la grille de simulation.
5. **Calcul automatique des coefficients aérodynamiques** ($C_d$ et $C_l$) par échange de quantité de mouvement aux bords de l'obstacle.
6. **Algorithme génétique fonctionnel** capable de muter, croiser et sélectionner des formes pour minimiser la traînée sous contraintes géométriques.
7. **Graphique de convergence en temps réel** affichant l'évolution du coefficient de traînée à chaque génération de l'optimisation.
8. **Sauvegarde et chargement de session** au format JSON, incluant le dessin vectoriel au complet et certains paramètres.
9. **Configuration persistante** des paramètres utilisateur au format INI (résolution, vitesse, contraintes de l'IA, etc.).
10. **Interface personnalisée** avec fenêtre sans bordures native, barre d'outils, panneaux d'analyse rétractables et gestion de projets via une page d'accueil.

#### Spécifications fonctionnelles abandonnées ou non terminées (Maximum 5 avec une phrase d'explication)

1. **Paramètres de simulation** : Plus de paramètres de simulation auraient pu être ajoutés, dont la qualité des calculs, fixée à 20% de la résolution du canevas interactif.

---

## Partie 2 - Synthèse individuelle

### Firas Ngazou

#### 1. Satisfaction personnelle

Je suis satisfait du résultat final. L'application fonctionne bien dans l'ensemble. L'interface est propre et les fonctionnalités principales sont toutes opérationnelles. J'aurais aimé ajouter plus de finitions visuelles et quelques fonctionnalités supplémentaires, mais le cœur du projet est solide et stable.

#### 2. Contribution personnelle et accomplissements (Minimum 2 par discipline)

##### Mathématiques
- J'ai implémenté l'algorithme de rastérisation qui convertit les formes vectorielles en matrices binaires.
- J'ai contribué sur la coloration de la heatmap, soit, le calcul des couleurs finales à partir des normes de vitesse.

##### Sciences
- J'ai contribué à l'intégration des sorties du moteur physique dans l'interface utilisateur, notamment le branchement des coefficients de traînée et de portance aux widgets d'affichage.
- J'ai participé au débogage des conditions aux limites en testant différentes formes et en signalant les anomalies visuelles dans la simulation. J'ai également grandement contribué au réglage des problèmes trouvés.

##### Informatique
- J'ai conçu et développé une grande partie de l'interface utilisateur : fenêtre personnalisée sans bordures, éditeur vectoriel interactif, barre d'outils, panneaux de paramètres, onglets d'analyse et widgets flottants.
- J'ai implémenté le système de gestion de projets (sauvegarde et chargement JSON, configuration INI, système de prefabs) ainsi que le `VideoController` avec stockage HDF5 pour les images de simulation, permettant des animations fluides sans saturer la RAM.

##### Gestion
- J'ai géré le dépôt GitHub : création des branches, revue des pull requests, résolution des conflits de fusion et maintien de la documentation Scrum.
- J'ai coordonné l'intégration entre les trois modules. Quand les interfaces changeaient, je m'assurais que les connexions UI-Physique-GA restaient fonctionnelles.

#### 3. Expérience personnelle du travail d'équipe

##### Collaboration au niveau de l'équipe
- **Meilleur aspect de la collaboration :** Chacun était motivé et prêt à aider. Quand quelqu'un bloquait sur un bug, les autres prenaient le temps de lire le code et de proposer des solutions.
- **Pire aspect de la collaboration :** La communication sur les changements de format de données arrivait parfois tard. Le moteur physique a changé sa structure de sortie plusieurs fois, ce qui nous a fait perdre du temps. Nous avons également eu un problème similaire pour le développement de l'algorithme génétique.

##### Collaboration au niveau de mon apport
- **Meilleur aspect de mon apport :** J'ai pris en charge l'intégration globale. Quand deux modules ne parlaient pas ensemble, je construisais souvent le pont pour les connecter.
- **Pire aspect de mon apport :** J'ai parfois passé trop de temps sur des détails visuels de l'interface et pas assez sur les tests d'intégration avec le moteur physique.

##### Leçons tirées pour les futurs projets
Pour mes futurs projets, je demanderai des mises à jour plus fréquentes sur les formats de données utilisés par mes coéquipiers. Aussi, je tâcherai de ne pas laisser un changement important traîner, aussi ennuyeux soit-il, jusqu'à la fin du projet, comme ça a été le cas avec le maintien du code écrit en camelCase avant d'être contraint à le modifier en snake_case à la fin du projet.

#### 4. Rétrospective globale (Bilan d'études)

##### Satisfaction face au projet d'intégration
Oui, je suis satisfait. C'est une application complète qui mélange trois disciplines complexes. Le résultat est fonctionnel et utile. Je n'hésiterais pas à l'ajouter à mon CV. :D

##### Satisfaction face aux études collégiales
Oui. Le programme m'a donné des bases solides en programmation, en mathématiques et en sciences, même si je pense que ces apprentissages n'auront d'impact significatif que plus tard (éventuellement, dans mon parcours scolaire).

##### Atteinte des objectifs initiaux du programme
Oui. Mon objectif était d'apprendre à construire une vraie application de bureau, et c'est ce que j'ai fait.

##### Préparation pour les études universitaires
Je me sens prêt. Je sais comment gérer un projet, travailler en équipe et apprendre rapidement de nouveaux concepts techniques.

##### Conseil ou avertissement pour la prochaine cohorte
Gardez la documentation de vos méthodes à jour pour permettre à vos coéquipiers de mieux les comprendre. Après plusieurs semaines de travail, on peut parfois oublier l'existence de certaines méthodes et ce qu'elles font réellement. À ces moments-là, une bonne documentation aide au rappel des détails techniques par rapport aux méthodes.

---

### Quang-Vinh Nguyen

#### 1. Satisfaction personnelle
Personnellement, je suis très satisfait des résultats finaux du projet. Il a dépassé mes attentes en début de session et c'est un projet que je ne me serais pas vu capable d'accomplir en si peu de temps. Le fait de voir une simulation fonctionnelle et fluide, codée entièrement par nous-mêmes, me rend très fier de tous les efforts investis à travers la session.

#### 2. Contribution personnelle et accomplissements

##### Mathématiques
- Accomplissement 1 : J'ai développé l'algorithme génétique dans le programme.
- Accomplissement 2 : J'ai travaillé sur la génération de la carte de chaleur des vitesses et des densités, notamment la logique derrière la normalisation des vecteurs.

##### Sciences
- Accomplissement 1 : J'ai contribué à la représentation visuelle des lignes d'écoulement.
- Accomplissement 2 : J'ai contribué à la représentation visuelle de la formation des tourbillons (zones de turbulence).

##### Informatique
- Accomplissement 1 : J'ai configuré et intégré la bibliothèque AeroSandbox dans l'algorithme génétique pour approximer les coefficients.
- Accomplissement 2 : J'ai activement contribué au développement du moteur de simulation (simulation_engine), incluant la programmation de fonctions telles que update_status_message, run, get_boltzmann_v, evaluate_max_step, apply_boundaries, end_current_frame, generate_heatmap.

##### Gestion
- Accomplissement 1 : Contribué à la planification des sprints lors des rencontres Scrum.
- Accomplissement 2 : Contribué en validant régulièrement l'état d'avancement des tâches partagées et en adaptant mes priorités pour soutenir mes coéquipiers.

#### 3. Expérience personnelle du travail d'équipe

##### Collaboration au niveau de l'équipe
- **Meilleur aspect de la collaboration :** La communication entre les coéquipiers. Nous partagions nos idées sur les besoins spécifiques de chaque section du programme et travaillions les parties qui demandaient une attention particulière.
- **Pire aspect de la collaboration :** La répartition du travail. Nous avons fonctionné en grand groupe pour la quasi-totalité du projet. Nous avons fait beaucoup de programmation en binôme, mais nous étions rarement chacun de notre côté ; le fait de ne pas bien diviser les tâches a eu un impact sur le temps de développement de notre programme.

##### Collaboration au niveau de mon apport
- **Meilleur aspect de mon apport :** Ma flexibilité. J'écoute les besoins de mes coéquipiers et j'ajuste mes priorités en fonction de ceux-ci. Par exemple, j'ai aidé avec le moteur de simulation et le vector_obstacle tout en travaillant sur ma partie qui était la heatmap.
- **Pire aspect de mon apport :** Mon aspect le moins fort a été ma présence parfois moins marquée dans la gestion globale et les prises de décision, ayant préféré me concentrer principalement sur la réalisation technique des tâches qui m'étaient données.

##### Leçons tirées pour les futurs projets
Cette expérience m'a appris l'importance d'une communication dans n'importe quel projet quelconque. J'ai réalisé qu'un bon coéquipier n'est pas seulement quelqu'un qui travaille de manière efficace, mais qui communique bien sur le progrès de son bord. Pour mes projets dans le futur, je veillerai à prendre une part plus active dans l'organisation des tâches pour maximiser l'efficacité de l'équipe.

#### 4. Rétrospective globale

##### Satisfaction face au projet d'intégration
Je suis très satisfait de notre projet d'intégration.

##### Satisfaction face aux études collégiales
Je suis moyennement satisfait des études collégiales.

##### Atteinte des objectifs initiaux du programme
Je pense que oui. Le programme a atteint son objectif qui était d'intégrer les maths, la physique, la chimie avec l'informatique.

##### Préparation pour les études universitaires
Je pense que ce programme prépare le mieux pour tous les programmes universitaires en ingénierie, puisque toutes les compétences de maths et physique sont déjà acquises. De plus, je pense que ce programme prépare aussi pour le marché du travail puisque maintenant l'informatique se trouve partout, alors développer les compétences de programmation à ce stade est justement bien pour l'avenir.

##### Conseil ou avertissement pour la prochaine cohorte
Bien diviser les tâches pour éviter de prendre du retard.

---

### Mehdi Achouri

#### 1. Satisfaction personnelle
Je suis très content du résultat final. En effet, je ne m'attendais pas au début à ce que nous arrivions à un tel résultat, tant sur le plan esthétique que scientifique. Nous sommes partis de l'idée de faire une simulation de l'air, ce qui paraissait quasiment impossible au départ, pour finalement arriver à un projet qui donne un véritable effet « WOW » lorsqu'on le voit. Au final, je suis fier de notre projet et de la manière dont il a évolué pour en arriver là.

#### 2. Contribution personnelle et accomplissements

##### Mathématiques
- Accomplissement 1 : Ma contribution dans cette discipline n'est pas significative, mais j'y ai participé implicitement à travers l'utilisation des équations physiques.
- Accomplissement 2 : J'ai aussi participé au calcul et à la génération des lignes d'écoulement.

##### Sciences
- Accomplissement 1 : J'ai créé le moteur physique en utilisant la méthode de Lattice Boltzmann et l'approximation BGK.
- Accomplissement 2 : J'ai déterminé les coefficients de traînée et de portance tout en les stabilisant, car ils ne fonctionnaient pas parfaitement dès le départ.

##### Informatique
- Accomplissement 1 : J'ai cherché des moyens d'optimiser le code afin de trouver une solution viable pour la visualisation en direct ; dans ce contexte, j'ai créé un buffer qui permet de réduire l'espace de stockage requis en mémoire vive.
- Accomplissement 2 : J'ai contribué à la gestion de l'animation, notamment pour l'affichage des lignes d'écoulement pendant la simulation.

##### Gestion
- Accomplissement 1 : J'ai grandement aidé à la coordination entre la physique et l'interface utilisateur afin d'assurer une efficacité maximale lors de l'implémentation et de la liaison des deux parties.
- Accomplissement 2 : Lors de la rédaction des documents de conception, je m'assurais que chacun avait fait son travail correctement et dans les délais prévus.


#### 3. Expérience personnelle du travail d'équipe

##### Collaboration au niveau de l'équipe
- **Meilleur aspect de la collaboration :** Le meilleur aspect du travail d'équipe a été de pouvoir s'entraider et de demander des conseils quand nous en avions besoin, ce qui nous a évité de perdre trop de temps. Toutefois, devoir attendre les versions des autres pour pouvoir continuer à travailler s'est souvent révélé frustrant quand quelqu'un voulait avancer mais qu'il ne pouvait pas.
- **Pire aspect de la collaboration :** La coordination lors des phases d'intégration a été le plus difficile. En effet, quand je modifiais le moteur physique pour corriger un bug ou ajouter une fonctionnalité, cela impactait souvent l'interface, et je ne m'en rendais pas toujours compte immédiatement. Dans ce contexte, nous avons dû passer beaucoup de temps à restructurer les connexions entre les modules, ce qui était parfois décourageant.

##### Collaboration au niveau de mon apport
- **Meilleur aspect de mon apport :** Le meilleur aspect de mon apport a été de réussir à créer un moteur physique fonctionnel à partir de zéro. En effet, transcrire les équations de Lattice Boltzmann en code Python et obtenir une simulation stable et visuellement convaincante était un défi majeur. Lorsque j'ai vu le fluide s'écouler correctement autour de la première forme et que les coefficients ont commencé à donner des valeurs cohérentes, j'ai ressenti une grande fierté, car j'avais réussi à donner vie à la partie scientifique du projet.
- **Pire aspect de mon apport :** Étant donné que j'étais responsable de la physique, j'ai dû transcrire des formules physiques en code et faire en sorte que le tout fonctionne. Cette tâche était assez complexe, mais je pense qu'elle était essentielle ; j'ai ainsi beaucoup apporté à mon équipe, notamment en les aidant à comprendre cette partie pour qu'ils puissent à leur tour utiliser les données efficacement. D'un autre côté, j'ai dû retravailler la physique à plusieurs reprises, ce qui a sûrement ralenti le développement et le travail de l'équipe de manière générale.

##### Leçons tirées pour les futurs projets
Je ne peux pas être parfait dans tous les domaines, j'ai donc tout intérêt à demander conseil aux personnes qui en savent plus que moi lorsque j'en ai besoin.

#### 4. Rétrospective globale

##### Satisfaction face au projet d'intégration
Oui, je suis très satisfait de mon projet d'intégration de par sa complexité et son résultat impressionnant. Je n'aurais pas pensé qu'en rentrant au cégep je pourrais produire avec une équipe en fin de DEC un tel projet. Il reste sûrement quelques points à retravailler ou certains qui peuvent être améliorés mais, de manière générale, je suis satisfait du projet d'intégration.

##### Satisfaction face aux études collégiales
Pour l'instant, je suis satisfait de mes études car elles m'ont ouvert les portes vers d'autres horizons, comme la programmation. Toutefois, j'attends de faire mes premiers pas à l'université pour pouvoir juger au mieux de l'intérêt de mes études par rapport à d'autres options, et ainsi donner un avis critique et honnête.

##### Atteinte des objectifs initiaux du programme
Je pense que oui car, avant d'entrer au cégep, je ne maîtrisais vraiment pas l'informatique. À force d'essais et de persévérance, je peux dire que je suis fier du chemin que j'ai parcouru. De plus, je pense avoir appris ce dont j'aurai besoin pour réussir cette étape universitaire à venir. À une semaine de la fin, je suis content de ce que j'ai accompli, car je ne me pensais pas capable de cela à mon arrivée.

##### Préparation pour les études universitaires
Je me sens prêt à poursuivre mes études, même si le stress reste présent. En effet, j'ai entendu beaucoup de bien de ma future université et à quel point sa formation est pertinente. Toutefois, elle est aussi reconnue pour être difficile. Dans ce contexte, je pense avoir acquis le bagage nécessaire pour réussir mes études à venir.

##### Conseil ou avertissement pour la prochaine cohorte
Si j'avais un conseil à donner aux prochains étudiants, je leur dirais de ne pas prendre de retard. Les moments qui ont été les plus difficiles, selon moi, sont ceux situés juste avant la fin d'un sprint; on doit alors accomplir tout ce que l'on a reporté à plus tard, et il est facile de se retrouver submergé si on ne fait pas attention.