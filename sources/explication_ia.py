"""Scène « Comment le robot apprend ? ».

Explique de façon visuelle et interactive la méthode d'apprentissage par
renforcement utilisée dans ia.py (idée des « boîtes d'allumettes et perles »
de Donald Michie / MENACE) :

- une BOÎTE par nombre de bonbons restants ;
- dans chaque boîte, des PERLES de couleur = les choix possibles
  (bleu = prendre 1, orange = prendre 2, vert = prendre 3) ;
- pour jouer, le robot pioche une perle au hasard dans la bonne boîte ;
- s'il GAGNE, on rajoute des perles des choix joués (récompense) ;
- s'il PERD, on enlève des perles des choix joués (punition).

Après beaucoup de parties, les bonnes perles deviennent majoritaires :
le robot « sait » jouer sans avoir de cerveau.
"""

from __future__ import annotations

import math

import pygame

import theme as T
import widgets as W
from ia import Case

# Petit modèle volontairement réduit pour rester lisible à l'écran.
NB_BONBONS = 7
MAX_RETRAIT = 2
PERLES_INIT = 4          # peu de perles au départ => apprentissage visible
PERLES_MIN = 1           # on ne vide jamais une boîte (garde l'affichage propre)
PERLES_MAX_AFF = 8       # perles dessinées au maximum par couleur


