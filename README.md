# AeroFlow

> #### 420-SF4-RE | Projet d’intégration en sciences, informatique et mathématique

## Présentation sommaire du projet
_AeroFlow_ est une application de bureau conçue pour dessiner des formes et simuler leur comportement aérodynamique. 
Elle intègre un éditeur vectoriel 2D interactif qui permet aux utilisateurs de créer et de manipuler de multiples formes 
indépendamment les unes des autres, agencé à un moteur physique capable de simuler les forces aérodynamiques qui 
s'exercent sur elles, ainsi que de visualiser le mouvement et le comportement de l'air.

## Fonctionnalités principales

### Éditeur graphique
- **Canevas 2D interactif** : Environnement quadrillé permettant de basculer facilement entre le mode de dessin 
et le mode libre.
- **Manipulation vectorielle dynamique** : Ajouter, sélectionner, déplacer et supprimer des sommets et des formes.

### Moteur physique
- **Coefficient de traînée et de portance** : Calculer les coefficients de traînée et de portance d'un dessin donné.
- **Modèle de Lattice Boltzmann** : Visualiser le mouvement et le comportement de l'air à l'aide du modèle de Lattice 
Boltzmann.

### Algorithme génétique
- **Modèle d'algorithme génétique** : Simuler l'évolution de formes aérodynamiques à l'aide d'un algorithme génétique.
- **Implémentation de l'algorithme génétique** : Optimiser les coefficients de traînée et de portance en modifiant la 
forme tout en respectant des contraintes données.

### Dépendances
- **Python 3.10+** : Langage de programmation principal
- **PySide6** : Framework d'interface utilisateur (GUI) et rendu 2D
- **NumPy** : Mathématiques vectorisées
- **Numba** : Compilation Just-In-Time pour les performances

### Auteurs
- **Firas Ngazou** : Architecture principale, UI/UX et logique **@Firas-Ngazou**
- **Mehdi Achouri** : Modèle de Boltzmann et calculs de traînée et portance **@Mehdiii07**
- **Quang-Vinh Nguyen** : Modèle d'algorithme génétique et implémentation **@vinh9336**

### Liens
- [Document de spécifications](./docs/extrants/conception/Spécifications.md)
- [Document de Conception](./docs/extrants/conception/Conception.md)
- [Document de Modélisation-Science](./docs/extrants/conception/Modélisation-Science.md)
- [Document de Modélisation-Math](./docs/extrants/conception/Modélisation-Math.md)
- [Contrat d'engagement](./docs/extrants/gestion/engagement/Contrat%20d'engagement.pdf)
- [Structure du projet](./docs/intrants/informations/Structure%20dossiers%20fichiers.png)