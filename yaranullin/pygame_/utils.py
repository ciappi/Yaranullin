# yaranullin/pygame_/base/utils.py
#
# Copyright (c) 2011 Marco Scopesi <marco.scopesi@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import pygame
import pygame.locals as pl

from yaranullin.config import YR_FONT_DIR
from yaranullin.config import YR_CACHE_DIR
from yaranullin.cache import cache


THECOLORS = pl.color.THECOLORS


def sign(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1


def saturation(x, low=None, high=None):
    if (low is not None and x < low):
        return low
    elif (high is not None and x > high):
        return high
    else:
        return x


@cache
def load_image(img_name, size, alpha=False, rotated=False):
    '''Load and resize an image using the cache'''
    if img_name in THECOLORS:
        surf = pygame.surface.Surface(size)
        surf.fill(THECOLORS[img_name])
    else:
        img_name = os.path.join(YR_CACHE_DIR, img_name)
        surf = pygame.image.load(img_name)
        surf_size = surf.get_size()
        ratio = size[0] / float(surf_size[0]), size[1] / float(surf_size[1])
        if ratio[0] <= ratio[1]:
            ratio = ratio[0]
        else:
            ratio = ratio[1]
        size = int(surf_size[0] * ratio), int(surf_size[0] * ratio)
        surf = pygame.transform.smoothscale(surf, size)
    if alpha:
        surf = surf.convert_alpha()
    else:
        surf = surf.convert()
    if rotated:
        surf = pygame.transform.rotate(surf, -90)
    return surf


@cache
def render_text(text, font_name, font_size, font_color, underline, italic):
    font_color = THECOLORS[font_color]
    try:
        font_name = os.path.join(YR_FONT_DIR, font_name)
        font = pygame.font.Font(font_name, font_size)
    except:
        default = pygame.font.get_default_font()
        font = pygame.font.SysFont(default, font_size)
    font.set_underline(underline)
    font.set_italic(italic)
    surf = font.render(text, True, font_color)
    return surf
