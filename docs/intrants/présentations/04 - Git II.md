
# Git II <br> <small><small><small>Pointeurs et branches</small></small></small>

<br>

## Mise en contexte et justification

Imaginez le scénario suivant : 
- Vous développez une nouvelle fonctionnalité pour votre application. 
- Ce travail prendra plusieurs jours et, pour l'instant, votre code est instable. Soudain, un bug critique est découvert dans la version actuelle utilisée par l'un de vos clients. 
- Comment pouvez-vous corriger ce bug immédiatement sans mélanger votre code inachevé à la version stable ? 

C'est ici qu'interviennent les **branches**. Au lieu de voir l'historique comme une ligne droite unique, Git permet de créer des chemins parallèles. On peut ainsi isoler chaque tâche dans son propre espace avant de les réunir une fois le travail validé. Les tyês de tâches parallèles sont nombreuses : 
- développement de nouvelles fonctionnalités
- corrections de bugs
- configurations expérimentales
- tests de performance, de vulnérabilité, de compatibilité, etc.
- maintenance de différentes versions (ex : v1.0, v2.0)
- expérimentations
- etc.

Cette pratique permet de maintenir un historique propre et organisé, tout en facilitant la collaboration entre les membres d'une équipe. Chaque développeur peut travailler sur sa propre branche sans craindre de perturber le travail des autres, et les changements peuvent être fusionnés de manière contrôlée une fois qu'ils sont prêts. 

Cette approche ne permet pas de résoudre tous les problèmes de gestion de code, l'équipe de développement doit également adopter des pratiques de communication et de coordination efficaces pour limiter les conflits et assurer une intégration fluide des changements. Toutefois, cette capacité à travailler en parallèle sur différentes branches est l'une des raisons pour lesquelles Git est devenu si populaire dans le développement logiciel moderne.

## Les pointeurs <small><small>_concept préliminaire_</small></small>

Dans Git, il existe un concept fondamental de **pointeur** qui joue un rôle crucial dans la gestion des opérations.

Les pointeurs sont des références symboliques qui pointent vers des objets Git. Ils permettent à Git de suivre l'état actuel de votre projet et de naviguer dans l'historique des modifications.

Il existe plusieurs types de pointeurs dans Git, chacun ayant une fonction spécifique. Nous en couvrons ici quelques uns.

- Les branches
    - Les branches sont les piliers du développement parallèle, permettant d'isoler des tâches de développement spécifique.
    - Considérations techniques :
        - Rôle : Elles marquent le sommet (_tip_) d'une ligne de travail active nommée branche. Elles servent de point de ralliement pour les nouveaux `commit` au sein d'un contexte nommé.
        - Comportement : Elles sont auto-incrémentales. Lorsque vous effectuez un `commit` alors qu'une branche est active, le pointeur se déplace automatiquement pour pointer vers l'identifiant du nouveau `commit`.
        - Stockage et contenu : Un fichier texte simple situé dans `.git/refs/heads/[nom-de-la-branche]`. Il contient uniquement le hash SHA-1 (40 caractères hexadécimaux) du dernier commit de la branche.
        - Caractéristique : Il s'agit d'une référence directe vers un `commit`.
- Le `HEAD` (pointeur de contexte)
    - Le `HEAD` est l'unique indicateur de l'état actuel de votre environnement de travail. Plus précisément, il définit à quel `commit` l'état de votre _Dossier de travail_ se trouve (les fichiers et leurs dossiers).
    - Considérations techniques :
        - Rôle : Il détermine quel `commit` ou quelle branche est actuellement extrait dans le _Dossier de travail_. C'est la référence de base pour les opérations de comparaison (`diff`) et de validation (`commit`). C'est un concept de contexte, pas un marqueur d'état de l'histoire. C'est aussi un concept fondamental pour la navigation dans l'historique et la gestion des branches.
        - Comportement : Il est mobile par navigation. Il change dès que vous utilisez `git checkout` ou `git switch`. Il agit comme une ombre : s'il pointe vers une branche, il suit les mouvements de celle-ci.
        - Stockage et contenu : Un fichier unique situé à la racine du dossier administratif : `.git/HEAD`. Son contenu est typiquement `git/refs/heads/nom-de-la-branche` ou un hash SHA-1 en état de _Detached HEAD_.
        - Caractéristique : Il s'agit généralement d'une référence symbolique (un pointeur vers un pointeur), sauf en état de _Detached HEAD_ où il devient une référence directe. Nous reviendrons sur le concept de _Detached HEAD_ plus tard.
