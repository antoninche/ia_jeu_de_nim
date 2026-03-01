# IA Jeu de Nim

Projet Python (niveau Terminale NSI) pour jouer au jeu de Nim avec une IA par renforcement.

## Objectif
Le jeu de Nim consiste à retirer des bâtons d'une pile.
- À chaque tour, un joueur prend entre **1 et max_retrait** bâtons.
- Celui qui prend le dernier bâton gagne.

Le projet contient :
- un moteur de jeu,
- une IA entraînable (poids par action),
- une version console,
- une version Pygame,
- des tests unitaires.

---

## Arborescence

```text
.
├── LICENSE
├── README.md
├── requirements.txt
└── sources/
    ├── game_logic.py
    ├── ia.py
    ├── nim_console.py
    ├── nim_pygame.py
    └── test_nim.py
```

---

## Installation

### 1) Cloner le dépôt

```bash
git clone https://github.com/AntoCheMaestro/ia_jeu_de_nim.git
cd ia_jeu_de_nim
```

### 2) Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## Utilisation

### 1) Démo IA (terminal)

Entraîne l'IA puis affiche un récapitulatif des préférences :

```bash
python sources/ia.py
```

### 2) Jouer en console

```bash
python sources/nim_console.py
```

Fonctionnalités :
- Humain vs Humain
- Humain vs IA
- Chargement/sauvegarde modèle IA (`modele_nim.json`)

### 3) Jouer en Pygame

```bash
python sources/nim_pygame.py
```

Fonctionnalités :
- UI graphique
- Modes `Humain vs Humain`, `Humain vs IA`, `IA vs IA`
- Difficulté IA (facile, moyen, difficile)
- Entraînement progressif avec barre d'avancement
- Raccourcis clavier :
  - `1`, `2`, `3` : jouer
  - `M` : menu config
  - `R` : relancer
  - `H` : aide en jeu
- Statistiques sauvegardées dans `stats_nim.json`

---

## Tests

Lancer les tests unitaires :

```bash
python -m unittest discover -s sources -p "test_*.py" -v
```

---

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE`.
