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

from yaranullin.config import CONFIG
from yaranullin.event_system import connect
from yaranullin.pygame_.widgets import Button


class PawnToken(Button):

    def __init__(self, parent, ev_dict):
        self.board = ev_dict['bname']
        self.name = ev_dict['pname']
        self.initiative = ev_dict['initiative']
        self.size = ev_dict['size']
        self.pos = ev_dict['pos']
        self.rotated = False  # ev_dict['rotated']
        self.tw = CONFIG.getint('graphics', 'tile-width')
        x, y = self.pos
        w, h = self.size
        tw = self.tw
        rect = pygame.rect.Rect(x * tw, y * tw, w * tw, h * tw)
        Button.__init__(self, parent, rect)
        self.image = 'magenta'
        connect('game-event-pawn-moved', self.handle_game_event_pawn_moved)

    def handle_game_event_pawn_moved(self, ev_dict):
        """Move the pawns."""
        if self.board == ev_dict['bname'] and self.name == ev_dict['pname']:
            self.pos = ev_dict['pos']
            self.rotated = ev_dict['rotated']
            x, y = self.pos
            w, h = self.size
            tw = self.tw
            self.rect = pygame.rect.Rect(x * tw, y * tw, w * tw, h * tw)
