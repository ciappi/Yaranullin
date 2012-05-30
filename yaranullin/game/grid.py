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

''' Low level interface to a 2D map object '''

import weakref


class Grid(object):

    ''' Indexed rectangular area '''

    def __init__(self, size):
        self.size = size
        # Use a weakref for content, to avoid keeping alive a dead object
        self._grid = {}
        self._contents = weakref.WeakKeyDictionary()

    def _get_cells(self, pos, size):
        ''' Iter through cells in the give range '''
        # Check if all cells are within the size of the grid
        max_pos = pos[0] + size[0] - 1, pos[1] + size[1] - 1
        if max_pos[0] >= self.size[0] or max_pos[1] >= self.size[1]:
            raise IndexError("Range between (%d, %d) and (%d, %d) contains "
                    "cells out of grid" % (pos[0], pos[1], max_pos[0],
                        max_pos[1]))
        # Start yielding cells
        for pos_x in xrange(pos[0], size[0] + pos[0]):
            for pos_y in xrange(pos[1], size[1] + pos[1]):
                yield (pos_x, pos_y)

    def clear(self):
        ''' Clear the grid '''
        self._grid.clear()
        self._contents.clear()

    def get(self, pos, size):
        ''' Get all contents in the given range '''
        cnts = set()
        for cell in self._get_cells(pos, size):
            if cell in self._grid:
                cnts |= set(self._grid[cell])
        return cnts

    def add(self, cnt, pos, size):
        ''' Add content to the cells in the given range '''
        if cnt not in self._contents:
            self._contents[cnt] = set()
        for cell in self._get_cells(pos, size):
            if cell not in self._grid:
                self._grid[cell] = weakref.WeakSet()
            self._grid[cell].add(cnt)
            self._contents[cnt].add(cell)
        cnt.pos = pos
        cnt.size = size

    def remove(self, cnt):
        ''' Remove content from the grid '''
        if cnt not in self._contents:
            return
        for cell in self._contents[cnt]:
            self._grid[cell].remove(cnt)
            # Delete cell if empty
            if not self._grid[cell]:
                del self._grid[cell]
        del self._contents[cnt]
        cnt.pos = None
