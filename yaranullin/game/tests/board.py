# yaranullin/game/tests/board.py
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

from yaranullin.game.board import Board


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.size = (100, 200)
        self.name = 'Test dungeon'
        self.board = Board(self.name, self.size)

    def test_create_pawn(self):
        pos = 3, 4
        size = 5, 6
        pawn = self.board.create_pawn('Dragon', 35, pos, size)
        self.assertIn(pawn.name, self.board.pawns)
        self.assertIs(pawn, self.board.pawns[pawn.name])
        self.assertIn(pawn, self.board.initiatives)

    def del_pawn(self):
        pos = 3, 4
        size = 5, 6
        self.board.create_pawn('Dragon', 35, pos, size)
        pawn = self.board.del_pawn('Dragon')
        self.assertNotIn(pawn.name, self.board.pawns)
        self.assertIsNot(pawn, self.board.pawns[pawn.name])
        self.assertNotIn(pawn, self.board.initiatives)



if __name__ == '__main__':
    unittest.main()
