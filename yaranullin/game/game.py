# yaranullin/game/game.py
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
from yaranullin.game.board import Board


class Game(EventManagerAndListener):

    """Container of Boards."""

    def __init__(self, event_manager):
        EventManagerAndListener.__init__(self, event_manager)
        self.boards = {}

    def add_board(self, **kargs):
        """Create and add a new Board."""
        new_board = Board(self, **kargs)
        new_board_id = new_board.uid
        self.boards[new_board_id] = new_board
        return new_board_id

    def del_board(self, board_id):
        """Delete a board."""
        board_to_del = self.boards.pop(board_id, None)
        if board_to_del is not None:
            pawns_to_del = list(board_to_del.initiatives)
            for pawn in pawns_to_del:
                board_to_del.del_pawn(pawn)
            del board_to_del.grid
        return board_to_del

    def handle_game_request_board_new(self, ev_type, **kargs):
        """Handle a request for a new Board."""
        new_board_id = self.add_board(**kargs)
        kargs['uid'] = new_board_id
        event = Event('game-event-board-new', **kargs)
        self.post(event)

    def handle_game_request_board_del(self, ev_type, uid):
        """Handle the deletion of a Board."""
        board_to_del = self.del_board(uid)
        if board_to_del is not None:
            event = Event('game-event-board-del', uid=uid)
            self.post(event)
