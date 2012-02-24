# yaranullin/pygame_/gui.py
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
import pygame.locals as PL

from base.event_manager import PygameGUI
from board import Board
from hud import HUD
from ..event_system import Event


class SimpleGUI(PygameGUI):

    """Create a simple gui.

    The elements on the gui are:
      * a HUD with pawn's names of the left;
      * a frame with the board on the right.

    """

    def __init__(self, event_manager):
        PygameGUI.__init__(self, event_manager)
        self.boards = {}
        self.huds = {}
        w, h = pygame.display.get_surface().get_size()
        # The dimensions of the elements are fixed.
        self.frame_rect = pygame.rect.Rect(201, 0, w - 201, h)
        self.hud_rect = pygame.rect.Rect(0, 0, 200, h)

    def handle_game_event_board_new(self, ev_type, **kargs):
        """Create a new board."""
        new_board_id = kargs['board_id']
        self.boards[new_board_id] = Board(self, rect=self.frame_rect, **kargs)
        self.huds[new_board_id] = HUD(self, new_board_id, self.hud_rect)

    def handle_game_event_board_del(self, ev_type, board_id):
        """Delete a board."""
        self.boards[board_id].pawns.clear()
        del self.boards[board_id]
        self.huds[board_id].clear()
        del self.huds[board_id]

    def handle_key_down(self, ev_type, key, mod, unicode):
        if key == PL.K_SPACE:
            self.post(Event('game-request-pawn-next'))
