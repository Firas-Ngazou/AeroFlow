# Spécifications fonctionnelles <br><small><small><small>Guide de rédaction</small></small></small>

> #### 420-SF4-RE | Projet d’intégration en sciences, informatique et mathématique


## Objectif des spécifications fonctionnelles

Les spécifications fonctionnelles servent à définir clairement les attentes et les exigences du logiciel à développer. Elles constituent un document de référence essentiel pour l'équipe de développement, les parties prenantes et les utilisateurs finaux. 

En industrie, ce document est souvent appelé _cahier des charges fonctionnel_ et constitue une base de travail solide entre le client et l'équipe de développement. Un tel travail n'est pas toujours à faire et peut nécessitér un effort considérable. 

Dans ce contexte académique, ce document vise à vous faire réfléchir sérieusement sur les aspects fonctionnels de votre projet avant de plonger dans la conception technique et le développement. Il vous aidera à clarifier vos idées, à identifier les besoins des utilisateurs et à définir les objectifs du logiciel. C'est un peu comme l'énoncé d'un projet qu'un enseignant pourrait vous donner.

Vous avez cinq parties à rédiger. Les quatre premières sont à faire en équipe alors que la dernière est individuelle.

### 1 - Vision du projet

Cette section sert à cadrer le projet dans son ensemble. Elle doit être claire et concise, car elle sera souvent référencée tout au long du développement. C'est la boussole du projet qui servira de guide général et de référence pour trancher.

Vous devez y présenter les éléments suivants :

