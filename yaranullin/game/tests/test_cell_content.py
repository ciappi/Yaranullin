# yaranullin/game/tests/test_cell_content.py
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


from main import TestBase
from ..cell_content import CellContent, CellContentInitializationError


class TestCellContent(TestBase):

    def setUp(self):

        TestBase.setUp(self)
        self.cell_content_1 = CellContent(self.board, x=1, y=2,
                                          width=4, height=5)

    def test___init__(self):

        self.assertEqual(1, self.cell_content_1.x)
        self.assertEqual(2, self.cell_content_1.y)
        self.assertEqual(4, self.cell_content_1.width)
        self.assertEqual(5, self.cell_content_1.height)
        self.assertRaises(CellContentInitializationError, CellContent,
                          self.board, x=1, y=2, width=1, height=2)

    def test_place(self):
        content = CellContent(self.board, x=19, y=20, width=1, height=1)
        placed = content.place(1, 2, False)
        self.assertFalse(placed)
        placed = content.place(10, 2, False)
        self.assertTrue(placed)