- Les étiquettes ou _tags_
    - Les _tags_ agissent comme des points de référence immuables dans l'histoire d'un projet. Ils servent habituellement pour donner un nom symbolique à un point spécifique de l'histoire, souvent utilisés pour marquer les versions de production.
    - Rôle : Ils servent à nommer de manière permanente un point spécifique de l'histoire pour une consultation ultérieure simplifiée (ex: v1.0.4). L'objectif étant de nommer un `commit` significatif avec un nom symbolique facilement identifiable pour les humains, plutôt que de devoir se souvenir d'un hash SHA-1 complexe.
    - Comportement : Ils sont statiques. Une fois créé, un tag ne bouge jamais, même si vous ajoutez de nouveaux `commits` par la suite. Pour déplacer un _tag_, il faut explicitement le supprimer et le recréer.
    - Stockage et contenu : Un fichier texte dans `.git/refs/tags/[nom-du-tag]`. Il contient le hash SHA-1 du `commit` visé ou le hash de l'objet _tag_ s'il est annoté.
    - Nature technique : Il existe deux types de _tag_ :
        - _tag_ léger (_lightweight tag_), une référence directe vers le `commit` sans métadonnées supplémentaires.
        - _tag_ annoté (_annotated tag_), un objet Git complet pointé par une référence dans la base d'objets incluant le `commit` et plusieurs métadonnées : auteur, date, signature GPG, message.
- Les pointeurs de synchronisation (_Remote References_)
    - Ces références permettent la synchronisation de l'état des dépôts distants avec la machine locale.
    - Rôle : Elles servent de miroirs locaux aux branches présentes sur un serveur (comme GitHub). Elles permettent de calculer la divergence (`commits` en avance ou en retard) sans solliciter le réseau à chaque commande.
    - Comportement : Elles sont mobiles lors des synchronisations avec le serveur distant. On ne peut pas les déplacer manuellement ni faire des `commit` sur ces références. Elles ne sont mises à jour que lors d'échanges réseau via les commandes spécifiques (`fetch`, `pull`, `push`).
    - Stockage et contenu : Des fichiers situés dans `.git/refs/remotes/[nom-du-remote]/[nom-de-la-branche]`. Comme les branches locales, ils contiennent le hash SHA-1 du dernier `commit` connu sur le serveur.
    - Nature technique : Il s'agit d'une référence directe en lecture seule pour l'utilisateur.
    - Note : Nous verrons les dépôts distants et les commandes associées plus en détail dans la section dédiée. Toutefois, il est important de comprendre que Git maintient des pointeurs locaux pour suivre l'état des branches sur les serveurs distants.

## Les branches

L'une des plus grandes forces de Git réside dans sa gestion extrêmement légère des branches.

### Définition

Contrairement à d'autres systèmes qui copient physiquement les fichiers dans de nouveaux dossiers, une branche Git est simplement un **pointeur mobile** vers un `commit` spécifique.

