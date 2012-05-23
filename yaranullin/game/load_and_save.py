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


class ParseError(SyntaxError):
    ''' Error parsing tmx file '''


def load_board_from_tmx(name, in_place=True):
    ''' Load and return a board from a tmx file '''
    if in_place:
        from yaranullin.game.board import Board
    else:
        from yaranullin.event_system import post
    complete_path = os.path.join(YR_SAVE_DIR, name) 
    try:
        with open(complete_path) as tmx_file:
            tmx_map = ElementTree.fromstring(tmx_file.read())
    except IOError:
        raise
    except:
        raise ParseError("Error parsing '%s'" % complete_path)
    # Save basic board attribute
    bname = os.path.splitext(os.path.basename(name))[0]
    size = int(tmx_map.attrib['width']), int(tmx_map.attrib['height'])
    tilewidth = int(tmx_map.attrib['tilewidth'])
    if tilewidth != int(tmx_map.attrib['tileheight']):
        raise ParseError("tilewidth != tileheight: tiles must be square")
    if in_place:
        # Create a new board
        board = Board(name, size)
    else:
        # Request a new board
        post('game-request-board-new', name=bname, size=size)
    # Find pawn object groups
    pawns = None
    for objectgroup in tmx_map.findall('objectgroup'):
        if objectgroup.attrib['name'] in ('Pawns', 'pawns', 'PAWNS'):
            pawns = objectgroup
            break
    if pawns is not None:
        for pawn in pawns.findall('object'):
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
            if in_place:
                board.create_pawn(name, initiative, pos, size)
            else:
                post('game-request-pawn-new', bname=bname, pname=name,
                        initiative=initiative, pos=pos, size=size)
    if in_place:
        return board


def _get_property(tag, name):
    ''' Get a property from within a tag '''
    properties = tag.find('properties')
    for prop in properties.findall('property'):
        if prop.attrib['name'] == name:
            return prop.attrib['value']
    raise KeyError("Property '%s' is not available" % name)
