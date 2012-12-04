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

from yaranullin.config import CONFIG
from yaranullin.event_system import connect, post
from yaranullin.pygame_.widgets import Widget
from yaranullin.pygame_.containers import ScrollableContainer
from yaranullin.pygame_.pawn import PawnToken


class Tile(Widget):

    pass


class Board(ScrollableContainer):

    """The view of a Board."""

    def __init__(self, parent, ev_dict, rect):
        ScrollableContainer.__init__(self, parent, rect)
        self.name = ev_dict['name']
        self.active_pawn = None
        self.size = ev_dict['size']
        self.pawns = WeakValueDictionary()
        self.tw = CONFIG.getint('graphics', 'tile-width')
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                tile = Tile(self, pygame.rect.Rect(x * self.tw, y * self.tw,
                    self.tw, self.tw))
                if (x + y) % 2:
                    tile.image = 'white'
                else:
                    tile.image = 'black'
                self.append(tile)
        self.fullsize = self.size[0] * self.tw, self.size[1] * self.tw
        connect('game-event-pawn-new', self.handle_game_event_pawn_new)
        connect('game-event-pawn-del', self.handle_game_event_pawn_del)
        connect('game-event-pawn-next', self.handle_game_event_pawn_next)
        connect('mouse-click-single-left', self.handle_mouse_click_single_left)

    def handle_game_event_pawn_new(self, ev_dict):
        """Handle the creation of a new Pawn view."""
        if self.name == ev_dict['bname']:
            new_pawn = PawnToken(self, ev_dict)
            self.pawns[ev_dict['pname']] = new_pawn
            self.append(new_pawn)
            self.active_pawn = new_pawn.name

    def handle_game_event_pawn_del(self, ev_dict):
        """Handle the deletion of a Pawn."""
        if self.name == ev_dict['bname']:
            self.remove(self.pawns[ev_dict['pname']])

    def handle_game_event_pawn_next(self, ev_dict):
        if self.name == ev_dict['bname']:
            self.active_pawn = ev_dict['pname']

    def handle_mouse_click_single_left(self, ev_dict):
        pos = ev_dict['pos']
        if self.abs_rect.collidepoint(pos):
            self.on_mouse_click_single_left(ev_dict)

    def on_mouse_click_single_left(self, ev_dict):
        pos = ev_dict['pos']
        pos = pos[0] - self.abs_rect.left, pos[1] - self.abs_rect.top
        pos = pos[0] - self.position[0], pos[1] - self.position[1]
        pos = pos[0] // self.tw, pos[1] // self.tw
        post('game-request-pawn-move', bname=self.name,
            pname=self.active_pawn, pos=pos, rotate=False)

    def on_mouse_click_single_right(self, ev_dict):
        pos = ev_dict['pos']
        pos = pos[0] - self.abs_rect.left, pos[1] - self.abs_rect.top
        pos = pos[0] - self.position[0], pos[1] - self.position[1]
        pos = pos[0] // self.tw, pos[1] // self.tw
        post('game-request-pawn-move', bname=self.name,
            pname=self.active_pawn, pos=pos, rotate=True)
