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


import shlex

import pygame.locals as PL

from yaranullin.event_system import Listener, Event
from yaranullin.game.state import State


class CommandPrompt(Listener, State):

    """Yaranullin's shell."""

    prompt = 'yrn$ '

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        State.__init__(self)
        self.cmd_line = ''
        self.post(Event('prompt', prompt=self.prompt))
        self.generate_main_doc_string()

    def generate_main_doc_string(self):
        lines = self.__doc__.split('\n')
        self.__doc__ = lines.pop(0).strip()
        for line in lines:
            self.__doc__ += '\n'
            self.__doc__ += line.strip()
        self.__doc__ += '\n\nCommands:'
        _do_methods = (getattr(self, attr) for attr in dir(self)
                              if (attr.startswith('do_') and
                                 callable(getattr(self, attr))))
        _do_docs = (m.__doc__.split('\n')[0] for m in _do_methods if m.__doc__)
        for d in _do_docs:
            self.__doc__ += '\n'
            self.__doc__ += d

    def handle_game_event_board_new(self, ev_type, **kargs):
        self.new_board(**kargs)

    def handle_key_down(self, ev_type, key, mod, unicode):
        if key == PL.K_BACKSPACE:
            self.cmd_line = self.cmd_line[:-1]
        elif key == PL.K_RETURN:
            if not self.execute(self.cmd_line):
                self.cmd_line = ''
        else:
            self.cmd_line += unicode
        self.post(Event('prompt', prompt=self.prompt + self.cmd_line))

    def parse_command(self, cmd):
        try:
            return shlex.split(str(cmd))
        except ValueError:
            pass

    def execute(self, text):
        method = None
        args = self.parse_command(text)
        if args:
            command = args.pop(0)
            if hasattr(self, 'do_' + command):
                method = getattr(self, 'do_' + command)
        if callable(method):
            method(args)
        else:
            return True

    def do_help(self, args):
        """help - get help for available commands.
        Usage: help [command]
        """
        help_str = ''
        n = len(args)
        if n == 1:
            arg = args.pop()
            try:
                method = getattr(self, 'do_' + arg)
                if not callable(method):
                    raise AttributeError
            except AttributeError:
                help_str = "Unknown command '" + str(arg) + "'"
            else:
                doc = method.__doc__ if method.__doc__ else ''
                lines = doc.split('\n')
                for line in lines:
                    help_str += line.strip()
                    help_str += '\n'
        elif n == 0:
            help_str = self.__doc__
        self.post(Event('print', text=help_str))

    def do_quit(self, args):
        """quit - quit Yaranullin."""
        self.post(Event('quit'))

    def do_clear(self, args):
        """clear - clear the output window."""
        self.post(Event('print', text=''))

    def do_boards(self, args):
        """boards - manage boards.
        Usage: board [commands] [args]
        board - list all the boards
        board add 'name' 'width' 'height' - add a board
        """
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
                    pass
        else:
            return True
