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
from yaranullin.game.tmx_wrapper import TmxWrapper, ParseError


class GameWrapper(object):

    def __init__(self):
        self.game = Game()
        self.tmx_wrapper = TmxWrapper()
        connect('game-request-board-new', self.create_board)
        connect('game-request-board-del', self.del_board)
        connect('game-request-pawn-new', self.create_pawn)
        connect('game-request-pawn-move', self.move_pawn)
        connect('game-request-pawn-del', self.del_pawn)
        connect('game-request-update', self.request_update)
        LOGGER.debug("GameWrapper initialized")

    def request_update(self):
        boards = self._dump_game()
        post('game-event-update', tmxs=boards)

    def _dump_game(self):
        boards = {}
        for name in self.game.boards:
            board = self.tmx_wrapper.get_tmx_board(name)
            if board:
                boards[name] = board
            else:
                LOGGER.error("Unable to dump board '%s' to a string", name)
        return boards

    def load_from_files(self, files):
        ''' Load a board and its pawns from a tmx file '''
        for tmx in files:
            try:
                self.tmx_wrapper.load_board_from_file(tmx)
            except IOError:
                LOGGER.exception("Unable to open file '%s'", tmx)
            except ParseError:
                LOGGER.exception("Unable to parse file '%s'", tmx)
            else:
                LOGGER.info("Loaded board from file '%s'", tmx)

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
        self.tmx_wrapper = TmxWrapper()
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
                self.tmx_wrapper.load_board_from_tmx(name, tmx_map)
            except ParseError:
                LOGGER.exception("Unable to load board '%s' from tmx string",
                        name)
            else:
                LOGGER.info("Loaded board '%s' from tmx string", name)

    def create_board(self, event_dict):
        self.boards.add(event_dict['name'])
        LOGGER.info("Created board with name '%s' and size (%d, %d)",
                event_dict['name'], event_dict['size'][0],
                event_dict['size'][1])
        post('game-event-board-new', event_dict)

    def del_board(self, event_dict):
        self.boards.remove(event_dict['name'])
        LOGGER.info("Deleted board with name '%s'", event_dict['name'])
        post('game-event-board-del', event_dict)

    def create_pawn(self, event_dict):
        LOGGER.info("Created pawn '%s' within board '%s'",
                event_dict['pname'], event_dict['bname'])
        post('game-event-pawn-new', event_dict)

    def move_pawn(self, event_dict):
        LOGGER.info("Moved pawn '%s' at pos (%d, %d) within board '%s'",
                event_dict['pname'], event_dict['pos'][0],
                event_dict['pos'][1], event_dict['bname'])
        post('game-event-pawn-moved', event_dict)

    def del_pawn(self, event_dict):
        LOGGER.info("Removed pawn '%s' from board '%s'", event_dict['pname'],
                event_dict['bname'])
        post('game-event-pawn-del', event_dict)

    def clear(self):
        for bname in self.boards:
            post('game-event-board-del', name=bname)
        self.boards.clear()
        LOGGER.info("All boards have been deleted")
