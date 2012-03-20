# yaranullin/game/board.py
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

from yaranullin.event_system import EventManagerAndListener, Event
from yaranullin.game.grid import Grid
from yaranullin.game.pawn import Pawn
from yaranullin.game.cell_content import CellContentInitializationError


class Board(EventManagerAndListener):

    """Board class, holds pawns and the grid."""

    def __init__(self, game, name, width, height, uid=None, **kargs):
        EventManagerAndListener.__init__(self, game)
        self.grid = Grid(width, height)
        self.uid = uid
        self.board_id = self.uid
        self.pawns = {}
        self.initiatives = []
        self.active = True
        self.active_pawn = None
        self.name = name

    def add_pawn(self, **kargs):
        """Create and add a Pawn to the Board."""
        try:
            new_pawn = Pawn(self, **kargs)
        except CellContentInitializationError:
            new_pawn_id = None
        else:
            new_pawn_id = new_pawn.uid
            self.pawns[new_pawn_id] = new_pawn
            self.initiatives.append(new_pawn)
            # Sort the initiatives list.
            self.initiatives.sort(key=lambda pawn: pawn.initiative,
                                  reverse=True)
        return new_pawn_id

    def del_pawn(self, pawn_id):
        """Delete all references to a Pawn."""
        pawn_to_del = self.pawns.pop(pawn_id, None)
        if pawn_to_del is not None:
            self.grid.del_content(pawn_to_del)
            self.initiatives.remove(pawn_to_del)
        return pawn_to_del

    def next_pawn(self, pawn_id):
        """Set active_pawn to the next pawn according to initiative order."""
        if pawn_id is not None:
            if pawn_id in self.pawns:
                self.active_pawn = self.pawns[pawn_id]
        elif len(self.initiatives):
            if self.active_pawn is None:
                self.active_pawn = self.initiatives[0]
            else:
                try:
                    index = self.initiatives.index(self.active_pawn) + 1
                    self.active_pawn = self.initiatives[index]
                except IndexError:
                    self.active_pawn = self.initiatives[0]
        else:
            self.active_pawn = None
        return self.active_pawn

    def handle_game_request_board_change(self, ev_type, uid):
        """Activate or deativate this Board."""
        if uid == self.uid:
            self.active = True
            event = Event('game-event-board-change', uid=uid)
            self.post(event)
        else:
            self.active = False

    def handle_game_request_pawn_new(self, ev_type, **kargs):
        """Handle the creation of a new Pawn."""
        if not self.active:
            return
        new_pawn_id = self.add_pawn(**kargs)
        if new_pawn_id:
            kargs['uid'] = new_pawn_id
            event = Event('game-event-pawn-new', **kargs)
            self.post(event)

    def handle_game_request_pawn_del(self, ev_type, uid):
        """Handle the deletion of a Pawn."""
        if not self.active:
            return
        pawn_to_del = self.del_pawn(uid)
        if pawn_to_del is not None:
            self.grid.del_content(pawn_to_del)
            event = Event('game-event-pawn-del', uid=uid)
            self.post(event)

    def handle_game_request_pawn_next(self, ev_type, uid=None):
        """Handle the request to change initiative."""
        if not self.active:
            return
        pawn = self.next_pawn(uid)
        event = Event('game-event-pawn-next', uid=pawn.uid)
        self.post(event)
