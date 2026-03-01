import os
import tempfile
import unittest

from game_logic import EtatPartie
from ia import creer_liste_cases, entrainer_ia, sauvegarder_modele, charger_modele


class TestEtatPartie(unittest.TestCase):
    def test_coups_valides_respectent_max_retrait(self):
        etat = EtatPartie(nb_batons_init=2, max_retrait=3)
        self.assertEqual(etat.coups_valides(), [1, 2])

    def test_jouer_coup_et_gagnant(self):
        etat = EtatPartie(nb_batons_init=3, max_retrait=2)
        self.assertTrue(etat.jouer_coup(2))
        self.assertEqual(etat.nb_batons, 1)
        self.assertEqual(etat.joueur_courant, 2)
        self.assertTrue(etat.jouer_coup(1))
        self.assertEqual(etat.gagnant, 2)


class TestIA(unittest.TestCase):
    def test_sauvegarde_et_chargement_modele(self):
        cases = creer_liste_cases(nb_batons=8, max_retrait=3)
        entrainer_ia(cases, nb_parties=30)

        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            sauvegarder_modele(cases, path)
            loaded = charger_modele(path)
            self.assertEqual(len(loaded), len(cases))
            self.assertEqual(loaded[0].max_retrait, 3)
            self.assertEqual(loaded[5].poids_actions, cases[5].poids_actions)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
