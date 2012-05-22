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

from yaranullin.game.board import Board
from yaranullin.game.load_and_save import load_board_from_tmx


class Game(object):

    ''' Model and state of Yaranullin '''

    def __init__(self, *tmxs):
        LOGGER.debug("Initializing game...")
        self._boards = {}
        for tmx in tmxs:
            LOGGER.info("Loading board from '%s'", tmx)
            self.add_board(load_board_from_tmx(tmx))
        LOGGER.debug("Initializing game... done")

    def create_board(self, name, size):
        ''' Create a new board '''
        board = Board(name, size)
        if name not in self._boards:
            self._boards[name] = board
            LOGGER.info("Created board with name '%s' and size (%d, %d)", 
                    name, size[0], size[1])
            return board

    def add_board(self, board):
        ''' Add a board to the game '''
        if board.name not in self._boards:
            self._boards[board.name] = board
            LOGGER.info("Added board '%s'", board.name)
            return board

    def del_board(self, name):
        ''' Delete the board 'name' '''
        if name in self._boards:
            board = self._boards.pop(name)
            LOGGER.info("Deleted board '%s'", name)
            return board

    def create_pawn(self, bname, pname, initiative, pos, size):
        ''' Add a pawn to a board '''
        try:
            board = self._boards[bname]
        except KeyError:
            LOGGER.warning("Board '%s' not found", bname)
        else:
            return board.create_pawn(pname, initiative, pos, size)

    def move_pawn(self, bname, pname, pos, size=None):
        ''' Move a pawn '''
        try:
            board = self._boards[bname]
        except KeyError:
            LOGGER.warning("Board '%s' not found", bname)
        else:
            return board.move_pawn(pname, pos, size)

    def del_pawn(self, bname, pname):
        ''' Remove a pawn '''
        try:
            board = self._boards[bname]
        except KeyError:
            LOGGER.warning("Board '%s' not found", bname)
        else:
            return board.del_pawn(pname)

    def clear(self):
        ''' Clear all the boards '''
        self._boards.clear()
        LOGGER.info("Deleted all boards from the game")
