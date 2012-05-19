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

from yaranullin.game.board import Board
from yaranullin.game.load_and_save import load_board_from_tmx


class Game(object):

    ''' Model and state of Yaranullin '''

    def __init__(self, tmxs=[]):
        self._boards = {}
        for tmx in tmxs:
            self.add_board(load_board_from_tmx(tmx))

    def create_board(self, name, size):
        ''' Create a new board '''
        board = Board(name, size)
        if name not in self._boards:
            self._boards[name] = board
            return board

    def add_board(self, board):
        ''' Add a board to the game '''
        if board.name not in self._boards:
            self._boards[board.name] = board
            return board

    def del_board(self, name):
        ''' Delete the board 'name' '''
        if name in self._boards:
            return self._boards.pop(name)

    def clear(self):
        ''' Clear all the boards '''
        self._boards.clear()
