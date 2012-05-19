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
import collections


class NotAValidPosition(Exception):
    ''' The given position is out of the board '''


class CellsAreNotEmpty(Exception):
    ''' The given cells are not empty '''


class Grid(object):

    ''' Indexed rectangular area '''

    def __init__(self, size):
        self.size = size
        self._grid = collections.defaultdict(weakref.WeakSet())
        self._contents = weakref.WeakKeyDictionary()

    def _put(self, content, pos, size):
        ''' Add content to the cells in the given range '''
        if content in self._contents:
            return
        self._contents[content] = set()
        for pos_x in xrange(pos[0], size[0] + pos[0]):
            for pos_y in xrange(pos[1], size[1] + pos[1]):
                self._grid[pos_x, pos_y].add(content)
                self._contents[content].add((pos_x, pos_y))
        content.pos = pos
        content.size = size

    def remove(self, content):
        ''' Remove content from the grid '''
        if content not in self._contents:
            return
        for cell in self._contents[content]:
            self._grid[cell].remove(content)
        del self._contents[content]
        content.pos = None
        content.size = None

    def get_content(self, pos, size):
        ''' Get all contents in the given range '''
        contents = set()
        for pos_x in xrange(pos[0], size[0] + pos[0]):
            for pos_y in xrange(pos[1], size[1] + pos[1]):
                if (pos_x, pos_y) in self._grid:
                    contents |= set(self._grid[pos_x, pos_y])
        return contents

    def place(self, content, pos, size=None):
        ''' Place a content in the grid '''
        if size is None:
            size = content.size
        # Check if the cells are within the grid.
        max_pos = pos[0] + size[0] - 1, pos[1] + size[1] - 1
        if max_pos[0] >= self.size[0] or max_pos[1] >= self.size[1]:
            raise NotAValidPosition
        # Get the contents already in those cells
        contents = self.get_content(pos, size)
        if not contents or (len(contents) == 1 and content in contents):
            self.remove(content)
            self._put(content, pos, size)
        else:
            raise CellsAreNotEmpty
 
