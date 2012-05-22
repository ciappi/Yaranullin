# yaranullin/game/tests/grid.py
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

from yaranullin.game.grid import Grid

class Content:

    def __init__(self):
        self.pos = None
        self.size = None


class TestGrid(unittest.TestCase):
    ''' Test Grid object '''

    def setUp(self):
        self.size = 200, 100
        self.grid = Grid(self.size)

    def test_add(self):
        content = Content()
        pos = 1, 2
        size = 2, 1
        cells = set([(1, 2), (2, 2)])
        self.grid.add(content, pos, size)
        self.assertEqual(cells, self.grid._contents[content])
        self.assertEqual([content, ], list(self.grid._grid[1, 2]))
        self.assertEqual([content, ], list(self.grid._grid[2, 2]))

    def test_remove(self):
        content = Content()
        pos = 1, 2
        size = 2, 1
        self.grid.add(content, pos, size)
        self.grid.remove(content)
        self.assertNotIn(content, self.grid._contents)
        cells = set([(1, 2), (2, 2)])
        for cell in cells:
            self.assertNotIn(cell, self.grid._grid)

    def test_get(self):
        content = Content()
        pos = 1, 2
        size = 2, 1
        self.grid.add(content, pos, size)
        grid_content = self.grid.get((0, 0), self.size)
        self.assertIn(content, grid_content)
        self.assertEqual(1, len(grid_content))


if __name__ == '__main__':
    unittest.main()