- Objectif général : En une phrase, quelle est la finalité du logiciel ? (par exemple : _Fournir un outil pédagogique interactif pour visualiser l'opération de composants optiques variés et configurables._).

- Objectifs spécifiques : Donnez une liste de tâches précises réalisables du logiciel. Le nombre d'éléments mentionnés n'est pas fixe et doit refléter le type de projet. C'est-à-dire que le nombre de tâches n'est pas lié à la complexité du projet mais plutôt à sa nature. On vous demande de faire un effort de réflexion collectif sérieux, car vous guiderez ici les décisions de conception et de développement. Ils correspondent aux besoins clés que le logiciel doit satisfaire. En même temps, toute l'équipe doit être d'accord sur ces objectifs principaux et leur formulation. Voici quelques exemples d'objectifs spécifiques :
    - Permettre à l'utilisateur de configurer différents types de lentilles et miroirs.
    - Offrir une visualisation en temps réel des rayons lumineux traversant les composants optiques.
    - Intégrer une bibliothèque de configurations prédéfinies pour des expériences courantes en optique.
    - Fournir des outils d'analyse pour mesurer les propriétés optiques (focale, aberrations, etc.).
    - Garantir la précision scientifique des simulations conformément aux principes de l'optique géométrique.

- Considérations scientifiques : Donner une liste des points importants décrivant quels sont les aspects scientifiques essentiels de ce projet? On veut s'assurer que le projet reste aligné avec les objectifs scientifiques initiaux. Pour chaque point, décrivez l'application scientifique et le rôle dans le cadre du projet. La liste doit être trier en ordre d'importance (du plus au moins).

- Considérations mathématiques : Donner une liste des points importants décrivant quels sont les aspects mathématiques essentiels de ce projet? Encore une fois, on veut s'assurer que le projet reste aligné avec les objectifs. Pour chaque point, décrivez l'application mathématique et le rôle dans le cadre du projet. Identifiez si le thème est lié directement à l'implémentation d'une considération scientifique. La liste doit être trier en ordre d'importance (du plus au moins).

Cette section doit être rédigée de manière claire et accessible, en évitant le jargon technique excessif. L'objectif est de définir les éléments importants du projet. Sans entrer dans les micro-détails, on commence à décrire les éléments constituants. De plus, il est important de comprendre qu'on désire situer le projet dans son intention, les détails techno-scientifiques ne sont pas attendus et sont prévu pour un autre document.


### 2 - Périmètre fonctionnel

Cette section vise à définir clairement les fonctionnalités que le logiciel doit offrir. Il est crucial de bien délimiter ce qui est inclus dans le périmètre du projet et ce qui en est exclu. Cela permet d'éviter les dérives de scope et de s'assurer que l'équipe reste concentrée sur les objectifs principaux.

- Décrivez à qui s'adresse le logiciel, c'est-à-dire les principaux acteurs du système.
- Listez les fonctionnalités principales que le logiciel doit offrir. Attention, cette section peut ressembler à la section précédente intitulée _Objectifs spécifiques_ mais elle diffère en un point important. Ici on veut plutôt décrire des scénarios narratifs courts décrivant l'interaction utilisateur-système. Au lien de dire qu'est-ce que le logiciel peut faire, on décrit comment l'utilisateur interagit avec le logiciel pour accomplir une tâche spécifique. Une tâche peut être composée de plusieurs fonctionnalités. 
- Concernant la manipulation directe des informations, identifiez clairement les intrants (inputs) et extrants (outputs) du système. Cela inclut les types de données que l'utilisateur peut fournir ainsi que les résultats que le logiciel doit produire. En d'autres mots, quelles sont les données saisies par l'utilisateur et quelles sont les données produites par le système pour l'utilisateur?
- Concernant les données persistantes, identifiez les différents cas d'utilisation. Pour chacun, nommez sommairement les contenus de ces données. 

### 3 - Vocabulaire et sémantique du domaine d'application

Pour tout projet interdisciplinaire, il est crucial d'aligner le langage de tous les intervenants (utilisateur, scientifique, mathématicien, développeur, client, ...). Cette section vise à définir clairement les termes, concepts et données clés utilisés dans le projet afin d'éviter toute confusion ou malentendu. On dira aussi que ce cette section constitue la définition _métier_ du projet.

Cette section sera inévitablement imparfaite lors de la première ébauche. Toutefois, il importe de faire un effort visant à identifier la terminologie issue des concepts majeurs liés au domaine du projet. L'objectif est de créer une base de communication commune entre tous les membres de l'équipe et les parties prenantes. 

Cette section doit refléter le fruit d'une recherche sérieuse et d'une réflexion collective. Il semble banal de faire cet exercice mais au contraire, ce dernier constitue un fondement essentiel pour la réussite du projet en formalisant les idées que chacun peu avoit en début de projet. Si vous avez des divergeances d'opinions sur un élément de terminologie, c'est sain, normal et c'est justement le temps de clarifier ces détails. 

Vous devez donc définir :

- Glossaire du domaine (du métier) : Définir les termes spécifiques utilisés dans votre projet. Pour chaque terme (mot ou expression), fournissez une définition concise et précise. 
- Dictionnaires des unités et constantes : en considérant les intrants et extrants du systèmes, listez les unités de mesure et constantes (chimie/physique/mathématique) utilisées dans le projet. Utilisez les unités internationales.

### 4 - Stratégie de livraison

Le projet est défini en 5 Sprints de deux sections distinctes :
- sections de définition, conception et planification 
    - Sprint 1 : Mise en place, conception et organisation 
    - Sprint 2 : Modélisation, conception et planification
- sections de développement 
    - Sprint 3 : Amorce du développement
    - Sprint 4 : Consolidation du développement
    - Sprint 5 : Finalisation du projet

On se concentre ici sur les 3 Sprints de développement et on défini clairement les livrables attendus à chacune des étapes. Notez que les livrables doient être spécifiquement des fonctionnalités implémentées, démontrables et utilisables (même si elles sont incomplètes).  

Pour chacun de ces trois sprints, vous devez définir :
- Titre du Sprint : Un nom court et évocateur reflétant la fonctionnalité principale. L'objectif est de capturer l'essence du Sprint en quelques mots et de remplacer les titres génériques déjà utilisés (comme _Amorce du développement_).
- Livrables spécifiques du Sprint : Sous forme de liste à puces, décrivez les objectifs concrets à atteindre durant le Sprint. Ces objectifs doivent être mesurables et réalisables dans le temps imparti.
- Finalement, vous devez décrire à quel moment les considérations scientifiques et mathématiques seront intégrées dans le développement. Cela peut être sous forme de jalons spécifiques ou d'objectifs à atteindre durant le Sprint.

### 5 - Partie individuelle

Chaque étudiant doit insérer dans ce document une partie individuelle qu'il rédige seul. Cette section vise à faire réfléchir chaque membre de l'équipe sur sa contribution personnelle au projet. Après une discussion en équipe, chaque étudiant doit y inclure les éléments suivants :
- Nom, prénom
- Rôles et responsabilités : 
    - Chaque étudiant doit être responsable d'au moins une tâche spécifique et significative du projet.
    - Attention :
        - Ça ne signifie pas que l'étudiant travaille seul sur cette tâche, mais plutôt qu'il est le point de contact principal et qu'il doit s'assurer de son avancement, de sa qualité et de son bon arrimage avec le reste du projet.
        - Vous devez considérer une tâche d'environ  
    - Indiquer en trois points :
        - Un titre décrivant la tâche prise en charge.
        - Une description décrivant cette tâche.
        - Quelles sont les limites, où ça commence et où ça s'arrête.
- Opinions personnelles : Selon vous, en considérant l'ensemble du projet :
    - Quelle partie sera la plus difficile à réaliser (en terme de complexité)? Pourquoi?
    - Quelle partie sera la plus longue à réaliser (en terme de temps)? Pourquoi?
    - Justifiez comment ce projet vous permet d'intégrer les compétences acquises dans votre formation collégiale.
