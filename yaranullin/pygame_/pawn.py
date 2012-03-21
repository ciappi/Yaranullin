# yaranullin/pygame_/board.py
#
# Copyright (c) 2012 Marco Scopesi <marco.scopesi@gmail.com>
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

import pygame

from yaranullin.config import CONFIG, COLORS
from yaranullin.cache import CacheMixIn
from yaranullin.pygame_.base.widgets import Widget
from yaranullin.pygame_.base.utils import load_image


def load_image_with_alpha(size):
    def loader(f):
        return load_image(f, size, True)
    return loader


class Pawn(Widget, CacheMixIn):

    def __init__(self, event_manager, uid, name, initiative, x, y, width,
                 height, rotated, color=None, image=None):
        Widget.__init__(self, event_manager)
        CacheMixIn.__init__(self)
        print image
        self.active = False
        self.uid = uid
        self.name = name
        self.initiative = initiative
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.image = image
        self.rotated = rotated
        self.tw = CONFIG.getint('graphics', 'tile-width')
        if self.color is None:
            n_colors = len(COLORS)
            color_index = len(self.event_manager.pawns) % n_colors
            color = COLORS[color_index]
            self.color = pygame.colordict.THECOLORS[color]
        tw = self.tw
        size = (width * tw - int(tw * 0.2), height * tw - int(tw * 0.2))
        default_image = pygame.surface.Surface(size).convert()
        default_image.fill(self.color)
        if image is None:
            self._image = default_image
        else:
            loader = load_image_with_alpha(size)
            self.set_cached_property('_image', image, loader, default_image)
        self.image = self._image.copy()
        self.update_rect()

    def update_rect(self):
        """Update."""
        if self.rotated:
            self.image = pygame.transform.rotate(self._image, -90)
            width, height = self.height, self.width
        else:
            self.image = self._image
            width, height = self.width, self.height
        self.rect.size = self.image.get_rect().size
        self.rect.center = (self.x * self.tw + width * self.tw // 2,
                            self.y * self.tw + height * self.tw // 2)

    def handle_game_event_pawn_next(self, ev_type, uid):
        """Handle a pawn change."""
        if uid == self.uid:
            self.active = True
        else:
            self.active = False

    def handle_game_event_pawn_updated(self, ev_type, uid, **kargs):
        """Move the pawns."""
        if self.uid != uid:
            return
        self.__dict__.update(**kargs)
        self.update_rect()
