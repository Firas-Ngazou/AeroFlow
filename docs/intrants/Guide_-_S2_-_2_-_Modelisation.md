# Modélisation scientifique et mathématique <br><small><small><small>Guide de rédaction</small></small></small>

> #### 420-SF4-RE | Projet d’intégration en sciences, informatique et mathématique

## Introduction

Ce guide définit les attentes relatives au document de modélisation. La conception théorique n'est pas une simple formalité, mais le fondement scientifique de votre projet. Vous devez y démontrer une capacité d'analyse rigoureuse, une transparence dans vos choix techniques et une maîtrise du formalisme propre aux disciplines du programme SIM.

## Le triptyque documentaire

Votre travail de conception se divise en trois documents distincts. Cette structure vise à isoler les concepts pour mieux les approfondir avant de les fusionner. Les documents I et II servent de références théoriques, tandis que le document III assure la cohérence de l'ensemble et prépare le passage vers l'implémentation informatique. L'excellence de la langue et l'usage précis de $\LaTeX$ pour le formalisme mathématique sont exigés pour l'ensemble des livrables.

--- 

## Document I : Fondements scientifiques

Ce premier volet documente votre compréhension du ou des phénomènes étudiés, qu'il relève de la physique ou de la chimie. Vous devez y exposer le fruit de vos recherches documentaires pour situer votre projet dans un contexte scientifique réel. Il ne s'agit pas uniquement de lister des lois, mais d'expliquer comment elles s'appliquent à votre problématique spécifique.

Une section cruciale de ce document concerne vos hypothèses de travail. La modélisation exige souvent des simplifications (par exemple, considérer un système comme isolé ou négliger la friction). Vous devez justifier chaque compromis : expliquez pourquoi une variable est négligée et quel est l'impact de ce choix sur la précision finale de votre simulation. Cette transparence démontre votre capacité à évaluer la portée de votre modèle.

Enfin, vous devez produire un lexique scientifique exhaustif. Pour chaque grandeur physique utilisée, vous devez fournir une description précise ainsi qu'une analyse rigoureuse des unités de mesure selon le Système international (SI). Par exemple, si vous utilisez une constante de rappel $k$, vous devez préciser qu'elle s'exprime en $N/m$ ou en $kg \cdot s^{-2}$ après analyse dimensionnelle.

Formellement, ce document doit inclure :
- Une introduction présentant le contexte scientifique et les objectifs de votre modélisation.
- * Une section détaillant les hypothèses initiales.
- * Une section présentant les équations fondamentales et les relations mathématiques qui régissent votre modèle.
- * Une section élaborant la résolution analytique et/ou numérique de ces équations, avec des démonstrations rigoureuses.
- Un lexique scientifique avec des descriptions précises et des analyses d'unités pour chaque grandeur utilisée.
- Une bibliographie complète et correctement formatée selon les normes académiques.

* Ici, la rigueur scientifique prime sur la concision. Vous devez démontrer une compréhension approfondie de votre sujet et justifier chaque étape de votre modélisation avec des arguments solides. De plus, vous devez justifier vos choix et compromis de manière transparente, en expliquant les impacts potentiels sur la précision et la validité de votre modèle.

Ce document peut faire référence au document II si ce dernier présente des éléments mathématiques nécessaires à la compréhension du modèle scientifique. 

## Document II : Fondements mathématiques

Le second document traite de la mathématique soit comme moteur de résolution du modèle scientifique, soit comme discipline autonome (ex: théorie des graphes, cryptographie ou optimisation). Vous devez d'abord positionner clairement le rôle de la mathématique dans votre projet. Si elle est appliquée, montrez comment elle traduit les concepts physiques en un système résoluble. Si elle est autonome, définissez rigoureusement le cadre théorique et les structures mathématiques utilisées.

L'exigence centrale de ce document est la démonstration formelle. Vous devez inclure des preuves mathématiques complètes (dérivation d'une équation, démonstration d'un théorème ou preuve de convergence d'un algorithme). Encore une fois, l'utilisation de $\LaTeX$ sera gage de votre compréhension de la syntaxe mathématique. 