class ExplicationIA:
    """Petit « laboratoire » animé, piloté par la boucle principale."""

    def __init__(self, fonts):
        self.f = fonts
        self.cases = self._modele_neuf()
        self.parties = 0

        # séquenceur de la partie au ralenti
        self.phase = "idle"          # idle | jouer | apprendre | fini
        self.moves = []              # [(etat, action, joueur)]
        self.gagnant = None
        self.idx = 0
        self.apprentissage = []      # [(etat, action, +1/-1)]
        self.prochain_pas = 0
        self.table = NB_BONBONS      # bonbons restants pendant la démo
        self.highlight = None        # boîte mise en avant
        self.flash = {}              # etat -> (couleur, fin_ms)
        self.narration = "Appuie sur « Une partie au ralenti » pour voir le robot jouer."

        self._build_ui()

    # ------------------------------------------------------------------
    # Modèle
    # ------------------------------------------------------------------
    def _modele_neuf(self):
        cases = [Case(0, MAX_RETRAIT, poids={a: 0 for a in range(1, MAX_RETRAIT + 1)})]
        for n in range(1, NB_BONBONS + 1):
            poids = {a: (PERLES_INIT if a <= n else 0) for a in range(1, MAX_RETRAIT + 1)}
            cases.append(Case(n, MAX_RETRAIT, poids=poids))
        return cases

    def reset(self):
        self.cases = self._modele_neuf()
        self.parties = 0
        self.phase = "idle"
        self.moves = []
        self.highlight = None
        self.flash = {}
        self.table = NB_BONBONS
        self.narration = "Mémoire effacée : le robot ne sait plus rien. Fais-le rejouer !"

    def _build_ui(self):
        y = 664
        self.btn_retour = W.Bouton(40, 30, 150, 52, "Menu", kind="neutral")
        self.btn_slow = W.Bouton(150, y, 300, 60, "Une partie au ralenti", kind="primary")
        self.btn_fast = W.Bouton(470, y, 250, 60, "Rejoue vite x50", kind="success")
        self.btn_reset = W.Bouton(740, y, 260, 60, "Efface la mémoire", kind="danger")

    # ------------------------------------------------------------------
    # Logique d'apprentissage (miroir de ia.py, avec plancher à 1 perle)
    # ------------------------------------------------------------------
    def _simuler_partie(self):
        etat = NB_BONBONS
        joueur = 1
        moves = []
        while etat != 0:
            action = self.cases[etat].tirage_pondere()
            moves.append((etat, action, joueur))
            etat -= action
            joueur = 2 if joueur == 1 else 1
        gagnant = moves[-1][2]
        return moves, gagnant

    def _preparer_apprentissage(self):
        appr = []
        for etat, action, joueur in self.moves:
            appr.append((etat, action, +1 if joueur == self.gagnant else -1))
        return appr

    def _appliquer(self, etat, action, delta):
        case = self.cases[etat]
        if delta > 0:
            case.ajouter_boule(action)
        else:
            if case.poids_actions.get(action, 0) > PERLES_MIN:
                case.supprimer_boule(action)

    def _entrainer_vite(self, n):
        for _ in range(n):
            moves, gagnant = self._simuler_partie()
            for etat, action, joueur in moves:
                self._appliquer(etat, action, +1 if joueur == gagnant else -1)
            self.parties += 1

    # ------------------------------------------------------------------
    # Démo au ralenti (machine à états pilotée par le temps)
    # ------------------------------------------------------------------
    def lancer_slow(self, now):
        self.moves, self.gagnant = self._simuler_partie()
        self.apprentissage = self._preparer_apprentissage()
        self.idx = 0
        self.table = NB_BONBONS
        self.phase = "jouer"
        self.prochain_pas = now + 300
        self.flash = {}
        self.highlight = None
        self.narration = "Le robot joue une partie contre lui-même…"

    def update(self, now):
        # nettoyage des flashs expirés
        self.flash = {k: v for k, v in self.flash.items() if v[1] > now}

        if self.phase == "jouer" and now >= self.prochain_pas:
            if self.idx < len(self.moves):
                etat, action, joueur = self.moves[self.idx]
                self.highlight = etat
                self.table = etat - action
                self.narration = (
                    f"Boîte {etat} : le robot pioche une perle "
                    f"{self._nom_couleur(action)}, il prend {action}."
                )
                self.flash[etat] = (T.LEMON, now + 700)
                self.idx += 1
                self.prochain_pas = now + 1150
            else:
                self.highlight = None
                gagne = "le premier" if self.gagnant == 1 else "le second"
                self.narration = f"Fini ! C'est {gagne} robot qui a pris le dernier bonbon."
                self.phase = "apprendre"
                self.idx = 0
                self.prochain_pas = now + 1000

        elif self.phase == "apprendre" and now >= self.prochain_pas:
            if self.idx < len(self.apprentissage):
                etat, action, delta = self.apprentissage[self.idx]
                self._appliquer(etat, action, delta)
                self.highlight = etat
                if delta > 0:
                    self.flash[etat] = (T.SUCCESS, now + 650)
                    self.narration = (
                        f"Bravo : coup gagnant. On AJOUTE une perle "
                        f"{self._nom_couleur(action)} dans la boîte {etat}."
                    )
                else:
                    self.flash[etat] = (T.DANGER, now + 650)
                    self.narration = (
                        f"Raté : coup perdant. On ENLÈVE une perle "
                        f"{self._nom_couleur(action)} de la boîte {etat}."
                    )
                self.idx += 1
                self.prochain_pas = now + 750
            else:
                self.parties += 1
                self.highlight = None
                self.phase = "fini"
                self.narration = ("Le robot a retenu la leçon ! Recommence : les bonnes "
                                  "perles deviennent peu à peu majoritaires.")

    def occupe(self):
        return self.phase in ("jouer", "apprendre")

    @staticmethod
    def _nom_couleur(action):
        return {1: "bleue", 2: "orange", 3: "verte"}.get(action, "bleue")

    # ------------------------------------------------------------------
    # Événements
    # ------------------------------------------------------------------
    def handle_click(self, pos, now):
        if self.btn_retour.est_clique(pos):
            return "menu"
        if self.occupe():
            return None
        if self.btn_slow.est_clique(pos):
            self.lancer_slow(now)
        elif self.btn_fast.est_clique(pos):
            self._entrainer_vite(50)
            self.narration = (f"50 parties jouées d'un coup ! Total : {self.parties}. "
                              "Les coches vertes montrent les boîtes que le robot a apprises.")
        elif self.btn_reset.est_clique(pos):
            self.reset()
        return None

    def update_boutons(self, pos):
        occ = self.occupe()
        self.btn_slow.enabled = not occ
        self.btn_fast.enabled = not occ
        self.btn_reset.enabled = not occ
        for b in (self.btn_retour, self.btn_slow, self.btn_fast, self.btn_reset):
            b.update(pos)

    # ------------------------------------------------------------------
    # Dessin
    # ------------------------------------------------------------------
    def _optimal(self, etat):
        """Coup parfait selon la théorie du Nim (None si position perdante)."""
        modulo = MAX_RETRAIT + 1
        reste = etat % modulo
        return reste if reste != 0 else None

    def dessiner(self, surface, now, souris_pos):
        largeur = surface.get_width()

        # Titre + retour
        self.btn_retour.dessiner(surface, self.f.small)
        T.draw_text_center(surface, "Comment le robot apprend ?", self.f.h1, T.INK, largeur // 2, 55)

        # Bandeau narration
        bandeau = pygame.Rect(120, 92, largeur - 240, 78)
        T.draw_round_rect(surface, bandeau, T.CARD, radius=18, shadow=True)
        W.draw_robot(surface, (bandeau.left + 46, bandeau.centery), 46,
                     mood="think" if self.occupe() else "happy", t=now / 1000)
        self._texte_multi(surface, self.narration, self.f.body, T.INK,
                          bandeau.left + 96, bandeau.top + 14, bandeau.width - 120)

        # Mini-table de bonbons (état courant de la démo)
        self._dessiner_table(surface, 120, 186, largeur - 240, 66)

        # Légende des perles
        self._dessiner_legende(surface, largeur // 2, 276)

        # Rangée de boîtes
        self._dessiner_boites(surface, now)

        # Compteur de parties
        T.draw_text_center(surface, f"Parties d'entraînement : {self.parties}",
                           self.f.body_b, T.INK_SOFT, largeur // 2, 620)

        # Boutons
        self.btn_slow.dessiner(surface, self.f.small)
        self.btn_fast.dessiner(surface, self.f.small)
        self.btn_reset.dessiner(surface, self.f.small)

    def _dessiner_table(self, surface, x, y, w, h):
        rect = pygame.Rect(x, y, w, h)
        T.draw_round_rect(surface, rect, T.CARD_SOFT, radius=16)
        n = max(0, self.table)
        T.draw_text(surface, f"Sur la table : {n}", self.f.small, T.INK_SOFT,
                    (x + 16, y + h // 2 - 10))
        cx = x + 220
        for i in range(n):
            W.draw_candy(surface, (cx + i * 34, y + h // 2), 12, T.candy_color(i))

    def _dessiner_legende(self, surface, cx, y):
        items = [(1, "prendre 1"), (2, "prendre 2")]
        if MAX_RETRAIT >= 3:
            items.append((3, "prendre 3"))
        total_w = len(items) * 200
        start = cx - total_w // 2
        for i, (action, label) in enumerate(items):
            ix = start + i * 200 + 20
            W.draw_bead(surface, (ix, y), 11, T.ACTION_COLORS[action])
            T.draw_text(surface, f"= {label}", self.f.small, T.INK, (ix + 22, y - 12))

    def _dessiner_boites(self, surface, now):
        n = NB_BONBONS
        bw, bh, gap = 118, 176, 14
        total = n * bw + (n - 1) * gap
        x0 = (surface.get_width() - total) // 2
        y0 = 320

        for i in range(1, n + 1):
            case = self.cases[i]
            bx = x0 + (i - 1) * (bw + gap)
            rect = pygame.Rect(bx, y0, bw, bh)

            # flash de fond (récompense/punition/sélection)
            fond = T.CARD
            if i in self.flash:
                fond = T.lighten(self.flash[i][0], 0.55)
            T.draw_round_rect(surface, rect, fond, radius=16, shadow=True)

            # contour mis en avant
            if self.highlight == i:
                pygame.draw.rect(surface, T.LEMON, rect, width=4, border_radius=16)

            # « couvercle » de la boîte
            couv = pygame.Rect(bx, y0, bw, 30)
            T.draw_round_rect(surface, couv, T.darken(fond, 0.06), radius=16)
            T.draw_text_center(surface, f"Boîte {i}", self.f.tiny, T.INK_SOFT,
                               rect.centerx, y0 + 15)

            # perles
            self._dessiner_perles(surface, rect, case)

            # coche « appris »
            opt = self._optimal(i)
            pref = case.action_preferee()
            sous_y = y0 + bh + 16
            if opt is None:
                T.draw_text_center(surface, "piège", self.f.tiny, T.INK_SOFT,
                                   rect.centerx, sous_y)
            elif pref == opt:
                pygame.draw.circle(surface, T.SUCCESS, (rect.centerx, sous_y), 13)
                W.draw_check(surface, (rect.centerx, sous_y), 12, T.INK_ON)

    def _dessiner_perles(self, surface, rect, case):
        # zone intérieure sous le couvercle
        zone = pygame.Rect(rect.x + 8, rect.y + 38, rect.w - 16, rect.h - 48)
        actions = [a for a in range(1, MAX_RETRAIT + 1) if a <= case.nombre_case]
        # une colonne par action
        col_w = zone.w // max(1, len(actions))
        for j, action in enumerate(actions):
            n = case.poids_actions.get(action, 0)
            col = T.ACTION_COLORS.get(action, T.SKY)
            cx = zone.x + col_w * j + col_w // 2
            # compteur numérique
            T.draw_text_center(surface, str(n), self.f.tiny, T.INK,
                               cx, zone.bottom - 6)
            # perles empilées (du bas vers le haut)
            aff = min(n, PERLES_MAX_AFF)
            for k in range(aff):
                by = zone.bottom - 26 - k * 15
                W.draw_bead(surface, (cx, by), 8, col)
            if n > PERLES_MAX_AFF:
                T.draw_text_center(surface, "+", self.f.tiny, T.INK, cx, zone.top + 6)

    def _texte_multi(self, surface, texte, font, color, x, y, largeur_max):
        mots = texte.split(" ")
        ligne = ""
        ly = y
        for mot in mots:
            test = (ligne + " " + mot).strip()
            if font.size(test)[0] > largeur_max and ligne:
                T.draw_text(surface, ligne, font, color, (x, ly))
                ligne = mot
                ly += font.get_height() + 2
            else:
                ligne = test
        if ligne:
            T.draw_text(surface, ligne, font, color, (x, ly))
