# -*- coding: utf-8 *-*
# yaranullin/game/tmx_wrapper.py
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

import os
import logging

LOGGER = logging.getLogger(__name__)

from xml.etree import ElementTree

from yaranullin.config import YR_SAVE_DIR
from yaranullin.event_system import connect


class ParseError(SyntaxError):
    ''' Error parsing tmx file '''


class TmxBoard(object):

    def __init__(self, name, size, tilewidth):
        self.name = name
        self.size = size
        self.tilewidth = tilewidth
        self.pawns = {}

    def create_pawn(self, name, initiative, pos, size):
        pass

    def del_pawn(self, name):
        pass

    def move_pawn(self, name, pos, size=None):
        pass


class TmxGame(object):

    def __init__(self):
        self.boards = {}

    def create_board(self, name, size, tilewidth):
        pass

    def del_board(self, name):
        pass

    def create_pawn(self, bname, pname, initiative, pos, size):
        pass

    def move_pawn(self, bname, pname, pos, size=None):
        pass

    def del_pawn(self, bname, pname):
        pass

    def clear(self):
        ''' Clear all the boards '''
        self.boards.clear()
        LOGGER.info("Deleted all boards from the game")


class TmxInterface(object):

    def __init__(self):
        self.game = TmxGame()
        connect('game-event-board-new', self.create_board)
        connect('game-event-board-del', self.del_board)
        connect('game-event-pawn-new', self.create_pawn)
        connect('game-event-pawn-move', self.move_pawn)
        connect('game-event-pawn-del', self.del_pawn)
        LOGGER.debug("TmxInterface initialized")

    def create_board(self, event_dict):
        pass

    def del_board(self, event_dict):
        pass

    def create_pawn(self, event_dict):
        pass

    def move_pawn(self, event_dict):
        pass

    def del_pawn(self, event_dict):
        pass

    def clear(self):
        pass