Si votre projet le requiert, le document doit également aborder la transition entre le modèle mathématique continu et sa résolution numérique discrète. Justifiez le choix de vos méthodes (ex: méthode d'Euler vs Runge-Kutta) en discutant de la précision et de la complexité. 

Un lexique mathématique définissant les domaines de définition, les ensembles et les opérateurs complétera ce volet.

Formalement, ce document doit inclure :
- Une introduction présentant le contexte mathématique et les objectifs de votre modélisation.
- * Une section détaillant les structures mathématiques utilisées (espaces vectoriels, graphes, etc.).
- * Une section présentant les démonstrations formelles des résultats mathématiques essentiels à votre projet.
- * Une section expliquant la transition entre le modèle mathématique continu et sa résolution numérique, avec une justification des méthodes choisies.
- Un lexique mathématique avec des définitions précises pour chaque concept utilisé.
- Une bibliographie complète et correctement formatée selon les normes académiques.

* La rigueur mathématique est essentielle. Vous devez démontrer une compréhension approfondie des concepts mathématiques et justifier chaque étape de vos démonstrations avec des arguments solides. 

Encore une fois, ce document peut faire référence au document I si ce dernier présente des éléments scientifiques nécessaires à la compréhension ou à la contextualisation du modèle mathématique.

## Document III : Synthèse et intégration

Le dernier document est la synthèse de votre travail. Il doit présenter une vision d'ensemble de votre projet, en montrant comment les éléments scientifiques et mathématiques s'articulent pour répondre à la problématique posée. Vous exposez uniquement les résultats finaux de vos modélisations, sans répéter les démonstrations ou les analyses détaillées des documents précédents. L'objectif est de présenter le projet dans sa globalité tout en mettant l'emphase sur les éléments clés issus de votre effort de modélisation.

Il faut construire un discours narratif qui explique comment les différentes parties du projet s'imbriquent pour atteindre les objectifs fixés. On désire une synthèse claire, concise, rigoureuse et actionnable. 

Ce document agit comme un pont entre la théorie et la conception logicielle. Il ne répète pas les documents précédents, mais expose comment ils s'articulent pour répondre aux objectifs du projet. 

Formellement, ce document doit inclure :
- Une introduction présentant une synthèse du projet et les objectifs atteints.
- Une section présentant les résultats finaux de votre modélisation, en mettant l'emphase sur les éléments clés issus de votre effort de modélisation.
- Une section expliquant comment les éléments scientifiques et mathématiques s'articulent pour répondre à la problématique posée.
- Si pertinent, quels sont les compromis faits au modèle final et quels sont les impacts.
- Une conclusion qui résume les points clés et ouvre sur les perspectives d'amélioration ou d'extension du projet.

Ce document doit abondamment référencer les documents I et II pour éviter toute redondance. Il doit être rédigé de manière à ce que le lecteur puisse comprendre la logique d'ensemble du projet sans avoir à plonger dans les détails techniques, tout en offrant des références précises pour ceux qui souhaitent approfondir.

## Normes sur ces documents

Puisque chaque projet est unique, il n'existe pas de modèle de document universel. Cependant, vous devez veiller à ce que votre rédaction soit claire, structurée et rigoureuse. L'utilisation de $\LaTeX$ est obligatoire pour la présentation des équations et des démonstrations mathématiques, afin d'assurer une lisibilité optimale. Ces documents doivent être rédigé en français avec une orthographe irréprochable. Les titres, sous-titres et légendes doivent être explicites et informatifs. Chaque section doit être clairement définie et suivre une logique de présentation cohérente.

Les documents doivent être nommés ainsi :
- I. `Modélisation-Science.md`
- II. `Modélisation-Math.md`
- III. `Modélisation.md`

Ils doivent se retrouver dans les dossiers indiqués dans le guide de gestion de projet.

---

## Normes de citation et documentation

La crédibilité de votre travail repose sur la qualité de vos sources. Toute information, équation ou donnée qui n'est pas le fruit de votre propre réflexion doit être citée selon les normes en vigueur.

### Exemple pour un livre
Nom de l'auteur, Initiale. (Année). *Titre de l'ouvrage*. Éditeur.  
Exemple : 
- Serway, R. A., & Jewett, J. W. (2018). *Physique pour scientifiques et ingénieurs*. De Boeck Supérieur.
- Harris, D. C. (2020). *Analyse chimique quantitative*. De Boeck Supérieur.

### Exemple pour un article ou une source en ligne
Organisation ou Auteur. (Date). *Titre de l'article ou de la page*. URL.  
Exemple : 
- Wolfram MathWorld. (2025). *Runge-Kutta Method*. [🡥](https://mathworld.wolfram.com/Runge-KuttaMethod.html)
- Wikipédia. (2025). *Intégration (mathématiques)*. [🡥](https://fr.wikipedia.org/wiki/Int%C3%A9grale_(math%C3%A9matiques))
- Wikipédia. (2025). *Champ électrique*. [🡥](https://fr.wikipedia.org/wiki/Champ_%C3%A9lectrique)

### Exemple pour une discussion avec une intelligence artificielle
L'usage de l'IA est permis pour l'aide à la compréhension ou au débogage, mais doit être déclaré avec précision.  
Modèle d'IA (Version). *Titre de la nature de l'intervention*[_, détail si pertinent_]. Date de consultation.  
Exemple : 
- OpenAI ChatGPT (GPT-4o). *Mise en forme LaTeX*, _aide à la mise en forme LaTeX d'un système d'équations différentielles non linéaires et clarification sur la conservation du moment cinétique_. Consulté le 10 février 2026.
- Google Gemini (3 Pro). *Comprendre le champ électrique*, _interprétation physique du champ électrique en lien avec la distance_. Consulté le 12 février 2026.
- Anthropic Claude (4.5 Opus). Compréhension O(1), _expliquation de la complexité moyenne O(1) des dictionnaires en Python_. Consulté le 15 février 2026.