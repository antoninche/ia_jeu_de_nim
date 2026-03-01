import math
import json
from pathlib import Path
import pygame

from game_logic import EtatPartie
from ia import Joueur, creer_liste_cases, entrainer_ia

# -------------------------------------------------
# Configuration générale
# -------------------------------------------------
LARGEUR = 1200
HAUTEUR = 760
FPS = 60

# Palette moderne (bon contraste)
BG = (14, 19, 30)
PANEL = (28, 35, 53)
PANEL_ALT = (36, 45, 67)
TEXT = (240, 244, 255)
TEXT_MUTED = (190, 202, 232)
PRIMARY = (82, 140, 255)
PRIMARY_HOVER = (109, 159, 255)
PRIMARY_SELECTED = (70, 196, 150)
DANGER = (236, 96, 121)
STICK_COLOR = (196, 145, 86)
DISABLED = (91, 102, 129)

NB_PARTIES_FACILE = 500
NB_PARTIES_MOYEN = 3000
NB_PARTIES_DIFFICILE = 12000
FICHIER_STATS = "stats_nim.json"


class Bouton:
    """Bouton simple avec états hover / disabled / selected."""

    def __init__(self, x, y, w, h, texte):
        self.rect = pygame.Rect(x, y, w, h)
        self.texte = texte
        self.enabled = True
        self.selected = False

    def dessiner(self, ecran, police, survol=False):
        if not self.enabled:
            color = DISABLED
            txt_color = (178, 186, 205)
        elif self.selected:
            color = PRIMARY_SELECTED
            txt_color = TEXT
        else:
            color = PRIMARY_HOVER if survol else PRIMARY
            txt_color = TEXT

        pygame.draw.rect(ecran, color, self.rect, border_radius=14)
        text_surface = police.render(self.texte, True, txt_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        ecran.blit(text_surface, text_rect)

    def est_clique(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


class JeuNim:
    """Interface Pygame du Nim : claire, moderne, non bloquante."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Nim - UI moderne")
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        self.clock = pygame.time.Clock()

        # Polices (fallback système)
        self.font_title = pygame.font.SysFont("segoeui,arial", 60, bold=True)
        self.font_h1 = pygame.font.SysFont("segoeui,arial", 38, bold=True)
        self.font_h2 = pygame.font.SysFont("segoeui,arial", 28, bold=True)
        self.font_text = pygame.font.SysFont("trebuchetms,arial", 24)
        self.font_small = pygame.font.SysFont("trebuchetms,arial", 20)

        # Scènes
        self.scene = "home"  # home | config | training | game | end | stats

        # Paramètres
        self.mode_jeu = "hvh"  # hvh | hvai | iavai
        self.max_retrait = 2
        self.nb_batons_init = 15
        self.difficulte = "moyen"
        self.nb_parties_entrainement = NB_PARTIES_MOYEN
        self.ia_commence = False

        # Moteur de partie
        self.etat = EtatPartie(self.nb_batons_init, self.max_retrait)

        # IA
        self.cases_ia = None
        self.joueur_ia = Joueur("IA")
        self.next_ai_time = 0

        # Entraînement non bloquant
        self.training_total = 0
        self.training_done = 0
        self.training_batch = 200

        # Animations
        self.sticks_affiches = float(self.etat.nb_batons)
        self.scene_alpha = 255

        # Aide
        self.show_help = False

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
        self.charger_stats()

        self._build_ui()

    # -------------------------------------------------
    # Setup UI
    # -------------------------------------------------
    def _build_ui(self):
        # Home
        self.btn_play = Bouton(450, 280, 300, 64, "Jouer")
        self.btn_stats = Bouton(450, 364, 300, 64, "Statistiques")
        self.btn_quit = Bouton(450, 448, 300, 64, "Quitter")

        # Config
        self.btn_mode_hvh = Bouton(90, 210, 300, 56, "Humain vs Humain")
        self.btn_mode_hvai = Bouton(90, 280, 300, 56, "Humain vs IA")
        self.btn_mode_iavai = Bouton(90, 350, 300, 56, "IA vs IA")

        self.btn_regle2 = Bouton(450, 210, 300, 56, "Règle 1..2")
        self.btn_regle3 = Bouton(450, 280, 300, 56, "Règle 1..3")

        self.btn_diff_easy = Bouton(810, 210, 300, 56, "IA Facile")
        self.btn_diff_med = Bouton(810, 280, 300, 56, "IA Moyen")
        self.btn_diff_hard = Bouton(810, 350, 300, 56, "IA Difficile")

        self.btn_stick_minus = Bouton(500, 460, 56, 50, "-")
        self.btn_stick_plus = Bouton(644, 460, 56, 50, "+")

        self.btn_ia_starts = Bouton(450, 540, 300, 52, "IA commence: Non")

        self.btn_back = Bouton(90, 660, 220, 52, "Retour")
        self.btn_start = Bouton(890, 660, 220, 52, "Lancer")

        # Game
        self.btn_take1 = Bouton(380, 666, 130, 50, "Prendre 1")
        self.btn_take2 = Bouton(535, 666, 130, 50, "Prendre 2")
        self.btn_take3 = Bouton(690, 666, 130, 50, "Prendre 3")
        self.btn_game_menu = Bouton(24, 24, 180, 46, "Menu")

        # End
        self.btn_replay = Bouton(360, 560, 220, 58, "Rejouer")
        self.btn_reconfig = Bouton(600, 560, 220, 58, "Configurer")

        # Stats
        self.btn_stats_back = Bouton(350, 660, 220, 52, "Retour")
        self.btn_stats_reset = Bouton(630, 660, 220, 52, "Réinitialiser")

    # -------------------------------------------------
    # Helpers UI
    # -------------------------------------------------
    def switch_scene(self, name: str):
        self.scene = name
        self.scene_alpha = 255

    def draw_scene_fade(self):
        if self.scene_alpha <= 0:
            return
        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.scene_alpha))
        self.ecran.blit(overlay, (0, 0))
        self.scene_alpha = max(0, self.scene_alpha - 18)

    def draw_text_center(self, txt, font, color, y):
        surf = font.render(txt, True, color)
        rect = surf.get_rect(center=(LARGEUR // 2, y))
        self.ecran.blit(surf, rect)

    def draw_panel(self, x, y, w, h, alt=False):
        color = PANEL_ALT if alt else PANEL
        pygame.draw.rect(self.ecran, color, (x, y, w, h), border_radius=18)

    def mode_label(self):
        if self.mode_jeu == "hvh":
            return "Humain vs Humain"
        if self.mode_jeu == "hvai":
            return "Humain vs IA"
        return "IA vs IA"

    def maj_difficulte(self, name: str):
        self.difficulte = name
        if name == "facile":
            self.nb_parties_entrainement = NB_PARTIES_FACILE
        elif name == "moyen":
            self.nb_parties_entrainement = NB_PARTIES_MOYEN
        else:
            self.nb_parties_entrainement = NB_PARTIES_DIFFICILE

    def sync_selected_buttons(self):
        # mode
        self.btn_mode_hvh.selected = self.mode_jeu == "hvh"
        self.btn_mode_hvai.selected = self.mode_jeu == "hvai"
        self.btn_mode_iavai.selected = self.mode_jeu == "iavai"

        # règle
        self.btn_regle2.selected = self.max_retrait == 2
        self.btn_regle3.selected = self.max_retrait == 3

        # difficulté
        self.btn_diff_easy.selected = self.difficulte == "facile"
        self.btn_diff_med.selected = self.difficulte == "moyen"
        self.btn_diff_hard.selected = self.difficulte == "difficile"

    # -------------------------------------------------
    # Moteur de partie
    # -------------------------------------------------
    def reset_state_from_config(self):
        self.etat = EtatPartie(self.nb_batons_init, self.max_retrait)
        self.sticks_affiches = float(self.etat.nb_batons)

    def demarrer_partie(self):
        self.reset_state_from_config()
        self.switch_scene("game")

        if self.mode_jeu == "hvai" and self.ia_commence:
            self.etat.joueur_courant = 2
            self.next_ai_time = pygame.time.get_ticks() + 450

        if self.mode_jeu == "iavai":
            self.etat.joueur_courant = 1
            self.next_ai_time = pygame.time.get_ticks() + 450

    def demarrer_entrainement(self):
        self.cases_ia = creer_liste_cases(self.nb_batons_init, self.max_retrait)
        self.training_total = self.nb_parties_entrainement
        self.training_done = 0
        self.switch_scene("training")

    def update_training(self):
        if self.scene != "training":
            return

        if self.training_done >= self.training_total:
            self.demarrer_partie()
            return

        reste = self.training_total - self.training_done
        lot = min(self.training_batch, reste)
        entrainer_ia(self.cases_ia, lot)
        self.training_done += lot

    def lancer_depuis_config(self):
        if self.mode_jeu in ("hvai", "iavai"):
            self.demarrer_entrainement()
        else:
            self.demarrer_partie()

    def jouer_coup(self, retrait: int):
        ok = self.etat.jouer_coup(retrait)
        if not ok:
            return

        if self.etat.gagnant is not None:
            self.switch_scene("end")
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
            self.sauvegarder_stats()
            return

        if self.mode_jeu in ("hvai", "iavai"):
            self.next_ai_time = pygame.time.get_ticks() + 450

    def update_ai(self):
        if self.scene != "game":
            return
        if self.mode_jeu not in ("hvai", "iavai"):
            return
        if pygame.time.get_ticks() < self.next_ai_time:
            return

        if self.mode_jeu == "hvai" and self.etat.joueur_courant != 2:
            return

        action = self.joueur_ia.tire_une_boule(self.cases_ia[self.etat.nb_batons])
        self.jouer_coup(action)

    def update_animations(self):
        """Animation douce du nombre de bâtons affichés."""
        target = float(self.etat.nb_batons)
        if abs(self.sticks_affiches - target) < 0.02:
            self.sticks_affiches = target
            return

        vitesse = 0.28
        self.sticks_affiches += (target - self.sticks_affiches) * vitesse

    def sauvegarder_stats(self):
        """Sauvegarde les stats de session sur disque."""
        with open(FICHIER_STATS, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def charger_stats(self):
        """Charge les stats si le fichier existe."""
        path = Path(FICHIER_STATS)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return

        for cle in self.stats:
            if cle in data and isinstance(data[cle], int):
                self.stats[cle] = data[cle]

    def reset_stats(self):
        for cle in self.stats:
            self.stats[cle] = 0
        self.sauvegarder_stats()

    # -------------------------------------------------
    # Dessin des scènes
    # -------------------------------------------------
    def draw_help_overlay(self):
        if not self.show_help:
            return

        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.ecran.blit(overlay, (0, 0))
        self.draw_panel(250, 200, 700, 300)
        self.draw_text_center("Aide rapide", self.font_h1, TEXT, 260)
        lines = [
            "1 / 2 / 3 : jouer un coup",
            "M : retour menu config",
            "R : relancer une partie",
            "H : afficher/masquer cette aide",
        ]
        y = 330
        for l in lines:
            self.draw_text_center(l, self.font_text, TEXT_MUTED, y)
            y += 46

    def draw_home(self):
        self.ecran.fill(BG)
        self.draw_panel(260, 80, 680, 600)
        self.draw_text_center("Nim", self.font_title, TEXT, 170)
        self.draw_text_center("Interface moderne • Lisible • Rapide", self.font_text, TEXT_MUTED, 220)

        pos = pygame.mouse.get_pos()
        self.btn_play.dessiner(self.ecran, self.font_h2, self.btn_play.rect.collidepoint(pos))
        self.btn_stats.dessiner(self.ecran, self.font_h2, self.btn_stats.rect.collidepoint(pos))
        self.btn_quit.dessiner(self.ecran, self.font_h2, self.btn_quit.rect.collidepoint(pos))

    def draw_config(self):
        self.sync_selected_buttons()

        self.ecran.fill(BG)
        self.draw_text_center("Configuration", self.font_h1, TEXT, 62)

        # 3 colonnes pour limiter la densité
        self.draw_panel(60, 140, 360, 470)
        self.draw_panel(430, 140, 340, 470)
        self.draw_panel(780, 140, 360, 470)

        self.ecran.blit(self.font_h2.render("Mode", True, TEXT), (90, 160))
        self.ecran.blit(self.font_h2.render("Règles", True, TEXT), (460, 160))
        self.ecran.blit(self.font_h2.render("IA", True, TEXT), (810, 160))

        pos = pygame.mouse.get_pos()

        self.btn_mode_hvh.dessiner(self.ecran, self.font_text, self.btn_mode_hvh.rect.collidepoint(pos))
        self.btn_mode_hvai.dessiner(self.ecran, self.font_text, self.btn_mode_hvai.rect.collidepoint(pos))
        self.btn_mode_iavai.dessiner(self.ecran, self.font_text, self.btn_mode_iavai.rect.collidepoint(pos))

        self.btn_regle2.dessiner(self.ecran, self.font_text, self.btn_regle2.rect.collidepoint(pos))
        self.btn_regle3.dessiner(self.ecran, self.font_text, self.btn_regle3.rect.collidepoint(pos))

        self.btn_diff_easy.enabled = self.mode_jeu in ("hvai", "iavai")
        self.btn_diff_med.enabled = self.mode_jeu in ("hvai", "iavai")
        self.btn_diff_hard.enabled = self.mode_jeu in ("hvai", "iavai")
        self.btn_diff_easy.dessiner(self.ecran, self.font_text, self.btn_diff_easy.rect.collidepoint(pos))
        self.btn_diff_med.dessiner(self.ecran, self.font_text, self.btn_diff_med.rect.collidepoint(pos))
        self.btn_diff_hard.dessiner(self.ecran, self.font_text, self.btn_diff_hard.rect.collidepoint(pos))

        info_lines = [
            f"Mode actuel: {self.mode_label()}",
            f"Règle: prendre 1..{self.max_retrait}",
            f"Difficulté IA: {self.difficulte} ({self.nb_parties_entrainement})",
        ]
        y = 430
        for line in info_lines:
            self.ecran.blit(self.font_small.render(line, True, TEXT_MUTED), (90, y))
            y += 30

        self.ecran.blit(self.font_text.render("Bâtons initiaux", True, TEXT), (488, 430))
        self.btn_stick_minus.dessiner(self.ecran, self.font_h2, self.btn_stick_minus.rect.collidepoint(pos))
        self.btn_stick_plus.dessiner(self.ecran, self.font_h2, self.btn_stick_plus.rect.collidepoint(pos))
        self.draw_panel(566, 458, 70, 52, alt=True)
        self.draw_text_center(str(self.nb_batons_init), self.font_text, TEXT, 485)

        self.btn_ia_starts.enabled = self.mode_jeu == "hvai"
        self.btn_ia_starts.texte = "IA commence: Oui" if self.ia_commence else "IA commence: Non"
        self.btn_ia_starts.dessiner(self.ecran, self.font_small, self.btn_ia_starts.rect.collidepoint(pos))

        self.btn_back.dessiner(self.ecran, self.font_text, self.btn_back.rect.collidepoint(pos))
        self.btn_start.dessiner(self.ecran, self.font_text, self.btn_start.rect.collidepoint(pos))

    def draw_training(self):
        self.ecran.fill(BG)
        self.draw_panel(250, 220, 700, 280)
        self.draw_text_center("Entraînement IA en cours...", self.font_h1, TEXT, 295)
        self.draw_text_center(
            f"{self.difficulte} ({self.training_done}/{self.training_total})", self.font_text, TEXT_MUTED, 340
        )

        # barre progression
        ratio = 0 if self.training_total == 0 else self.training_done / self.training_total
        bx, by, bw, bh = 330, 390, 540, 28
        pygame.draw.rect(self.ecran, PANEL_ALT, (bx, by, bw, bh), border_radius=12)
        pygame.draw.rect(self.ecran, PRIMARY_SELECTED, (bx, by, int(bw * ratio), bh), border_radius=12)

    def draw_game(self):
        self.ecran.fill(BG)
        self.draw_panel(20, 20, 1160, 720)

        pos = pygame.mouse.get_pos()
        self.btn_game_menu.dessiner(self.ecran, self.font_small, self.btn_game_menu.rect.collidepoint(pos))

        if self.mode_jeu == "hvai":
            tour_txt = "Tour de l'IA" if self.etat.joueur_courant == 2 else "Tour de l'humain"
            tour_color = PRIMARY if self.etat.joueur_courant == 2 else PRIMARY_SELECTED
        elif self.mode_jeu == "iavai":
            tour_txt = f"Tour IA {self.etat.joueur_courant}"
            tour_color = PRIMARY
        else:
            tour_txt = f"Tour Joueur {self.etat.joueur_courant}"
            tour_color = PRIMARY_SELECTED if self.etat.joueur_courant == 1 else DANGER

        self.draw_text_center(tour_txt, self.font_h1, tour_color, 72)
        self.draw_text_center(f"Bâtons restants: {self.etat.nb_batons}", self.font_text, TEXT, 112)

        # Zone bâtons
        zone_x, zone_y, zone_w = 120, 160, 760
        cols = 20
        step = max(1, zone_w // cols)
        nb_aff = int(math.ceil(self.sticks_affiches))

        for i in range(nb_aff):
            c = i % cols
            r = i // cols
            x = zone_x + c * step
            y = zone_y + r * 90
            pygame.draw.rect(self.ecran, STICK_COLOR, (x, y, 12, 72), border_radius=4)

        # panneau infos réduit
        self.draw_panel(920, 160, 230, 250, alt=True)
        info = [
            f"Mode: {self.mode_label()}",
            f"Règle: 1..{self.max_retrait}",
            "H: aide  M: menu",
            "R: relancer",
        ]
        y = 190
        for line in info:
            self.ecran.blit(self.font_small.render(line, True, TEXT_MUTED), (940, y))
            y += 36

        valid = self.etat.coups_valides()
        self.btn_take1.enabled = 1 in valid
        self.btn_take2.enabled = 2 in valid
        self.btn_take3.enabled = 3 in valid and self.max_retrait >= 3

        if (self.mode_jeu == "hvai" and self.etat.joueur_courant == 2) or self.mode_jeu == "iavai":
            self.btn_take1.enabled = False
            self.btn_take2.enabled = False
            self.btn_take3.enabled = False

        self.btn_take1.dessiner(self.ecran, self.font_text, self.btn_take1.rect.collidepoint(pos))
        self.btn_take2.dessiner(self.ecran, self.font_text, self.btn_take2.rect.collidepoint(pos))
        self.btn_take3.dessiner(self.ecran, self.font_text, self.btn_take3.rect.collidepoint(pos))

        self.draw_help_overlay()

    def draw_end(self):
        self.ecran.fill(BG)
        self.draw_panel(220, 120, 760, 520)
        self.draw_text_center("Fin de partie", self.font_title, TEXT, 220)

        if self.mode_jeu == "hvai":
            winner = "Humain" if self.etat.gagnant == 1 else "IA"
        elif self.mode_jeu == "iavai":
            winner = f"IA {self.etat.gagnant}"
        else:
            winner = f"Joueur {self.etat.gagnant}"

        self.draw_text_center(f"Victoire: {winner}", self.font_h1, TEXT, 320)
        self.draw_text_center(f"Parties session: {self.stats['parties']}", self.font_text, TEXT_MUTED, 370)

        pos = pygame.mouse.get_pos()
        self.btn_replay.dessiner(self.ecran, self.font_text, self.btn_replay.rect.collidepoint(pos))
        self.btn_reconfig.dessiner(self.ecran, self.font_text, self.btn_reconfig.rect.collidepoint(pos))

    def draw_stats(self):
        self.ecran.fill(BG)
        self.draw_panel(180, 80, 840, 600)
        self.draw_text_center("Statistiques", self.font_title, TEXT, 170)

        lines = [
            f"Parties jouées: {self.stats['parties']}",
            f"HvH -> J1: {self.stats['hvh_j1']} | J2: {self.stats['hvh_j2']}",
            f"HvIA -> Humain: {self.stats['hvai_humain']} | IA: {self.stats['hvai_ia']}",
            f"IAvIA -> IA1: {self.stats['iavai_ia1']} | IA2: {self.stats['iavai_ia2']}",
        ]

        y = 280
        for line in lines:
            self.draw_text_center(line, self.font_text, TEXT_MUTED, y)
            y += 58

        pos = pygame.mouse.get_pos()
        self.btn_stats_back.dessiner(self.ecran, self.font_text, self.btn_stats_back.rect.collidepoint(pos))
        self.btn_stats_reset.dessiner(self.ecran, self.font_text, self.btn_stats_reset.rect.collidepoint(pos))

    # -------------------------------------------------
    # Gestion événements
    # -------------------------------------------------
    def handle_click_home(self, pos):
        if self.btn_play.est_clique(pos):
            self.switch_scene("config")
        elif self.btn_stats.est_clique(pos):
            self.switch_scene("stats")
        elif self.btn_quit.est_clique(pos):
            return False
        return True

    def handle_click_config(self, pos):
        if self.btn_mode_hvh.est_clique(pos):
            self.mode_jeu = "hvh"
        elif self.btn_mode_hvai.est_clique(pos):
            self.mode_jeu = "hvai"
        elif self.btn_mode_iavai.est_clique(pos):
            self.mode_jeu = "iavai"

        elif self.btn_regle2.est_clique(pos):
            self.max_retrait = 2
        elif self.btn_regle3.est_clique(pos):
            self.max_retrait = 3

        elif self.btn_diff_easy.est_clique(pos):
            self.maj_difficulte("facile")
        elif self.btn_diff_med.est_clique(pos):
            self.maj_difficulte("moyen")
        elif self.btn_diff_hard.est_clique(pos):
            self.maj_difficulte("difficile")

        elif self.btn_stick_minus.est_clique(pos):
            self.nb_batons_init = max(5, self.nb_batons_init - 1)
        elif self.btn_stick_plus.est_clique(pos):
            self.nb_batons_init = min(120, self.nb_batons_init + 1)

        elif self.btn_ia_starts.est_clique(pos):
            self.ia_commence = not self.ia_commence

        elif self.btn_back.est_clique(pos):
            self.switch_scene("home")
        elif self.btn_start.est_clique(pos):
            self.lancer_depuis_config()

    def handle_click_game(self, pos):
        if self.btn_game_menu.est_clique(pos):
            self.switch_scene("config")
            return

        if self.btn_take1.est_clique(pos):
            self.jouer_coup(1)
        elif self.btn_take2.est_clique(pos):
            self.jouer_coup(2)
        elif self.btn_take3.est_clique(pos):
            self.jouer_coup(3)

    def handle_click_end(self, pos):
        if self.btn_replay.est_clique(pos):
            self.demarrer_partie()
        elif self.btn_reconfig.est_clique(pos):
            self.switch_scene("config")

    def handle_click_stats(self, pos):
        if self.btn_stats_back.est_clique(pos):
            self.switch_scene("home")
        elif self.btn_stats_reset.est_clique(pos):
            self.reset_stats()

    def handle_shortcuts(self, event):
        if event.key == pygame.K_h:
            self.show_help = not self.show_help
            return

        if event.key == pygame.K_m:
            self.switch_scene("config")
            return

        if event.key == pygame.K_r and self.scene in ("game", "end"):
            self.demarrer_partie()
            return

        if self.scene != "game":
            return

        if event.key == pygame.K_1:
            self.jouer_coup(1)
        elif event.key == pygame.K_2:
            self.jouer_coup(2)
        elif event.key == pygame.K_3:
            self.jouer_coup(3)

    # -------------------------------------------------
    # Boucle principale
    # -------------------------------------------------
    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    self.handle_shortcuts(event)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.scene == "home":
                        running = self.handle_click_home(event.pos)
                    elif self.scene == "config":
                        self.handle_click_config(event.pos)
                    elif self.scene == "game":
                        self.handle_click_game(event.pos)
                    elif self.scene == "end":
                        self.handle_click_end(event.pos)
                    elif self.scene == "stats":
                        self.handle_click_stats(event.pos)

            self.update_training()
            self.update_ai()
            self.update_animations()

            if self.scene == "home":
                self.draw_home()
            elif self.scene == "config":
                self.draw_config()
            elif self.scene == "training":
                self.draw_training()
            elif self.scene == "game":
                self.draw_game()
            elif self.scene == "end":
                self.draw_end()
            elif self.scene == "stats":
                self.draw_stats()

            self.draw_scene_fade()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    jeu = JeuNim()
    jeu.run()


if __name__ == "__main__":
    main()
