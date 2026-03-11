# GitHub I <br> <small><small><small>Collaboration et dépôts distants</small></small></small>

<br>

## Mise en contexte et justification

Jusqu’à présent, nous avons utilisé Git comme un outil individuel. Tout le contenu, les connaissances, l'historique et les branches résident exclusivement sur la machine locale. Mais la force de l'ingénierie moderne réside dans le développement distribué.

Le défi est le suivant : _Comment permettre à 10 ingénieurs de travailler sur le même projet sans qu'un serveur central ne devienne un goulot d'étranglement ?_ 

Git répond à cela par son architecture **décentralisée**, son **modèle de collaboration distribué** et son **protocole de synchronisation distant**. Contrairement à d'autres outils, on considère que chaque copie du projet se trouvant chez les participants sont des clones complet possédant toute la base de données. Le serveur n'est alors qu'un point de convergence commun. C'est le point de référence absolu vers lequel tous les participants au projet synchronisent leurs travaux.


## Git et son infrastructure de communication

Dans un système de gestion de versions distribué, l'un des défis techniques principaux est l'efficacité des transferts. Il suffit d'imaginer un projet contenant des milliers de fichiers et des années d'historique. Si, à chaque fois que l'on désire récupérer une simple mise à jour, nous devions télécharger l'intégralité du projet, le réseau serait rapidement saturé et nous serions en attente permanente.

Git résout ce problème par une négociation intelligente. Au lieu de copier aveuglément des fichiers, Git utilise deux processus de bas niveau (appelés commandes de _plumbing_) qui discutent entre le client et le serveur pour déterminer quel est le strict minimum de données à transférer.

Bien que l'on parle parfois de _protocole Git_, il est plus précis de parler d'exécutables implémentant un protocole de transfert filaire (_wire protocol_). Ces exécutables sont `git-upload-pack` et `git-receive-pack`.

Ils peuvent être transportés par différents protocoles réseau, mais la logique d'échange reste identique :
* **SSH** : Le serveur lance ces programmes via une session sécurisée.
* **HTTPS** : Le serveur web déclenche ces programmes via des scripts spécialisés.

### La distribution : Serveur → Client

Ce processus s'exécute sur le serveur lorsque vous effectuez des commandes où l'information est sur le serveur (`git fetch`, `git pull` ou `git clone` par exemple). Son rôle est d'envoyer les données manquantes au client. C'est le programme `git-upload-pack` qui s'en charge.

L'opération suit un cycle de discussion très précis :
1. **Annonce des références** : Le serveur commence par lister toutes les branches et tous les tags qu'il possède, avec leurs hash SHA-1 respectifs.
2. **Détermination des besoins** : Le client compare cette liste avec sa propre base de données locale. Il répond au serveur avec deux listes :
    * **"wants"** : Les _commits_ que le client désire (ceux qu'il n'a pas).
    * **"haves"** : Les _commits_ que le client possède déjà (pour que le serveur sache où s'arrêter dans l'historique).
3. **Génération du Packfile** : Le serveur calcule la différence, génère un fichier unique compressé (le `.pack`) contenant uniquement les objets nécessaires, et l'envoie au client.
4. **Intégration locale** : Le client reçoit le `packfile`, le décompresse, et intègre les nouveaux objets dans sa base de données locale.

> Note : C'est cette phase de négociation qui rend Git extrêmement performant. Le serveur ne devine pas ce dont vous avez besoin ; il le calcule mathématiquement à partir de ce que vous avez déjà.

### La réception : Client → Serveur

Ce processus s'exécute sur le serveur lorsque vous effectuez une commande où l'information est envoyée au serveur (`git push` par exemple). Son rôle est de recevoir et de valider les données envoyées par le client. C'est le programme `git-receive-pack` qui s'en charge.

L'opération suit également un cycle de discussion précis, mais avec une logique inverse :
1. **Annonce de l'état** : Le serveur indique au client où en sont ses branches actuelles.
2. **Réception du flux** : Le client envoie un `packfile` contenant les nouveaux _commits_ et objets.
3. **Vérification d'intégrité** : Le processus vérifie que les nouveaux _commits_ sont valides et, surtout, qu'ils respectent la lignée de l'historique des branches.
4. **Mise à jour des pointeurs** : Si toutes les vérifications passent, le serveur met à jour les fichiers de référence (les branches) pour pointer vers les nouveaux sommets (_tips_).

### Une infrastructure pour la collaboration distante

Git offre cette architecture logicielle pour permettre la création de n'importe quel outil de travail à distance. Cette infrastructure repose sur trois piliers :

