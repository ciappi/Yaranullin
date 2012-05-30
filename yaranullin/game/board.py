# yaranullin/game/board.py
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

''' Board object '''

import logging

LOGGER = logging.getLogger(__name__)

from yaranullin.game.cell_content import Pawn
from yaranullin.game.grid import Grid


class Board(object):
    
    ''' The board where the pawns lie '''

    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.initiatives = []
        self.pawns = {}
        self._grid = Grid(size)
        LOGGER.debug("Initialized board '%s' with size (%d, %d)", name,
                size[0], size[1])

    def _place_pawn(self, pawn, pos, size):
        ''' Place a pawn on the grid '''
        contents = self._grid.get(pos, size)
        # Add a pawn only if the cells are empty or taken by this pawn
        if contents and pawn not in contents:
            raise IndexError
        self._grid.remove(pawn)
        self._grid.add(pawn, pos, size)

    def create_pawn(self, name, initiative, pos, size):
        ''' Create a new Pawn '''
        pawn = Pawn(name, initiative, size)
        try:
            self._place_pawn(pawn, pos, size)
        except IndexError:
            LOGGER.warning("Cannot create pawn '%s' at pos (%d, %d) with "
                "size (%d, %d)", name, pos[0], pos[1], size[0], size[1])
        else:
            self.pawns[pawn.name] = pawn
            self.initiatives.append(pawn)
            self.initiatives.sort(key=lambda pawn: pawn.initiative,
                    reverse=True)
            LOGGER.info("Created a pawn with name '%s' inside board '%s'", name,
                    self.name)
            return pawn

    def del_pawn(self, name):
        ''' Delete the pawn 'name' '''
        try:
            pawn = self.pawns.pop(name)
        except KeyError:
            LOGGER.warning("Pawn '%s' was not in board '%s'", name,
                self.name)
        else:
            self.initiatives.remove(pawn)
            self._grid.remove(pawn)
            LOGGER.info("Removed pawn '%s' from board '%s'", name,
                    self.name)
            return pawn

    def move_pawn(self, name, pos, size=None):
        ''' Move the pawn 'name' to pos'''
        LOGGER.debug("Moving pawn '%s' to (%d, %d)...", name, pos[0], pos[1])
        try:
            pawn = self.pawns[name]
            if size is None:
                size = pawn.size
            self._place_pawn(pawn, pos, size)
        except KeyError:
            LOGGER.warning("Pawn '%s' was not in board '%s'", name,
                self.name)
        except IndexError:
            LOGGER.warning("Cannot move pawn '%s' of size (%d, %d) at "
                "pos (%d, %d) within board '%s'", name, size[0], size[1],
                pos[0], pos[1], self.name)
        else:
            LOGGER.info("Moved pawn '%s' at pos (%d, %d) within board '%s'",
                    name, pos[0], pos[1], self.name)
            return pawn
