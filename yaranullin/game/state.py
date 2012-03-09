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


import logging
import os
import json
import bz2

from ..event_system import Listener, Event
from ..config import YR_SAVE_DIR


class ClientState(Listener):

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.state = {}

    def handle_game_event_update(self, ev_type, state):
        self.update_state(state)

    def load(self, new_state):
        events = []
        boards = new_state['boards']
        for board in boards:
            pawns = board.pop('pawns')
            active_pawn_uid = board.pop('active_pawn_uid')
            events.append(Event('game-event-board-new', **board))
            for pawn in pawns:
                events.append(Event('game-event-pawn-new', **pawn))
            events.append(Event('game-event-pawn-next', uid=active_pawn_uid))
        events.append(Event('game-event-board-change',
                            uid=new_state['active_board_uid']))
        return events

    def clear(self):
        events = []
        if 'boards' in self.state:
            boards = self.state['boards']['board']
            for board in boards:
                events.append(Event('game-event-board-del', uid=board['uid']))
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
        self.game_dir = None
        self.clean_exit = False
        self.state = {}
        self.uids = {}
        self.cache = {}

    def load(self, new_state):
        events = []
        boards = new_state['boards']
        for board in boards:
            pawns = board.pop('pawns')
            active_pawn_uid = board.pop('active_pawn_uid')
            events.append(Event('game-request-board-new', **board))
            for pawn in pawns:
                events.append(Event('game-request-pawn-new', **pawn))
            events.append(Event('game-request-pawn-next', uid=active_pawn_uid))
        events.append(Event('game-request-board-change',
                            uid=new_state['active_board_uid']))
        return events

    def load_from_file(self, dir_name):
        self.game_dir = os.path.join(YR_SAVE_DIR, dir_name)
        try:
            with open(os.path.join(self.game_dir, 'main.json'), 'r') as main:
                data = main.read()
        except IOError:
            logging.error('Error loading ' + self.game_dir)
        else:
            new_state = json.loads(data)
            events = self.load(new_state)
            self.post(*events)

    def save_to_file(self):
        data = json.dumps(self.state, indent=2, sort_keys=True)
        fname = os.path.join(self.game_dir, 'main.json')
        with open(fname, mode='w') as main:
            main.write(data)

    def handle_texture_request(self, ev_type, name):
        fname = os.path.join(self.game_dir, 'textures', name)
        event = None
        if name in self.cache:
            data = self.cache[name]
            event = Event('texture-update', name=name, data=data)
        else:
            try:
                with open(fname, 'rb') as f:
                    data = bz2.compress(f.read())
                event = Event('texture-update', name=name, data=data)
                # For now alpha is always False
                self.cache[name] = data
            except IOError:
                logging.error('Error loading image ' + fname)
        if event:
            self.post(event)

    def handle_game_load(self, ev_type, fname):
        self.load_from_file(fname)

    def handle_game_request_update(self, ev_type):
        event = Event('game-event-update', state=self.state)
        self.post(event)

    def handle_game_event_board_change(self, ev_type, uid):
        self.state['active_board_uid'] = uid

    def handle_game_event_board_new(self, ev_type, **kargs):
        if 'boards' not in self.state:
            self.state['boards'] = []
        board = kargs
        self.state['boards'].append(board)
        self.state['active_board_uid'] = board['uid']
        self.uids[board['uid']] = board

    def handle_game_event_board_del(self, ev_type, uid):
        boards = self.state['boards']
        if uid in self.uids:
            board = self.uids[uid]
            boards.remove(board)
            del self.uids[uid]

    def handle_game_event_pawn_next(self, ev_type, uid):
        board = self.uids[self.state['active_board_uid']]
        board['active_pawn_uid'] = uid

    def handle_game_event_pawn_new(self, ev_type, **kargs):
        board = self.uids[self.state['active_board_uid']]
        if 'pawns' not in board:
            board['pawns'] = []
        pawns = board['pawns']
        pawn = kargs
        pawns.append(pawn)
        self.uids[pawn['uid']] = pawn

    def handle_game_event_pawn_updated(self, ev_type, uid, **kargs):
        pawn = self.uids[uid]
        pawn.update(kargs)

    def handle_game_event_pawn_del(self, ev_type, uid):
        board = self.uids[self.state['active_board_uid']]
        pawn = self.uids[uid]
        del self.uids[uid]
        pawns = board['pawns']
        pawns.remove(pawn)

    def handle_quit(self, event):
        self.clean_exit = True

    def handle_game_save(self, ev_type):
        self.save_to_file()

#    def __del__(self):
#        """Dumps the game state in 'restore.yrn'.
#
#        This should save the game state in the likely event of a failure of
#        Yaranullin. This function is called when the instance of XMLDump is
#        garbage collected. It won't save a restore file if the cause of the
#        exit is a quit event.
#        """
#
#        if not self.clean_exit:
#            self.save_to_file('restore')
