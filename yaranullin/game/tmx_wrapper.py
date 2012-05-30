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

from xml.etree import ElementTree

from yaranullin.config import YR_SAVE_DIR
from yaranullin.event_system import post, connect


class ParseError(SyntaxError):
    ''' Error parsing tmx file '''


def _get_object_layer(tag, layer_name):
    ''' Get a layer of a tmx map '''
    for objectgroup in tag.findall('objectgroup'):
        if objectgroup.attrib['name'] == layer_name:
            return objectgroup


def _get_property(tag, name):
    ''' Get a property of a tmx map '''
    properties = tag.find('properties')
    if properties is None:
        raise KeyError("No child element 'properties' inside tag '%s'" %
                repr(tag))
    for prop in properties.findall('property'):
        if prop.attrib['name'] == name:
            return prop.attrib['value']
    raise KeyError("Property '%s' is not available" % name)


def _set_property(tag, name, value):
    ''' Set a property of a tmx map '''
    properties = tag.find('properties')
    if not properties:
        properties = ElementTree.Element('properties')
        tag.append(properties)
    properties.append(ElementTree.Element('property', name=name, value=value))


class TmxWrapper(object):

    def __init__(self):
        self._maps = {}
        connect('game-event-pawn-moved', self.move_pawn)

    def move_pawn(self, event_dict):
        ''' Change pawn position '''
        bname = event_dict['bname']
        pname = event_dict['pname']
        pos = event_dict['pos']
        try:
            xml_board = self._maps[bname]
        except KeyError:
            # The board was not loaded from a file
            return
        pawn_layer = _get_object_layer(xml_board, 'pawns')
        for pawn in pawn_layer.findall('object'):
            name = pawn.attrib['name']
            if name == pname:
                pawn.attrib['width'] = pos[0]
                pawn.attrib['height'] = pos[0]

    def load_board_from_file(self, fname):
        ''' Load and return a board from a tmx file '''
        complete_path = os.path.join(YR_SAVE_DIR, fname) 
        with open(complete_path) as tmx_file:
            tmx_map = tmx_file.read()
        bname = os.path.splitext(os.path.basename(fname))[0]
        self.load_board_from_tmx(bname, tmx_map)


    def load_board_from_tmx(self, bname, tmx_map):
        ''' Load and return a board from a string '''
        try:
            tmx_map = ElementTree.fromstring(tmx_map)
        except:
            raise ParseError("Error parsing '%s'" % bname)
        events = []
        # Save basic board attribute
        size = int(tmx_map.attrib['width']), int(tmx_map.attrib['height'])
        tilewidth = int(tmx_map.attrib['tilewidth'])
        if tilewidth != int(tmx_map.attrib['tileheight']):
            raise ParseError("tilewidth != tileheight: tiles must be square")
        # Append a new board event
        board_event = ('game-request-board-new', dict(name=bname, size=size))
        events.append(board_event)
        # Find pawn object group
        pawn_layer = _get_object_layer(tmx_map, 'pawns')
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
                    raise ParseError("Error parsing pawn '%s': missing "
                            "initiative value" % name)
                new_pawn_event = ('game-request-pawn-new', dict(bname=bname,
                        pname=name, initiative=initiative, pos=pos,
                        size=size))
                events.append(new_pawn_event)
        # Now add the board to _maps
        self._maps[bname] = tmx_map
        for event in events:
            post(event[0], event[1])


    def get_tmx_board(self, bname):
        ''' Return an tmx version of board '''
        if bname in self._maps:
            return ElementTree.tostring(self._maps[bname])

