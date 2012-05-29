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

import logging

LOGGER = logging.getLogger(__name__)

from yaranullin.game.game import Game
from yaranullin.event_system import post, connect
from yaranullin.game.load_and_save import load_board_from_tmx,\
        load_board_from_file, get_tmx_board


class GameWrapper(object):

    def __init__(self, tmxs):
        self.game = Game()
        connect('game-request-board-new', self.create_board)
        connect('game-request-board-del', self.del_board)
        connect('game-request-pawn-new', self.create_pawn)
        connect('game-request-pawn-move', self.move_pawn)
        connect('game-request-pawn-del', self.del_pawn)
        connect('game-request-update', self.request_update)
        self.load_from_files(tmxs)
        LOGGER.debug("GameWrapper initialized")

    def request_update(self):
        boards = self._dump_game()
        post('game-event-update', tmxs=boards)

    def _dump_game(self):
        boards = {}
        for name in self.game.boards:
            board = get_tmx_board(name)
            if board:
                boards[name] = board
            else:
                LOGGER.error("Unable to dump board '%s' to a string", name)
        return boards

    def load_from_files(self, files):
        ''' Load a board and its pawns from a tmx file '''
        for tmx in files:
            try:
                board, pawns = load_board_from_file(tmx, ext=True)
            except:
                LOGGER.exception("Unable to load tmx file '%s'", tmx)
                continue
            board = self.game.add_board(board)
            if not board:
                continue
            loaded_pawns = set()
            for pawn in pawns:
                pawn = self.game.add_pawn(board.name, pawn)
                if not pawn:
                    continue
                loaded_pawns.add(pawn)
            post('game-event-board-new', board.__dict__)
            for pawn in loaded_pawns:
                post('game-event-pawn-new', pawn.__dict__)

    def create_board(self, event_dict):
        name = event_dict['name']
        size = event_dict['size']
        board = self.game.create_board(name, size)
        if board:
            post('game-event-board-new', event_dict)

    def del_board(self, event_dict):
        board = self.game.del_board(event_dict['name'])
        if board:
            post('game-event-board-del', event_dict)

    def create_pawn(self, event_dict):
        bname = event_dict['bname']
        pname = event_dict['pname']
        initiative = event_dict['initiative']
        pos = event_dict['pos']
        size = event_dict['size']
        pawn = self.game.create_pawn(bname, pname, initiative, pos, size)
        if pawn:
            post('game-event-pawn-new', event_dict)

    def move_pawn(self, event_dict):
        bname = event_dict['bname']
        pname = event_dict['pname']
        pos = event_dict['pos']
        try:
            size = event_dict['size']
        except KeyError:
            size = None
        pawn = self.game.move_pawn(bname, pname, pos, size)
        if pawn:
            post('game-event-pawn-moved', event_dict)

    def del_pawn(self, event_dict):
        bname = event_dict['bname']
        pname = event_dict['pname']
        pawn = self.game.del_pawn(bname, pname)
        if pawn:
            post('game-event-pawn-del', event_dict)

    def clear(self):
        for bname in self.game.boards:
            self.game.del_board(bname)
            post('game-event-board-del', name=bname)


class DummyGameWrapper(object):

    def __init__(self):
        self.boards = set()
        connect('game-event-update', self.update)
        connect('game-request-board-new', self.create_board)
        connect('game-request-board-del', self.del_board)
        connect('game-request-pawn-new', self.create_pawn)
        connect('game-request-pawn-move', self.move_pawn)
        connect('game-request-pawn-del', self.del_pawn)

    def update(self, event_dict):
        self.clear()
        tmxs = event_dict['tmxs']
        for name, tmx_map in tmxs.iteritems():
            try:
                board, pawns = load_board_from_tmx(name, tmx_map, ext=True)
                LOGGER.info("Loaded board '%s' from tmx string", name)
            except:
                LOGGER.exception("Unable to load board '%s' from tmx string",
                        name)
            else:
                post('game-event-board-new', board.__dict__)
                for pawn in pawns:
                    post('game-event-pawn-new', pawn.__dict__)

    def create_board(self, event_dict):
        self.boards.add(event_dict['name'])
        post('game-event-board-new', event_dict)

    def del_board(self, event_dict):
        self.boards.remove(event_dict['name'])
        post('game-event-board-del', event_dict)

    def create_pawn(self, event_dict):
        post('game-event-pawn-new', event_dict)

    def move_pawn(self, event_dict):
        post('game-event-pawn-moved', event_dict)

    def del_pawn(self, event_dict):
        post('game-event-pawn-del', event_dict)

    def clear(self):
        for bname in self.boards:
            self.boards.remove(bname)
            post('game-event-board-del', name=bname)
