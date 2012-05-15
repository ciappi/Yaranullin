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
import logging

LOGGER = logging.getLogger(__name__)

from xml.etree import ElementTree

from yaranullin.config import YR_SAVE_DIR
from yaranullin.game.board import Board


def load_board_from_tmx(name):
    ''' Load and return a board from a tmx file '''
    complete_path = os.path.join(YR_SAVE_DIR, name) 
    tmx_map = None
    try:
        with open(complete_path) as tmx_file:
            tmx_map = ElementTree.fromstring(tmx_file.read())
    except IOError:
        pass
    if tmx_map is None:
        LOGGER.error("Cannot open tmx file '%s'", complete_path)
        return
    # Save basic board attribute
    name = os.path.splitext(os.path.basename(name))[0]
    width = int(tmx_map.attrib['width'])
    height = int(tmx_map.attrib['height'])
    tilewidth = int(tmx_map.attrib['tilewidth'])
    if tilewidth != int(tmx_map.attrib['tileheight']):
        LOGGER.error("tilewidth != tileheight: tiles must be square")
        return
    # Create a new board
    board =  Board(name, width, height)
    # Find pawn object groups
    pawns = None
    for objectgroup in tmx_map.findall('objectgroup'):
        if objectgroup.attrib['name'] in ('Pawns', 'pawns', 'PAWNS'):
            pawns = objectgroup
    if pawns is not None:
        for pawn in pawns.findall('object'):
            name = pawn.attrib['name']
            # Minimum width and height must be 1
            width = max(int(pawn.attrib['width']) // tilewidth, 1)
            height = max(int(pawn.attrib['height']) // tilewidth, 1)
            x = int(pawn.attrib['x']) // tilewidth
            y = int(pawn.attrib['y']) // tilewidth
            initiative = int(_get_property(pawn, 'initiative'))
            board.create_pawn(name, initiative, x, y, width, height)
    return board


def _get_property(tag, name):
    ''' Get a property from within a tag '''
    properties = tag.find('properties')
    for prop in properties.findall('property'):
        if prop.attrib['name'] == name:
            return prop.attrib['value']
    raise KeyError("Property '%s' is not available" % name)