- Techniquement, une branche est un petit fichier texte contenant l'**id**entifiant SHA-1 du dernier `commit` de cette lignée parfois nommé _tip_.
- Lorsque vous créez un nouveau `commit`, le pointeur de la branche active avance automatiquement.
- Lors de la création d'un nouveau dépôt, la branche par défaut est nommée `master` ou `main` - `master` étant l'ancienne convention, `main` étant la nouvelle norme adoptée pour éviter les connotations négatives (juillet 2020, Git 2.28). 
    > Note : 
    > 
    > Malgré cette convention, lors de l'installation de Git, la branche par défaut se nomme toujours `master` pour plusieurs raisons techniques et historiques. Toutefois, tous les mécanismes sont présents pour modifier le nom afin d'adopter la nouvelle convention : 
    > - changer manuellement le nom de la branche du nouveau dépôt : <br> `git branch -m master main`
    > - changer la configuration globale pour que tous les nouveaux dépôts utilisent `main` par défaut : <br>`git config --global init.defaultBranch main`
    >
    > Finalement, GitHub a adopté `main` comme nom de branche par défaut pour tous les nouveaux dépôts créés sur sa plateforme à partir de 2021, ce qui a accéléré l'adoption de cette nouvelle convention dans la communauté.

### Commandes utilitaires pour la visualisation de l'historique

- `git log` <br> Pour visualiser l'historique de votre projet, la commande `git log` est votre meilleur allié. Par défaut, elle affiche une liste détaillée de tous les `commits` dans l'ordre chronologique inverse (du plus récent au plus ancien). Cependant, pour une vue plus condensée et structurée, vous pouvez utiliser des options supplémentaires.
- `git log --oneline --graph` <br> Cette commande affiche chaque `commit` sur une seule ligne, avec une représentation graphique des branches et des fusions. Cette commande n'affiche que les `commits` de la branche active. 
- `git log --oneline --graph --all` <br> L'une des commandes les plus intéressantes pour visualiser l'état du dépôt est `git log --oneline --graph --all`. Cette commande affiche l'historique de tous les `commits` de manière condensée, avec une représentation graphique des branches et des fusions. C'est un excellent moyen de comprendre la structure de votre projet et de voir comment les différentes branches évoluent au fil du temps. Cette commande affiche tous les pointeurs inclus dans `.git/refs/`.
- `git log ... -n <n>` <br> Si trop de `commit` sont affichés, vous pouvez limiter le nombre de `commit` affichés avec l'option `-n` ou `--max-count`<br> Par exemple, cette commande affiche les 10 derniers `commits` <br> `git log --oneline --graph --all -n 10`
- Si en cours de présentation, vous souhaitez arrêter la commande `git log ...` pour revenir à l'invite de commande, il suffit d'appuyer sur la touche `q` (pour _**q**uit_).

### Création d'une nouvelle branche

Pour créer une nouvelle branche, il suffit de la créer en lui donnant un nom approprié. 

> Note 
>
> Il existe des conventions de nommage pour les branches. Comme pour les `commit`, ces conventions ne sont pas strictes mais aident à maintenir un historique clair et plus facile à interpréter. Souvent, les entreprises adoptent des conventions de nommage spécifiques pour leurs branches et les documentent dans leurs guides de contribution.

Lorsque vous créez une nouvelle branche, elle pointe initialement vers le même `commit` que votre branche actuelle (par exemple, `main`). À ce moment, les deux branches pointent vers le même `commit`, mais elles sont indépendantes. Le pointer `HEAD` lui, n'a pas changé et pointe toujours vers la branche active. Si on désire travailler sur la nouvelle branche, il faut y basculer pour que le `HEAD` pointe vers elle.

Voici les commandes importantes à comprendre :

| Commande | Action |
|:---------|:-------|
| `git branch <nom>` | Crée une nouvelle branche (étiquette) sur le commit actuel. |
| `git switch <nom>` | Déplace le `HEAD` vers la branche spécifiée et met à jour vos fichiers. |
| `git switch -c <nom>` | Crée la branche **et** y bascule immédiatement (raccourci). Le `c` fait référence à _create_. |