1. Le dépôt nu ou _Bare Repository_ <br> Pour qu'un serveur puisse fonctionner efficacement avec ces outils, on utilise généralement un dépôt `--bare`. 
    - Un dépôt nu n'a aucun _dossier de travail_ (on ne peut pas y éditer de fichiers). 
    - Il ne contient que la base de données (le contenu du dossier `.git`). 
    - C'est la cible idéale pour `receive-pack` car il n'y a jamais de risque de conflit avec des modifications en cours sur le serveur.
2. L'abstraction du transport <br> L'infrastructure Git est agnostique. Elle se moque de savoir si les données passent par un câble réseau, un tunnel crypté ou même un dossier partagé sur un réseau local. Les commandes de transfert restent les mêmes.
3.  Les déclencheurs ou les _hooks_ <br> `git-receive-pack` permet de lancer des scripts automatiquement sur le serveur :
    - `pre-receive` : Peut être utilisé pour refuser un `push` si le code ne compile pas ou ne respecte pas les normes de l'entreprise.
    - `post-receive` : Peut être utilisé pour déclencher une action, comme le déploiement automatique du code sur un serveur web dès qu'il est reçu.

## Les forges logicielles

Puisque Git est un standard ouvert, plusieurs entreprises ont créé des plateformes (appelées **Forges**) pour héberger ces dépôts et y ajouter des services collaboratifs (interface web, gestion de tickets, sécurité, etc.).

### Les principaux acteurs

| Plateforme | Propriétaire | Points forts |
|:-----------|:----------------|:-------------|
| **GitHub** | Microsoft | Communauté immense, écosystème d'outils tiers. |
| **GitLab** | GitLab Inc. | Outils de déploiement (CI/CD) intégrés, très flexible. |
| **Bitbucket** | Atlassian | Intégration parfaite avec Jira et Trello. |
| **Azure DevOps** | Microsoft | Orienté vers les grandes structures et le cloud Azure. |
| **Gitea** | Communauté open source | Léger, facile à auto-héberger, idéal pour les petites équipes. |

### Le serveur local

Une entreprise n'est pas obligée d'utiliser un service tiers. Elle peut héberger ses propres dépôts :
- **Serveur nu** : Un simple serveur Linux avec `git init --bare`. C'est l'approche la plus légère et sécurisée.
- **Auto-hébergement** : Installer sa propre instance de `GitLab` ou `Gitea` sur ses serveurs privés pour garder un contrôle total sur les données.

### Domination de GitHub

