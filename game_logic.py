"""Moteur de partie Nim séparé de l'interface graphique.

Ce module contient uniquement la logique de jeu :
- état de partie,
- validation des coups,
- alternance des joueurs,
- détection du gagnant.
"""


class EtatPartie:
    """État d'une partie de Nim.

    joueur_courant:
    - 1 pour joueur 1 / humain
    - 2 pour joueur 2 / IA
    """

    def __init__(self, nb_batons_init: int, max_retrait: int):
        self.nb_batons_init = nb_batons_init
        self.max_retrait = max_retrait
        self.nb_batons = nb_batons_init
        self.joueur_courant = 1
        self.gagnant = None

    def reset(self):
        self.nb_batons = self.nb_batons_init
        self.joueur_courant = 1
        self.gagnant = None

    def coups_valides(self) -> list[int]:
        return [c for c in range(1, self.max_retrait + 1) if c <= self.nb_batons]

    def coup_est_valide(self, retrait: int) -> bool:
        return retrait in self.coups_valides()

    def jouer_coup(self, retrait: int) -> bool:
        """Joue un coup.

        Retourne True si le coup a bien été appliqué, sinon False.
        """
        if not self.coup_est_valide(retrait):
            return False

        self.nb_batons -= retrait

        if self.nb_batons == 0:
            self.gagnant = self.joueur_courant
        else:
            self.joueur_courant = 2 if self.joueur_courant == 1 else 1

        return True