**Exemple concret :**
```bash
# Création d'une branche pour une nouvelle fonctionnalité
git switch -c feature-friction

# Après quelques modifications...
git add .
git commit -m "feat: ajout de la friction dans le modèle physique"

# Le pointeur 'feature-friction' a avancé, mais 'main' est resté derrière.
```

### Navigation entre les branches

Pour basculer entre les branches, vous utilisez la commande `git switch <nom-de-la-branche>`. Lorsque vous basculez vers une branche, Git met à jour votre _Dossier de travail_ pour refléter l'état du `commit` pointé par cette branche.

Chaque branche peut évoluer indépendamment, ce qui vous permet de travailler sur différentes fonctionnalités ou corrections de bugs en parallèle sans interférer les unes avec les autres.

### Fusion d'une branche

La fusion est le processus de prise des changements d'une branche et de les intégrer dans une autre. Il existe plusieurs types de fusion, mais les deux principaux sont :
- **Avance rapide** ou _**Fast-forward**_ :
    - Cette apporoche n'est pas une fusion au sens structurel du terme, mais plutôt un déplacement linéaire de pointeur.
    - L'intention : Intégrer des modifications d'une branche source vers une branche cible lorsque l'historique de la cible n'a pas divergé. C'est le cas typique où vous travaillez seul sur une branche de fonctionnalité alors que `main` est resté immobile.
    - Considérations techniques : 
        - Git vérifie que le sommet (_tip_) de la branche cible est un ancêtre direct du sommet de la branche source. Aucune modification de code n'est réellement calculée par Git. Il se contente de déplacer le pointeur adéquatement. Si la branche cible a avancé depuis la création de la branche source, Git ne peut pas faire un fast-forward et doit recourir à une fusion classique (_three-way merge_).
        - Pointeurs et fichiers : Le fichier `.git/refs/heads/<target>` reçoit simplement le hash SHA-1 contenu dans `.git/refs/heads/<source>`.
        - Visibilité de la structure : La branche fusionnée devient totalement invisible dans l'historique du graphe. Puisque Git se contente de déplacer le pointeur main vers le haut, la lignée de commits **apparaît** comme une suite continue sur `main`. On perd la trace visuelle indiquant que ce travail a été réalisé sur une autre branche.
        - Existence après merge : Le pointeur de la branche existe toujours et pointe désormais sur le même `commit` que `main`. Techniquement, la branche est devenue redondante. Il est possible de la supprimer (`git branch -d`) sans qu'aucune information structurelle ne disparaisse du graphe.
        - La position du `HEAD` : Après un fast-forward, le `HEAD` continue de pointer vers la branche cible (ex: `main`), qui a été avancée pour inclure les changements de la branche source. Le `HEAD` ne change pas de branche, il suit simplement le mouvement de la branche cible.
        - `commit` : Aucun nouveau `commit` n'est créé. L'historique reste une ligne droite parfaite.
    - Commandes : L'opération de fusion doit se faire manuellement en deux étapes :
        1. Si ce n'est pas déjà fait, basculez sur la branche cible - la fusion se fait à partir de la cible : <br> `git switch main`
        2. Lancez la fusion : <br> `git merge feature-branch` Git choisi le _fast-forward_ par défaut si possible, sinon il lancera une fusion classique (_three-way merge_). <br> `git merge --ff-only feature-branch` Cette commande force Git à faire un _fast-forward_ uniquement. Si ce n'est pas possible, la fusion échouera et vous devrez résoudre le problème manuellement. Cette approche est celle préconisée pour les développeurs qui veulent s'assurer que leur historique reste linéaire et propre, sans `commit` de fusion superflu.
    - Résultat : Si la fusion est réussie, la branche cible (ex: `main`) pointera désormais vers le même `commit` que la branche source (ex: `feature-branch`), et l'historique du projet apparaîtra comme une ligne droite continue, sans indication visuelle de la branche source.
    - Recommandation : Après un _fast-forward_, la branche source (ex: `feature-branch`) est devenue redondante car elle pointe désormais vers le même `commit` que la branche cible (ex: `main`). 
        - Il est généralement recommandé de supprimer la branche source pour éviter toute confusion future. Cette commande supprimera la branche source en toute sécurité, car les changements ont déjà été intégrés dans la branche cible. <br> `git branch -d feature-branch` 

