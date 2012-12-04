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

from yaranullin.event_system import connect, post
from yaranullin.pygame_.containers import Container
from yaranullin.pygame_.board import Board
from yaranullin.pygame_.hud import HUD


class PygameGui(Container):

    """Assemble a simple gui.

    The elements on the gui are:
      * a HUD with pawn's names of the left;
      * a frame with the board on the right.

    """

    def __init__(self):
        w, h = pygame.display.get_surface().get_size()
        # The dimensions of the elements are fixed.
        self.board_rect = pygame.rect.Rect(201, 0, w - 201, h)
        self.hud_rect = pygame.rect.Rect(0, 0, 200, h)
        Container.__init__(self, None, pygame.rect.Rect(0, 0, w, h))
        self.boards = {}
        self.huds = {}
        connect('game-event-board-new', self.handle_game_event_board_new)
        connect('game-event-board-del', self.handle_game_event_board_del)
        connect('key-down', self.handle_key_down)
        connect('tick', self.handle_tick)

    def handle_game_event_board_new(self, ev_dict):
        """Create a new board."""
        board_name = ev_dict['name']
        new_board = Board(self, ev_dict, rect=self.board_rect)
        new_hud = HUD(self, ev_dict, rect=self.hud_rect)
        self.child_widgets = []
        self.append(new_board)
        self.append(new_hud)
        self.boards[board_name] = new_board
        self.huds[board_name] = new_hud

    def handle_game_event_board_del(self, ev_dict):
        """Delete a board."""
        board_name = ev_dict['name']
        self.boards[board_name].pawns.clear()
        del self.boards[board_name]
        self.huds[board_name].pawns.clear()
        del self.huds[board_name]

    def handle_key_down(self, ev_dict):
        key = ev_dict['key']
        if key == PL.K_SPACE:
            post('game-request-pawn-next')
        elif key == PL.K_ESCAPE:
            post('quit')

    def handle_tick(self, ev_dict):
        """Handle tick event."""
        self.update(ev_dict['dt'])
        self.draw(pygame.display.get_surface())
