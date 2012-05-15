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

import weakref


class NotAValidPosition(Exception):
    ''' The given position is out of the board '''


class CellsAreNotEmpty(Exception):
    ''' The given cells are not empty '''


class Grid(object):

    ''' Indexed rectangular area '''

    def __init__(self, width, height):
        self._grid = {}
        for x in xrange(width):
            for y in xrange(height):
                self._grid[x, y] = weakref.WeakSet()

    def _check_range(self, x, y, width, height):
        ''' Check if within range '''
        for xx in xrange(x, width + x):
            for yy in xrange(y, height + y):
                if (xx, yy) not in self._grid:
                    raise NotAValidPosition

    def _set(self, content, x, y, width, height):
        ''' Add content to the cells in the given range '''
        for xx in xrange(x, width + x):
            for yy in xrange(y, height + y):
                self._grid[xx, yy].add(content)
        content.pos = x, y
        content.size = width, height

    def remove(self, content):
        ''' Remove content from the grid '''
        x, y = content.pos
        width, height = content.size
        for xx in xrange(x, width + x):
            for yy in xrange(y, height + y):
                if content in self._grid[xx, yy]:
                    self._grid[xx, yy].remove(content)
        content.pos = None
        content.size = None

    def get_content(self, x, y, width, height):
        ''' Get all contents in the given range '''
        contents = set()
        for xx in xrange(x, width + x):
            for yy in xrange(y, height + y):
                if (xx, yy) in self._grid:
                    contents |= set(self._grid[xx, yy])
        return contents

    def place(self, content, x, y, width=None, height=None):
        ''' Place a content in the grid '''
        if not width or not height:
            width, height = content.size
        self._check_range(x, y, width, height)
        contents = self.get_content(x, y, width, height)
        if not contents or (len(contents) == 1 and content in contents):
            if content.pos:
                self.remove(content)
            self._set(content, x, y, width, height)
        else:
            raise CellsAreNotEmpty
 
