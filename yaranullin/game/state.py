# yaranullin/game/state.py
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

"""State of the game."""


import zipfile
import logging
import os
from xml.etree.ElementTree import Element, tostring, XML

from ..event_system import Listener, Event
from ..config import YR_SAVE_DIR


def _load(state_elem, xml_elem):
    """Recursive loading of an xml state to a state dict."""
    for key, value in xml_elem.attrib.items():
        try:
            value = int(value)
        except ValueError:
            value = eval(value) if value in ('False', 'True') else value
        state_elem[key] = value
    for sub_elem in xml_elem.getchildren():
        tag = sub_elem.tag
        prefix = 'id_'
        if tag.startswith(prefix):
            tag = int(tag[len(prefix):])
        state_elem[tag] = _load({}, sub_elem)
    return state_elem


def load(xml_state):
    """Return a state dict given the state as xml."""
    return _load({}, xml_state)


def _dump(xml_elem, state_elem):
    """Recursive convertion of a state dict to an xml document."""
    for key, value in state_elem.items():
        if isinstance(value, dict):
            # XML do not allow tag starting with a number
            if isinstance(key, int):
                key = 'id_' + str(key)
            sub_elem = Element(key)
            xml_elem.append(_dump(sub_elem, value))
        else:
            xml_elem.set(key, str(value))
    return xml_elem


def dump(state):
    """Return the xml representation of a state.

    The state is a dict and each of its keys can be a dict (will be
    converted into a child element), an int or string (converted to an
    attribute).

    """
    return _dump(Element('yaranullin'), state)


class ClientState(Listener):

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.state = {}

    def handle_game_event_update(self, ev_type, xml):
        self.update_state(load(XML(xml)))

    def load(self, new_state):
        events = []
        for board_id, board in new_state['boards'].items():
            args = [(key, value) for key, value in board.items() if key not in
                    ('active_pawn_id', 'pawns')]
            kargs = dict(args)
            events.append(Event('game-event-board-new', board_id=board_id,
                                **kargs))
            for pawn_id, pawn in board['pawns'].items():
                events.append(Event('game-event-pawn-new', pawn_id=pawn_id,
                                    **pawn))
        return events

    def clear(self):
        events = []
        if 'boards' in self.state:
            for key in self.state['boards']:
                if isinstance(key, int):
                    events.append(Event('game-event-board-del', board_id=key))
        return events

    def update_state(self, new_state):
        if self.state != new_state:
            events = []
            # Erase the old state.
            events += self.clear()
            # Load the new state.
            events += self.load(new_state)
            # Save the new state
            self.state = new_state
            if events:
                self.post(*events)


class ServerState(Listener):

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.save_dir = YR_SAVE_DIR
        self.clean_exit = False
        self.state = {}

    def load(self, new_state):
        events = []
        for board in new_state['boards'].values():
            args = [(key, value) for key, value in board.items() if key not in
                    ('active_pawn_id', 'pawns')]
            kargs = dict(args)
            events.append(Event('game-request-board-new', **kargs))
            for pawn in board['pawns'].values():
                events.append(Event('game-request-pawn-new', **pawn))
        return events

    def load_from_file(self, fname):
        fname = os.path.join(self.save_dir, fname)
        try:
            with zipfile.ZipFile(fname, 'r') as yrn_file:
                data = yrn_file.read('main.xml')
        except (zipfile.BadZipfile, KeyError, IOError):
            logging.error('Invalid file name ' + fname)
        else:
            new_state = load(XML(data))
            events = self.load(new_state)
            self.post(*events)

    def save(self):
        xml_state = dump(self.state)
        return tostring(xml_state, encoding='utf-8')

    def save_to_file(self, fname):
        data = self.save()
        fname = os.path.join(self.save_dir, fname + '.yrn')
        with zipfile.ZipFile(fname, mode='w') as zf:
            zf.writestr('main.xml', data)

    def handle_game_load(self, ev_type, fname):
        self.load_from_file(fname)

    def handle_game_request_update(self, ev_type):
        event = Event('game-event-update', xml=self.save())
        self.post(event)

    def handle_game_event_board_change(self, ev_type, board_id):
        self.state['active_board_id'] = board_id

    def handle_game_event_board_new(self, ev_type, board_id, **kargs):
        if 'boards' not in self.state:
            self.state['boards'] = {}
        self.state['boards'][board_id] = kargs
        self.state['boards'][board_id]['pawns'] = {}
        self.state['active_board_id'] = board_id

    def handle_game_event_board_del(self, ev_type, board_id):
        del self.state['boards'][board_id]

    def handle_game_event_pawn_next(self, ev_type, pawn_id):
        board_id = self.state['active_board_id']
        self.state['boards'][board_id]['active_pawn_id'] = pawn_id

    def handle_game_event_pawn_new(self, ev_type, pawn_id, **kargs):
        board_id = self.state['active_board_id']
        if 'pawns' not in self.state['boards'][board_id]:
            self.state['boards'][board_id]['pawns'] = {}
        self.state['boards'][board_id]['pawns'][pawn_id] = kargs

    def handle_game_event_pawn_updated(self, ev_type, pawn_id, **kargs):
        board_id = self.state['active_board_id']
        self.state['boards'][board_id]['pawns'][pawn_id].update(**kargs)

    def handle_game_event_pawn_del(self, ev_type, pawn_id):
        board_id = self.state['active_board_id']
        del self.state['boards'][board_id]['pawns'][pawn_id]

    def handle_quit(self, event):
        self.clean_exit = True

    def handle_game_save(self, ev_type, fname):
        self.save_to_file(fname)

    def __del__(self):
        """Dumps the game state in 'restore.yrn'.

        This should save the game state in the likely event of a failure of
        Yaranullin. This function is called when the instance of XMLDump is
        garbage collected. It won't save a restore file if the cause of the
        exit is a quit event.
        """

        if not self.clean_exit:
            self.save_to_file('restore')
