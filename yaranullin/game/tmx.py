# -*- coding: utf-8 *-*
# yaranullin/game/tmx.py
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

LOGGER = logging.getLogger(__name__)

from xml.etree import ElementTree


TW = 32


class Object(ElementTree.Element):

    def __init__(self):
        super(Object, self).__init__('object')
        self._properties = ElementTree.Element('properties')
        self.append(self._properties)

    def _get_size(self):
        return (int(self.get('width')) / TW,
            int(self.get('height')) / TW)

    def _set_size(self, value):
        self.set('width', str(value[0] * TW))
        self.set('height', str(value[1] * TW))

    size = property(_get_size, _set_size)

    def _get_pos(self):
        return (int(self.get('x')) / TW,
            int(self.get('y')) / TW)

    def _set_pos(self, value):
        self.set('x', str(value[0] * TW))
        self.set('y', str(value[1] * TW))

    pos = property(_get_pos, _set_pos)

    def set_property(self, name, value):
        for prop in self._properties.findall('property'):
            if prop.attrib['name'] == name:
                prop.attrib['value'] = value
                return
        prop = ElementTree.Element('property', name=name,
            value=str(value))
        self._properties.append(prop)

    def get_property(self, name):
        for prop in self._properties.findall('property'):
            if prop.attrib['name'] == name:
                try:
                    return int(prop.attrib['value'])
                except ValueError:
                    return prop.attrib['value']


class TmxPawn(Object):

    def __init__(self, name, initiative, size):
        super(TmxPawn, self).__init__()
        self.set('name', name)
        self.set_property('initiative', initiative)
        self.size = size


class TmxBoard(ElementTree.Element):

    VERSION = '1.0'

    def __init__(self, name, size):
        super(TmxBoard, self).__init__('map')
        self.set('version', self.VERSION)
        self.set('orientation', 'orthogonal')
        self.set('name', name)
        self.set('width', str(size[0]))
        self.set('height', str(size[1]))
        self.set('tilewidth', str(TW))
        self.set('tileheight', str(TW))
        self.grid = ElementTree.Element('layer', name='bg',
            width=str(size[0]), height=str(size[1]))
        self.tiles = ElementTree.Element('data', encoding='base64',
            compression='zlib')
        self.tiles.text = ''
        self.grid.append(self.tiles)
        self.append(self.grid)
        self.pawns = ElementTree.Element('objectgroup',
            name='pawns', width=str(size[0]), height=str(size[1]))
        self.append(self.pawns)

    def _get_pawn(self, name):
        for pawn in self.pawns.findall('object'):
            if pawn.get('name') == name:
                return pawn

    def create_pawn(self, name, initiative, pos, size):
        pawn = self._get_pawn(name)
        if pawn is not None:
            return
        pawn = TmxPawn(name, initiative, size)
        pawn.pos = pos
        self.pawns.append(pawn)

    def del_pawn(self, name):
        pawn = self._get_pawn(name)
        if pawn is not None:
            self.pawns.remove(pawn)

    def move_pawn(self, name, pos, size=None):
        pawn = self._get_pawn(name)
        if pawn is not None:
            pawn.pos = pos


class TmxGame(object):

    def __init__(self):
        self.boards = {}

    def create_board(self, name, size):
        self.boards[name] = TmxBoard(name, size)

    def del_board(self, name):
        if name in self.boards:
            del self.boards[name]

    def create_pawn(self, bname, pname, initiative, pos, size):
        if bname not in self.boards:
            return
        self.boards[bname].create_pawn(pname, initiative, pos, size)

    def move_pawn(self, bname, pname, pos, size=None):
        if bname not in self.boards:
            return
        self.boards[bname].create_pawn(pname, pos, size)

    def del_pawn(self, bname, pname):
        if bname not in self.boards:
            return
        self.boards[bname].del_pawn(pname)

    def clear(self):
        ''' Clear all the boards '''
        self.boards.clear()
        LOGGER.info("Deleted all boards from the game")
