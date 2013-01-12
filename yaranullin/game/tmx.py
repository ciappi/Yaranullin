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

from xml.etree import ElementTree

from yaranullin.config import YR_SAVE_DIR


class ParseError(SyntaxError):
    ''' Error parsing tmx file '''

#TODO: create a TmxBoard like a Board object, a TmxGame like a Game object
#      then a TmxWrapper like a GameWrapper.

class TmxBoard(object):

    def __init__(self, name, size, tilewidth):
        self.name = name
        self.size = size
        self.tilewidth = tilewidth
        self.layer = None
        self.properties = {}

    @classmethod
    def open(cls, fname):
        ''' Load and return a board from a tmx file '''
        complete_path = os.path.join(YR_SAVE_DIR, fname)
        with open(complete_path) as tmx_file:
            tmx_map = tmx_file.read()
        bname = os.path.splitext(os.path.basename(fname))[0]
        return TmxBoard.load(bname, tmx_map)

    @classmethod
    def load(cls, bname, tmx_map):
        ''' Load and return a board from a string '''
        try:
            tmx_map = ElementTree.fromstring(tmx_map)
        except:
            raise ParseError("Error parsing '%s'" % bname)
        # Save basic board attribute
        size = int(tmx_map.attrib['width']), int(tmx_map.attrib['height'])
        tilewidth = int(tmx_map.attrib['tilewidth'])
        return cls(bname, size, tilewidth)
