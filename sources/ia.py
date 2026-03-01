from __future__ import annotations

from random import randint
import json

NOMBRE_BOULES_INIT = 20
NB_BATONS_DEFAUT = 10
MAX_RETRAIT_DEFAUT = 2


class Case:
    """État du jeu pour un nombre de bâtons donné."""

    def __init__(self, nombre_case: int, max_retrait: int, poids: dict[int, int] | None = None):
        self.nombre_case = nombre_case
        self.max_retrait = max_retrait

        if poids is None:
            self.poids_actions = self._poids_initiaux()
        else:
            self.poids_actions = {action: int(val) for action, val in poids.items()}

    @property
    def boules_jaune(self) -> int:
        """Compatibilité avec l'ancien code (action 1)."""
        return self.poids_actions.get(1, 0)

    @property
    def boules_rouge(self) -> int:
        """Compatibilité avec l'ancien code (action 2)."""
        return self.poids_actions.get(2, 0)

    def __eq__(self, o):
        return isinstance(o, Case) and self.nombre_case == o.nombre_case

    def __repr__(self):
        return f"Case {self.nombre_case} | poids={self.poids_actions}"

    def _poids_initiaux(self) -> dict[int, int]:
        if self.nombre_case == 0:
            return {action: 0 for action in range(1, self.max_retrait + 1)}

        poids = {}
        for action in range(1, self.max_retrait + 1):
            # action impossible si elle dépasse le nombre de bâtons restants
            if action > self.nombre_case:
                poids[action] = 0
            else:
                poids[action] = NOMBRE_BOULES_INIT
        return poids

    def reset(self):
        self.poids_actions = self._poids_initiaux()

    def actions_valides(self) -> list[int]:
        return [action for action in range(1, self.max_retrait + 1) if action <= self.nombre_case]

    def ajouter_boule(self, action: int):
        if action not in self.poids_actions:
            return
        self.poids_actions[action] += 1

    def supprimer_boule(self, action: int):
        if action not in self.poids_actions:
            return
        if self.poids_actions[action] > 0:
            self.poids_actions[action] -= 1

    def total_boules(self) -> int:
        return sum(self.poids_actions.values())

    def tirage_pondere(self) -> int:
        """Retourne l'action tirée selon les poids. Fallback uniforme si total=0."""
        total = self.total_boules()
        if total == 0:
            self.reset()
            total = self.total_boules()

        if total == 0:
            # Cas limite : sécurité
            return 1

        tirage = randint(1, total)
        cumul = 0
        for action in range(1, self.max_retrait + 1):
            cumul += self.poids_actions.get(action, 0)
            if tirage <= cumul:
                return action

        return 1

    def action_preferee(self) -> int | None:
        meilleures = []
        max_boules = -1
        for action in self.actions_valides():
            valeur = self.poids_actions.get(action, 0)
            if valeur > max_boules:
                max_boules = valeur
                meilleures = [action]
            elif valeur == max_boules:
                meilleures.append(action)

        if not meilleures:
            return None
        if len(meilleures) > 1:
            return None
        return meilleures[0]

    def recap(self):
        print(f"\nCase {self.nombre_case}")
        for action in self.actions_valides():
            print(f"  Boules action {action} : {self.poids_actions[action]}")

        if self.nombre_case == 0:
            print("  Position terminale : partie finie.")
            return

        # Théorie Nim : positions perdantes = multiples de (max_retrait + 1)
        modulo = self.max_retrait + 1
        if self.nombre_case % modulo == 0:
            print(f"  Théorie : POSITION PERDANTE (multiple de {modulo})")
            print("  Aucun coup gagnant garanti.")
        else:
            coup_theorique = self.nombre_case % modulo
            print("  Théorie : POSITION GAGNANTE")
            print(f"  Coup optimal théorique : prendre {coup_theorique}")

        coup_ia = self.action_preferee()
        if coup_ia is None:
            print("  IA : indécise (répartition équilibrée)")
        else:
            print(f"  IA : préfère prendre {coup_ia}")


class Joueur:
    def __init__(self, num_j):
        self.num_j = num_j

    def __repr__(self):
        return "Joueur " + str(self.num_j)

    def tire_une_boule(self, case: Case):
        return case.tirage_pondere()


def creer_liste_cases(
    nb_batons: int = NB_BATONS_DEFAUT, max_retrait: int = MAX_RETRAIT_DEFAUT
) -> list[Case]:
    """Crée les cases de 0 à nb_batons."""
    return [Case(numero, max_retrait=max_retrait) for numero in range(nb_batons + 1)]


def tour(j1: Joueur, j2: Joueur, liste_cases: list[Case], case_depart: int):
    liste_jeu_j1 = []  # liste de (etat, action)
    liste_jeu_j2 = []

    case_actuelle = case_depart
    joueur1_joue = True
    dernier_joueur = None

    while case_actuelle != 0:
        case_obj = liste_cases[case_actuelle]

        if joueur1_joue:
            action = j1.tire_une_boule(case_obj)
            liste_jeu_j1.append((case_actuelle, action))
            case_actuelle -= action
            dernier_joueur = 1
        else:
            action = j2.tire_une_boule(case_obj)
            liste_jeu_j2.append((case_actuelle, action))
            case_actuelle -= action
            dernier_joueur = 2

        joueur1_joue = not joueur1_joue

    if dernier_joueur == 1:
        coups_gagnant, coups_perdant = liste_jeu_j1, liste_jeu_j2
        gagnant = j1
    else:
        coups_gagnant, coups_perdant = liste_jeu_j2, liste_jeu_j1
        gagnant = j2

    for etat, action in coups_gagnant:
        liste_cases[etat].ajouter_boule(action)
    for etat, action in coups_perdant:
        liste_cases[etat].supprimer_boule(action)

    return gagnant


def entrainer_ia(liste_cases: list[Case], nb_parties: int):
    """Fait jouer 2 IA entre elles pour entraîner la stratégie."""
    joueur1 = Joueur(1)
    joueur2 = Joueur(2)
    case_depart = len(liste_cases) - 1

    for _ in range(nb_parties):
        tour(joueur1, joueur2, liste_cases, case_depart)


def afficher_recapitulatif(liste_cases: list[Case]):
    for case in liste_cases[1:]:
        case.recap()


def sauvegarder_modele(liste_cases: list[Case], chemin_fichier: str):
    """Sauvegarde les poids de l'IA dans un fichier JSON."""
    if not liste_cases:
        return

    data = {
        "max_retrait": liste_cases[0].max_retrait,
        "nb_batons": len(liste_cases) - 1,
        "cases": [case.poids_actions for case in liste_cases],
    }

    with open(chemin_fichier, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def charger_modele(chemin_fichier: str) -> list[Case]:
    """Charge les poids d'une IA depuis un fichier JSON."""
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        data = json.load(f)

    max_retrait = int(data["max_retrait"])
    cases_data = data["cases"]

    cases = []
    for numero, poids in enumerate(cases_data):
        poids_int = {int(action): int(valeur) for action, valeur in poids.items()}
        cases.append(Case(numero, max_retrait=max_retrait, poids=poids_int))
    return cases


def main():
    liste_cases = creer_liste_cases(NB_BATONS_DEFAUT, MAX_RETRAIT_DEFAUT)
    entrainer_ia(liste_cases, nb_parties=1000)
    afficher_recapitulatif(liste_cases)


if __name__ == "__main__":
    main()
