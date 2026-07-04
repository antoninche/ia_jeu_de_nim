"""Composants visuels réutilisables : boutons, stepper, confettis,
mascotte robot et dessin de bonbons / perles.

Aucune logique de jeu ici — uniquement de l'affichage animé.
"""

from __future__ import annotations

import math
from random import Random

import pygame

import theme as T


class Bouton:
    """Gros bouton arrondi, coloré et « qui rebondit » au survol.

    kind : "primary" | "success" | "danger" | "neutral"
    """

    COULEURS = {
        "primary": (T.PRIMARY, T.PRIMARY_DK),
        "success": (T.SUCCESS, T.SUCCESS_DK),
        "danger": (T.DANGER, T.DANGER_DK),
        "info": (T.SKY, T.SKY_DK),
        "warn": (T.TANGERINE, T.darken(T.TANGERINE, 0.16)),
        "neutral": ((236, 230, 244), (214, 206, 224)),
    }

    def __init__(self, x, y, w, h, texte, kind="primary", icon=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.texte = texte
        self.kind = kind
        self.icon = icon
        self.enabled = True
        self.selected = False
        self._lift = 0.0  # animation douce de survol

    def centre_x(self, cx):
        self.rect.centerx = cx
        return self

    def update(self, souris_pos):
        cible = 5.0 if (self.enabled and self.rect.collidepoint(souris_pos)) else 0.0
        self._lift += (cible - self._lift) * 0.25

    def dessiner(self, surface, font):
        base, ombre = self.COULEURS.get(self.kind, self.COULEURS["primary"])
        neutre = self.kind == "neutral"

        if not self.enabled:
            base = T.DISABLED
            ombre = T.darken(T.DISABLED, 0.1)
            txt_col = T.DISABLED_INK
        elif self.selected:
            base = T.SUCCESS
            ombre = T.SUCCESS_DK
            txt_col = T.INK_ON
        else:
            txt_col = T.INK if neutre else T.INK_ON

        lift = int(self._lift) if self.enabled else 0
        r = self.rect.move(0, -lift)

        # « socle » 3D : partie basse plus foncée
        socle = r.copy()
        socle.height += 6
        T.draw_round_rect(surface, socle, ombre, radius=r.height // 2)
        top = r.copy()
        T.draw_round_rect(surface, top, base, radius=r.height // 2)

        label = self.texte if not self.icon else f"{self.icon}  {self.texte}"
        T.draw_text_center(surface, label, font, txt_col, top.centerx, top.centery)

    def est_clique(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


class Stepper:
    """Sélecteur numérique - [ valeur ] + arrondi et lisible."""

    def __init__(self, cx, y, valeur, mini, maxi, largeur_val=96):
        self.valeur = valeur
        self.mini = mini
        self.maxi = maxi
        h = 60
        self.moins = Bouton(cx - largeur_val // 2 - 66, y, 60, h, "–", kind="neutral")
        self.plus = Bouton(cx + largeur_val // 2 + 6, y, 60, h, "+", kind="neutral")
        self.val_rect = pygame.Rect(cx - largeur_val // 2, y, largeur_val, h)

    def update(self, pos):
        self.moins.enabled = self.valeur > self.mini
        self.plus.enabled = self.valeur < self.maxi
        self.moins.update(pos)
        self.plus.update(pos)

    def dessiner(self, surface, font):
        T.draw_round_rect(surface, self.val_rect, T.CARD_SOFT, radius=16, shadow=True)
        T.draw_text_center(surface, str(self.valeur), font, T.INK,
                           self.val_rect.centerx, self.val_rect.centery)
        self.moins.dessiner(surface, font)
        self.plus.dessiner(surface, font)

    def handle_click(self, pos) -> bool:
        if self.moins.est_clique(pos):
            self.valeur = max(self.mini, self.valeur - 1)
            return True
        if self.plus.est_clique(pos):
            self.valeur = min(self.maxi, self.valeur + 1)
            return True
        return False


# -------------------------------------------------------------------------
# Bonbons & perles
# -------------------------------------------------------------------------
def draw_candy(surface, center, radius, color, wobble=0.0):
    """Dessine un bonbon rond brillant (avec petit rebond vertical)."""
    cx, cy = center
    cy += int(math.sin(wobble) * 3)

    # ombre au sol
    ombre = pygame.Surface((radius * 2, radius), pygame.SRCALPHA)
    pygame.draw.ellipse(ombre, (60, 40, 80, 55), (0, 0, radius * 2, radius))
    surface.blit(ombre, (cx - radius, cy + radius - 4))

    pygame.draw.circle(surface, T.darken(color, 0.18), (cx, cy), radius)
    pygame.draw.circle(surface, color, (cx, cy), radius - 2)
    # reflet
    pygame.draw.circle(surface, T.lighten(color, 0.45),
                       (cx - radius // 3, cy - radius // 3), max(2, radius // 4))
    pygame.draw.circle(surface, (255, 255, 255),
                       (cx - radius // 3, cy - radius // 3), max(1, radius // 8))


def draw_star(surface, center, r, color):
    """Petite étoile à 5 branches (dessinée, pour éviter les glyphes manquants)."""
    cx, cy = center
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    pygame.draw.polygon(surface, color, pts)


def draw_stars(surface, center, n, r=9, color=T.LEMON):
    """Rangée de n étoiles centrée sur `center`."""
    cx, cy = center
    ecart = r * 2 + 4
    x0 = cx - (n - 1) * ecart / 2
    for i in range(n):
        draw_star(surface, (int(x0 + i * ecart), cy), r, color)


def draw_check(surface, center, r, color):
    """Coche « ✓ » dessinée (glyphe absent de certaines polices)."""
    cx, cy = center
    pygame.draw.lines(surface, color, False,
                      [(cx - r * 0.5, cy), (cx - r * 0.1, cy + r * 0.5),
                       (cx + r * 0.6, cy - r * 0.5)], max(2, r // 3))


def draw_bead(surface, center, radius, color):
    """Petite perle (utilisée dans l'explication de l'IA)."""
    cx, cy = center
    pygame.draw.circle(surface, T.darken(color, 0.2), (cx, cy), radius)
    pygame.draw.circle(surface, color, (cx, cy), radius - 1)
    pygame.draw.circle(surface, T.lighten(color, 0.5),
                       (cx - radius // 3, cy - radius // 3), max(1, radius // 3))


# -------------------------------------------------------------------------
# Mascotte robot (l'IA)
# -------------------------------------------------------------------------
def draw_robot(surface, center, size, mood="idle", t=0.0):
    """Dessine une petite mascotte robot mignonne.

    mood : "idle" | "think" | "happy" | "sad"
    t    : temps (secondes) pour l'animation (clignement / rebond).
    """
    cx, cy = center
    bob = int(math.sin(t * 2.2) * size * 0.03)
    cy += bob

    body = T.SKY
    body_dk = T.SKY_DK
    if mood == "happy":
        body, body_dk = T.MINT, T.MINT_DK
    elif mood == "sad":
        body, body_dk = (150, 160, 180), (120, 130, 150)

    # antenne
    ax, ay = cx, cy - int(size * 0.62)
    pygame.draw.line(surface, body_dk, (cx, cy - int(size * 0.45)), (ax, ay), 5)
    pygame.draw.circle(surface, T.BERRY, (ax, ay), max(4, size // 12))

    # tête
    head = pygame.Rect(0, 0, size, int(size * 0.9))
    head.center = (cx, cy)
    T.draw_round_rect(surface, head, body_dk, radius=size // 3, shadow=True)
    inner = head.inflate(-8, -8)
    T.draw_round_rect(surface, inner, body, radius=size // 3)

    # écran du visage
    face = pygame.Rect(0, 0, int(size * 0.74), int(size * 0.5))
    face.center = (cx, cy - int(size * 0.02))
    T.draw_round_rect(surface, face, (38, 42, 66), radius=size // 6)

    # yeux (clignement périodique)
    cligne = (math.sin(t * 1.6) > 0.97)
    eye_y = face.centery - int(size * 0.03)
    eye_dx = int(size * 0.16)
    eye_r = max(3, size // 12)
    eye_col = T.LEMON if mood != "sad" else T.SKY
    for sx in (-eye_dx, eye_dx):
        ex = face.centerx + sx
        if cligne and mood != "happy":
            pygame.draw.line(surface, eye_col, (ex - eye_r, eye_y), (ex + eye_r, eye_y), 4)
        elif mood == "happy":
            # yeux joyeux ^ ^
            pygame.draw.lines(surface, eye_col, False,
                              [(ex - eye_r, eye_y + 3), (ex, eye_y - 3),
                               (ex + eye_r, eye_y + 3)], 4)
        else:
            pygame.draw.circle(surface, eye_col, (ex, eye_y), eye_r)
            pygame.draw.circle(surface, (255, 255, 255), (ex - 1, eye_y - 1), max(1, eye_r // 3))

    # bouche selon l'humeur
    my = face.centery + int(size * 0.16)
    mw = int(size * 0.3)
    if mood == "happy":
        pygame.draw.arc(surface, eye_col, (face.centerx - mw // 2, my - 8, mw, 20),
                        math.pi, 2 * math.pi, 4)
    elif mood == "sad":
        pygame.draw.arc(surface, T.SKY, (face.centerx - mw // 2, my, mw, 20),
                        0, math.pi, 4)
    elif mood == "think":
        dots = 3
        phase = int((t * 3) % (dots + 1))
        for i in range(dots):
            col = T.LEMON if i < phase else (90, 96, 120)
            pygame.draw.circle(surface, col,
                               (face.centerx - mw // 2 + i * (mw // 2), my), 4)
    else:
        pygame.draw.line(surface, eye_col, (face.centerx - mw // 3, my),
                         (face.centerx + mw // 3, my), 4)

    # petites oreilles/boulons
    for sx in (-1, 1):
        pygame.draw.circle(surface, body_dk,
                           (cx + sx * (size // 2 + 2), cy), max(4, size // 12))


# -------------------------------------------------------------------------
# Confettis (écran de victoire)
# -------------------------------------------------------------------------
class Confetti:
    """Petit système de confettis festif (déterministe, sans Math.random)."""

    def __init__(self, largeur, hauteur, graine=7):
        self.largeur = largeur
        self.hauteur = hauteur
        self.rng = Random(graine)
        self.pieces = []

    def burst(self, quantite=140):
        self.pieces = []
        for _ in range(quantite):
            self.pieces.append({
                "x": self.rng.uniform(0, self.largeur),
                "y": self.rng.uniform(-self.hauteur, 0),
                "vx": self.rng.uniform(-0.6, 0.6),
                "vy": self.rng.uniform(1.6, 4.2),
                "s": self.rng.randint(6, 12),
                "col": self.rng.choice(T.CANDY_COLORS),
                "spin": self.rng.uniform(-6, 6),
                "ang": self.rng.uniform(0, 360),
            })

    def update(self):
        for p in self.pieces:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["ang"] += p["spin"]
            if p["y"] > self.hauteur + 20:
                p["y"] = self.rng.uniform(-60, -10)
                p["x"] = self.rng.uniform(0, self.largeur)

    def dessiner(self, surface):
        for p in self.pieces:
            s = p["s"]
            conf = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.rect(conf, p["col"], (0, 0, s, s), border_radius=2)
            conf = pygame.transform.rotate(conf, p["ang"])
            surface.blit(conf, (p["x"], p["y"]))
