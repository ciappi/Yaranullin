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
from weakref import WeakValueDictionary

from base.containers import ScrollableContainer
from pawn import Pawn
from yaranullin.config import CONFIG
from yaranullin.event_system import Event


class Board(ScrollableContainer):

    """The view of a Board."""

    def __init__(self, event_manager, uid, name, width, height, rect=None,
                 tiles=None):
        ScrollableContainer.__init__(self, event_manager, rect)
#        print tiles
        self.uid = uid
        self.active_pawn_uid = None
        self.name = name
        self.width = width
        self.height = height
        self.active = True
        self.pawns = WeakValueDictionary()
        self.tw = CONFIG.getint('graphics', 'tile-width')
        surf = pygame.surface.Surface((self.tw * self.width,
                                       self.tw * self.height)).convert()
        self.image = surf
        self._image = self.image.copy()
        self.init_background(tiles)

    def init_background(self, tiles):
        self.tiles = {}
        self.to_blit = {}
        for tile in tiles:
            x, y = tile['x'], tile['y']
            self.tiles[x, y] = tile['image']
            self.to_blit[x, y] = True

    def draw(self):
        cells = ((x, y) for (x, y) in self.to_blit if self.to_blit[x, y])
        dirty = False
        for x, y in cells:
            tile = self.tiles[x, y]
            pos = self.tw * x, self.tw * y
            texture = self.cache.get(tile)
            size = self.tw, self.tw
            if texture:
                dirty = True
                texture = pygame.transform.smoothscale(texture, size)
                self._image.blit(texture, pos)
                self.to_blit[x, y] = False
        if dirty:
            self.image = self._image.copy()
        ScrollableContainer.draw(self)

    def handle_game_event_pawn_new(self, ev_type, **kargs):
        """Handle the creation of a new Pawn view."""
        if not self.active:
            return
        new_pawn = Pawn(self, **kargs)
        self.pawns[kargs['uid']] = new_pawn
        self.append(new_pawn)

    def handle_game_event_pawn_del(self, ev_type, uid):
        """Handle the deletion of a Pawn."""
        if not self.active:
            return
        self.remove(self.pawns[uid])

    def handle_game_event_board_change(self, ev_type, uid):
        if self.uid == uid:
            self.active = True
        else:
            self.active = False

    def handle_tick(self, ev_type, dt):
        """Handle ticks if the board is active."""
        if self.active:
            ScrollableContainer.handle_tick(self, ev_type, dt)

    def handle_game_event_pawn_next(self, ev_type, uid):
        if self.active:
            self.active_pawn_uid = uid

    def handle_mouse_click_single_left(self, ev_type, pos):
        if self.active and self.abs_rect.collidepoint(pos):
            # Find the hitted cell
            pos = pos[0] - self.abs_rect.left, pos[1] - self.abs_rect.top
            pos = pos[0] - self.view[0], pos[1] - self.view[1]
            x, y = pos[0] // self.tw, pos[1] // self.tw
            event = Event('game-request-pawn-place',
                          uid=self.active_pawn_uid, x=x, y=y, rotate=False)
            self.post(event)
