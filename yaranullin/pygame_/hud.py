# yaranullin/pygame_/hud.py
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

from base.widgets import TextLabel
from base.containers import VContainer

from ..config import COLORS


class PawnToken(TextLabel):

    """A simple text label with the name of a pawn."""

    def __init__(self, event_manager, uid, name, initiative, color=None,
                 **kargs):
        self.uid = uid
        self.name = name
        self.initiative = initiative
        if color is None:
            n_colors = len(COLORS)
            color_index = len(event_manager.pawns) % n_colors
            color = COLORS[color_index]
            color = pygame.colordict.THECOLORS[color]
        TextLabel.__init__(self, event_manager, text=name, font_color=color,
                           font_size=20, font_name='hud_font.ttf')

    def handle_game_event_pawn_next(self, ev_type, uid):
        if self.uid == uid:
            self.font.set_underline(True)
            self.font.set_italic(True)
        else:
            self.font.set_underline(False)
            self.font.set_italic(False)
        self.render_text()


class HUD(VContainer):

    """HUD.

    Print a list of pawns ordered by initiative.

    """

    def __init__(self, event_manager, uid, rect):
        VContainer.__init__(self, event_manager, rect)
        self.uid = uid
        self.active = True
        self.pawns = {}

    def handle_game_event_pawn_new(self, ev_type, **kargs):
        """Handle a new pawn."""
        new_pawn_token = PawnToken(self, **kargs)
        self.pawns[kargs['uid']] = new_pawn_token
        self.append(new_pawn_token)
        self.sort(key=lambda pawn: pawn.initiative, reverse=True)

    def handle_game_event_pawn_del(self, ev_type, uid):
        """Handle pawn deletion."""
        pawn_to_del = self.pawns.pop(uid)
        self.remove(pawn_to_del)

    def handle_game_event_board_change(self, ev_type, uid):
        if self.uid == uid:
            self.active = True
        else:
            self.active = False

    def handle_tick(self, ev_type, dt):
        """Handle ticks if the board is active."""
        if self.active:
            VContainer.handle_tick(self, ev_type, dt)
