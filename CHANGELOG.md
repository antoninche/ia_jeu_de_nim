# Journal des versions

## v2.0.0

Refonte complète en un jeu graphique fini, coloré et éducatif pour enfants.

### Ajouts
- Interface graphique entièrement repensée (thème « bonbons ») : accueil,
  configuration, partie, écran de victoire avec confettis, statistiques.
- Trois modes de jeu : Toi vs Toi, Toi vs Robot, Robot vs Robot.
- Mascotte robot expressive et bouton « Indice » qui montre le coup parfait.
- Nouvelle partie éducative « Apprends à gagner » (École du Nim) : leçons
  animées, entraînement noté et diplôme, pour apprendre la stratégie gagnante.
- Scène « Comment le robot apprend ? » : visualisation en direct de
  l'apprentissage par renforcement de l'IA (boîtes et perles).
- Exécutables prêts à l'emploi pour Windows (`.exe`) et macOS (`.app`),
  construits automatiquement par intégration continue.

### Technique
- Découpage clair : `theme`, `widgets`, `game_logic`, `ia`, `jeu_nim`,
  `ecole_nim`, `explication_ia`.
- Empaquetage PyInstaller et workflow GitHub Actions de publication.

## v1.0.0
- Première version : logique du Nim, IA par renforcement et exécutable Windows.
