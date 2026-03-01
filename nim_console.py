from ia import (
    MAX_RETRAIT_DEFAUT,
    NB_BATONS_DEFAUT,
    Joueur,
    creer_liste_cases,
    entrainer_ia,
    sauvegarder_modele,
    charger_modele,
)

NB_PARTIES_ENTRAINEMENT = 3000
FICHIER_MODELE = "modele_nim.json"


def afficher_regles():
    print("\n=== Jeu de Nim (console) ===")
    print("Règle : à chaque tour, on prend de 1 à max_retrait bâtons.")
    print("Le joueur qui prend le dernier bâton gagne.\n")


def demander_entier(message: str, minimum: int, maximum: int) -> int:
    while True:
        texte = input(message).strip()
        if texte.isdigit():
            valeur = int(texte)
            if minimum <= valeur <= maximum:
                return valeur
        print(f"Entrée invalide. Donne un nombre entre {minimum} et {maximum}.")


def demander_mode() -> int:
    print("Choisis un mode :")
    print("1 - Humain contre Humain")
    print("2 - Humain contre IA")
    return demander_entier("Ton choix (1 ou 2) : ", 1, 2)


def demander_joueur_depart() -> bool:
    print("\nQui commence ?")
    print("1 - Humain")
    print("2 - IA")
    return demander_entier("Ton choix (1 ou 2) : ", 1, 2) == 1


def coup_humain(nb_batons_restants: int, max_retrait: int, nom_joueur: str) -> int:
    max_autorise = min(max_retrait, nb_batons_restants)
    return demander_entier(
        f"{nom_joueur}, combien prends-tu ? (1-{max_autorise}) : ", 1, max_autorise
    )


def coup_ia(joueur_ia: Joueur, cases, nb_batons_restants: int) -> int:
    return joueur_ia.tire_une_boule(cases[nb_batons_restants])


def afficher_resume_ia(cases):
    print("\n--- Résumé des préférences de l'IA ---")
    for etat in range(1, len(cases)):
        case = cases[etat]
        pref = case.action_preferee()
        texte_pref = f"prendre {pref}" if pref is not None else "indécise"
        print(f"État {etat:2d} | poids={case.poids_actions} | préférence: {texte_pref}")


def jouer_partie_humain_vs_humain(nb_batons: int, max_retrait: int):
    restant = nb_batons
    joueur_courant = 1

    while restant > 0:
        print(f"\nIl reste {restant} bâton(s).")
        coup = coup_humain(restant, max_retrait, f"Joueur {joueur_courant}")
        restant -= coup

        if restant == 0:
            print(f"\n🎉 Joueur {joueur_courant} a gagné !")
            return

        joueur_courant = 2 if joueur_courant == 1 else 1


def jouer_partie_humain_vs_ia(cases, nb_batons: int, max_retrait: int):
    restant = nb_batons
    joueur_ia = Joueur("IA")
    tour_humain = demander_joueur_depart()

    while restant > 0:
        print(f"\nIl reste {restant} bâton(s).")

        if tour_humain:
            coup = coup_humain(restant, max_retrait, "Humain")
            print(f"Humain prend {coup} bâton(s).")
        else:
            coup = coup_ia(joueur_ia, cases, restant)
            print(f"IA prend {coup} bâton(s).")

        restant -= coup

        if restant == 0:
            if tour_humain:
                print("\n🎉 Bravo, tu as gagné contre l'IA !")
            else:
                print("\n🤖 L'IA a gagné.")
            return

        tour_humain = not tour_humain


def charger_ou_entrainer_ia(nb_batons: int, max_retrait: int):
    print("\n1 - Charger un modèle sauvegardé")
    print("2 - Entraîner une nouvelle IA")
    choix = demander_entier("Ton choix (1 ou 2) : ", 1, 2)

    if choix == 1:
        try:
            cases = charger_modele(FICHIER_MODELE)
            if len(cases) - 1 != nb_batons or cases[0].max_retrait != max_retrait:
                print("Le modèle ne correspond pas aux paramètres choisis. Ré-entraînement.")
            else:
                print("Modèle chargé ✅")
                return cases
        except FileNotFoundError:
            print("Aucun modèle sauvegardé. Ré-entraînement.")

    print("Entraînement de l'IA en cours...")
    cases = creer_liste_cases(nb_batons, max_retrait)
    entrainer_ia(cases, nb_parties=NB_PARTIES_ENTRAINEMENT)
    sauvegarder_modele(cases, FICHIER_MODELE)
    print("IA entraînée et sauvegardée ✅")
    return cases


def main():
    afficher_regles()

    max_retrait = demander_entier(
        f"Choisis la règle (2 ou 3 retraits max) [{MAX_RETRAIT_DEFAUT}] : ", 2, 3
    )
    nb_batons = demander_entier(
        f"Nombre initial de bâtons (5-60) [{NB_BATONS_DEFAUT}] : ", 5, 60
    )

    mode = demander_mode()

    if mode == 1:
        jouer_partie_humain_vs_humain(nb_batons, max_retrait)
    else:
        cases = charger_ou_entrainer_ia(nb_batons, max_retrait)
        afficher_resume_ia(cases)
        jouer_partie_humain_vs_ia(cases, nb_batons, max_retrait)


if __name__ == "__main__":
    main()
