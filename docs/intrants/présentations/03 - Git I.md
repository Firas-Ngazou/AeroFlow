# Git I <br> <small><small><small>Une gestion saine du travail</small></small></small>

<br>

## Mise en contexte et justification

Considérez ces deux mises en situation :
- Vous développez un projet complexe sur plusieurs mois. Vous avez besoin de garder une trace de l'évolution du code, de pouvoir revenir à une version précédente en cas de problème, et de collaborer efficacement avec d'autres développeurs. Comment gérez-vous les différentes versions du code et la collaboration?
- Imaginez que nous sommes en 1990. Vous travaillez sur un logiciel avec un collègue situé à distance. Internet est lent, et envoyer l'intégralité du code source (plusieurs mégaoctets) à chaque modification est impensable. Comment lui envoyer uniquement vos changements pour qu'il puisse les intégrer à sa propre copie du code sans tout casser?

Ces scénarios sont des exemples parmi des centaines possibles. Ils illustrent les défis de la gestion de version et de la collaboration dans le développement logiciel. C'est ici qu'interviennent les deux piliers du développeur _old school_ :  `diff` et `patch`.

### diff : l'outil de comparaison
- `diff` est un outil de ligne de commande qui compare deux fichiers ou répertoires et affiche les différences entre eux.
- Il génère un rapport indiquant quelles lignes ont été :
    - ajoutées
    - supprimées
    - modifiées.
- Par exemple, si vous avez deux versions d'un fichier de code source, `diff` peut vous montrer exactement quelles lignes ont changées.

Voici un exemple simpliste. Plus bas, se trouve deux versions du même fichier `code.py` qui ont changées dans le temps.

```python 
# code_v1.py

def add(a, b):
    return a + b

def substract(a, b):
    return a - b

def multiply(a, b):
    return a * b

```

```python
# code_v2.py

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def negate(a):
    return -a

```

La commande `diff code_v1.py code_v2.py` donne la différence normale entre les fichiers mentionnés. La différence normale constitue une liste de lignes précédées d'un symbole indiquant le type de changement :
- `<` : indique une ligne qui a été supprimée de la première version (code_v1.py).
- `>` : indique une ligne qui a été ajoutée dans la deuxième version (code_v2.py).
- `c` : indique une ligne qui a été modifiée entre les deux versions.
- `d` : indique une ligne qui a été supprimée de la première version (code_v1.py) et qui n'existe pas dans la deuxième version (code_v2.py).
- `a` : indique une ligne qui a été ajoutée dans la deuxième version (code_v2.py) et qui n'existe pas dans la première version (code_v1.py).
- les numéros de ligne à gauche des symboles indiquent les lignes concernées dans la première version (code_v1.py), tandis que les numéros de ligne à droite indiquent les lignes concernées dans la deuxième version (code_v2.py).

```diff
1c1
< # code_v1.py
---
> # code_v2.py
6,8d5
< def substract(a, b):
<     return a - b
< 
10a8,10
> 
> def negate(a):
>     return -a

```

On peut donc interpréter ce résultat de la manière suivante en analysant les 3 blocs de changements :
- Le premier bloc `1c1` indique que la ligne 1 a été modifiée entre les deux fichiers. La ligne `# code_v1.py` a été remplacée par `# code_v2.py`.
- Le deuxième bloc `6,8d5` indique que les lignes 6 à 8 du premier fichier (code_v1.py) ont été supprimées et n'existent pas dans le deuxième fichier (code_v2.py). Ces lignes correspondent à la fonction `substract`. Le 5 indique que ces lignes ont été supprimées après la ligne 5 du deuxième fichier.
- Le troisième bloc `10a8,10` indique que des lignes ont été ajoutées après la ligne 10 du premier fichier (code_v1.py) et qu'elles correspondent aux lignes 8 à 10 du deuxième fichier (code_v2.py). Ces lignes correspondent à la fonction `negate`.

