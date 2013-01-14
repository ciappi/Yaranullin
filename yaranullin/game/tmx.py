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


TW = 32


class ParseError(SyntaxError):
    ''' Error parsing tmx file '''


class Object(ElementTree.Element):

    def __init__(self):
        super(Object, self).__init__('object')
        self._properties = ElementTree.Element('properties')
        self.append(self._properties)

    def _get_size(self):
        return self.get('width') / TW, self.get('height') / TW

    def _set_size(self, value):
        self.set('width', value[0] * TW)
        self.set('height', value[1] * TW)

    size = property(_get_size, _set_size)

    def _get_pos(self):
        return self.get('x') / TW, self.get('y') / TW

    def _set_pos(self, value):
        self.set('x', value[0] * TW)
        self.set('y', value[1] * TW)

    pos = property(_get_pos, _set_pos)

    def set_property(self, name, value):
        for prop in self._properties.findall('property'):
            if prop.attrib['name'] == name:
                prop.attrib['value'] = value
                return
        prop = ElementTree.Element('property', name=name,
            value=value)
        self._properties.append(prop)

    def get_property(self, name):
        for prop in self._properties.findall('property'):
            if prop.attrib['name'] == name:
                return prop.attrib['value']


class TmxPawn(Object):

    def __init__(self, name, initiative, size):
        super(TmxPawn, self).__init__()
        self.set('name', name)
        self.set_property('initiative', initiative)
        self.size = size


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
