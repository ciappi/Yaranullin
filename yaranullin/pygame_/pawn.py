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

from base.widgets import Widget
from ..config import CONFIG, COLORS


class Pawn(Widget):

    def __init__(self, event_manager, pawn_id, name, initiative, x, y, width,
                 height, rotated, color=None, image=None):
        Widget.__init__(self, event_manager)
        self.active = False
        self.pawn_id = pawn_id
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
        if self.image is None:
            tw = self.tw
            size = (width * tw - int(tw * 0.2), height * tw - int(tw * 0.2))
            self.image = pygame.surface.Surface(size).convert()
            self.image.fill(self.color)
        self._image = self.image.copy()
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

    def handle_game_event_pawn_next(self, ev_type, pawn_id):
        """Handle a pawn change."""
        if pawn_id == self.pawn_id:
            self.active = True
        else:
            self.active = False

    def handle_game_event_pawn_updated(self, ev_type, pawn_id, **kargs):
        """Move the pawns."""
        if self.pawn_id != pawn_id:
            return
        self.__dict__.update(**kargs)
        self.update_rect()
