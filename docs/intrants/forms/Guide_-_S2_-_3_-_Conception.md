# Conception logicielle <br><small><small><small>Guide de rédaction</small></small></small>

> #### 420-SF4-RE | Projet d’intégration en sciences, informatique et mathématique

## Introduction

Ce guide définit les attentes relatives au document de conception logicielle. Cette étape marque le passage de la théorie à la structure technique. Un logiciel de qualité ne repose pas uniquement sur un code fonctionnel, mais sur une architecture réfléchie, une interface ergonomique et une gestion rigoureuse des données. Vous devez démontrer ici votre capacité à organiser la complexité informatique pour répondre aux besoins de votre modélisation.

Bien que ce document comporte moins de texte narratif que les précédents, il exige un effort de production graphique (diagrammes et maquettes) de haut niveau. Ces graphiques doivent refléter la profondeur de vos réflexions.

## Choix technologiques

Dans cette section, vous devez identifier et lister l'ensemble des outils techniques qui seront utilisés pour créer votre application. La sélection doit être précise et tenir compte des contraintes imposées.

### Technologies imposées
* **Langage de programmation :** L'utilisation de Python est obligatoire.
* **Calcul numérique :** L'utilisation de **NumPy** est obligatoire. Toute alternative basée sur une bibliothèque alternative ou par compilation juste-à-temps (JIT) doit faire l'objet d'une validation préalable avec l'enseignant. 
* **Interface graphique (GUI) :** L'utilisation de **Qt** (PySide6) est obligatoire. Toute alternative doit impérativement reposer sur le paradigme de la programmation orientée objet et être validée par l'enseignant.

### Bibliothèques utilitaires
Si applicable, produisez une liste des bibliothèques complémentaires que vous pensez utiliser (ex: Matplotlib, Pandas, SciPy, SymPy, PyTorch, etc.). Cette liste ne doit pas être une simple énumération ; elle doit résulter d'une recherche pertinente démontrant que vous avez choisi les meilleurs outils pour répondre aux besoins spécifiques de votre projet. De plus, pour chaque bibliothèque listée, vous devez fournir une justification succincte de sa pertinence. 

## Architecture logicielle (UML)

Vous devez produire un diagramme de classes UML complet, professionnel et détaillé. Ce diagramme doit représenter la structure logique de votre programme, en mettant l'accent sur les classes du **modèle**. 

> **Attention** : Les classes liées à l'interface utilisateur (fenêtres, boutons, widgets) ne **doivent pas** être incluses dans le diagramme de classes. 
>
> L'objectif est de mettre en lumière la logique applicative, les structures de données et les algorithmes de calcul, indépendamment de l'interaction avec l'utilisateur.

Votre diagramme doit être professionnel et inclure :
- Les attributs (avec types) ainsi que les opérations (avec paramètres et types de retour).
- L'identification claire des propriétés Python (avec la notation enseignée).
- L'affichage clair des concepts supplémentaires comme les méthodes et classes abstraites ainsi que les membres statiques, etc. 
- Les relations de dépendance, d'agrégation, de composition, d'héritage et autres.
- Une organisation visuelle facilitant la lecture des flux de données.

## Interface utilisateur (GUI)

L'interface est le point de contact entre l'utilisateur et les manipulations possibles de votre application. Vous devez produire toutes les **maquettes** détaillées de l'ensemble des écrans du logiciel. 

Votre interface doit minimalement inclure et démontrer :
- **Saisie de champs :** Une zone de saisie pour au moins chacun de ces types de données :
    - un nombre entier
    - un nombre réel
    - un champ de texte
    - une liste déroulante
- **Affichage :** Une zone dédiée à l'affichage de résultats ou d'informations pour chacune de ces considérations :
    - un dessin personnalisé (_custom drawing_) par  l'affichage d'une image ou d'un schéma généré par dessin programmable
    - un graphique technique pour l'affichage d'un graphique (ex: courbes de résultats, histogrammes) représentant vos données

## Gestion des données persistantes

La persistance des données assure la survie de l'information entre deux exécutions du logiciel ou entre deux exécution de simulation. 

Dans cette section, vous devez documenter rigoureusement le contenu des entrées et sorties (I/O) du logiciel.

Deux catégories d'informations doivent être couvertes :
- La **configuration** du logiciel entre deux exécutions. 
    - Le logiciel doit offrir au moins 3 éléments de configuration différents ajustables par l'utilisateur. Ces éléments doivent être sauvegardés et persistents entre deux exécutions du logiciel. Par exemple, cela peut être la dernière configuration de simulation, les préférences d'affichage, etc. 
    - Vous devez utiliser un fichier de configuration pour stocker ces éléments. Ce fichier doit se trouver à la racine du projet et être nommé `settings.ini`.
- Les **données scientifiques** générées par le logiciel.
    - Il s'agit des données de simulation ou de modélisation que votre logiciel produit. 
    - Ces données doivent être sauvegardées dans un format structuré à votre discrétion. 
    - La sauvegarde et le chargement du fichier doit utiliser la boîte de dialogue appropriée. 

Pour les deux catégories, vous devez fournir une documentation complète et rigoureuse comprenant :
- Le format de fichier utilisé (ex: JSON, CSV, binaire, etc.) et la justification de ce choix.
- Un dictionnaire de données détaillé décrivant chaque élément stocké : 
    - nom de la donnée
    - type de donnée
    - unités (si applicable)
    - rôle dans le logiciel (seulement pour la première catégorie)

## Normes de présentation

Ce document suit la même rigueur formelle que les précédents. Cependant, la nature technique de ce livrable exige une attention particulière à la qualité visuelle et à la clarté des graphiques où ces derniers sont disponibles en haute résolution. Voir la section _Normes de citation et documentation_ du guide de rédaction du document de modélisation.

Tous les graphiques doivent être inclus dans ce document avec la contextualisation appropriée et une mise en page soignée.

De plus, le document produit doit être nommé `Conception.md` et déposé dans le répertoire approprié du projet.
