# yaranullin/game/tests/game.py
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

import unittest
import sys

if __name__ == '__main__':
    sys.path.insert(0, ".")

from yaranullin.game.game import Game
from yaranullin.game.board import Board


class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_create_board(self):
        board = self.game.create_board('Nasty Dungeon', (1000, 2000))
        self.assertIn(board.name, self.game._boards)
        self.assertIs(board, self.game._boards[board.name])

    def test_add_board(self):
        board = self.game.add_board(Board('Creepy Dungeon', (10, 20)))
        self.assertIn(board.name, self.game._boards)
        self.assertIs(board, self.game._boards[board.name])

    def test_del_board(self):
        board = self.game.create_board('Nasty Dungeon', (1000, 2000))
        self.game.del_board(board.name)
        self.assertNotIn(board.name, self.game._boards)


if __name__ == '__main__':
    unittest.main()