GitHub est devenu le standard de facto pour l'hébergement de projets open source et privés. Sa popularité s'explique par :
- Une interface utilisateur intuitive.
- Un écosystème riche de plugins et d'intégrations.
- Une communauté active qui facilite la collaboration et le partage de code.
- Une multitude de fonctionnalités supplémentaires (actions pour _CI/CD_, pages d'hébergement de sites statiques, etc.) qui en font une plateforme complète pour les développeurs.
- Sa capacité à élargir son offre pour des projets d'ingénierie variés dépassant le cadre du développement logiciel (documentation, gestion de projet, etc.).

Dans le cadre de cette présentation, nous allons utiliser GitHub pour illustrer les concepts de collaboration à distance, mais les principes s'appliquent à n'importe quelle forge logicielle compatible avec Git.

## Concepts clés à comprendre

### Distinction fondamentale : Git vs GitHub

C'est la confusion la plus fréquente lors d'une première introduction. 

- **Git :** C'est le moteur technique. C'est l'outil en ligne de commande qui gère les _commits_, les branches et le calcul des différences (`diff`). Il fonctionne parfaitement sans internet et sans forge.
- **GitHub :** C'est une plateforme d'hébergement et une forge logicielle. Elle fournit un serveur distant pour stocker vos dépôts Git et ajoute, via une interface web, des outils de gestion de projet, des mécanismes de sécurité ainsi qu'une multitude de fonctionnalités supplémentaires.

### Le concept de dépôt distant (_remote repository_)

Un dépôt distant n'est rien d'autre qu'une adresse URL vers une version de votre projet stockée ailleurs. Il peut s'agir d'un serveur privé, d'une instance auto-hébergée ou d'une plateforme comme GitHub. Il est aussi possible d'avoir plusieurs dépôts distants pour un même projet (par exemple, un dépôt sur GitHub et un autre sur GitLab).

- **Le nom _origin_** : 
    - Par convention, le premier serveur distant ajouté à un projet Git est nommé `origin`. 
    - Ce n'est pas un nom imposé par Git, mais une norme universelle suivie par les développeurs. 
    - Ce premier dépôt distant est généralement celui vers lequel vous poussez votre code et d'où vous tirez les mises à jour. 
    - Il a aussi la particularité d'être le dépôt de référence pour la plupart des commandes Git qui impliquent un serveur distant.
- **Lien avec le serveur** : S'il n'est pas déjà établi, on lier notre dépôt local et le serveur distant avec la commande suivante : <br>
    `git remote add origin https://github.com/<utilisateur>/<projet>.git`
---

### L'état local vs l'état distant

Il est crucial de comprendre que votre dépôt local et le dépôt distant sont deux entités distinctes. Votre dépôt local contient votre historique de _commits_, vos branches, vos _tags_ et vos fichiers, tandis que le dépôt distant est une copie de référence qui peut être mise à jour par d'autres collaborateurs. 

Lorsque vous travaillez sur votre machine, vous modifiez votre dépôt local. Les changements ne sont pas automatiquement reflétés sur le serveur tant que vous ne les avez pas poussés (_push_). De même, les changements effectués par d'autres collaborateurs sur le serveur ne sont pas visibles dans votre dépôt local tant que vous ne les avez pas récupérés (_pull_).

La synchronisation entre ces deux mondes se reflète directement par l'état de vos _pointeurs_. Votre branche locale `main` peut être en avance ou en retard par rapport à `origin/main`, et c'est cette relation qui détermine les actions à entreprendre pour rester à jour avec le projet.

La gestion des actions à apporter est parfois très simple et parfois plus complexe selon l'état des différences et des intentions du développeur. 

Pour éviter de solliciter le réseau à chaque commande, Git crée des branches de suivi à distance (_remote tracking branches_) dans votre dossier `.git`. Considérez ces deux pointeurs :
1. `main` : Votre pointeur local (où vous travaillez).
2. `origin/main` : Le miroir de l'état du serveur au moment de votre **dernière synchronisation**.

## Synchronisation des travaux

La synchronisation consiste à mettre à jour les pointeurs locaux par rapport aux pointeurs distants. On présente ici quelques opérations fondamentales, leurs intentions et leurs effets.

### Récupération sans modification

`git fetch` est la commande la plus sûre. Elle télécharge les nouveaux objets depuis le serveur et déplace le pointeur `origin/main` vers le haut. 

Cette commande ne touche **jamais** à votre travail en cours (`main`). C'est une simple mise à jour de votre miroir. Vous ne verrez pas de différence dans votre espace de travail tant que vous n'aurez pas décidé d'intégrer ces changements manuellement par une fusion.

Cette commande peut se faire sans risque de conflit, car elle ne modifie pas votre branche locale. C'est un excellent moyen de vérifier ce que les autres ont fait avant de décider comment intégrer ces changements. Vous pouvez ensuite faire un `git diff main origin/main` pour voir les différences entre votre travail et ce qui est sur le serveur.

### Récupération avec modification

`git pull` est une commande raccourci qui exécute deux actions à la suite : 
    1. `git fetch`
    1. `git merge`

> **Résolution inévitable** : Puisqu'il y a un `merge` automatique, un `pull` peut déclencher des conflits de fusion sur votre machine si vous et un collègue avez modifié les mêmes lignes. Ces situations sont inévitables dans un environnement collaboratif, mais elles nécessitent une résolution manuelle. 
>
> Certaines pratiques de travail peuvent minimiser les risques de conflits (commits fréquents, communication avec l'équipe, etc.), mais il est impossible de les éliminer complètement. C'est pourquoi il est important de comprendre comment résoudre ces conflits lorsque vous utilisez `git pull`.
>
> Finalement, les pratiques en entreprises varient beaucoup. Certaines équipes préfèrent éviter les `pull` automatiques et recommandent plutôt de faire un `fetch` suivi d'un `merge` ou d'un `rebase` manuel pour garder un contrôle total sur le processus de fusion.

### Envoie de son travail

`git push` télécharge vos commits locaux vers le serveur et déplace le pointeur `main` du serveur.

Lorsque cette commande réussit, cela signifie que votre travail a été intégré dans le dépôt distant et est désormais visible par tous les collaborateurs. 

> **Condition importante** :
> 
> Pour que le `push` réussisse, votre branche locale doit être à jour par rapport au serveur. Ceci veut dire que votre pointeur `main` doit être un descendant de `origin/main`. Si quelqu'un d'autre a poussé des commits sur le serveur depuis votre dernière synchronisation, votre `push` sera rejeté avec un message du type _non-fast-forward_.
> 
> Autrement dit, le serveur n'acceptera votre `push` que s'il peut effectuer un _Fast-forward_. Si ce n'est pas le cas, cela signifie que vous devez d'abord intégrer les changements distants dans votre branche locale (via un `git pull` ou un `git pull --rebase`) avant de pouvoir pousser à nouveau.

### Clônage d'un dépôt

`git clone` est la méthode standard pour démarrer un projet existant sur GitHub. Cette commande automatise trois étapes :
1.  `git init` (création du dépôt).
2.  `git remote add origin` (création du lien).
3.  `git pull` (téléchargement des données).


## Premier contact avec GitHub

### Création d'un compte

Pour utiliser GitHub, la première étape est de créer un compte sur la plateforme. Cela vous permettra d'héberger vos projets, de collaborer avec d'autres développeurs et d'accéder à une multitude de fonctionnalités supplémentaires. La création d'un compte est gratuite et ne prend que quelques minutes. Vous devrez fournir une adresse e-mail valide, choisir un nom d'utilisateur unique et créer un mot de passe sécurisé. Une fois votre compte créé, vous pourrez personnaliser votre profil, suivre d'autres utilisateurs et commencer à explorer les projets open source disponibles sur GitHub.

Le lien pour créer un compte GitHub : [https://github.com/join](https://github.com/join)

### Création d'un dépôt distant

#### Considérations préalables
- **Public vs Privé** : Un dépôt public est visible par tous, tandis qu'un dépôt privé est restreint aux collaborateurs que vous invitez. Choisissez en fonction de la nature de votre projet et de vos besoins de confidentialité.
- **README.md** : Ce fichier de documentation est essentiel pour présenter votre projet, expliquer son objectif, et fournir des instructions d'utilisation. Il est recommandé de le créer dès la création du dépôt pour donner une première impression professionnelle.
- **.gitignore** : Ce fichier permet de spécifier les fichiers ou dossiers que Git doit ignorer. Il est crucial de le configurer correctement pour éviter de commettre des fichiers sensibles ou inutiles (ex: fichiers de configuration locaux, dossiers de build, etc.).
- **Collaborateurs** : Vous pouvez inviter des collaborateurs à rejoindre votre projet en leur donnant des droits d'accès spécifiques (lecture, écriture, administration). Assurez-vous de gérer ces permissions avec soin pour protéger l'intégrité de votre projet.

#### Considérations pour ce cours

- Idéalement, l'étudiant qui crée le dépôt doit être le représentant en gestion de l'équipe. Il doit réaliser ces étapes :
    - Création du dépôt sur GitHub avec les paramètres appropriés :
        - Nom du dépôt : Le nom du dépôt doit être celui de votre projet. Utilisez le nom que vous avez choisi pour votre projet dans les documents de conception. N'utilisez pas de noms génériques comme _projet1_ ou _test_ ou introduire une référence au cours lui-même. Un nom de projet clair et descriptif est essentiel pour donner une première impression professionnelle et faciliter la navigation dans votre compte GitHub. 
        - Visibilité : Choisissez un dépôt privé afin de protéger la confidentialité de votre projet.
        - Description : Fournissez une brève description de votre projet pour informer les visiteurs de son objectif et de son contenu.
        - `README.md` : Initialisez le dépôt avec un fichier `README.md` pour fournir des informations de base sur votre projet.
        - `.gitignore` : Créez un fichier `.gitignore` adapté à l'environnement Python.
        - Licence : Aucune.
    - Inviter immédiatement vos collaborateurs à rejoindre le projet :
        - tous les autres membres de l'équipe
        - l'enseignant pour permettre le suivi et l'évaluation du projet
    - Remplir la version initiale du `README.md`. Son contenu évoluera au fil de la session mais vous devez y inclure les informations suivantes dès la création du projet :
        - titre du projet
        - noms des membres de l'équipe
        - description générale du projet
        - d'autres sections devront éventuellement être ajoutées au fur et à mesure de l'avancement du projet
    - Faites votre premier `commit` et `push` pour déposer les fichiers de travail dans les dossiers appropriés et maintenir une organisation claire et professionnelle du projet.
    - Définir l'arborescence du projet en créant les dossiers nécessaires et en ajoutant les fichiers du projet ainsi que les fichiers `.gitkeep` si nécessaire. N'oubliez pas de respecter la structure imposée.
    - Faites votre second `commit` et `push` après avoir ajouté l'arborescence et tous les fichiers (incluant `.gitkeep` si nécessaire).

#### Création d'un dépôt pour un nouveau projet

Les étapes à suivre sont les suivantes :
1. Connectez-vous à votre compte GitHub.
2. Cliquez sur le bouton "New" ou "Create repository" pour créer un nouveau dépôt.
3. Remplissez les informations requises (nom du dépôt, description, visibilité, etc.).
4. Cochez les options pour initialiser le dépôt avec un `README.md`, un `.gitignore` adapté à Python et une licence (MIT ou GPL).
5. Cliquez sur "Create repository" pour finaliser la création du dépôt.
6. Une fois le dépôt créé, invitez :
    - tous les membres de votre équipe en tant que collaborateurs en allant dans les paramètres du dépôt et en ajoutant leurs noms d'utilisateur GitHub
    - l'enseignant en tant que collaborateur pour permettre le suivi et l'évaluation du projet.
7. Clônez le dépôt sur votre machine locale en utilisant la commande `git clone <url-du-dépôt>`.

#### Création d'un dépôt pour un projet existant localement

Si vous avez déjà un projet local que vous souhaitez héberger sur GitHub, les étapes sont les suivantes :
1. Connectez-vous à votre compte GitHub et créez un nouveau dépôt comme décrit précédemment, mais sans initialiser de aucun fichier de travail auto-générés comme `README.md`, `.gitignore` et la licence.
2. Sur votre machine locale, ouvrez un terminal et naviguez jusqu'au dossier de votre projet.
3. Initialisez un dépôt Git local avec la commande `git init`.
4. Ajoutez tous les fichiers de votre projet au suivi de Git avec `git add .`.
5. Faites un commit initial avec `git commit -m "Initial commit"`.
6. Liez votre dépôt local au dépôt distant sur GitHub avec la commande `git remote add origin <url-du-dépôt>`.
7. Poussez votre code vers GitHub avec `git push -u origin main`.


## Authentification et le _Secret Handshake_

Pour toutes les commandes sur GitHub, vous devez prouver votre identité. Le serveur doit s'assurer que vous avez les droits d'écriture.

Historiquement, on utilisait un simple mot de passe. Aujourd'hui, pour des raisons de sécurité, GitHub exige :
* **HTTPS + Personal Access Token (PAT)** : Un code généré dans vos réglages GitHub qui remplace votre mot de passe.
* **SSH (Secure Shell)** : Une paire de clés (publique/privée). Votre machine possède la clé privée, et vous donnez la clé publique à GitHub. La connexion se fait alors par un "échange de poignée de main" cryptographique invisible.

_... plus de détails à venir ..._



## Résumé des commandes GitHub I

| Commande | Action technique | Intention |
|:---------|:-----------------|:----------|
| `git remote add origin <url-du-dépôt>` | Lier un dépôt local à un dépôt distant. | Préparer la synchronisation avec GitHub. |
| `git remote -v` | Liste les serveurs distants liés. | Vérifier vers où l'on envoie son code. |
| `git clone <url>` | Copie intégrale d'un dépôt. | Commencer à travailler sur un projet existant. |
| `git fetch` | Met à jour les miroirs (`origin/...`). | Voir ce que les autres ont fait sans risquer de conflits. |
| `git pull` | `fetch` + `merge`. | Synchroniser son espace de travail avec le groupe. |
| `git push origin main` | Envoie les commits de `main` vers `origin`. | Publier ses résultats officiels. |


## Résolution de problèmes récurrents

- **Rejected - non-fast-forward** après un `git push` : 
    - Cela signifie que le serveur contient des `commits` que vous n'avez pas. 
    - Solution : Faites un `git pull` pour intégrer les travaux distants, puis retentez le `push`.
- **Everything up-to-date** après un `git push` : 
    - Votre pointeur local et votre miroir `origin/main` sont identiques. 
    - Inutile de pousser.
- **Your branch is ahead of 'origin/main' by X commits** après un `git commit` : 
    - Vous avez fait des _commits_ locaux qui n'ont pas encore été poussés. 
    - Solution : Faites un `git push` pour synchroniser votre travail avec le serveur.
- **Your branch is behind 'origin/main' by X commits** après un `git commit` : 
    - D'autres ont poussé des _commits_ sur le serveur depuis votre dernière synchronisation. 
    - Solution : Faites un `git pull` pour intégrer les changements distants avant de pousser à nouveau.
- **Merge conflict** après un `git pull` : 
    - Vous et un collègue avez modifié les mêmes lignes de code. 
    - Solution : Résolvez manuellement les conflits dans les fichiers concernés, puis faites un `commit` pour finaliser la fusion.

**Désambiguation importante** : Lorsque Git vous dit _Your branch is ahead of 'origin/main' by 2 commits_, il ne demande pas au serveur en temps réel. Il compare simplement votre pointeur `main` avec son "miroir" local `origin/main`.