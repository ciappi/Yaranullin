# yaranullin/game/tests/test_cell.py
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

from ..grid import Cell, Grid, IndexOutOfGrid


class SampleContent(object):

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 1
        self.height = 1


class TestCell(unittest.TestCase):

    def test___init__(self):

        cell = Cell(2, 3, 'sample content')
        self.assertEqual(2, cell.x)
        self.assertEqual(3, cell.y)
        self.assertEqual('sample content', cell.content)


class TestGrid(unittest.TestCase):

    def setUp(self):
        self.grid = Grid(1000, 9000)

    def test_cell_creation(self):
        self.grid.set_cells(9, 10, 100, 10, 'sample content')
        n_cells = 100 * 10
        self.assertEqual(n_cells, len(self.grid._cells))
        for cell in self.grid._cells.values():
            self.assertEqual('sample content', cell.content)
        # Get cells.
        cells = self.grid.get_cells(0, 0, 1000, 9000)
        self.assertEqual(n_cells, len(cells))
        # Delete cells.
        self.grid.del_cells(9, 10, 100, 10)
        self.assertEqual(0, len(self.grid._cells))

    def test_validate_position(self):
        self.assertRaises(IndexOutOfGrid, self.grid.validate_position,
                          10000, 20000, 3, 3)
#        self.assertNotRaises(IndexOutOfGrid, self.grid.validate_position,
#                             1, 2, 3, 4)

    def test_is_free(self):
        self.grid.set_cells(9, 10, 100, 10, 'sample content')
        self.assertTrue(self.grid.is_free(0, 0, 5, 5))
        self.assertFalse(self.grid.is_free(0, 0, 20, 50))

    def test_set_content(self):
        sample_content = SampleContent()
        self.grid.set_content(9, 10, 100, 10, sample_content)
        self.assertFalse(self.grid.set_content(9, 10, 2, 4,
                         SampleContent()))
