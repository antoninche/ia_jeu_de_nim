"""Scène « École du Nim » — un tutoriel graphique et éducatif.

But : apprendre à l'enfant *le secret mathématique* pour gagner au Nim
(avec la règle « prendre 1 ou 2 ») : il faut toujours laisser à l'adversaire
un nombre de bonbons **multiple de 3**.

La scène enchaîne des leçons animées puis un petit **entraînement noté**
(questions/réponses avec un coach robot), et se termine par un diplôme.
"""

from __future__ import annotations

import pygame

import theme as T
import widgets as W

# Suite de défis : (bonbons restants) -> il faut laisser un multiple de 3.
QUESTIONS = [7, 5, 10, 8, 4]
NB_PAGES = 6  # intro, but, nombre magique, règle d'or, entraînement, diplôme


class EcoleNim:
    def __init__(self, fonts):
        self.f = fonts
        self.page = 0
        # état du quiz
        self.q = 0
        self.repondu = False
        self.bon = False
        self.score = 0
        self._build_ui()

    def reset(self):
        self.page = 0
        self.q = 0
        self.repondu = False
        self.bon = False
        self.score = 0

    def _build_ui(self):
        cx = 600
        self.btn_menu = W.Bouton(40, 30, 150, 52, "Menu", kind="neutral")
        self.btn_prec = W.Bouton(0, 672, 210, 58, "Précédent", kind="neutral").centre_x(cx - 240)
        self.btn_suiv = W.Bouton(0, 672, 210, 58, "Suivant", kind="primary").centre_x(cx + 240)

        # quiz
        self.btn_rep1 = W.Bouton(0, 596, 200, 60, "Prends 1", kind="info").centre_x(cx - 120)
        self.btn_rep2 = W.Bouton(0, 596, 200, 60, "Prends 2", kind="warn").centre_x(cx + 120)
        self.btn_continuer = W.Bouton(0, 672, 240, 58, "Continuer", kind="success").centre_x(cx)

        # diplôme
        self.btn_jouer = W.Bouton(0, 590, 300, 60, "Jouer contre le robot", kind="success").centre_x(cx - 170)
        self.btn_refaire = W.Bouton(0, 590, 210, 60, "Recommencer", kind="neutral").centre_x(cx + 180)

    # ------------------------------------------------------------------
    # Aide stratégie
    # ------------------------------------------------------------------
    @staticmethod
    def bonne_action(n):
        """Coup qui laisse un multiple de 3 (règle prendre 1 ou 2)."""
        return n % 3  # 1 ou 2 quand n n'est pas multiple de 3

    # ------------------------------------------------------------------
    # Événements
    # ------------------------------------------------------------------
    def handle_click(self, pos):
        if self.btn_menu.est_clique(pos):
            return "menu"

        if self.page == 4:
            return self._click_quiz(pos)
        if self.page == 5:
            if self.btn_jouer.est_clique(pos):
                return "jouer"
            if self.btn_refaire.est_clique(pos):
                self.reset()
            if self.btn_menu.est_clique(pos):
                return "menu"
            return None

        # pages d'explication : navigation
        if self.btn_prec.est_clique(pos):
            self.page = max(0, self.page - 1)
        elif self.btn_suiv.est_clique(pos):
            self.page = min(NB_PAGES - 1, self.page + 1)
        return None

    def _click_quiz(self, pos):
        if not self.repondu:
            choix = None
            if self.btn_rep1.est_clique(pos):
                choix = 1
            elif self.btn_rep2.est_clique(pos):
                choix = 2
            if choix is not None:
                self.repondu = True
                self.bon = (choix == self.bonne_action(QUESTIONS[self.q]))
                if self.bon:
                    self.score += 1
        else:
            if self.btn_continuer.est_clique(pos):
                if self.q < len(QUESTIONS) - 1:
                    self.q += 1
                    self.repondu = False
                    self.bon = False
                else:
                    self.page = 5  # diplôme
        # possibilité de revenir en arrière depuis le quiz
        if self.btn_prec.est_clique(pos) and not self.repondu:
            self.page = 3
        return None

    def update_boutons(self, pos):
        boutons = [self.btn_menu]
        if self.page == 4:
            boutons += [self.btn_prec]
            if self.repondu:
                boutons += [self.btn_continuer]
            else:
                boutons += [self.btn_rep1, self.btn_rep2]
        elif self.page == 5:
            boutons += [self.btn_jouer, self.btn_refaire]
        else:
            boutons += [self.btn_prec, self.btn_suiv]
            self.btn_prec.enabled = self.page > 0
            self.btn_suiv.enabled = self.page < NB_PAGES - 1
        for b in boutons:
            b.update(pos)

    # ------------------------------------------------------------------
    # Dessin
    # ------------------------------------------------------------------
    def dessiner(self, surface, now, pos):
        t = now / 1000.0
        self.btn_menu.dessiner(surface, self.f.small)
        self._points_progression(surface)

        if self.page == 0:
            self._page_intro(surface, t)
        elif self.page == 1:
            self._page_but(surface, t)
        elif self.page == 2:
            self._page_magique(surface, t)
        elif self.page == 3:
            self._page_regle(surface, t)
        elif self.page == 4:
            self._page_quiz(surface, t)
        elif self.page == 5:
            self._page_diplome(surface, t)

        # navigation bas (pages d'explication)
        if self.page < 4:
            self.btn_prec.dessiner(surface, self.f.body_b)
            self.btn_suiv.dessiner(surface, self.f.body_b)

    def _points_progression(self, surface):
        n = NB_PAGES
        cx0 = 600 - (n - 1) * 16
        for i in range(n):
            col = T.PRIMARY if i == self.page else (i < self.page and T.SUCCESS or T.DISABLED)
            pygame.draw.circle(surface, col, (cx0 + i * 32, 110), 7)

    def _bulle(self, surface, x, y, w, h, lignes, font, mascotte_mood="idle", t=0.0):
        """Mascotte + bulle de dialogue avec plusieurs lignes."""
        W.draw_robot(surface, (x - 10, y + h // 2), 76, mood=mascotte_mood, t=t)
        bulle = pygame.Rect(x + 50, y, w, h)
        T.draw_round_rect(surface, bulle, T.CARD, radius=20, shadow=True)
        # petite pointe vers la mascotte
        pygame.draw.polygon(surface, T.CARD, [
            (bulle.left, bulle.centery - 12), (bulle.left, bulle.centery + 12),
            (bulle.left - 16, bulle.centery)])
        ly = y + 22
        for ligne, gras in lignes:
            f = self.f.body_b if gras else self.f.body
            T.draw_text(surface, ligne, f, T.INK, (bulle.left + 26, ly))
            ly += f.get_height() + 6

    # --- Page 0 : intro
    def _page_intro(self, surface, t):
        T.draw_text_center(surface, "L'École du Nim", self.f.title, T.PRIMARY, 600, 175)
        T.draw_text_center(surface, "Apprends le secret pour gagner à tous les coups !",
                           self.f.h2, T.INK_SOFT, 600, 245)
        W.draw_robot(surface, (600, 380), 110, mood="happy", t=t)
        T.draw_text_center(surface, "Suis les leçons avec le robot-professeur,",
                           self.f.body, T.INK, 600, 500)
        T.draw_text_center(surface, "puis relève les défis pour gagner ton diplôme.",
                           self.f.body, T.INK, 600, 534)

    # --- Page 1 : le but
    def _page_but(self, surface, t):
        T.draw_text_center(surface, "Leçon 1 — Le but du jeu", self.f.h1, T.INK, 600, 165)
        self._bulle(surface, 150, 220, 800, 120, [
            ("On enlève 1 ou 2 bonbons chacun son tour.", True),
            ("Celui qui prend le TOUT DERNIER bonbon a gagné !", False),
        ], self.f.body, "happy", t)
        for i in range(6):
            col = T.candy_color(i)
            W.draw_candy(surface, (330 + i * 90, 470), 30, col, wobble=t * 2 + i)
        W.draw_star(surface, (330 + 5 * 90, 405), 16, T.LEMON)
        T.draw_text_center(surface, "Le dernier bonbon est le plus précieux !",
                           self.f.body, T.GRAPE_DK, 600, 545)

    # --- Page 2 : le nombre magique
    def _page_magique(self, surface, t):
        T.draw_text_center(surface, "Leçon 2 — Le nombre magique : 3", self.f.h1, T.INK, 600, 158)
        self._bulle(surface, 150, 205, 800, 118, [
            ("Regarde les nombres PIÈGES : 3, 6, 9, 12…", True),
            ("Ce sont les multiples de 3 (1 + 2 = 3).", False),
        ], self.f.body, "think", t)

        # ligne des nombres 0..12
        y = 430
        x0, ecart = 200, 66
        for n in range(0, 13):
            x = x0 + n * ecart
            piege = (n % 3 == 0)
            col = T.BERRY if piege else T.MINT
            pygame.draw.circle(surface, col, (x, y), 24)
            pygame.draw.circle(surface, T.lighten(col, 0.4), (x - 7, y - 7), 6)
            T.draw_text_center(surface, str(n), self.f.small, T.INK_ON, x, y)
            if piege and n != 0:
                W.draw_star(surface, (x, y - 44), 11, T.BERRY)
        T.draw_text_center(surface, "Cases rouges = pièges à offrir à l'adversaire.",
                           self.f.body, T.INK, 600, 505)
        T.draw_text_center(surface, "S'il prend 1, tu prends 2. S'il prend 2, tu prends 1. Toujours 3 !",
                           self.f.body_b, T.GRAPE_DK, 600, 545)

    # --- Page 3 : la règle d'or
    def _page_regle(self, surface, t):
        T.draw_text_center(surface, "Leçon 3 — La règle d'or", self.f.h1, T.INK, 600, 158)
        self._bulle(surface, 150, 205, 800, 130, [
            ("À TON tour, prends ce qu'il faut pour laisser", True),
            ("un multiple de 3 à ton adversaire.", True),
            ("Exemple : il reste 10, prends 1, tu laisses 9 !", False),
        ], self.f.body, "happy", t)

        # illustration 10 -> 9
        y = 470
        for i in range(10):
            mange = (i == 9)
            col = T.DISABLED if mange else T.candy_color(i)
            W.draw_candy(surface, (300 + i * 60, y), 22, col, wobble=t * 2 + i)
            if mange:
                W.draw_check(surface, (300 + i * 60, y), 16, T.DANGER)
        T.draw_text_center(surface, "Tu prends 1 bonbon, il en reste 9 (un piège !)",
                           self.f.body_b, T.GRAPE_DK, 600, 545)

    # --- Page 4 : entraînement noté
    def _page_quiz(self, surface, t):
        n = QUESTIONS[self.q]
        T.draw_text_center(surface, f"Entraînement — défi {self.q + 1}/{len(QUESTIONS)}",
                           self.f.h1, T.INK, 600, 150)
        # étoiles de score
        for i in range(len(QUESTIONS)):
            col = T.LEMON if i < self.score else T.DISABLED
            W.draw_star(surface, (470 + i * 34, 200), 12, col)

        T.draw_text_center(surface, f"Il reste {n} bonbons. C'est à toi !",
                           self.f.h2, T.INK, 600, 258)

        # bonbons (10 par rangée, centrés)
        cols = min(n, 10)
        start = 600 - (cols - 1) * 26
        for i in range(n):
            r, c = divmod(i, 10)
            W.draw_candy(surface, (start + c * 52, 340 + r * 60), 20,
                         T.candy_color(i), wobble=t * 2 + i)

        if not self.repondu:
            T.draw_text_center(surface, "Combien prends-tu pour piéger l'adversaire ?",
                               self.f.body_b, T.GRAPE_DK, 600, 470)
            self.btn_rep1.dessiner(surface, self.f.body_b)
            self.btn_rep2.dessiner(surface, self.f.body_b)
        else:
            bonne = self.bonne_action(n)
            if self.bon:
                W.draw_robot(surface, (360, 500), 66, mood="happy", t=t)
                T.draw_text_center(surface, "Bravo ! Tu laisses un multiple de 3.",
                                   self.f.h2, T.SUCCESS_DK, 630, 485)
            else:
                W.draw_robot(surface, (360, 500), 66, mood="sad", t=t)
                T.draw_text_center(surface, "Presque ! La bonne réponse :",
                                   self.f.h2, T.DANGER, 640, 478)
            T.draw_text_center(surface, f"prends {bonne}, il reste {n - bonne} (un piège).",
                               self.f.body_b, T.INK, 640, 516)
            self.btn_continuer.dessiner(surface, self.f.body_b)

        self.btn_prec.enabled = not self.repondu
        self.btn_prec.dessiner(surface, self.f.body_b)

    # --- Page 5 : diplôme
    def _page_diplome(self, surface, t):
        carte = pygame.Rect(0, 150, 760, 380)
        carte.centerx = 600
        T.draw_round_rect(surface, carte, T.CARD, radius=26, shadow=True)
        T.draw_text_center(surface, "Diplôme du Nim", self.f.title, T.PRIMARY, 600, 220)
        W.draw_robot(surface, (600, 320), 78, mood="happy", t=t)

        for i in range(len(QUESTIONS)):
            col = T.LEMON if i < self.score else T.DISABLED
            W.draw_star(surface, (470 + i * 34, 415), 15, col)

        if self.score >= 4:
            msg = "Champion(ne) du Nim ! Tu connais le secret."
        elif self.score >= 2:
            msg = "Bien joué ! Encore un peu d'entraînement."
        else:
            msg = "Bon début ! Refais les leçons pour progresser."
        T.draw_text_center(surface, f"Score : {self.score}/{len(QUESTIONS)}",
                           self.f.h2, T.INK, 600, 455)
        T.draw_text_center(surface, msg, self.f.body, T.INK_SOFT, 600, 495)

        self.btn_jouer.dessiner(surface, self.f.body_b)
        self.btn_refaire.dessiner(surface, self.f.body_b)
