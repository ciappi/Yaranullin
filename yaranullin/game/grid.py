# yaranullin/game/grid.py
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


class IndexOutOfGrid(Exception):

    pass


class Cell(object):

    """A simple cell on a board."""

    def __init__(self, x, y, content):
        """Initialize the Cell.

        Positional arguments:
        x -- cell column on the grid
        y -- cell row on the grid
        content -- the desired content of the cell (i.e. a Pawn)

        """
        self.x = x
        self.y = y
        self.content = content

    def is_free(self, content=None):
        """True if the content of the cell is content."""
        if self.content is content:
            return True
        else:
            return False


class Grid(object):

    """Container of Cell objects.

    Container for all the cells on the same board.

    """

    def __init__(self, width, height):
        """Initialize the Grid.

        Positional arguments:
        width -- the width of the cell (int >= 1)
        height -- the height of the cell (int >= 1)

        """
        # (x, y): Cell
        self._cells = {}
        assert(width >= 1)
        assert(height >= 1)
        self.width = width
        self.height = height

    def validate_position(self, x1, y1, x2, y2):
        """Verify that all indexes are within grid boundaries.

        Raise an IndexOutOfGrid exception.

        """
        if not (0 <= x1 < self.width and 0 <= y1 < self.height):
            raise IndexOutOfGrid
        if x2 >= self.width or y2 >= self.height:
            raise IndexOutOfGrid

    def set_cells(self, x1, y1, width, height, content):
        """Create the cells within the range."""
        assert(width >= 1)
        assert(height >= 1)
        x2, y2 = x1 + width - 1, y1 + height - 1
        self.validate_position(x1, y1, x2, y2)
        # Create a cell or delete it if content is None.
        for dx in xrange(width):
            for dy in xrange(height):
                p = x1 + dx, y1 + dy
                x, y = p
                if content is not None:
                    self._cells[p] = Cell(x, y, content)
                elif p in self._cells:
                    del self._cells[p]

    def get_cells(self, x1, y1, width, height):
        """Get the cells within the range."""
        assert(width >= 1)
        assert(height >= 1)
        cells = []
        x2, y2 = x1 + width - 1, y1 + height - 1
        self.validate_position(x1, y1, x2, y2)
        for pos, cell in self._cells.items():
            if (x1 <= pos[0] <= x2) and (y1 <= pos[1] <= y2):
                cells.append(cell)
        return cells

    def is_free(self, x1, y1, width, height, content=None):
        """True if all Cells within the range are free."""
        cells = self.get_cells(x1, y1, width, height)
        for cell in cells:
            if not cell.is_free(content):
                return False
        return True

    def del_cells(self, x1, y1, width, height):
        """Delete the cells within the range."""
        self.set_cells(x1, y1, width, height, None)

    def set_content(self, x1, y1, width, height, content):
        """Set the cells for the given content."""
        c = content
        ok = self.is_free(x1, y1, width, height, c)
        if ok:
            self.del_content(c)
            self.set_cells(x1, y1, width, height, c)
            c.x, c.y, c.width, c.height = x1, y1, width, height
        return ok

    def del_content(self, content):
        """Remove the content from the Cells."""
        c = content
        self.del_cells(c.x, c.y, c.width, c.height)
        c.x, c.y, c.width, c.height = -1, -1, 1, 1