Il est possible de produire une version plus détaillée de ce rapport en utilisant l'option `-u` (diff unifié, davantage lisible pour un humain) qui affiche les lignes de contexte autour des changements. En utilisant la commande `diff -u code_v1.py code_v2.py` la sortie suivante est produite. La présentation prend plutôt la forme suivante :
- Les lignes précédées de `-` indiquent les lignes qui ont été supprimées de la première version (code_v1.py).
- Les lignes précédées de `+` indiquent les lignes qui ont été ajoutées dans la deuxième version (code_v2.py).
- Les lignes bornées par `@@` indiquent les numéros de ligne dans les deux fichiers où les changements ont eu lieu, ainsi que le nombre de lignes concernées.

```diff
--- code_v1.py	2026-02-08 16:57:35.799754000 -0500
+++ code_v2.py	2026-02-08 16:58:36.141307900 -0500
@@ -1,10 +1,10 @@
-# code_v1.py
+# code_v2.py
 
 def add(a, b):
     return a + b
 
-def substract(a, b):
-    return a - b
-
 def multiply(a, b):
     return a * b
+
+def negate(a):
+    return -a
```

On peut interpréter ce résultat de la manière suivante :
- La ligne `--- code_v1.py` indique le nom du premier fichier comparé, suivi de sa date de modification.
- La ligne `+++ code_v2.py` indique le nom du deuxième fichier comparé, suivi de sa date de modification.
- Le bloc `@@ -1,10 +1,10 @@` indique que les changements concernent les lignes 1 à 10 dans les deux fichiers.
- Les lignes précédées de `-` indiquent les lignes qui ont été supprimées de la première version (code_v1.py). Dans ce cas, la ligne `# code_v1.py` et la fonction `substract` ont été supprimées.
- Les lignes précédées de `+` indiquent les lignes qui ont été ajoutées dans la deuxième version (code_v2.py). Dans ce cas, la ligne `# code_v2.py` et la fonction `negate` ont été ajoutées.

### patch : l'outil de mise à jour
- `patch` est un outil de ligne de commande qui applique les changements décrits dans un fichier de différences (généré par `diff`) à un fichier ou répertoire cible.
- Il prend un fichier de différences (généralement au format unifié) et modifie le fichier cible en fonction des instructions contenues dans le fichier de différences.
- Par exemple, si vous avez un fichier de différences généré par `diff -u code_v1.py code_v2.py`, vous pouvez utiliser `patch` pour appliquer ces changements à `code_v1.py` afin de le transformer en `code_v2.py`.

Cet outil est particulièrement utile dans les scénarios où vous devez partager des modifications avec d'autres développeurs sans envoyer l'intégralité du code source. En envoyant simplement le fichier de différences, les autres développeurs peuvent appliquer les changements à leur propre copie du code source en utilisant `patch`, ce qui facilite la collaboration et la gestion des versions. De plus, `patch` peut gérer les conflits de manière efficace en signalant les sections du code qui ont été modifiées par plusieurs personnes, ce qui permet aux développeurs de résoudre ces conflits manuellement.

`patch` fonctionne autant sur le format de différences normal que sur le format unifié, mais il est généralement recommandé d'utiliser le format unifié pour une meilleure lisibilité et une gestion plus efficace des conflits. En fait, si le fichier original est modifié après la génération du fichier de différences, `patch` pourrait échouer lamentablement et corrompre le fichier cible. Cependant, grâce aux lignes de contexte fournies par le format unifié, `patch` peut détecter les changements et tenter de les appliquer même si les numéros de ligne ne correspondent plus exactement.

### Notes importantes

- `diff` et `patch` sont des outils puissants pour la gestion de version, mais ils ont leurs limites. Ils ne gèrent pas les conflits de manière automatique et peuvent être difficiles à utiliser pour des projets complexes avec de nombreux fichiers.
- Ces outils sont initialement développé pour les systèmes Unix/Linux, mais des versions compatibles sont disponibles pour d'autres systèmes d'exploitation.
- Ce n'est pas toutes les distributions de Linux qui incluent `diff` et `patch` par défaut, mais ils sont généralement disponibles dans les dépôts de logiciels et peuvent être installés facilement.
- Sous Windows, ces outils ne sont pas disponibles nativement. Toutefois, l'installation de Git Bash ou d'autres environnements de développement peut les inclure.
- Ces outils fonctionnent bien pour des fichiers texte, mais ils ne sont pas adaptés pour les fichiers binaires (comme les images ou les fichiers exécutables). Pour ces types de fichiers, d'autres solutions de gestion de version sont nécessaires. 


