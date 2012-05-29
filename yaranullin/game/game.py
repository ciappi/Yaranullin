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

    def __init__(self):
        self.boards = {}
        LOGGER.debug("Game initialized")

    def create_board(self, name, size):
        ''' Create a new board '''
        board = Board(name, size)
        if name not in self.boards:
            self.boards[name] = board
            LOGGER.info("Created board with name '%s' and size (%d, %d)", 
                    name, size[0], size[1])
            return board
        LOGGER.warning("A board '%s' already exists", name)

    def add_board(self, board):
        ''' Create a new board '''
        if not isinstance(board, Board):
            LOGGER.warning("Object '%s' is not a Board", repr(board))
            return
        name = board.name
        size = board.size
        if name not in self.boards:
            self.boards[name] = board
            LOGGER.info("Added board with name '%s' and size (%d, %d)", 
                    name, size[0], size[1])
            return board
        LOGGER.warning("A board '%s' already exists", name)

    def del_board(self, name):
        ''' Delete the board 'name' '''
        if name in self.boards:
            board = self.boards.pop(name)
            LOGGER.info("Deleted board '%s'", name)
            return board
        LOGGER.warning("A board '%s' cannot be found", name)

    def create_pawn(self, bname, pname, initiative, pos, size):
        ''' Add a pawn to a board '''
        try:
            board = self.boards[bname]
        except KeyError:
            LOGGER.warning("Board '%s' not found", bname)
        else:
            return board.create_pawn(pname, initiative, pos, size)

    def add_pawn(self, bname, pawn):
        ''' Add a pawn to a board '''
        try:
            board = self.boards[bname]
        except KeyError:
            LOGGER.warning("Board '%s' not found", bname)
        else:
            return board.add_pawn(pawn)

    def move_pawn(self, bname, pname, pos, size=None):
        ''' Move a pawn '''
        try:
            board = self.boards[bname]
        except KeyError:
            LOGGER.warning("Board '%s' not found", bname)
        else:
            return board.move_pawn(pname, pos, size)

    def del_pawn(self, bname, pname):
        ''' Remove a pawn '''
        try:
            board = self.boards[bname]
        except KeyError:
            LOGGER.warning("Board '%s' not found", bname)
        else:
            return board.del_pawn(pname)

    def clear(self):
        ''' Clear all the boards '''
        self.boards.clear()
        LOGGER.info("Deleted all boards from the game")

