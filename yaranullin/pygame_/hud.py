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

from yaranullin.event_system import connect
from yaranullin.pygame_.widgets import TextLabel
from yaranullin.pygame_.containers import VContainer


class PawnToken(TextLabel):

    """A simple text label with the name of a pawn."""

    def __init__(self, ev_dict):
        self.name = ev_dict['pname']
        self.board = ev_dict['bname']
        self.initiative = ev_dict['initiative']
        TextLabel.__init__(self, text=self.name, font_name='hud_font.ttf',
            font_size=25)
        connect('game-event-pawn-next', self.handle_game_event_pawn_next)

    def handle_game_event_pawn_next(self, ev_dict):
        if self.board == ev_dict['bname']:
            if self.name == ev_dict['pname']:
                self.underline = True
                self.italic = True
            else:
                self.underline = False
                self.italic = False


class HUD(VContainer):

    """HUD.

    Print a list of pawns ordered by initiative.

    """

    def __init__(self, parent, ev_dict, rect):
        VContainer.__init__(self, parent, rect)
        self.board_name = ev_dict['name']
        self.pawns = {}
        connect('game-event-pawn-new', self.handle_game_event_pawn_new)
        connect('game-event-pawn-del', self.handle_game_event_pawn_del)

    def handle_game_event_pawn_new(self, ev_dict):
        """Handle a new pawn."""
        new_pawn_token = PawnToken(ev_dict)
        self.pawns[ev_dict['pname']] = new_pawn_token
        self.append(new_pawn_token)
        self.sort(key=lambda pawn: pawn.initiative, reverse=True)

    def handle_game_event_pawn_del(self, ev_type, uid):
        """Handle pawn deletion."""
        pawn_to_del = self.pawns.pop(uid)
        self.remove(pawn_to_del)