## Git : l'automatisation naturelle de `diff` et `patch`

Si l'on devait résumer, **Git est une base de données intelligente de gestion de versions de fichiers** construite au-dessus de la logique de diff et patch.

Le problème avec `patch` est qu'il s'agit d'opérations ponctuelles. Vous avez le fichier A, vous appliquez le patch, vous obtenez le fichier B. Mais où est passée la trace du changement ? Qui l'a fait ? Pourquoi ? L'a-t-on sauvegardé quelque part ? 

La solution Git : Au lieu de manipuler des fichiers `*.diff`/`*.patch` flottants, Git automatise le calcul des différences et les enferme dans une structure de données robuste, immuable et facilement consultable.

### Les fondations de Git 

#### Quatre concepts clés

Pour comprendre Git, il faut oublier l'idée d'un simple dossier de fichiers et visualiser une structure plus profonde qui implique le temps et l'espace des données (les fichiers).

1. L'instantané, le _snapshot_

    - Contrairement à d'autres systèmes de gestion de versions qui ne stockent que la liste des changements (les deltas), Git prend une photo complète de votre projet à chaque sauvegarde.
    - L'illusion du changement : Pour l'utilisateur, Git affiche des + et des - (comme diff), mais en interne, il garde une version entière de chaque fichier. Cette approche simplifie énormément la gestion des versions et accélère les opérations courantes.
    - L'efficacité : Si un fichier ne change pas entre deux sauvegardes, Git ne le duplique pas; il crée simplement un lien vers la version précédente. C'est ce qu'on appelle l'adressage par contenu.

2. Le `commit`, l'unité de base
    - Un `commit`, c'est bien plus qu'une sauvegarde. C'est un objet qui contient trois éléments essentiels :
        - Un ID unique : C'est l'empreinte numérique (SHA-1) calculée à partir du contenu. Si un seul caractère change, l'ID change. Il est unique dans la base de données Git et permet de retrouver précisément cette version.
        - Les métadonnées : Qui (auteur), quand (horodatage) et pourquoi (message de commit).
        - Le _snapshot_ : Le pointeur vers l'état de tous les fichiers à ce moment précis.

3. La structure en graphe, le chaînage
    - Git utilise une structure de données appelée graphe orienté acyclique qui correspond à une structure où chaque noeud réfère à un autre mais où il n'y a pas de cycle. 
    - Les noeuds de ce graphe sont les objets créés par les `commit`. 
    - Chacun noeud, connaît son parent mais pas ses enfants. Il est donc possible de remonter l'historique mais pas de le descendre. À partir d'un `commit`, on peut retrouver tous ses ancêtres jusqu'au tout premier `commit` du projet.
    - Ainsi, ce graphe crée une flèche du temps où l'on retrouve plusieurs futurs possibles, l'histoire de Git n'est pas nécessairement une ligne droite. Cette possibilité donne un éventail de scénarios de travail collaboratif très puissant. Nous verrons les branches et les fusions qui donnent vie à ces concepts.

