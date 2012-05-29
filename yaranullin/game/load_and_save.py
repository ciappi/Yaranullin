# yaranullin/game/load_and_save.py
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

from xml.etree import ElementTree

from yaranullin.config import YR_SAVE_DIR
from yaranullin.game.board import Board
from yaranullin.game.cell_content import Pawn

_MAPS = {}


class ParseError(SyntaxError):
    ''' Error parsing tmx file '''


def _get_object_layer(tag, layer_name):
    for objectgroup in tag.findall('objectgroup'):
        if objectgroup.attrib['name'] == layer_name:
            return objectgroup


def _get_property(tag, name):
    ''' Get a property from within a tag '''
    properties = tag.find('properties')
    if properties is None:
        raise KeyError("No properties inside tag '%s'" % repr(tag))
    for prop in properties.findall('property'):
        if prop.attrib['name'] == name:
            return prop.attrib['value']
    raise KeyError("Property '%s' is not available" % name)


def _set_property(tag, name, value):
    ''' Get a property from within a tag '''
    properties = tag.find('properties')
    if not properties:
        properties = ElementTree.Element('properties')
        tag.append(properties)
    properties.append(ElementTree.Element('property', name=name, value=value))


def load_board_from_file(fname, ext=False):
    ''' Load and return a board from a tmx file '''
    complete_path = os.path.join(YR_SAVE_DIR, fname) 
    try:
        with open(complete_path) as tmx_file:
            tmx_map = tmx_file.read()
    except IOError:
        raise
    bname = os.path.splitext(os.path.basename(fname))[0]
    return load_board_from_tmx(bname, tmx_map, ext)


def load_board_from_tmx(bname, tmx_map, ext=False):
    ''' Load and return a board from a string '''
    try:
        tmx_map = ElementTree.fromstring(tmx_map)
    except:
        raise ParseError("Error parsing '%s'" % bname)
    # Save basic board attribute
    size = int(tmx_map.attrib['width']), int(tmx_map.attrib['height'])
    tilewidth = int(tmx_map.attrib['tilewidth'])
    if tilewidth != int(tmx_map.attrib['tileheight']):
        raise ParseError("tilewidth != tileheight: tiles must be square")
    # Create a new board
    board = Board(bname, size)
    # Find pawn object group
    pawn_layer = _get_object_layer(tmx_map, 'pawns')
    pawns = set()
    if pawn_layer is not None:
        for pawn in pawn_layer.findall('object'):
            name = pawn.attrib['name']
            # Minimum width and height must be 1
            size = (max(int(pawn.attrib['width']) // tilewidth, 1),
                    max(int(pawn.attrib['height']) // tilewidth, 1))
            pos = (int(pawn.attrib['x']) // tilewidth,
                    int(pawn.attrib['y']) // tilewidth)
            try:
                initiative = int(_get_property(pawn, 'initiative'))
            except KeyError:
                raise ParseError("Error parsing pawn '%s'" % name)
            pawn = Pawn(name, initiative, size)
            pawn.pos = pos
            pawns.add(pawn)
    # Now add the board to _MAPS
    _MAPS[board.name] = tmx_map
    return board, pawns


def get_tmx_board(bname, ext=False):
    ''' Return an tmx version of board '''
    if bname in _MAPS:
        return ElementTree.tostring(_MAPS[bname])
