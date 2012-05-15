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

from yaranullin.game.cell_content import Pawn
from yaranullin.game.grid import Grid, CellsAreNotEmpty, NotAValidPosition


class Board(object):
    
    ''' The board where the pawns lie '''

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.initiatives = []
        self.pawns = {}
        self.grid = Grid(width, height)

    def create_pawn(self, name, initiative, x, y, width, height):
        ''' Create a new Pawn '''
        pawn = Pawn(name, initiative, width, height)
        try:
            self.grid.place(pawn, x, y)
        except (NotAValidPosition, CellsAreNotEmpty):
            pass
        else:
            self.pawns[pawn.name] = pawn
            self.initiatives.append(pawn)
            self.initiatives.sort(key=lambda pawn: pawn.initiative,
                    reverse=True)

    def del_pawn(self, name):
        ''' Delete the pawn 'name' '''
        try:
            pawn = self.pawns.pop(name)
            self.initiatives.remove(pawn)
        except KeyError:
            return

    def move_pawn(self, pawn, x, y):
        ''' Move the pawn 'name' to x, y '''
        try:
            self.grid.place(pawn, x, y)
        except (NotAValidPosition, CellsAreNotEmpty):
            pass
