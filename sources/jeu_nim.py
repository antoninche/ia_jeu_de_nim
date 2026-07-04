"""Jeu de Nim « des bonbons » — version complète et colorée pour enfants.

Règle : sur la table il y a des bonbons. Chacun son tour, on en prend 1, 2
(ou 3). Celui qui prend le DERNIER bonbon gagne !

Modes : Toi vs Toi, Toi vs Robot, Robot vs Robot.
Le Robot est une IA qui a appris toute seule (voir la scène « Comment le
robot apprend ? »).

Lancement :  python jeu_nim.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pygame

import theme as T
import widgets as W
from widgets import Bouton
from game_logic import EtatPartie
from ia import Joueur, creer_liste_cases, entrainer_ia
from explication_ia import ExplicationIA
from ecole_nim import EcoleNim

LARGEUR = 1200
HAUTEUR = 760
FPS = 60

NB_PARTIES = {"facile": 400, "moyen": 3000, "difficile": 12000}
DELAI_IA_MS = 650
FICHIER_STATS = "stats_nim.json"


class JeuNim:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Nim — Le jeu des bonbons")
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        self.clock = pygame.time.Clock()
        self.fonts = T.Fonts()
        self.fond = T.make_background(LARGEUR, HAUTEUR)

        self.scene = "accueil"

        # Paramètres de partie
        self.mode = "hvai"            # hvh | hvai | iavai
        self.max_retrait = 2
        self.nb_bonbons = 12
        self.difficulte = "moyen"
        self.ia_commence = False
        self.indice = False

        # Moteur
        self.etat = EtatPartie(self.nb_bonbons, self.max_retrait)
        self.bonbons_affiches = float(self.nb_bonbons)

        # IA
        self.cases_ia = None
        self.joueur_ia = Joueur("Robot")
        self.next_ai = 0

        # Entraînement non bloquant
        self.train_total = 0
        self.train_done = 0
        self.train_batch = 250

        # Effets
        self.confetti = W.Confetti(LARGEUR, HAUTEUR)
        self.t = 0.0

        # Stats
        self.stats = {"parties": 0, "hvh_j1": 0, "hvh_j2": 0,
                      "hvai_humain": 0, "hvai_ia": 0, "iavai_ia1": 0, "iavai_ia2": 0}
        self._charger_stats()

        # Scènes éducatives
        self.explication = ExplicationIA(self.fonts)
        self.ecole = EcoleNim(self.fonts)

        self._build_ui()

    # ------------------------------------------------------------------
    # Construction des boutons
    # ------------------------------------------------------------------
    def _build_ui(self):
        cx = LARGEUR // 2

        # Accueil
        self.btn_jouer = Bouton(0, 356, 380, 58, "Jouer", "primary").centre_x(cx)
        self.btn_ecole = Bouton(0, 420, 380, 58, "Apprends à gagner", "success").centre_x(cx)
        self.btn_apprendre = Bouton(0, 484, 380, 58, "Comment le robot apprend ?", "info").centre_x(cx)
        self.btn_stats = Bouton(0, 548, 380, 58, "Statistiques", "neutral").centre_x(cx)
        self.btn_quitter = Bouton(0, 612, 380, 58, "Quitter", "danger").centre_x(cx)

        # Config — colonne gauche (centre 372) / droite (centre 828)
        gx, dx = 372, 828
        self.btn_hvh = Bouton(0, 196, 250, 54, "Toi vs Toi", "primary").centre_x(gx)
        self.btn_hvai = Bouton(0, 258, 250, 54, "Toi vs Robot", "primary").centre_x(gx)
        self.btn_iavai = Bouton(0, 320, 250, 54, "Robot vs Robot", "primary").centre_x(gx)
        self.btn_start_moi = Bouton(0, 452, 160, 50, "Toi", "primary").centre_x(gx - 90)
        self.btn_start_ia = Bouton(0, 452, 160, 50, "Robot", "primary").centre_x(gx + 90)

        self.btn_regle2 = Bouton(0, 196, 250, 54, "1 ou 2", "primary").centre_x(dx)
        self.btn_regle3 = Bouton(0, 258, 250, 54, "1, 2 ou 3", "primary").centre_x(dx)
        self.btn_facile = Bouton(0, 378, 140, 50, "Facile", "primary").centre_x(dx - 150)
        self.btn_moyen = Bouton(0, 378, 140, 50, "Moyen", "primary").centre_x(dx)
        self.btn_malin = Bouton(0, 378, 140, 50, "Malin", "primary").centre_x(dx + 150)
        self.stepper = W.Stepper(dx, 512, self.nb_bonbons, 3, 25)

        self.btn_config_retour = Bouton(0, 690, 220, 56, "Menu", "neutral").centre_x(430)
        self.btn_config_start = Bouton(0, 690, 260, 56, "C'est parti !", "success").centre_x(770)

        # Jeu
        self.btn_menu = Bouton(30, 28, 140, 50, "Menu", "neutral")
        self.btn_indice = Bouton(LARGEUR - 220, 28, 190, 50, "Indice : non", "neutral")
        self.btn_prendre1 = Bouton(0, 664, 180, 62, "Prends 1", "primary").centre_x(cx - 200)
        self.btn_prendre2 = Bouton(0, 664, 180, 62, "Prends 2", "primary").centre_x(cx)
        self.btn_prendre3 = Bouton(0, 664, 180, 62, "Prends 3", "primary").centre_x(cx + 200)

        # Fin
        self.btn_rejouer = Bouton(0, 560, 220, 60, "Rejouer", "success").centre_x(cx - 250)
        self.btn_fin_config = Bouton(0, 560, 220, 60, "Configurer", "primary").centre_x(cx)
        self.btn_fin_menu = Bouton(0, 560, 220, 60, "Menu", "neutral").centre_x(cx + 250)

        # Stats
        self.btn_stats_retour = Bouton(0, 668, 220, 54, "Menu", "neutral").centre_x(cx - 140)
        self.btn_stats_reset = Bouton(0, 668, 240, 54, "Tout remettre à 0", "danger").centre_x(cx + 140)

    # ------------------------------------------------------------------
    # Aides / état
    # ------------------------------------------------------------------
    def switch(self, scene):
        self.scene = scene

    def _mode_label(self):
        return {"hvh": "Toi vs Toi", "hvai": "Toi vs Robot", "iavai": "Robot vs Robot"}[self.mode]

    def _coup_optimal(self):
        """Coup parfait selon la théorie du Nim (0 = position piège)."""
        return self.etat.nb_batons % (self.max_retrait + 1)

    def _c_est_le_tour_ia(self):
        if self.mode == "iavai":
            return True
        if self.mode == "hvai" and self.etat.joueur_courant == 2:
            return True
        return False

    # ------------------------------------------------------------------
    # Cycle de partie
    # ------------------------------------------------------------------
    def demarrer_partie(self):
        self.etat = EtatPartie(self.nb_bonbons, self.max_retrait)
        self.bonbons_affiches = float(self.nb_bonbons)
        self.switch("jeu")

        if self.mode == "hvai" and self.ia_commence:
            self.etat.joueur_courant = 2
        if self._c_est_le_tour_ia():
            self.next_ai = pygame.time.get_ticks() + DELAI_IA_MS

    def lancer_depuis_config(self):
        self.nb_bonbons = self.stepper.valeur
        if self.mode in ("hvai", "iavai"):
            self.cases_ia = creer_liste_cases(self.nb_bonbons, self.max_retrait)
            self.train_total = NB_PARTIES[self.difficulte]
            self.train_done = 0
            self.switch("entrainement")
        else:
            self.demarrer_partie()

    def update_entrainement(self):
        if self.scene != "entrainement":
            return
        if self.train_done >= self.train_total:
            self.demarrer_partie()
            return
        lot = min(self.train_batch, self.train_total - self.train_done)
        entrainer_ia(self.cases_ia, lot)
        self.train_done += lot

    def jouer_coup(self, retrait):
        if self.scene != "jeu":
            return
        if not self.etat.jouer_coup(retrait):
            return

        if self.etat.gagnant is not None:
            self._enregistrer_fin()
            self.confetti.burst()
            self.switch("fin")
            return

        if self._c_est_le_tour_ia():
            self.next_ai = pygame.time.get_ticks() + DELAI_IA_MS

    def update_ia(self):
        if self.scene != "jeu" or not self._c_est_le_tour_ia():
            return
        if pygame.time.get_ticks() < self.next_ai:
            return
        action = self.joueur_ia.tire_une_boule(self.cases_ia[self.etat.nb_batons])
        self.jouer_coup(action)

    def update_anim(self):
        cible = float(self.etat.nb_batons)
        if abs(self.bonbons_affiches - cible) < 0.03:
            self.bonbons_affiches = cible
        else:
            self.bonbons_affiches += (cible - self.bonbons_affiches) * 0.3

    def _enregistrer_fin(self):
        self.stats["parties"] += 1
        g = self.etat.gagnant
        if self.mode == "hvh":
            self.stats["hvh_j1" if g == 1 else "hvh_j2"] += 1
        elif self.mode == "hvai":
            self.stats["hvai_humain" if g == 1 else "hvai_ia"] += 1
        else:
            self.stats["iavai_ia1" if g == 1 else "iavai_ia2"] += 1
        self._sauver_stats()

    # ------------------------------------------------------------------
    # Persistance stats
    # ------------------------------------------------------------------
    def _sauver_stats(self):
        try:
            with open(FICHIER_STATS, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def _charger_stats(self):
        p = Path(FICHIER_STATS)
        if not p.exists():
            return
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        for k in self.stats:
            if isinstance(data.get(k), int):
                self.stats[k] = data[k]

    def _reset_stats(self):
        for k in self.stats:
            self.stats[k] = 0
        self._sauver_stats()

    # ==================================================================
    # DESSIN DES SCÈNES
    # ==================================================================
    def _fond(self):
        self.ecran.blit(self.fond, (0, 0))

    def draw_accueil(self):
        self._fond()
        T.draw_text_center(self.ecran, "N I M", self.fonts.title, T.PRIMARY, LARGEUR // 2, 120)
        T.draw_text_center(self.ecran, "Le jeu des bonbons", self.fonts.h2, T.INK_SOFT, LARGEUR // 2, 182)
        T.draw_text_center(self.ecran, "Prends le dernier bonbon pour gagner !",
                           self.fonts.body, T.INK_SOFT, LARGEUR // 2, 222)
        W.draw_robot(self.ecran, (LARGEUR // 2, 290), 74, mood="happy", t=self.t)

        for b in (self.btn_jouer, self.btn_ecole, self.btn_apprendre, self.btn_stats, self.btn_quitter):
            b.dessiner(self.ecran, self.fonts.h2 if b is self.btn_jouer else self.fonts.body_b)

    def draw_config(self):
        self._fond()
        T.draw_text_center(self.ecran, "Prépare ta partie", self.fonts.h1, T.INK, LARGEUR // 2, 70)

        T.draw_round_rect(self.ecran, (120, 120, 460, 540), T.CARD, radius=22, shadow=True)
        T.draw_round_rect(self.ecran, (620, 120, 460, 540), T.CARD, radius=22, shadow=True)

        # Colonne gauche
        T.draw_text_center(self.ecran, "Qui joue ?", self.fonts.h2, T.INK, 372, 160)
        self.btn_hvh.selected = self.mode == "hvh"
        self.btn_hvai.selected = self.mode == "hvai"
        self.btn_iavai.selected = self.mode == "iavai"
        for b in (self.btn_hvh, self.btn_hvai, self.btn_iavai):
            b.dessiner(self.ecran, self.fonts.body_b)

        T.draw_text_center(self.ecran, "Qui commence ?", self.fonts.h2, T.INK, 372, 415)
        peut_choisir = self.mode == "hvai"
        self.btn_start_moi.enabled = peut_choisir
        self.btn_start_ia.enabled = peut_choisir
        self.btn_start_moi.selected = peut_choisir and not self.ia_commence
        self.btn_start_ia.selected = peut_choisir and self.ia_commence
        self.btn_start_moi.dessiner(self.ecran, self.fonts.body_b)
        self.btn_start_ia.dessiner(self.ecran, self.fonts.body_b)
        if not peut_choisir:
            T.draw_text_center(self.ecran, "(seulement en Toi vs Robot)",
                               self.fonts.small, T.INK_SOFT, 372, 540)

        # Colonne droite
        T.draw_text_center(self.ecran, "On peut prendre…", self.fonts.h2, T.INK, 828, 160)
        self.btn_regle2.selected = self.max_retrait == 2
        self.btn_regle3.selected = self.max_retrait == 3
        self.btn_regle2.dessiner(self.ecran, self.fonts.body_b)
        self.btn_regle3.dessiner(self.ecran, self.fonts.body_b)

        T.draw_text_center(self.ecran, "Niveau du robot", self.fonts.h2, T.INK, 828, 330)
        actif_ia = self.mode in ("hvai", "iavai")
        etoiles = {"facile": 1, "moyen": 2, "difficile": 3}
        for b, niv in ((self.btn_facile, "facile"), (self.btn_moyen, "moyen"), (self.btn_malin, "difficile")):
            b.enabled = actif_ia
            b.selected = actif_ia and self.difficulte == niv
            col_etoile = T.LEMON if actif_ia else T.DISABLED
            W.draw_stars(self.ecran, (b.rect.centerx, 360), etoiles[niv], r=7, color=col_etoile)
            b.dessiner(self.ecran, self.fonts.small)

        T.draw_text_center(self.ecran, "Combien de bonbons ?", self.fonts.h2, T.INK, 828, 470)
        self.stepper.dessiner(self.ecran, self.fonts.h2)

        self.btn_config_retour.dessiner(self.ecran, self.fonts.body_b)
        self.btn_config_start.dessiner(self.ecran, self.fonts.body_b)

    def draw_entrainement(self):
        self._fond()
        W.draw_robot(self.ecran, (LARGEUR // 2, 260), 100, mood="think", t=self.t)
        T.draw_text_center(self.ecran, "Le robot s'entraîne…", self.fonts.h1, T.INK, LARGEUR // 2, 380)
        T.draw_text_center(self.ecran, "Il joue plein de parties pour devenir plus malin.",
                           self.fonts.body, T.INK_SOFT, LARGEUR // 2, 428)

        ratio = 0 if self.train_total == 0 else self.train_done / self.train_total
        bx, by, bw, bh = 300, 480, 600, 30
        T.draw_round_rect(self.ecran, (bx, by, bw, bh), T.CARD, radius=15)
        if ratio > 0:
            T.draw_round_rect(self.ecran, (bx, by, max(bh, int(bw * ratio)), bh), T.SUCCESS, radius=15)
        T.draw_text_center(self.ecran, f"{int(ratio * 100)} %", self.fonts.body_b,
                           T.INK_SOFT, LARGEUR // 2, 540)

    def _positions_bonbons(self, n):
        cols = min(9, max(1, n))
        rows = math.ceil(n / cols) if n else 0
        cell = 84
        total_w = cols * cell
        x0 = LARGEUR // 2 - total_w // 2 + cell // 2
        y0 = 300
        pos = []
        for i in range(n):
            r, c = divmod(i, cols)
            # dernière rangée centrée
            in_row = cols if (r < rows - 1) else (n - cols * (rows - 1))
            offset = (cols - in_row) * cell // 2
            pos.append((x0 + c * cell + offset, y0 + r * cell))
        return pos

    def draw_jeu(self):
        self._fond()
        self.btn_menu.dessiner(self.ecran, self.fonts.small)

        # bandeau « à qui de jouer »
        tour_ia = self._c_est_le_tour_ia()
        if self.mode == "hvh":
            txt = f"Au tour du joueur {self.etat.joueur_courant}"
            couleur = T.SKY if self.etat.joueur_courant == 1 else T.BERRY
        elif self.mode == "hvai":
            txt = "Au robot de jouer…" if tour_ia else "À toi de jouer !"
            couleur = T.GRAPE if tour_ia else T.MINT
        else:
            txt = f"Robot {self.etat.joueur_courant} réfléchit…"
            couleur = T.GRAPE

        pill = pygame.Rect(0, 96, 560, 62)
        pill.centerx = LARGEUR // 2
        T.draw_round_rect(self.ecran, pill, T.CARD, radius=31, shadow=True)
        if tour_ia:
            W.draw_robot(self.ecran, (pill.left + 40, pill.centery), 42, mood="think", t=self.t)
        T.draw_text_center(self.ecran, txt, self.fonts.h2, couleur, pill.centerx + 20, pill.centery)

        T.draw_text_center(self.ecran, f"Bonbons sur la table : {self.etat.nb_batons}",
                           self.fonts.body_b, T.INK_SOFT, LARGEUR // 2, 200)

        # bonbons
        n = int(math.ceil(self.bonbons_affiches - 0.001))
        n = max(self.etat.nb_batons, min(n, self.nb_bonbons))
        for i, (x, y) in enumerate(self._positions_bonbons(n)):
            W.draw_candy(self.ecran, (x, y), 26, T.candy_color(i), wobble=self.t * 2 + i * 0.5)

        # indice pédagogique
        if self.indice and not tour_ia and self.mode != "iavai":
            opt = self._coup_optimal()
            if opt == 0:
                msg = "Position piège : quoi que tu joues, tente ta chance !"
            else:
                msg = f"Astuce : prends {opt} pour jouer parfaitement."
            T.draw_text_center(self.ecran, msg, self.fonts.body, T.GRAPE_DK, LARGEUR // 2, 610)

        # boutons prendre
        valides = self.etat.coups_valides()
        humain = not tour_ia and self.mode != "iavai"
        for b, v in ((self.btn_prendre1, 1), (self.btn_prendre2, 2), (self.btn_prendre3, 3)):
            actif = humain and (v in valides) and (v <= self.max_retrait)
            b.enabled = actif
            b.selected = self.indice and humain and v == self._coup_optimal()
            if v == 3 and self.max_retrait < 3:
                continue
            b.dessiner(self.ecran, self.fonts.body_b)

        self.btn_indice.texte = f"Indice : {'oui' if self.indice else 'non'}"
        self.btn_indice.selected = self.indice
        self.btn_indice.dessiner(self.ecran, self.fonts.small)

    def draw_fin(self):
        self._fond()
        self.confetti.dessiner(self.ecran)

        if self.mode == "hvai":
            humain_gagne = self.etat.gagnant == 1
            titre = "Bravo, tu as gagné !" if humain_gagne else "Le robot a gagné !"
            mood = "sad" if not humain_gagne else "happy"
            sous = "Tu as pris le dernier bonbon." if humain_gagne else "Réessaie, tu peux le battre !"
        elif self.mode == "iavai":
            titre = f"Le robot {self.etat.gagnant} gagne !"
            mood = "happy"
            sous = "Deux robots se sont affrontés."
        else:
            titre = f"Le joueur {self.etat.gagnant} gagne !"
            mood = "happy"
            sous = "Bien joué !"

        carte = pygame.Rect(0, 150, 720, 360)
        carte.centerx = LARGEUR // 2
        T.draw_round_rect(self.ecran, carte, T.CARD, radius=26, shadow=True)
        W.draw_robot(self.ecran, (LARGEUR // 2, 250), 84, mood=mood, t=self.t)
        T.draw_text_center(self.ecran, titre, self.fonts.h1, T.INK, LARGEUR // 2, 360)
        T.draw_text_center(self.ecran, sous, self.fonts.body, T.INK_SOFT, LARGEUR // 2, 410)

        for b in (self.btn_rejouer, self.btn_fin_config, self.btn_fin_menu):
            b.dessiner(self.ecran, self.fonts.body_b)

    def draw_stats(self):
        self._fond()
        T.draw_text_center(self.ecran, "Statistiques", self.fonts.h1, T.INK, LARGEUR // 2, 80)
        T.draw_text_center(self.ecran, f"Parties jouées : {self.stats['parties']}",
                           self.fonts.h2, T.INK_SOFT, LARGEUR // 2, 140)

        lignes = [
            ("Toi vs Toi", [("Joueur 1", self.stats["hvh_j1"], T.SKY),
                            ("Joueur 2", self.stats["hvh_j2"], T.BERRY)]),
            ("Toi vs Robot", [("Toi", self.stats["hvai_humain"], T.MINT),
                              ("Robot", self.stats["hvai_ia"], T.GRAPE)]),
            ("Robot vs Robot", [("Robot 1", self.stats["iavai_ia1"], T.TANGERINE),
                                ("Robot 2", self.stats["iavai_ia2"], T.SKY)]),
        ]
        y = 210
        for titre, items in lignes:
            T.draw_text(self.ecran, titre, self.fonts.body_b, T.INK, (200, y))
            maxi = max(1, max(v for _, v, _ in items))
            by = y + 40
            for nom, val, col in items:
                T.draw_text(self.ecran, nom, self.fonts.small, T.INK_SOFT, (200, by))
                barre_x, barre_w = 360, 520
                T.draw_round_rect(self.ecran, (barre_x, by, barre_w, 26), T.CARD, radius=13)
                largeur = int(barre_w * val / maxi)
                if largeur > 0:
                    T.draw_round_rect(self.ecran, (barre_x, by, max(26, largeur), 26), col, radius=13)
                T.draw_text(self.ecran, str(val), self.fonts.small, T.INK, (barre_x + barre_w + 16, by))
                by += 36
            y += 150

        self.btn_stats_retour.dessiner(self.ecran, self.fonts.body_b)
        self.btn_stats_reset.dessiner(self.ecran, self.fonts.body_b)

    # ==================================================================
    # ÉVÉNEMENTS
    # ==================================================================
    def click_accueil(self, pos):
        if self.btn_jouer.est_clique(pos):
            self.switch("config")
        elif self.btn_ecole.est_clique(pos):
            self.switch("ecole")
        elif self.btn_apprendre.est_clique(pos):
            self.switch("explication")
        elif self.btn_stats.est_clique(pos):
            self.switch("stats")
        elif self.btn_quitter.est_clique(pos):
            return False
        return True

    def click_config(self, pos):
        if self.btn_hvh.est_clique(pos):
            self.mode = "hvh"
        elif self.btn_hvai.est_clique(pos):
            self.mode = "hvai"
        elif self.btn_iavai.est_clique(pos):
            self.mode = "iavai"
        elif self.btn_regle2.est_clique(pos):
            self.max_retrait = 2
        elif self.btn_regle3.est_clique(pos):
            self.max_retrait = 3
        elif self.btn_facile.est_clique(pos):
            self.difficulte = "facile"
        elif self.btn_moyen.est_clique(pos):
            self.difficulte = "moyen"
        elif self.btn_malin.est_clique(pos):
            self.difficulte = "difficile"
        elif self.btn_start_moi.est_clique(pos):
            self.ia_commence = False
        elif self.btn_start_ia.est_clique(pos):
            self.ia_commence = True
        elif self.stepper.handle_click(pos):
            pass
        elif self.btn_config_retour.est_clique(pos):
            self.switch("accueil")
        elif self.btn_config_start.est_clique(pos):
            self.lancer_depuis_config()

    def click_jeu(self, pos):
        if self.btn_menu.est_clique(pos):
            self.switch("config")
        elif self.btn_indice.est_clique(pos):
            self.indice = not self.indice
        elif self.btn_prendre1.est_clique(pos):
            self.jouer_coup(1)
        elif self.btn_prendre2.est_clique(pos):
            self.jouer_coup(2)
        elif self.btn_prendre3.est_clique(pos):
            self.jouer_coup(3)

    def click_fin(self, pos):
        if self.btn_rejouer.est_clique(pos):
            self.demarrer_partie()
        elif self.btn_fin_config.est_clique(pos):
            self.switch("config")
        elif self.btn_fin_menu.est_clique(pos):
            self.switch("accueil")

    def click_stats(self, pos):
        if self.btn_stats_retour.est_clique(pos):
            self.switch("accueil")
        elif self.btn_stats_reset.est_clique(pos):
            self._reset_stats()

    def raccourcis(self, event):
        if event.key == pygame.K_ESCAPE:
            self.switch("accueil" if self.scene != "accueil" else self.scene)
        if self.scene == "jeu":
            if event.key == pygame.K_1:
                self.jouer_coup(1)
            elif event.key == pygame.K_2:
                self.jouer_coup(2)
            elif event.key == pygame.K_3:
                self.jouer_coup(3)
            elif event.key == pygame.K_i:
                self.indice = not self.indice

    # ==================================================================
    # BOUCLE PRINCIPALE
    # ==================================================================
    def _update_hover(self, pos):
        groupes = {
            "accueil": [self.btn_jouer, self.btn_ecole, self.btn_apprendre, self.btn_stats, self.btn_quitter],
            "config": [self.btn_hvh, self.btn_hvai, self.btn_iavai, self.btn_start_moi,
                       self.btn_start_ia, self.btn_regle2, self.btn_regle3, self.btn_facile,
                       self.btn_moyen, self.btn_malin, self.btn_config_retour, self.btn_config_start],
            "jeu": [self.btn_menu, self.btn_indice, self.btn_prendre1, self.btn_prendre2, self.btn_prendre3],
            "fin": [self.btn_rejouer, self.btn_fin_config, self.btn_fin_menu],
            "stats": [self.btn_stats_retour, self.btn_stats_reset],
        }
        for b in groupes.get(self.scene, []):
            b.update(pos)
        if self.scene == "config":
            self.stepper.update(pos)

    def run(self):
        running = True
        while running:
            now = pygame.time.get_ticks()
            pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.raccourcis(event)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.scene == "accueil":
                        running = self.click_accueil(event.pos)
                    elif self.scene == "config":
                        self.click_config(event.pos)
                    elif self.scene == "jeu":
                        self.click_jeu(event.pos)
                    elif self.scene == "fin":
                        self.click_fin(event.pos)
                    elif self.scene == "stats":
                        self.click_stats(event.pos)
                    elif self.scene == "explication":
                        if self.explication.handle_click(event.pos, now) == "menu":
                            self.switch("accueil")
                    elif self.scene == "ecole":
                        res = self.ecole.handle_click(event.pos)
                        if res == "menu":
                            self.switch("accueil")
                        elif res == "jouer":
                            self.mode = "hvai"
                            self.switch("config")

            self.t = now / 1000.0
            self._update_hover(pos)
            self.update_entrainement()
            self.update_ia()
            self.update_anim()
            self.confetti.update()
            if self.scene == "explication":
                self.explication.update_boutons(pos)
                self.explication.update(now)
            elif self.scene == "ecole":
                self.ecole.update_boutons(pos)

            if self.scene == "accueil":
                self.draw_accueil()
            elif self.scene == "config":
                self.draw_config()
            elif self.scene == "entrainement":
                self.draw_entrainement()
            elif self.scene == "jeu":
                self.draw_jeu()
            elif self.scene == "fin":
                self.draw_fin()
            elif self.scene == "stats":
                self.draw_stats()
            elif self.scene == "explication":
                self._fond()
                self.explication.dessiner(self.ecran, now, pos)
            elif self.scene == "ecole":
                self._fond()
                self.ecole.dessiner(self.ecran, now, pos)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    JeuNim().run()


if __name__ == "__main__":
    main()
