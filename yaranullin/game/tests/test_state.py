# yaranullin/game/tests/test_state.py
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

import unittest

from xml.etree.ElementTree import XML
from main import TestBase
from ..state import load, dump, MirrorState


simple_xml_game = XML("""\
<yaranullin active_board_id="1234">
 <boards>
  <id_1234 name="Test Board" width="8" height="10" active_pawn_id="4321">
   <pawns>
    <id_4321 name="Pawn 1" width="1" height="2" x="1" y="2" initiative="20" />
    <id_4322 name="Pawn 2" width="3" height="3" x="4" y="4" initiative="2" />
   </pawns>
  </id_1234>
 </boards>
</yaranullin>
""")

simple_state_game = {'active_board_id': 1234,
 'boards': {1234: {'active_pawn_id': 4321,
                   'height': 10,
                   'name': 'Test Board',
                   'pawns': {4321: {'height': 2,
                                    'initiative': 20,
                                    'name': 'Pawn 1',
                                    'width': 1,
                                    'x': 1,
                                    'y': 2},
                             4322: {'height': 3,
                                    'initiative': 2,
                                    'name': 'Pawn 2',
                                    'width': 3,
                                    'x': 4,
                                    'y': 4}},
                   'width': 8}}}

events = [
{'width': 8, 'ev_type': 'game-request-board-new', 'name': 'Test Board',
    'height': 10},
{'width': 1, 'initiative': 20, 'name': 'Pawn 1', 'y': 2, 'x': 1,
    'ev_type': 'game-request-pawn-new', 'height': 2},
{'width': 3, 'initiative': 2, 'name': 'Pawn 2', 'y': 4, 'x': 4,
    'ev_type': 'game-request-pawn-new', 'height': 3},
{'ev_type': 'game-request-pawn-next', 'pawn_id': 4321},
{'board_id': 1234, 'ev_type': 'game-request-board-change'}
]


class TestBasic(unittest.TestCase):

    def test_load(self):
        state_loaded = load(simple_xml_game)
        self.assertEqual(simple_state_game, state_loaded)

    def test_dump(self):
        state_dumped = dump(simple_state_game)
        state_loaded = load(state_dumped)
        self.assertEqual(simple_state_game, state_loaded)


class TestMirrorState(TestBase):

    def test_load(self):
        ms = MirrorState(self.game)
        loaded_events = [e.__dict__ for e in ms.load(simple_state_game)]
        # Compare the arguments of all the events.
        self.assertEqual(events, loaded_events)
