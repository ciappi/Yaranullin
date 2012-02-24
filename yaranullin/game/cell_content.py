# yaranullin/game/cell_content.py
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

from ..event_system import Listener


class CellContentInitializationError(Exception):
    pass


class CellContent(Listener):

    """The content of a cell."""

    def __init__(self, board, x, y, width, height, rotated):
        Listener.__init__(self, board)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.rotated = False
        placed = self.place(x, y, rotated)
        if not placed:
            logging.info('Unable to create CellContent at (' + str(self.x) +
                         ',' + str(self.y) + ')')
            raise CellContentInitializationError

    @property
    def grid(self):
        """Return a reference to the grid."""
        return self.event_manager.grid

    def place(self, x, y, rotate):
        """Place the CellContent on the grid."""
        if rotate:
            width, height = self.height, self.width
        else:
            width, height = self.width, self.height
        placed = self.grid.set_content(x, y, width, height, self)
        if not placed:
            logging.info('Cannot move ' + str(self) + ' to (' + str(x) +
                         ',' + str(y) + ')')
        # Boolean xor.
        self.rotated = self.rotated != rotate
        return placed

    def move(self, dx, dy, rotate):
        """Move the CellContent on the grid."""
        x, y = self.x + dx, self.y + dy
        moved = self.place(x, y, rotate)
        return moved
