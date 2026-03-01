# Jeu de Nim – Projet Python / NSI

## Description
Ce projet implémente le jeu de Nim en Python, avec une IA qui apprend par renforcement (méthode des boules/urnes).

Tu peux :
- entraîner l’IA,
- jouer en console,
- jouer avec une interface Pygame moderne.

Le principe : on retire de **1 à N bâtons** (N=2 ou 3 selon la règle), et le joueur qui prend le dernier bâton gagne.

---

## Fichiers principaux

- `ia.py`
  - Cœur de l’IA (classes `Case`, `Joueur`, entraînement, sauvegarde/chargement JSON).
- `game_logic.py`
  - Moteur de partie Nim (état, coups valides, alternance des joueurs).
- `nim_console.py`
  - Interface console simple : humain vs humain ou humain vs IA.
- `nim_pygame.py`
  - Interface graphique Pygame entièrement revue (layout moderne, lisible, sans chevauchement).

---

## Installation

```bash
git clone https://github.com/AntoCheMaestro/ia_jeu_de_nim.git
cd ia_jeu_de_nim
```

### Dépendance pour l’interface graphique

```bash
pip install pygame
```

---

## Lancer le projet

### 1) Mode IA seul (analyse / debug)

```bash
python ia.py
```

### 2) Mode console

```bash
python nim_console.py
```

### 3) Mode Pygame

```bash
python nim_pygame.py
```

Dans le menu Pygame, tu peux configurer :
- le mode (`Humain vs Humain`, `Humain vs IA`, `IA vs IA`),
- la règle (2 ou 3 retraits max),
- le nombre initial de bâtons,
- la difficulté IA (`facile`, `moyen`, `difficile`).

En partie, tu peux utiliser les touches :
- `1`, `2`, `3` pour jouer,
- `M` pour retourner au menu,
- `R` pour relancer rapidement,
- `H` pour afficher/masquer l'aide en jeu.

Les statistiques sont sauvegardées automatiquement dans `stats_nim.json` (réinitialisation possible depuis l'écran stats).

---

## Idées d’amélioration

- Ajouter des animations plus avancées (transitions, effets de victoire).
- Ajouter une sauvegarde de statistiques sur disque.
- Enregistrer plusieurs profils IA selon les réglages.

---

### Tests rapides

```bash
python -m unittest -v
```
