# yaranullin/editor/control.py
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


"""Yaranullin's shell.

Commands:
ls - list something
"""



import shlex

import pygame.locals as PL

from pygcurse import pygcurse
from yaranullin.event_system import Listener, Event
from yaranullin.game.state import State


class CommandPrompt(Listener, State):

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        State.__init__(self)
        self.text_box = pygcurse.PygcurseTextbox(self.win,
                                                 region=(0, 21, 80, 3),
                                                 caption="shell")

    @property
    def win(self):
        return self.event_manager.win

    def __set_prompt(self, text):
        self.text_box.text = text

    def __get_prompt(self):
        return self.text_box.text

    prompt = property(__get_prompt, __set_prompt)

    def handle_tick(self, ev_type, dt):
        self.text_box.update()

    def handle_game_event_board_new(self, ev_type, **kargs):
        self.new_board(**kargs)

    def handle_key_down(self, ev_type, key, mod, unicode):
        if key == PL.K_BACKSPACE:
            self.prompt = self.prompt[:-1]
        elif key == PL.K_RETURN:
            if not self.execute(self.prompt):
                self.prompt = ''
        else:
            self.prompt += unicode

    def parse_command(self, cmd):
        try:
            return shlex.split(str(cmd))
        except ValueError:
            pass

    def execute(self, text):
        args = self.parse_command(text)
        if args:
            command = args.pop(0)
        else:
            command = None
        if command == 'clear':
            self.post(Event('print', text=''))
        elif command == 'quit':
            self.post(Event('quit'))
        elif command == 'boards':
            return self.boards(args)
        elif command == 'help':
            self.post(Event('print', text=__doc__))
        else:
            return True

    def boards(self, args):
        n = len(args)
        if n == 0:
            # Just list the boards in the game, if any.
            text = ''
            try:
                boards = self.state['boards']
            except KeyError:
                boards = []
            for board in boards:
                text += board['name'] + '\n'
            self.post(Event('print', text=text))
        elif n >= 2:
            # Add a new board.
            # board add --name test_board -w 3 -h 2
            if args.pop(0) == 'add':
                if len(args) == 6:

        else:
            return True
