import pygame

from game_logic import EtatPartie
from ia import Joueur, creer_liste_cases, entrainer_ia

# ------------------------------
# Configuration générale
# ------------------------------
LARGEUR = 1000
HAUTEUR = 680
FPS = 60

# Couleurs modernes
FOND = (18, 24, 38)
CARTE = (30, 39, 60)
CARTE_2 = (40, 50, 74)
TEXTE = (235, 240, 255)
TEXTE_FAIBLE = (170, 180, 210)
ACCENT = (95, 145, 255)
ACCENT_HOVER = (120, 165, 255)
VERT = (67, 196, 126)
ROUGE = (239, 94, 110)

NB_PARTIES_FACILE = 500
NB_PARTIES_MOYEN = 3000
NB_PARTIES_DIFFICILE = 12000


class Bouton:
    """Bouton simple avec état activé/désactivé."""

    def __init__(self, x, y, w, h, texte):
        self.rect = pygame.Rect(x, y, w, h)
        self.texte = texte
        self.enabled = True

    def dessiner(self, ecran, police, survol=False):
        if not self.enabled:
            couleur = (75, 82, 102)
            texte_couleur = (160, 165, 180)
        else:
            couleur = ACCENT_HOVER if survol else ACCENT
            texte_couleur = TEXTE

        pygame.draw.rect(ecran, couleur, self.rect, border_radius=12)
        texte_surface = police.render(self.texte, True, texte_couleur)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        ecran.blit(texte_surface, texte_rect)

    def est_clique(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


class JeuNim:
    """Version Pygame moderne et simple du jeu de Nim."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Nim - Interface moderne")
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        self.clock = pygame.time.Clock()

        self.police_titre = pygame.font.SysFont("arial", 50, bold=True)
        self.police_h2 = pygame.font.SysFont("arial", 32, bold=True)
        self.police_texte = pygame.font.SysFont("arial", 24)
        self.police_small = pygame.font.SysFont("arial", 20)

        # Scènes : accueil -> tutoriel -> config -> entrainement -> jeu -> fin -> stats
        self.scene = "accueil"

        # Paramètres de jeu
        self.mode_jeu = "hvh"  # hvh | hvai | iavai
        self.max_retrait = 2
        self.nb_batons_init = 15

        # Difficulté IA (utilisée pour hvai et iavai)
        self.difficulte = "moyen"
        self.nb_parties_entrainement = NB_PARTIES_MOYEN

        # État partie (moteur séparé)
        self.etat = EtatPartie(self.nb_batons_init, self.max_retrait)

        # IA
        self.cases_ia = None
        self.joueur_ia = Joueur("IA")
        self.ia_commence = False
        self.next_ai_time = 0

        # Stats session
        self.stats = {
            "parties": 0,
            "hvh_j1": 0,
            "hvh_j2": 0,
            "hvai_humain": 0,
            "hvai_ia": 0,
            "iavai_ia1": 0,
            "iavai_ia2": 0,
        }

        self._build_ui()

    # ------------------------------
    # UI setup
    # ------------------------------
    def _build_ui(self):
        # Accueil
        self.btn_jouer = Bouton(350, 220, 300, 70, "Jouer")
        self.btn_tuto = Bouton(350, 305, 300, 70, "Tutoriel")
        self.btn_stats = Bouton(350, 390, 300, 70, "Statistiques")
        self.btn_quitter = Bouton(350, 475, 300, 70, "Quitter")

        # Tutoriel
        self.btn_tuto_retour = Bouton(390, 575, 220, 55, "Retour")

        # Configuration
        self.btn_mode_hvh = Bouton(70, 170, 270, 55, "Humain vs Humain")
        self.btn_mode_hvai = Bouton(365, 170, 270, 55, "Humain vs IA")
        self.btn_mode_iavai = Bouton(660, 170, 270, 55, "IA vs IA")

        self.btn_regle_2 = Bouton(200, 255, 270, 55, "Règle: 1 à 2")
        self.btn_regle_3 = Bouton(530, 255, 270, 55, "Règle: 1 à 3")

        self.btn_diff_facile = Bouton(140, 340, 220, 55, "IA Facile")
        self.btn_diff_moyen = Bouton(390, 340, 220, 55, "IA Moyen")
        self.btn_diff_difficile = Bouton(640, 340, 220, 55, "IA Difficile")

        self.btn_batons_moins = Bouton(250, 430, 60, 50, "-")
        self.btn_batons_plus = Bouton(690, 430, 60, 50, "+")

        self.btn_ia_commence = Bouton(320, 515, 360, 50, "IA commence: Non")

        self.btn_lancer = Bouton(720, 610, 220, 45, "Lancer")
        self.btn_retour = Bouton(60, 610, 220, 45, "Retour")

        # Jeu
        self.btn_take_1 = Bouton(230, 560, 160, 65, "Prendre 1")
        self.btn_take_2 = Bouton(420, 560, 160, 65, "Prendre 2")
        self.btn_take_3 = Bouton(610, 560, 160, 65, "Prendre 3")

        self.btn_menu = Bouton(40, 30, 180, 45, "Menu")

        # Fin
        self.btn_rejouer = Bouton(220, 500, 220, 65, "Rejouer")
        self.btn_reconfig = Bouton(470, 500, 220, 65, "Reconfigurer")
        self.btn_rapide = Bouton(720, 500, 180, 65, "Partie rapide")

        # Stats
        self.btn_stats_retour = Bouton(390, 575, 220, 55, "Retour")

    # ------------------------------
    # Logique de jeu
    # ------------------------------
    def maj_etat_depuis_config(self):
        self.etat = EtatPartie(self.nb_batons_init, self.max_retrait)

    def maj_difficulte(self, difficulte: str):
        self.difficulte = difficulte
        if difficulte == "facile":
            self.nb_parties_entrainement = NB_PARTIES_FACILE
        elif difficulte == "moyen":
            self.nb_parties_entrainement = NB_PARTIES_MOYEN
        else:
            self.nb_parties_entrainement = NB_PARTIES_DIFFICILE

    def texte_mode(self):
        if self.mode_jeu == "hvh":
            return "Humain vs Humain"
        if self.mode_jeu == "hvai":
            return "Humain vs IA"
        return "IA vs IA"

    def demarrer_partie(self):
        self.maj_etat_depuis_config()
        self.scene = "jeu"

        if self.mode_jeu == "hvai" and self.ia_commence:
            self.etat.joueur_courant = 2
            self.next_ai_time = pygame.time.get_ticks() + 500

        if self.mode_jeu == "iavai":
            self.etat.joueur_courant = 1
            self.next_ai_time = pygame.time.get_ticks() + 500

    def lancer_partie_depuis_config(self):
        # Entraînement nécessaire si l'IA participe
        if self.mode_jeu in ("hvai", "iavai"):
            self.scene = "entrainement"
            self.ecran.fill(FOND)
            self.dessiner_texte_centre("Entraînement IA en cours...", self.police_h2, TEXTE, 300)
            self.dessiner_texte_centre(
                f"Difficulté: {self.difficulte} ({self.nb_parties_entrainement} parties)",
                self.police_texte,
                TEXTE_FAIBLE,
                350,
            )
            pygame.display.flip()

            self.cases_ia = creer_liste_cases(self.nb_batons_init, self.max_retrait)
            entrainer_ia(self.cases_ia, self.nb_parties_entrainement)

        self.demarrer_partie()

    def jouer_coup(self, retrait: int):
        ok = self.etat.jouer_coup(retrait)
        if not ok:
            return

        if self.etat.gagnant is not None:
            self.scene = "fin"
            self.stats["parties"] += 1

            if self.mode_jeu == "hvh":
                if self.etat.gagnant == 1:
                    self.stats["hvh_j1"] += 1
                else:
                    self.stats["hvh_j2"] += 1
            elif self.mode_jeu == "hvai":
                if self.etat.gagnant == 1:
                    self.stats["hvai_humain"] += 1
                else:
                    self.stats["hvai_ia"] += 1
            else:
                if self.etat.gagnant == 1:
                    self.stats["iavai_ia1"] += 1
                else:
                    self.stats["iavai_ia2"] += 1
            return

        if self.mode_jeu in ("hvai", "iavai"):
            self.next_ai_time = pygame.time.get_ticks() + 500

    def jouer_coup_ia_si_necessaire(self):
        if self.scene != "jeu":
            return
        if self.mode_jeu not in ("hvai", "iavai"):
            return
        if pygame.time.get_ticks() < self.next_ai_time:
            return

        if self.mode_jeu == "hvai" and self.etat.joueur_courant != 2:
            return

        action = self.joueur_ia.tire_une_boule(self.cases_ia[self.etat.nb_batons])
        self.jouer_coup(action)

    # ------------------------------
    # Dessin utilitaire
    # ------------------------------
    def dessiner_texte_centre(self, texte, police, couleur, y):
        surf = police.render(texte, True, couleur)
        rect = surf.get_rect(center=(LARGEUR // 2, y))
        self.ecran.blit(surf, rect)

    def dessiner_carte(self, x, y, w, h):
        pygame.draw.rect(self.ecran, CARTE, (x, y, w, h), border_radius=18)

    def dessiner_batons(self):
        zone_x = 120
        zone_y = 210
        zone_w = 760
        colonnes = 14
        espacement = zone_w // colonnes

        for i in range(self.etat.nb_batons):
            c = i % colonnes
            l = i // colonnes
            x = zone_x + c * espacement + 8
            y = zone_y + l * 105
            pygame.draw.rect(self.ecran, (191, 139, 82), (x, y, 14, 86), border_radius=4)

    def dessiner_resume_partie(self):
        """Affiche les paramètres actifs pour une prise en main rapide."""
        lignes = [
            f"Mode: {self.texte_mode()}",
            f"Règle: 1 à {self.max_retrait}",
            f"Bâtons initiaux: {self.nb_batons_init}",
            "Raccourcis: 1/2/3 pour jouer, M menu, R partie rapide",
        ]

        if self.mode_jeu in ("hvai", "iavai"):
            lignes.append(f"Difficulté IA: {self.difficulte} ({self.nb_parties_entrainement} parties)")

        y = 70
        for ligne in lignes:
            texte = self.police_small.render(ligne, True, TEXTE_FAIBLE)
            self.ecran.blit(texte, (560, y))
            y += 24

    # ------------------------------
    # Dessin scènes
    # ------------------------------
    def dessiner_accueil(self):
        self.ecran.fill(FOND)
        self.dessiner_carte(170, 80, 660, 520)
        self.dessiner_texte_centre("Jeu de Nim", self.police_titre, TEXTE, 150)
        self.dessiner_texte_centre("Simple, stratégique, moderne", self.police_texte, TEXTE_FAIBLE, 200)

        pos = pygame.mouse.get_pos()
        self.btn_jouer.dessiner(self.ecran, self.police_h2, self.btn_jouer.rect.collidepoint(pos))
        self.btn_tuto.dessiner(self.ecran, self.police_h2, self.btn_tuto.rect.collidepoint(pos))
        self.btn_stats.dessiner(self.ecran, self.police_h2, self.btn_stats.rect.collidepoint(pos))
        self.btn_quitter.dessiner(self.ecran, self.police_h2, self.btn_quitter.rect.collidepoint(pos))

    def dessiner_tutoriel(self):
        self.ecran.fill(FOND)
        self.dessiner_carte(90, 60, 820, 560)
        self.dessiner_texte_centre("Tutoriel rapide", self.police_h2, TEXTE, 120)

        lignes = [
            "Objectif : prendre le dernier bâton pour gagner.",
            "À chaque tour, tu prends entre 1 et max_retrait bâtons.",
            "En mode Humain vs IA : la difficulté change le nombre de parties d'entraînement.",
            "Raccourcis clavier en partie : 1/2/3 pour jouer, M menu, R partie rapide.",
        ]

        y = 210
        for ligne in lignes:
            self.dessiner_texte_centre(ligne, self.police_texte, TEXTE_FAIBLE, y)
            y += 70

        pos = pygame.mouse.get_pos()
        self.btn_tuto_retour.dessiner(
            self.ecran, self.police_texte, self.btn_tuto_retour.rect.collidepoint(pos)
        )

    def dessiner_config(self):
        self.ecran.fill(FOND)
        self.dessiner_carte(35, 35, 930, 610)
        self.dessiner_texte_centre("Configuration de la partie", self.police_h2, TEXTE, 78)

        pos = pygame.mouse.get_pos()

        # Modes
        self.btn_mode_hvh.dessiner(self.ecran, self.police_small, self.btn_mode_hvh.rect.collidepoint(pos))
        self.btn_mode_hvai.dessiner(self.ecran, self.police_small, self.btn_mode_hvai.rect.collidepoint(pos))
        self.btn_mode_iavai.dessiner(self.ecran, self.police_small, self.btn_mode_iavai.rect.collidepoint(pos))
        self.ecran.blit(self.police_small.render(f"Mode actuel : {self.texte_mode()}", True, TEXTE_FAIBLE), (390, 230))

        # Règle
        self.btn_regle_2.dessiner(self.ecran, self.police_texte, self.btn_regle_2.rect.collidepoint(pos))
        self.btn_regle_3.dessiner(self.ecran, self.police_texte, self.btn_regle_3.rect.collidepoint(pos))
        self.ecran.blit(
            self.police_small.render(f"Règle actuelle : prendre 1 à {self.max_retrait}", True, TEXTE_FAIBLE),
            (350, 320),
        )

        # Difficulté
        self.btn_diff_facile.enabled = self.mode_jeu in ("hvai", "iavai")
        self.btn_diff_moyen.enabled = self.mode_jeu in ("hvai", "iavai")
        self.btn_diff_difficile.enabled = self.mode_jeu in ("hvai", "iavai")

        self.btn_diff_facile.dessiner(
            self.ecran, self.police_small, self.btn_diff_facile.rect.collidepoint(pos)
        )
        self.btn_diff_moyen.dessiner(
            self.ecran, self.police_small, self.btn_diff_moyen.rect.collidepoint(pos)
        )
        self.btn_diff_difficile.dessiner(
            self.ecran, self.police_small, self.btn_diff_difficile.rect.collidepoint(pos)
        )

        diff_txt = f"Difficulté actuelle : {self.difficulte} ({self.nb_parties_entrainement} parties)"
        self.ecran.blit(self.police_small.render(diff_txt, True, TEXTE_FAIBLE), (270, 405))

        # Bâtons initiaux
        self.ecran.blit(self.police_texte.render("Bâtons initiaux", True, TEXTE), (90, 444))
        self.btn_batons_moins.dessiner(
            self.ecran, self.police_texte, self.btn_batons_moins.rect.collidepoint(pos)
        )
        self.btn_batons_plus.dessiner(self.ecran, self.police_texte, self.btn_batons_plus.rect.collidepoint(pos))
        pygame.draw.rect(self.ecran, CARTE_2, (380, 430, 240, 52), border_radius=10)
        self.dessiner_texte_centre(str(self.nb_batons_init), self.police_texte, TEXTE, 456)

        # IA commence
        self.btn_ia_commence.enabled = self.mode_jeu == "hvai"
        texte_start = "IA commence: Oui" if self.ia_commence else "IA commence: Non"
        self.btn_ia_commence.texte = texte_start
        self.btn_ia_commence.dessiner(
            self.ecran, self.police_small, self.btn_ia_commence.rect.collidepoint(pos)
        )

        self.btn_retour.dessiner(self.ecran, self.police_small, self.btn_retour.rect.collidepoint(pos))
        self.btn_lancer.dessiner(self.ecran, self.police_small, self.btn_lancer.rect.collidepoint(pos))

    def dessiner_jeu(self):
        self.ecran.fill(FOND)
        self.dessiner_carte(20, 20, 960, 640)

        pos = pygame.mouse.get_pos()
        self.btn_menu.dessiner(self.ecran, self.police_small, self.btn_menu.rect.collidepoint(pos))

        if self.mode_jeu == "hvai":
            if self.etat.joueur_courant == 2:
                tour_txt = "Tour de l'IA..."
                couleur_tour = ACCENT
            else:
                tour_txt = "Tour de l'humain"
                couleur_tour = VERT
        elif self.mode_jeu == "iavai":
            tour_txt = f"Tour de l'IA {self.etat.joueur_courant}"
            couleur_tour = ACCENT
        else:
            tour_txt = f"Tour du Joueur {self.etat.joueur_courant}"
            couleur_tour = VERT if self.etat.joueur_courant == 1 else ROUGE

        self.dessiner_texte_centre(tour_txt, self.police_h2, couleur_tour, 90)
        self.dessiner_texte_centre(f"Bâtons restants : {self.etat.nb_batons}", self.police_texte, TEXTE, 130)

        self.dessiner_resume_partie()
        self.dessiner_batons()

        # Boutons de coups
        coups_valides = self.etat.coups_valides()
        self.btn_take_1.enabled = 1 in coups_valides
        self.btn_take_2.enabled = 2 in coups_valides
        self.btn_take_3.enabled = 3 in coups_valides and self.max_retrait >= 3

        # En mode IA, on bloque les boutons pendant les tours IA
        if self.mode_jeu == "hvai" and self.etat.joueur_courant == 2:
            self.btn_take_1.enabled = False
            self.btn_take_2.enabled = False
            self.btn_take_3.enabled = False

        if self.mode_jeu == "iavai":
            self.btn_take_1.enabled = False
            self.btn_take_2.enabled = False
            self.btn_take_3.enabled = False

        self.btn_take_1.dessiner(self.ecran, self.police_texte, self.btn_take_1.rect.collidepoint(pos))
        self.btn_take_2.dessiner(self.ecran, self.police_texte, self.btn_take_2.rect.collidepoint(pos))
        self.btn_take_3.dessiner(self.ecran, self.police_texte, self.btn_take_3.rect.collidepoint(pos))

    def dessiner_fin(self):
        self.ecran.fill(FOND)
        self.dessiner_carte(100, 90, 800, 500)
        self.dessiner_texte_centre("Fin de partie", self.police_titre, TEXTE, 170)

        if self.mode_jeu == "hvai":
            gagnant_txt = "Humain" if self.etat.gagnant == 1 else "IA"
        elif self.mode_jeu == "iavai":
            gagnant_txt = f"IA {self.etat.gagnant}"
        else:
            gagnant_txt = f"Joueur {self.etat.gagnant}"

        self.dessiner_texte_centre(f"🎉 Victoire : {gagnant_txt}", self.police_h2, TEXTE, 270)
        self.dessiner_texte_centre(
            f"Parties jouées (session): {self.stats['parties']}", self.police_texte, TEXTE_FAIBLE, 330
        )

        pos = pygame.mouse.get_pos()
        self.btn_rejouer.dessiner(self.ecran, self.police_texte, self.btn_rejouer.rect.collidepoint(pos))
        self.btn_reconfig.dessiner(self.ecran, self.police_texte, self.btn_reconfig.rect.collidepoint(pos))
        self.btn_rapide.dessiner(self.ecran, self.police_small, self.btn_rapide.rect.collidepoint(pos))

    def dessiner_stats(self):
        self.ecran.fill(FOND)
        self.dessiner_carte(120, 60, 760, 560)
        self.dessiner_texte_centre("Statistiques de session", self.police_h2, TEXTE, 120)

        lignes = [
            f"Parties jouées : {self.stats['parties']}",
            f"Humain vs Humain -> J1: {self.stats['hvh_j1']} | J2: {self.stats['hvh_j2']}",
            f"Humain vs IA -> Humain: {self.stats['hvai_humain']} | IA: {self.stats['hvai_ia']}",
            f"IA vs IA -> IA1: {self.stats['iavai_ia1']} | IA2: {self.stats['iavai_ia2']}",
        ]

        y = 220
        for ligne in lignes:
            self.dessiner_texte_centre(ligne, self.police_texte, TEXTE_FAIBLE, y)
            y += 58

        pos = pygame.mouse.get_pos()
        self.btn_stats_retour.dessiner(
            self.ecran, self.police_texte, self.btn_stats_retour.rect.collidepoint(pos)
        )

    # ------------------------------
    # Événements
    # ------------------------------
    def clic_accueil(self, pos):
        if self.btn_jouer.est_clique(pos):
            self.scene = "config"
        elif self.btn_tuto.est_clique(pos):
            self.scene = "tutoriel"
        elif self.btn_stats.est_clique(pos):
            self.scene = "stats"
        elif self.btn_quitter.est_clique(pos):
            return False
        return True

    def clic_tutoriel(self, pos):
        if self.btn_tuto_retour.est_clique(pos):
            self.scene = "accueil"

    def clic_config(self, pos):
        if self.btn_mode_hvh.est_clique(pos):
            self.mode_jeu = "hvh"
        elif self.btn_mode_hvai.est_clique(pos):
            self.mode_jeu = "hvai"
        elif self.btn_mode_iavai.est_clique(pos):
            self.mode_jeu = "iavai"

        elif self.btn_regle_2.est_clique(pos):
            self.max_retrait = 2
        elif self.btn_regle_3.est_clique(pos):
            self.max_retrait = 3

        elif self.btn_diff_facile.est_clique(pos):
            self.maj_difficulte("facile")
        elif self.btn_diff_moyen.est_clique(pos):
            self.maj_difficulte("moyen")
        elif self.btn_diff_difficile.est_clique(pos):
            self.maj_difficulte("difficile")

        elif self.btn_batons_moins.est_clique(pos):
            self.nb_batons_init = max(5, self.nb_batons_init - 1)
        elif self.btn_batons_plus.est_clique(pos):
            self.nb_batons_init = min(80, self.nb_batons_init + 1)

        elif self.btn_ia_commence.est_clique(pos):
            self.ia_commence = not self.ia_commence

        elif self.btn_retour.est_clique(pos):
            self.scene = "accueil"
        elif self.btn_lancer.est_clique(pos):
            self.lancer_partie_depuis_config()

    def clic_jeu(self, pos):
        if self.btn_menu.est_clique(pos):
            self.scene = "config"
            return

        if self.btn_take_1.est_clique(pos):
            self.jouer_coup(1)
        elif self.btn_take_2.est_clique(pos):
            self.jouer_coup(2)
        elif self.btn_take_3.est_clique(pos):
            self.jouer_coup(3)

    def clic_fin(self, pos):
        if self.btn_rejouer.est_clique(pos):
            self.demarrer_partie()
        elif self.btn_reconfig.est_clique(pos):
            self.scene = "config"
        elif self.btn_rapide.est_clique(pos):
            self.demarrer_partie()

    def clic_stats(self, pos):
        if self.btn_stats_retour.est_clique(pos):
            self.scene = "accueil"

    def gerer_raccourcis_clavier(self, event):
        """UX: raccourcis pour jouer plus vite."""
        if event.key == pygame.K_m:
            self.scene = "config"
            return

        if event.key == pygame.K_r and self.scene in ("jeu", "fin"):
            self.demarrer_partie()
            return

        if self.scene != "jeu":
            return

        if event.key == pygame.K_1:
            self.jouer_coup(1)
        elif event.key == pygame.K_2:
            self.jouer_coup(2)
        elif event.key == pygame.K_3:
            self.jouer_coup(3)

    # ------------------------------
    # Boucle principale
    # ------------------------------
    def run(self):
        en_cours = True

        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False

                if event.type == pygame.KEYDOWN:
                    self.gerer_raccourcis_clavier(event)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.scene == "accueil":
                        en_cours = self.clic_accueil(event.pos)
                    elif self.scene == "tutoriel":
                        self.clic_tutoriel(event.pos)
                    elif self.scene == "config":
                        self.clic_config(event.pos)
                    elif self.scene == "jeu":
                        self.clic_jeu(event.pos)
                    elif self.scene == "fin":
                        self.clic_fin(event.pos)
                    elif self.scene == "stats":
                        self.clic_stats(event.pos)

            self.jouer_coup_ia_si_necessaire()

            if self.scene == "accueil":
                self.dessiner_accueil()
            elif self.scene == "tutoriel":
                self.dessiner_tutoriel()
            elif self.scene in ("config", "entrainement"):
                self.dessiner_config()
            elif self.scene == "jeu":
                self.dessiner_jeu()
            elif self.scene == "fin":
                self.dessiner_fin()
            elif self.scene == "stats":
                self.dessiner_stats()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    jeu = JeuNim()
    jeu.run()


if __name__ == "__main__":
    main()