- **Fusion à trois points** ou _**Three-Way Merge**_
    - Cette méthode intervient lorsque les deux branches ont divergé, c'est-à-dire que des `commits` ont été ajoutés sur `main` **et** sur `feature-branch` depuis leur ancêtre commun.
    - L'intention : Réunifier deux lignées de développement distinctes en créant un nouvel état qui combine les deux historiques.
    - Considérations techniques :
        - Git utilise l'algorithme de fusion récursive. Il identifie trois points : le sommet de _A_, le sommet de _B_, et l'ancêtre commun le plus proche (appelé le _merge base_). Git compare les différences à partir de cet ancêtre pour générer le résultat final.
        - Pointeurs et fichiers : Le fichier de branche cible `main` est mis à jour pour pointer vers un tout nouveau `commit` créé explicitement pour cette opération.
        - Visibilité de la structure : La branche est préservée visuellement dans l'histoire grâce au nouveau `commit` convergeant créé par la fusion. Même après des années, on peut voir l'endroit précis où la branche a bifurqué de `main` et où elle y est retournée. C'est une structure distinctive qui documente le cycle de vie d'une fonctionnalité.
        - Existence après merge : Bien que le pointeur `feature-branch` puisse être supprimé, la trace de son existence demeure gravée dans le graphe grâce au deuxième parent de la fusion. La structure en _losange_ survit à la suppression de l'étiquette de la branche, car le `commit` de fusion pointe vers ses deux parents (les deux lignées parallèles de `commit`)
        - La position du `HEAD` : Après une fusion à trois points, le `HEAD` continue de pointer vers la branche cible (ex: `main`), qui a été mise à jour pour inclure les changements de la branche source. Le `HEAD` ne change pas de branche, il suit simplement le mouvement de la branche cible et pointe vers le nouveau `commit` créé.
        - `commit` : Un nouveau `commit` est créé. Dans le jargon, on l'appel spécifiquement `merge commit`. Ce commit possède la particularité d'avoir deux parents au lieu d'un seul.
    - Commandes : La fusion à trois points se fait de la même manière que le _fast-forward_, mais Git choisira automatiquement la méthode appropriée en fonction de l'état des branches. 
        1. Si ce n'est pas déjà fait, basculez sur la branche cible - la fusion se fait à partir de la cible : <br> `git switch main`
        2. Lancez la fusion : <br> `git merge feature-branch` Git choisi le _three-way merge_ si le _fast-foward_ n'est pas possible. <br> `git merge --no-ff feature-branch` Cette commande force Git à faire un _three-way merge_ uniquement. Cette approche est celle préconisée pour les développeurs qui veulent s'assurer de garder la trace de toutes les modifications.
    - Recommandations : 
        - Après une fusion à trois points, la branche source (ex: `feature-branch`) peut être supprimée en toute sécurité, car les changements ont déjà été intégrés dans la branche cible. 
        - Il est important de comprendre que l'on supprime une branche ou non, la trace de son existence restera toujours visible dans l'historique grâce au `merge commit` et au fait que tous les `commits` de la branche sont présents dans la base de données Git. 
        - En général, il est recommandé de supprimer la branche source après la fusion pour plusieurs considérations comme la surcharge de branche dans la liste des branches, la confusion potentielle pour les nouveaux développeurs, ou simplement pour maintenir une liste de branches plus propre et plus facile à gérer. Aussi, il est préférable de supprimer la branche pour éviter les conflits de nommage dans le futur où le même nom pourrait être réutilisé. Finalement, le message du `commit` devrait inclure le nom de la branche source pour garder une trace claire de l'origine des changements, même après la suppression de la branche.
        - Il existe quand même quelques situations où on ne supprime pas une branche. Voici quelques cas significatifs :
            - Si la fusion est incrémentale sur une branche dont la fonctionnalité continuera à évoluer.
            - Si la branche source est utilisée comme base pour d'autres branches qui sont encore en développement.
            - Si la branche source est une branche de longue durée qui sert de référence pour des travaux futurs (par exemple, différentes versions d'un logiciel).
        - `git branch -d feature-branch` <br> est la commande pour supprimer la branche source.

Pour les étudiants curieux, voici quelques autres types de fusion possibles :
- _**Squash merge**_ : Cette méthode combine tous les changements d'une branche source en un seul `commit` avant de les intégrer dans la branche cible. Cela permet de garder un historique plus propre, surtout si la branche source contient de nombreux `commits` intermédiaires qui ne sont pas significatifs individuellement.
- _**Rebase**_ : Plutôt que de créer un `commit` de fusion, le rebase réécrit l'historique de la branche source pour qu'elle semble avoir été créée à partir du dernier `commit` de la branche cible. Cela peut rendre l'historique plus linéaire et plus facile à suivre, mais il faut faire attention lors de l'utilisation du rebase, surtout si la branche source a déjà été partagée avec d'autres développeurs.
- _**Cherry-pick**_ : Cette méthode permet de sélectionner des `commits` spécifiques d'une branche source et de les appliquer à une branche cible, sans fusionner l'ensemble de la branche source. C'est utile pour intégrer des changements spécifiques sans avoir à fusionner toute la branche.

### Résolution de conflits de fusion

Lorsqu'une fusion entraîne des conflits, Git marque les fichiers concernés et vous devez les résoudre manuellement. Voici les étapes générales pour résoudre un conflit de fusion :
1. Identifiez les fichiers en conflit : Git vous indiquera quels fichiers sont en conflit après la tentative de fusion. Vous pouvez également utiliser `git status` pour voir la liste des fichiers en conflit.
2. Ouvrez les fichiers en conflit : Les fichiers en conflit contiendront des marqueurs spéciaux pour indiquer les sections de code en conflit. Ces marqueurs ressemblent à ceci :
    ```diff
    <<<<<<< HEAD
    // Code de la branche cible (ex: main)
    =======
    // Code de la branche source (ex: feature-branch)
    >>>>>>> feature-branch
    ```
3. Résolvez les conflits : Modifiez le fichier pour conserver le code que vous souhaitez garder et supprimer les marqueurs de conflit. Vous pouvez choisir de conserver le code de la branche cible, le code de la branche source, ou une combinaison des deux.
4. Marquez les conflits comme résolus : Une fois que vous avez résolu les conflits dans tous les fichiers concernés, vous devez les ajouter à l'index pour indiquer à Git que les conflits ont été résolus. Utilisez la commande `git add <fichier>` pour chaque fichier résolu.
5. Finalisez la fusion : Après avoir ajouté tous les fichiers résolus, vous pouvez finaliser la fusion en créant un `commit` de fusion. Utilisez la commande `git commit` pour créer ce `commit`. Git ouvrira votre éditeur de texte par défaut pour vous permettre de saisir un message de commit. Par défaut, le message de commit contiendra une description de la fusion, mais vous pouvez le modifier si nécessaire.

Il est possible d'indiquer quel outil de fusion vous souhaitez utiliser pour résoudre les conflits. Git prend en charge plusieurs outils de fusion tiers, tels que `meld`, `kdiff3`, `vimdiff`, `vscode`, etc. Vous pouvez configurer votre outil de fusion préféré en utilisant la commande `git config --global merge.tool <nom-de-l'outil>`. Par exemple, pour configurer `vscode` comme outil de fusion par défaut, vous pouvez utiliser la commande suivante : `git config --global merge.tool code`. Ensuite, lorsque vous rencontrerez un conflit de fusion, vous pourrez lancer l'outil de fusion en utilisant la commande `git mergetool`, qui ouvrira l'interface graphique de l'outil pour vous aider à résoudre les conflits.

Certaines configurations de `vscode` limitent l'exécution de son usage en tant qu'outil de fusion par défaut. Les commandes suivantes permettent de résoudre plusieurs problèmes de configuration. Ces trois lignes sont nécessaires :
- `git config --global merge.tool code`
- `git config --global mergetool.code.cmd 'code --wait --merge "$LOCAL" "$REMOTE" "$BASE" "$MERGED"'`
- `git config --global mergetool.keepBackup false`

### Bonnes pratiques

La gestion des branches est un aspect crucial du développement avec Git. Voici quelques bonnes pratiques à suivre pour tirer le meilleur parti de ce système de contrôle de version :
- Nommez vos branches de manière descriptive en utilisant les normes de nommage établies par l'entreprise où vous vous trouvez ou en établissant vos propres conventions claires.
- Utilisez `git switch -c <nom-de-la-branche>` pour créer une nouvelle branche et y basculer immédiatement, afin de vous assurer que vous travaillez dans le bon contexte dès le départ.
- Fusionnez régulièrement les branches pour éviter les divergences importantes qui peuvent rendre la fusion plus complexe.
- Sauf pour les cas énumérés, supprimez les branches une fois qu'elles ont été fusionnées pour maintenir un historique propre et éviter la confusion.
- Utilisez des messages de `commit` clairs et descriptifs pour faciliter la compréhension de l'historique du projet, surtout lors de la fusion de branches.
- Communiquez efficacement avec votre équipe pour coordonner les travaux sur différentes branches et éviter les conflits de fusion.

## Les _tags_

Les _tags_ sont des pointeurs immuables qui servent à marquer des points spécifiques dans l'histoire de votre projet. Ils sont souvent utilisés pour marquer les versions de production ou les étapes importantes du développement.

Ils sont faciles à manipuler et offrent une manière simple de référencer des `commits` significatifs sans avoir à se souvenir de leurs hash SHA-1 complexes.

Commandes importantes pour les _tags_ :
| Commande | Action |
|:---------|:-------|
| `git tag <nom-du-tag>` | Crée un _tag_ léger pointant vers le `commit` actuel. <br> `git tag v1.0` |
| `git tag -a <nom-du-tag> -m "<message>"` | Crée un _tag_ annoté avec un message descriptif. |
| `git show <nom-du-tag>` | Affiche les détails du _tag_, y compris le `commit` pointé et les métadonnées si c'est un _tag_ annoté. |
| `git tag` | Liste tous les _tags_ dans le dépôt. |
| `git tag -d <nom-du-tag>` | Supprime un tag existant. |
| `git tag -l "v1.*"` | Liste les _tags_ correspondant au motif spécifié (ex: tous les _tags_ commençant par "v1."). |

Attention, les _tags_ sont immuables par nature. Si vous souhaitez déplacer un _tag_ pour qu'il pointe vers un autre `commit`, vous devez d'abord supprimer le _tag_ existant et en créer un nouveau avec le même nom pointant vers le nouveau `commit`. Par exemple :
```bash
git tag -d <nom-du-tag>
git tag <nom-du-tag> <nouveau-commit>
```

## Commandes utilitaires pour la navigation relative à partir d'un pointeur

Il est plutôt fréquent d'avoir à faire référence à un `commit` spécifique dans l'historique pour effectuer une opération. Plutôt que de devoir copier-coller le hash SHA-1 du `commit`, Git offre des raccourcis de navigation très pratiques basés sur la position relative d'un pointeur (généralement `HEAD`).

Voici les principaux raccourcis de navigation :
| Raccourci | Signification | Exemple d'utilisation |
|:---------|:--------------|:----------------------|
| `HEAD` | Le `commit` actuellement extrait dans le _Dossier de travail_. | `git log HEAD` |
| `HEAD~n` | Le `commit` _n_ positions avant le `HEAD`. | `git log HEAD~3` |
| `HEAD^` | Le parent du `commit` pointé par `HEAD`. | `git log HEAD^` |
| `HEAD^n` | Le n-ième parent du `commit` pointé par `HEAD`. <br> Utile pour les `merge commit` qui ont plusieurs parents où _n_ indique le _n-ième_ parent. | `git log HEAD^2` |
| `HEAD@{n}` | Le `commit` pointé par `HEAD` _n_ positions dans le passé. <br> Ne vient pas de l'historique des _commits_ mais du _ref log_ (journal d'activités) affichant où se trouvait le `HEAD` il y a _n_ _commits_. | `git log HEAD@{1}` |


## Résolution de problèmes classiques

### On a créé une branche mais on a oublié d'y basculer avant de faire des commits.

L'une des méthodes les plus simples pour résoudre ce problème proprement se passe en 3 étapes :
1. Repositionner la branche cible sur le dernier `commit` <br> `git branch -f <new-branch> <previous-branch>` <br> `git branch -f new-feature main`
2. Reculer la branche précédente pour revenir à l'état avant les `commits` <br> `git reset --hard HEAD~<n>` <br> `git reset --hard HEAD~1` (si un seul commit a été fait)
3. Basculez sur la nouvelle branche <br> `git switch <new-branch>` <br> `git switch new-feature`

Pratiquez vous, essayez de faire ce scénario dans votre dépôt de test pour bien comprendre les étapes et les commandes associées. Surtout, faites des `git log` à chaque étape pour visualiser l'évolution de l'historique et des pointeurs.

Dans ce cas précis, l'utilisation initiale de la commande `git switch -c <new-branch>` aurait permis de créer la branche et d'y basculer immédiatement, évitant ainsi ce problème. C'est une bonne pratique de toujours utiliser cette commande pour créer une nouvelle branche afin de s'assurer que vous travaillez dans le bon contexte dès le départ.

### ...

## Résumé des commandes Git 

| Commande | Action |
|:---------|:-------|
| `git branch` | Liste toutes les branches locales et indique la branche actuelle avec un `*`. |
| `git branch <nom>` | Crée une nouvelle branche (étiquette) sur le commit actuel. |
| `git switch <nom>` | Déplace le `HEAD` vers la branche spécifiée
| `git switch -c <nom>` | Crée la branche **et** y bascule immédiatement (raccourci). Le `c` fait référence à _create_. |
| `git merge <nom-de-la-branche>` | Fusionne la branche spécifiée dans la branche active. Git choisira automatiquement la méthode de fusion appropriée (fast-forward ou three-way merge) en fonction de l'état des branches. |
| `git merge --ff-only <nom-de-la-branche>` | Force Git à faire un fast-forward uniquement. Si ce n'est pas possible, la fusion échouera et vous devrez résoudre le problème manuellement. |
| `git merge --no-ff <nom-de-la-branche>` | Force Git à faire un three-way merge uniquement, même si un fast-forward serait possible. |
| `git branch -d <nom-de-la-branche>` | Supprime la branche spécifiée. Cette commande vérifie que la branche a été fusionnée avant de la supprimer pour éviter toute perte de données. |
| `git log` | Affiche l'historique des commits. |
| `git log --oneline --graph` | Affiche l'historique des commits
| `git log --oneline --graph --all` | Affiche l'historique de tous les commits de manière condensée, avec une représentation graphique des branches et des fusions. |
| `git log --oneline --graph --all -n <n>` | Affiche les _n_ derniers commits de manière condensée, avec une représentation graphique des branches et des fusions. |
| `git status` | Affiche l'état actuel du dépôt, y compris les fichiers modifiés, les fichiers en conflit, et les branches. |
| `git mergetool` | Lance l'outil de fusion configuré pour résoudre les conflits de fusion. |

