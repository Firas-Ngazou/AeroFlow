# Manuel d'utilisation — AeroFlow

> #### Guide complet pour tester et utiliser l'application

---

## Table des matières

1. [Lancement de l'application](#1-lancement-de-lapplication)
2. [Page d'accueil](#2-page-daccueil)
3. [Éditeur vectoriel](#3-éditeur-vectoriel)
4. [Barre d'outils](#4-barre-doutils)
5. [Raccourcis clavier](#5-raccourcis-clavier)
6. [Panneau de paramètres](#6-panneau-de-paramètres)
7. [Lancement et contrôle de la simulation](#7-lancement-et-contrôle-de-la-simulation)
8. [Modes de visualisation](#8-modes-de-visualisation)
9. [Panneau d'analyse](#9-panneau-danalyse)
10. [Algorithme génétique](#10-algorithme-génétique)
11. [Sauvegarde et chargement](#11-sauvegarde-et-chargement)
12. [Fenêtre personnalisée](#12-fenêtre-personnalisée)

---

## 1. Lancement de l'application

```bash
python run.py
```

L'application s'ouvre sur une **page d'accueil** présentant les projets existants et un bouton pour en créer un nouveau.

---

## 2. Page d'accueil

### Créer un nouveau projet
- Cliquez sur le bouton **"Nouveau"**.
- L'éditeur s'ouvre avec une grille vide.

### Ouvrir un projet existant
- Cliquez sur la vignette d'un projet sauvegardé dans la liste.
- Le projet se charge avec sa forme et ses paramètres.

### Aperçu des projets
- Chaque vignette affiche le nom du projet et un aperçu visuel de la forme sauvegardée.

---

## 3. Éditeur vectoriel

### Mode dessin
- Activez le mode dessin via la barre d'outils (icône stylo).
- **Cliquez** sur la grille pour placer des sommets (vertices).
- Les sommets se relient automatiquement pour former un polygone fermé.

### Mode sélection (flèche)
- Activez le mode sélection via la barre d'outils (icône flèche).
- **Cliquez** sur un sommet pour le sélectionner.
- **Cliquez et glissez** pour déplacer un sommet.
- **Maj + clic** pour sélectionner plusieurs sommets.
- **Cliquez et glissez** sur le canevas pour créer une zone de sélection rectangulaire.

### Manipulation des formes
- **Déplacement** : sélectionnez des sommets et faites-les glisser.
- **Mise à l'échelle** : appuyez sur `S`, puis déplacez la souris pour agrandir ou rétrécir la sélection.
- **Rotation** : appuyez sur `R`, puis déplacez la souris pour faire pivoter la sélection.
- **Translation globale** : appuyez sur `G`, puis déplacez la souris pour déplacer toute la forme. Maintenez `Maj` enfoncée lors du déplacement pour activer l'aimantation à la grille.
- **Suppression** : sélectionnez des sommets et appuyez sur `Suppr`, ou créez une zone de sélection avec `Ctrl` enfoncé pour supprimer ce qui se trouve dedans.

### Ajout de sommets
- En mode sélection, passez la souris sur un segment de la forme.
- Un indicateur apparaît au milieu du segment : **cliquez** pour insérer un nouveau sommet à cet endroit.

### Undo / Redo
- `Ctrl + Z` : annuler la dernière action.
- `Ctrl + Maj + Z` : refaire l'action annulée.

---

## 4. Barre d'outils

La barre d'outils se trouve en bas de l'écran.

| Icône | Fonction |
|-------|----------|
| Stylo | Basculer en mode dessin |
| Flèche | Basculer en mode sélection |
| Formes | Ouvrir le navigateur de `prefabs` (formes sauvegardées) |

### Prefabs (formes prédéfinies)
- Cliquez sur l'icône **Formes** pour ouvrir le menu déroulant de prefabs.
- Cliquez sur une forme pour l'insérer sur le canevas.
- Faites un clic droit sur une forme pour l'enregistrer.
- Faites un clic droit sur une forme **déjà enregistrée** pour la supprimer du menu déroulant.

---

## 5. Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl + Z` | Annuler |
| `Ctrl + Maj + Z` | Refaire |
| `S` | Mode mise à l'échelle |
| `R` | Mode rotation |
| `G` | Mode translation globale |
| `A` | Tout sélectionner |
| `Esc` | Quitter la forme |
| `Suppr` | Supprimer la sélection |

---

## 6. Panneau de paramètres

Cliquez sur la barre latérale pour ouvrir le panneau rétractable. Le panneau contient deux onglets.

### Onglet Général

| Paramètre | Description |
|-----------|-------------|
| **Vitesse du vent** | Vitesse initiale de l'écoulement d'air (m/s) |
| **Viscosité** | Viscosité cinématique du fluide |
| **Qualité** | Résolution de l'image |
| **Live Edit** | Active la mise à jour en temps réel de la simulation quand vous modifiez la forme |
| **Vitesse** | Affiche la heatmap de vitesse |
| **Densité** | Affiche la heatmap de densité |
| **Lignes d'écoulement** | Affiche les lignes d'écoulement (streamlines) |
| **Tourbillons** | Affiche la carte de vorticité |
| **Effet escalier** | Applique un effet de pixelisation sur les visualisations |

### Onglet Optimisation

| Paramètre | Description |
|-----------|-------------|
| **Contrainte** | Méthode de contrainte géométrique : `DISTANCE` ou `SURFACE` (variation d'aire max) |
| **Cible** | Objectif de l'optimisation : `TRAÎNÉ` (minimiser le $C_d$) ou `PORTANCE` (maximiser le $C_l$) |
| **Type** | Direction de l'optimisation : `MINIMUM` ou `MAXIMUM` |
| **Seuil** | Tolérance de la contrainte (par exemple, 0.1 = 10 % de variation autorisée) |
| **Itérations** | Nombre maximal de générations |
| **Population** | Taille de la population à chaque génération |
| **Taux de mutation** | Probabilité qu'un sommet soit déplacé aléatoirement |
| **Démarrer** | Lance l'algorithme génétique |
| **Arrêter** | Force l'arrêt de l'optimisation en cours |

---

## 7. Lancement et contrôle de la simulation

### Démarrer une simulation
1. Dessinez une forme fermée sur le canevas.
2. Cliquez sur le bouton **▶** en bas au centre de l'écran.
3. La simulation démarre et la heatmap apparaît.

### Contrôles de lecture
Une barre de contrôle apparaît en bas de la zone de simulation :

| Contrôle | Action |
|----------|--------|
| ▶ / ⏸ | Lire ou mettre en pause la simulation |
| Slider | Faire défiler manuellement les frames de la simulation |
| Horloge | Affiche le temps écoulé (MM:SS) |
| FPS | Affiche le nombre d'images par seconde actuel |

### Pause et reprise
- Cliquez sur le bouton de lecture pendant la simulation pour la mettre en pause.
- Cliquez à nouveau pour reprendre.
- En mode pause, vous pouvez faire glisser le slider pour inspecter n'importe quelle frame.

### Live Edit
- Activez le toggle **Live Edit** dans les paramètres.
- Pendant la simulation, modifiez la forme (déplacez des sommets, supprimez-en, etc.).
- Le fluide se met à jour dynamiquement sans redémarrer la simulation.

---

## 8. Modes de visualisation

Les modes se combinent via les cases à cocher de l'onglet **Général**.

### Modes de base
- **Vitesse** : heatmap colorée de la norme du vecteur vitesse (bleu = lent, rouge = rapide).
- **Densité** : heatmap de la densité locale du fluide par rapport à la densité initiale.

### Superpositions
- **Vitesse + Lignes d'écoulement** : heatmap de vitesse avec des lignes de courant blanches par-dessus.
- **Vitesse + Tourbillons** : heatmap de vitesse avec la carte de vorticité superposée.
- **Densité + Lignes d'écoulement** : heatmap de densité avec des lignes de courant.
- **Densité + Tourbillons** : heatmap de densité avec la carte de vorticité superposée.

### Vorticité seule
- Affiche une carte en niveaux de gris de la vorticité (tourbillons) avec transparence variable.

---

## 9. Panneau d'analyse

Cliquez sur le bouton **Analyse** dans la barre de titre pour ouvrir le panneau flottant. Le panneau contient deux onglets.

### Onglet Résultats
Affiche les valeurs physiques calculées par le moteur LBM en temps réel :

- **Coefficient de traînée ($C_d$)**
- **Coefficient de portance ($C_l$)**
- **Nombre de Reynolds**
- **Nombre de Mach**
- **Énergie cinétique**
- **Chute de pression**
- **Masse totale**
- **Enstrophie totale**
- **Vorticité maximale**

### Onglet Optimisation
Affiche les résultats de l'algorithme génétique :

- **Gain aérodynamique** : pourcentage d'amélioration par rapport à la forme initiale.
- **Traînée projetée** : meilleur $C_d$ trouvé par le GA.
- **Portance projetée** : meilleur $C_l$ trouvé par le GA.
- **Graphique de convergence** : courbe montrant l'évolution de la fitness à chaque génération.

---

## 10. Algorithme génétique

### Principe
L'algorithme génétique optimise la forme actuelle en faisant évoluer une population de variants. Il utilise la bibliothèque **AeroSandbox** pour évaluer les coefficients aérodynamiques ($C_d$, $C_l$) de chaque candidat.

### Comment l'utiliser
1. Dessinez une forme de base sur le canevas.
2. Ouvrez le panneau **Paramètres** et allez dans l'onglet **Optimisation**.
3. Choisissez :
   - **Contrainte** : `DISTANCE` (les sommets ne peuvent pas s'éloigner trop de leur position initiale) ou `SURFACE` (l'aire de la forme doit rester quasi constante).
   - **Cible** : `TRAÎNÉ` ou `PORTANCE`.
   - **Type** : `MINIMUM` (pour minimiser la traînée) ou `MAXIMUM` (pour maximiser la portance).
   - **Seuil** : tolérance de la contrainte (ex : 0.1 pour 10 %).
   - **Itérations** et **Population** : paramètres de convergence.
4. Faites un clic droit sur la forme à optimiser, puis sélectionnez **Optimiser**.
5. Observez le **graphique de convergence** dans le panneau d'analyse.
6. La forme optimisée remplace automatiquement la forme actuelle sur le canevas à la fin.

### Arrêt forcé
- Cliquez sur **Arrêt** (dans les paramètres d'optimisation) à tout moment pour interrompre l'optimisation.
- Le meilleur résultat trouvé jusqu'à présent est conservé.

---

## 11. Sauvegarde et chargement

### Sauvegarder un projet
- Utilisez les raccourcis `Ctrl+S` ou `Ctrl+Maj+S` ou allez dans le menu du projet (bouton **Fichier** en haut de la fenêtre) et cliquez sur **Sauvegarder**.
- Choisissez un emplacement sur votre disque.
- Le fichier `.json` contient :
  - Le nom du projet
  - Les sommets du dessin vectoriel
  - Un aperçu du projet (en base64)
  - Quelques paramètres de simulation (modes de visualisation)

### Charger un projet
- Depuis la **page d'accueil**, cliquez sur la vignette du projet désiré.
- Ou utilisez le menu du projet pour ouvrir un fichier `.json` existant.

### Configuration
- Les préférences de l'application (derniers paramètres utilisés) sont stockées dans le fichier `aeroflow.ini` à la racine du projet.

---

### Retour à l'accueil
- Cliquez sur le **logo AeroFlow** dans la barre de titre pour revenir à la page d'accueil.

### Fermer l'application
- Il suffit d'appuyer sur le bouton `X`.
- Si des modifications non sauvegardées existent, une boîte de dialogue vous demandera confirmation.

---

*Document généré avec l'aide de Kimi*
