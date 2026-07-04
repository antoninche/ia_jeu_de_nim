"""Thème visuel du jeu de Nim « pour enfants ».

Palette « bonbon », polices arrondies et petits utilitaires de dessin
(dégradés, rectangles arrondis, ombres douces, texte). Tout est regroupé
ici pour garder une identité visuelle cohérente dans tout le jeu.
"""

from __future__ import annotations

import pygame

# -------------------------------------------------------------------------
# Palette « bonbon » — claire, chaleureuse, forte lisibilité
# -------------------------------------------------------------------------
BG_TOP = (255, 243, 224)      # crème
BG_BOT = (255, 214, 226)      # rose barbe-à-papa

CARD = (255, 255, 255)        # cartes / panneaux
CARD_SOFT = (255, 249, 240)   # panneau secondaire
SHADOW = (60, 40, 80)         # ombre (utilisée en translucide)

INK = (63, 48, 82)            # texte principal (violet foncé lisible)
INK_SOFT = (135, 118, 158)    # texte secondaire
INK_ON = (255, 255, 255)      # texte sur aplat coloré

# Couleurs vives de bonbons
GRAPE = (146, 100, 214)       # violet
GRAPE_DK = (120, 78, 190)
BERRY = (240, 90, 126)        # framboise
BERRY_DK = (214, 66, 104)
TANGERINE = (255, 150, 66)    # orange
LEMON = (255, 205, 70)        # citron
MINT = (72, 200, 158)         # menthe
MINT_DK = (46, 176, 134)
SKY = (86, 178, 236)          # ciel
SKY_DK = (58, 152, 214)

# Rôles sémantiques
PRIMARY = GRAPE
PRIMARY_DK = GRAPE_DK
SUCCESS = MINT
SUCCESS_DK = MINT_DK
DANGER = BERRY
DANGER_DK = BERRY_DK
DISABLED = (214, 206, 224)
DISABLED_INK = (150, 142, 165)

# Couleurs cycliques pour les bonbons et les perles
CANDY_COLORS = [BERRY, TANGERINE, LEMON, MINT, SKY, GRAPE]

# Couleur d'une perle / bonbon selon l'action (prendre 1 / 2 / 3)
ACTION_COLORS = {1: SKY, 2: TANGERINE, 3: MINT}


def candy_color(index: int) -> tuple[int, int, int]:
    return CANDY_COLORS[index % len(CANDY_COLORS)]


# -------------------------------------------------------------------------
# Polices
# -------------------------------------------------------------------------
class Fonts:
    """Charge des polices arrondies « enfant » avec repli système."""

    # Polices amusantes présentes sur la plupart des Mac / Windows,
    # sinon repli sur Arial.
    FAMILLE = "chalkboardse,comicsansms,arialroundedmtbold,verdana,arial"

    def __init__(self):
        self.title = pygame.font.SysFont(self.FAMILLE, 78, bold=True)
        self.h1 = pygame.font.SysFont(self.FAMILLE, 46, bold=True)
        self.h2 = pygame.font.SysFont(self.FAMILLE, 32, bold=True)
        self.body = pygame.font.SysFont(self.FAMILLE, 26)
        self.body_b = pygame.font.SysFont(self.FAMILLE, 26, bold=True)
        self.small = pygame.font.SysFont(self.FAMILLE, 21)
        self.tiny = pygame.font.SysFont(self.FAMILLE, 17, bold=True)


# -------------------------------------------------------------------------
# Utilitaires de dessin
# -------------------------------------------------------------------------
def draw_vertical_gradient(surface: pygame.Surface, top, bottom):
    """Remplit toute la surface d'un dégradé vertical doux."""
    h = surface.get_height()
    w = surface.get_width()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))


def make_background(width: int, height: int) -> pygame.Surface:
    """Crée un fond dégradé (pré-rendu une seule fois) avec quelques
    bulles décoratives translucides."""
    surf = pygame.Surface((width, height))
    draw_vertical_gradient(surf, BG_TOP, BG_BOT)

    # bulles douces
    bulle = pygame.Surface((width, height), pygame.SRCALPHA)
    deco = [
        (150, 140, 120, (255, 255, 255, 60)),
        (980, 120, 90, (255, 255, 255, 45)),
        (240, 620, 70, (255, 255, 255, 40)),
        (1040, 640, 110, (255, 255, 255, 50)),
        (620, 90, 60, (255, 255, 255, 35)),
    ]
    for x, y, r, col in deco:
        pygame.draw.circle(bulle, col, (x, y), r)
    surf.blit(bulle, (0, 0))
    return surf


def draw_round_rect(surface, rect, color, radius=18, shadow=False,
                    shadow_offset=6, shadow_alpha=55):
    """Rectangle arrondi, avec ombre portée douce optionnelle."""
    rect = pygame.Rect(rect)
    if shadow:
        sh = pygame.Surface((rect.w + shadow_offset * 2,
                             rect.h + shadow_offset * 2), pygame.SRCALPHA)
        pygame.draw.rect(
            sh, (*SHADOW, shadow_alpha),
            (shadow_offset, shadow_offset + shadow_offset // 2,
             rect.w, rect.h),
            border_radius=radius,
        )
        surface.blit(sh, (rect.x - shadow_offset, rect.y - shadow_offset))
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_text(surface, text, font, color, pos, center=False, anchor_right=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = pos
    elif anchor_right:
        rect.topright = pos
    else:
        rect.topleft = pos
    surface.blit(surf, rect)
    return rect


def draw_text_center(surface, text, font, color, x, y):
    return draw_text(surface, text, font, color, (x, y), center=True)


def lighten(color, amount=0.12):
    return tuple(min(255, int(c + (255 - c) * amount)) for c in color)


def darken(color, amount=0.12):
    return tuple(max(0, int(c * (1 - amount))) for c in color)