4. Un nouveau paradigme : Git comme système de gestion de projet
    - Git n'est pas une simple _clé USB améliorée_, c'est le journal de bord d'un groupe d'ingénierie.
    - L'historique comme infrastructure de traçabilité : Au-delà d'une simple sauvegarde, Git agit comme une documentation vivante. Dans un cadre professionnel, le chemin parcouru est aussi crucial que le code final ; il justifie les choix d'architecture et facilite la maintenance à long terme.
    - La puissance du `commit` atomique : La qualité d'un dépôt repose sur des changements petits, ciblés et stables. Cette granularité permet d'isoler précisément une erreur ou de revenir en arrière sans perdre de travaux annexes, assurant un équilibre entre clarté et progression.
    - L'intentionnalité (le _pourquoi_ vs le _quoi_) : Alors que le `diff` montre techniquement le changement, le message de commit doit en expliquer l'intention. L'adoption de conventions de nommage (_Conventional Commits_) transforme l'historique en une base de données exploitable par l'équipe et les outils automatisés.
    - Vecteur de collaboration et de qualité : Un historique propre est le premier rempart contre la dette technique. Il structure la revue de code et impose une discipline collective qui garantit que chaque ajout respecte les standards de qualité et de rigueur de l'ingénierie. Cet historique facilite la validation rigoureuse, la recherche d'information cruciale et la compréhension du projet par tous les membres de l'équipe, même ceux qui rejoignent tardivement.   

#### Trois états de travail

La plupart des systèmes de fichiers fonctionnent de manière binaire : un fichier est soit _enregistré_, soit _en cours de modification_. Git introduit un troisième état intermédiaire pour une raison fondamentale : l'intentionnalité. L'objectif est de définir précisément ce qui doit être inclus dans le prochain `commit` du projet. Même si plusieurs modifications sont en cours, il est possible de créer _n_ _commits_ différents à partir de ces changements, chacun avec une intention claire et un message de `commit` précis.

Dans un flux de travail réel, on modifie souvent plusieurs fichiers pour différentes raisons (un correctif, une nouvelle fonction, de la documentation). Si Git enregistrait tout d'un coup, l'historique serait brouillon. Cette structure en trois étapes permet au développeur de sélectionner précisément quelles modifications méritent de faire partie du prochain instantané officiel. C'est la différence entre _sauvegarder son travail_ et _publier une version_. Cette approche permet aussi au développeur de rester concentré sur une tâche à la fois, de faire des `commits` atomiques et de maintenir un historique clair et exploitable pour toute l'équipe.

Les trois zones de Git sont :
1. Le **Répertoire de travail** (le _Working Directory_) : 
    - C'est l'espace de création brut, votre espace de travail.
    - Ce sont les fichiers réels que vous voyez et éditez sur votre disque dur. C'est l'état courant de vos fichiers.
    - Les fichiers ici sont considérés comme **Modifiés** (_Modified_) s'ils ont été changés depuis le dernier `commit`, ou **Non suivis** (_Untracked_) s'ils n'ont jamais été ajoutés à Git.
2. La **Zone de Préparation** (l'_Index_ ou le _Staging Area_)
    - C'est le sas de contrôle ou la salle de tri.
    - Techniquement, c'est un fichier unique (souvent nommé index) qui contient la liste des changements des fichiers que vous avez choisi d'inclure dans le prochain `commit`.
    - Elle permet de préparer des _commits atomiques_ et de les structurer de façon à les rendre cohérents et ciblés avec un message de `commit` précis.
3. Le **Dépôt** (le _Repository_)
    - C'est la mémoire immuable du projet. La base de données `.git`.
    - C'est le dossier caché `.git` où se trouve la base de données d'objets (`blobs`, `trees`, `commit`) et l'historique complet.
    - Une fois ici, les fichiers sont considérés comme **Validés** (_Committed_). Ils sont stockés de façon permanente sous forme de snapshots compressés. Tant que le dossier `.git` existe, ces versions sont accessibles et traçables, même si elles ne sont plus visibles dans le répertoire de travail.

### Démarrage d'un projet Git

Il existe plusieurs outils différents permettant de gérer les opérations Git. 
- Git CLI : C'est l'interface en ligne de commande, la plus puissante et la plus flexible. Elle permet d'exécuter toutes les commandes Git avec une syntaxe précise.
- Git GUI : Il existe plusieurs interfaces graphiques pour Git (Git Turtoise, GitHub Desktop, Sourcetree, GitKraken, etc.) qui offrent une expérience plus visuelle et intuitive pour les utilisateurs moins à l'aise avec la ligne de commande.
- Intégration dans les IDE : De nombreux environnements de développement intégrés (IDE) comme Visual Studio Code, PyCharm, Eclipse, etc. intègrent des fonctionnalités Git directement dans l'interface de développement, facilitant ainsi la gestion des versions sans quitter l'IDE.
- Plateformes de gestion de code : Des plateformes comme GitHub, GitLab, Bitbucket, etc. offrent des interfaces web pour gérer les dépôts Git, collaborer avec d'autres développeurs, et intégrer des outils de CI/CD.

Pour ce premier contact, nous utiliserons principalement la ligne de commande pour comprendre les concepts fondamentaux de Git. Cependant, il est important de noter que dans un contexte professionnel, l'utilisation d'une interface graphique ou d'une intégration dans un IDE peut être plus efficace pour certaines tâches, notamment pour la gestion des branches, la résolution des conflits, et la visualisation de l'historique des commits.

Aussi, on encourage l'utilisation des outils intégrés dans VSCode pour les opérations courantes, mais il est essentiel de comprendre ce qui se passe en arrière-plan avec Git CLI pour pouvoir résoudre les problèmes plus complexes et pour avoir une maîtrise complète de la gestion de version. GitHub Desktop est un bon outil pour les débutants, mais il peut masquer certains détails importants de Git. Il est donc recommandé de l'utiliser en complément de la ligne de commande pour une compréhension approfondie.

### Installation de Git

Nous couvrons ici l'utilisation de Git CLI sous Windows. Vous devez d'abord télécharger et installer Git pour Windows depuis le site officiel : https://git-scm.com/download/win. Transférer l'installateur et démarrez-le. 

Important : pendant l'installation, prenez les options par défaut mais choisir ces options spécifiques :
| Fenêtre | Choix |
|:--------|:------|
| _Choose the default editor used by Git_ | _Use Visual Studio Code as Git's default editor_ |
| _Adusting the name of the initial branch in new repositories_ | _Override the default branch name for new repositories_ <br> laisser `main` |

Suite à l'installation, vous pouvez démarrer Git Bash (la touche Windows et tapez _Git Bash_) pour accéder à l'interface en ligne de commande. Tapez ensuite `git --version` pour vérifier que Git est correctement installé. Vous devriez voir la version de Git affichée, ce qui confirme que l'installation a réussi.

### Configuration initiale de Git

Avant de commencer à utiliser Git, il est important de configurer votre identité. Git utilise ces informations pour associer vos commits à votre nom et à votre adresse e-mail. Pour configurer votre nom d'utilisateur et votre adresse e-mail, utilisez les commandes suivantes dans Git Bash :

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

ou, pour une configuration locale :

```bash
git config --local user.name "Votre Nom"
git config --local user.email "votre.email@example.com"
```

Il existe plusieurs autres options de configuration que vous pouvez personnaliser selon vos préférences, comme le format de sortie des commandes, les alias pour les commandes courantes, etc. Nous en couvrirons davantage dans les sections suivantes.

### Initialisation d'un dépôt Git

Que vous commenciez un nouveau projet ou que vous souhaitiez suivre les modifications d'un projet existant, la première étape consiste à initialiser un dépôt Git. Vous pouvez initialiser un dépôt Git dans n'importe quel répertoire de votre ordinateur. Pour ce faire, naviguez vers le répertoire où vous souhaitez créer votre projet et exécutez la commande suivante :

```bash
git init
```

Cette commande crée un nouveau sous-répertoire `.git` dans le répertoire courant, qui contient tous les fichiers nécessaires pour suivre les versions de votre projet. Vous pouvez maintenant commencer à ajouter des fichiers et à faire des commits pour enregistrer l'historique de votre projet.

Les commandes de navigation en ligne de commande sont les suivantes :
| Commande | Description |
|:--------|:------------|
| `cd c:` | Change de lecteur. Par exemple, `cd c:` pour aller sur le lecteur C. |
| `cd ..` | Remonte d'un niveau dans l'arborescence des répertoires. |
| `cd <mon répertoire>` | Change de répertoire. |
| `ls` ou `dir` | Liste les fichiers et dossiers dans le répertoire courant. |
| `pwd` | Affiche le chemin complet du répertoire courant. |
| `mkdir <nom nouveau répertoire>` | Crée un nouveau répertoire. |
| `rmdir <nom répertoire>` | Supprimer un répertoire. **attention** |

Historiquement, la convention de nom pour la branche principale est `master`. Cette convention a récemment changé et est maintneant `main`. Si la création de votre dépôt Git possède le nom `master`, il est recommandé de la changer pour `main`. Voici la commande pour le faire.

`git branch -m master main`


## Le flux de travail Git

Le flux de travail est relativement simple et se compose des trois étapes associés aux trois états présentés antérieurement.

1. Travailler sur le répertoire de travail : C'est là que vous faites vos modifications. Vous pouvez ajouter, supprimer ou modifier des fichiers. Tant que vous êtes dans cette zone, les changements ne sont pas encore enregistrés dans Git.
2. Ajouter les changements à la zone de préparation : Lorsque vous êtes prêt à enregistrer les changements apportés, vous devez les ajouter à la zone de préparation. Cela se fait avec la commande `git add`. Attention, cette opération est nécessaire autant pour les fichiers ajoutés, modifiés que supprimés. 
3. Valider les changements dans le dépôt : Une fois que les changements sont dans la zone de préparation, vous pouvez les valider dans le dépôt avec la commande `git commit`. Cette étape enregistre `commit` de votre projet à ce moment précis, avec un message expliquant l'intention du changement.

N'oubliez pas que Git est un outil professionnel et qu'il permet d'innombrables scénarios de travail collaboratif. Ainsi, les différentes commandes possèdes plusieurs options possibles et il est très facile de s'y perdre. Il est donc important de comprendre les commandes fondamentales et d'apprendre à les utiliser progressivement, en fonction des besoins spécifiques de votre projet et de votre équipe.

Voici en rafal quelques commandes de base pour le flux de travail Git :
| Commande | Description |
|:--------|:------------|
| `git add <fichier>` | Ajoute un fichier spécifique à la zone de préparation. |
| `git add .` | Ajoute tous les fichiers modifiés et nouveaux à la zone de préparation. |
| `git commit` | Ouvre l'éditeur de texte pour saisir un message de `commit` décrivant les changements. |
| `git commit -m "message de commit"` | Valide les changements dans le dépôt avec un message de `commit` décrivant l'intention du changement. |
| `git commit -a -m "message de commit"` | Valide tous les changements modifiés (à l'exception des nouveaux fichiers) dans le dépôt avec un message de `commit`. |
| `git status` | Affiche l'état actuel du répertoire de travail et de la zone de préparation, montrant les fichiers modifiés, ajoutés ou supprimés. |
| `git status -s` | Affiche un résumé concis de l'état actuel du répertoire de travail et de la zone de préparation. |
| `git diff` | Affiche les différences entre les fichiers modifiés dans le répertoire de travail et la dernière version validée dans le dépôt. |
| `git log` | Affiche l'historique des commits, montrant les messages de commit, les auteurs et les dates. |


## Modifier un commit

Il arrive parfois que vous ayez besoin de modifier un `commit` après l'avoir créé. Git offre plusieurs options pour cela, en fonction de ce que vous souhaitez modifier et de l'impact que cela aura sur l'historique du projet.

> **Attention** : Il est important de noter que la modification de l'historique du projet peut causer des problèmes de collaboration si d'autres développeurs ont déjà basé leur travail sur les commits que vous modifiez. Par conséquent, il est fortement recommandé de modifier l'historique que si vous êtes certain que le `commit` n'a pas encore été partagé avec d'autres développeurs. Nous verrons bientôt comment partager le travail avec d'autres développeurs, mais pour l'instant, nous allons nous concentrer sur la modification de l'historique local.

| Commande | Description |
|:--------|:------------|
| `git commit --amend` | Permet de modifier le dernier `commit`. Vous pouvez changer le message de commit ou ajouter des changements supplémentaires à ce `commit`. Attention, cette commande modifie l'historique du projet, donc elle ne doit être utilisée que si le `commit` n'a pas encore été partagé avec d'autres développeurs. |
| `git commit --amend -m <message>` | Permet de modifier le dernier `commit` en changeant uniquement le message de commit. Les changements associés à ce `commit` restent inchangés. |
| `git add <file>` <br> `git commit --amend --no-edit` | Permet de modifier le dernier `commit` en ajoutant des changements supplémentaires. La commande `git add <file>` ajoute les changements du fichier spécifié à la zone de préparation, puis la commande `git commit --amend --no-edit` modifie le dernier `commit` en incluant ces changements sans changer le message de commit. |
| `git reset --soft HEAD~1` | Permet de réinitialiser le dernier `commit` tout en conservant les changements dans la zone de préparation. Cela vous permet de refaire le `commit` avec un message différent ou d'ajouter des changements supplémentaires. Cette commande modifie l'historique du projet, donc elle doit être utilisée avec précaution. |
| `git reset --mixed HEAD~1` | Permet de réinitialiser le dernier `commit` tout en conservant les changements dans le répertoire de travail, mais en supprimant les changements de la zone de préparation. Cela vous permet de modifier les fichiers avant de les ajouter à nouveau à la zone de préparation. Cette commande modifie l'historique du projet, donc elle doit être utilisée avec précaution. |
| `git reset --hard HEAD~1` | Permet de réinitialiser le dernier `commit` et de supprimer tous les changements associés dans le répertoire de travail. **Attention**, cette commande est destructive et doit être utilisée avec une extrême prudence, car elle supprime définitivement les commits et les changements associés. |

## Accéder à une version antérieure du projet

Il peut arriver que vous ayez besoin d'accéder à une version antérieure de votre projet pour diverses raisons, comme la correction d'un bug ou la comparaison de différentes versions du code. Git offre plusieurs commandes pour naviguer dans l'historique des commits et accéder à des versions spécifiques.

| Commande | Description |
|:--------|:------------|
| `git checkout <commit>` | Permet de basculer vers un `commit` spécifique. Cela met votre répertoire de travail dans l'état de ce `commit`, mais vous êtes en mode "détaché" (detached HEAD), ce qui signifie que vous n'êtes pas sur une branche. Vous pouvez explorer le code, mais les changements que vous faites ne seront pas associés à une branche tant que vous ne créerez pas une nouvelle branche à partir de ce `commit`. |
| `git checkout <branch>` | Permet de basculer vers le dernier `commit` de la branche concernée. À la base, l'utilisation de `master` ou `main` est généralement utilisé pour les usages de base.
| `git checkout <branche>` | Permet de basculer vers une branche spécifique. Cela met votre répertoire de travail dans l'état du dernier `commit` de cette branche. Vous pouvez faire des changements et les _commiter_ sur cette branche. |
| `git checkout <commit> -- <fichier>` | Permet de récupérer une version spécifique d'un fichier à partir d'un `commit`. Cela remplace le fichier dans votre répertoire de travail par la version du fichier à ce `commit`, mais cela ne change pas votre branche actuelle. |

## Fichiers de gestion

Git utilise plusieurs fichiers pour gérer différentes options et configurations. Nous verrons ici simplement les fichiers de configuration, d'ignore et de sauvegarde explicite de dossiers.

### Fichier de configuration : `.git/config`
- Ce fichier contient les paramètres de configuration spécifiques à votre dépôt Git. Il est créé automatiquement lors de l'initialisation du dépôt avec `git init`.
- Vous pouvez y définir des paramètres tels que les branches distantes, les alias de commandes, les hooks, etc. Il est généralement recommandé de modifier la configuration à l'aide de la commande `git config` plutôt que d'éditer directement ce fichier, car cela garantit que les modifications sont correctement appliquées et évite les erreurs de syntaxe.
- Ce fichier se trouve dans le répertoire `.git` de votre projet, et il est spécifique à ce dépôt. Si vous avez plusieurs dépôts Git sur votre machine, chacun aura son propre fichier de configuration.

### Fichier d'ignore : `.gitignore`
- Ce fichier est utilisé pour spécifier les fichiers ou les répertoires que Git doit ignorer. Cela signifie que les fichiers listés dans ce fichier ne seront pas suivis par Git et ne seront pas inclus dans les commits.
- Le fichier `.gitignore` est généralement placé à la racine de votre projet, mais vous pouvez également en avoir dans des sous-répertoires pour des règles d'ignorance spécifiques à ces répertoires.
- Les règles dans le fichier `.gitignore` peuvent inclure des noms de fichiers spécifiques, des motifs génériques (_wildcards_), ou des chemins relatifs. Par exemple, vous pouvez ignorer tous les fichiers `.log` en ajoutant `*.log` à votre fichier `.gitignore`.
- Ce fichier doit se trouver à la racine du projet. Il est important de noter que les fichiers déjà suivis par Git ne seront pas ignorés même s'ils sont listés dans le fichier `.gitignore`. Si vous souhaitez ignorer un fichier qui est déjà suivi, vous devez d'abord le supprimer de l'index avec `git rm --cached <fichier>` avant de l'ajouter à `.gitignore`. C'est pourquoi il est recommandé de créer un fichier `.gitignore` dès le début de votre projet pour éviter d'ajouter accidentellement des fichiers indésirables à votre dépôt.
- Il est possible d'ajouter des commentaires dans le fichier `.gitignore` en utilisant le symbole `#`. Les lignes commençant par `#` sont considérées comme des commentaires et ne sont pas prises en compte par Git. Cela peut être utile pour expliquer pourquoi certains fichiers ou répertoires sont ignorés, ou pour organiser les règles d'ignorance de manière plus claire.
- Voici un exemple de contenu pour un fichier `.gitignore` dans un projet Python :
    ```
    # =========================
    # Python bytecode
    # =========================
    __pycache__/
    *.py[cod]
    *$py.class

    # =========================
    # Environnements virtuels
    # =========================
    venv/
    .venv/
    env/
    ENV/

    # =========================
    # Distribution / packaging
    # =========================
    build/
    dist/
    *.egg-info/
    .eggs/

    # =========================
    # Fichiers de logs
    # =========================
    *.log

    # =========================
    # Tests / coverage
    # =========================
    .coverage
    .coverage.*
    htmlcov/
    .pytest_cache/

    # =========================
    # IDE / éditeurs
    # =========================
    .vscode/
    .idea/

    # =========================
    # Système
    # =========================
    .DS_Store
    Thumbs.db

    # =========================
    # Fichiers temporaires
    # =========================
    *.swp
    *.tmp
 
    # =========================
    # Fichiers temporaires Microsoft Office
    # =========================
    ~$*.doc*
    ~$*.xls*
    ~$*.ppt*

    *.tmp
    *.bak
    ```

### Fichier de sauvegarde explicite de dossiers : `.gitkeep`
- Git ne suit pas les dossiers vides, ce qui peut poser problème si vous souhaitez inclure un dossier dans votre projet qui doit être présent mais qui ne contient pas encore de fichiers. 
- Pour contourner ce problème, il est de convention courante d'ajouter un fichier vide nommé `.gitkeep` dans le dossier que vous souhaitez suivre.
- Le fichier `.gitkeep` n'a pas de signification spéciale pour Git, c'est simplement un fichier vide qui sert à forcer Git à suivre le dossier. Généralement, ce fichier est un fichier texte vide. Optionnellement, il peut contenir un message expliquant pourquoi le dossier doit être suivi, par exemple : _Ce dossier est destiné à contenir les fichiers de configuration_ ou _Ce dossier est destiné à contenir les fichiers temporaires_ etc.