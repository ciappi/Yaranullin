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

"""Control classes for the game editor."""

import os
import shlex

import pygame.locals as PL

from yaranullin.event_system import Listener, Event
from yaranullin.game.state import State
from yaranullin.config import __version__, YR_DIR


class CommandPrompt(Listener, State):

    """Yaranullin's shell.
    
    This class is similar to the Cmd framework of Python but it fits better to
    Yaranullin's event system.

    Basically it defines a set of commands to modify the parameters of a game,
    i.e. adding/remove a board, adding/remove a pawn and so on.

    It tries to be as cross platform as possible, so it do not use readline or
    ncurses which are specific to Unixes.

    For now, apart from a very basic set of commands, it implements an help
    system and an history of the used commands (saved across different
    sessions).

    This class do not implements any graphic functions.
    
    """

    prompt = 'yrn$ '
    fhist = os.path.join(YR_DIR, 'history.log')

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        State.__init__(self)
        self.cmd_line = ''
        self.post(Event('prompt', prompt=self.prompt))
        self.generate_main_doc_string()
        # Tries to load the command history from disk.
        try:
            with open(self.fhist) as f:
                self.hist = (f.read()).split('\n')
        except IOError:
            self.hist = ['', ]
        self.hist_idx = len(self.hist) - 1

    def handle_quit(self, ev_type):
        """Save history upon quit."""
        # FIXME: the lenght of the history should be limited, maybe using a
        # deque instead of a simple list.
        with open(self.fhist, 'w+a') as f:
            for line in self.hist:
                if line:
                    f.write(line)
                    f.write('\n')

    def generate_main_doc_string(self):
        """Refactors this class docstring.
        
        Remove code related spaces and add a brief description of every
        available command (every method starting with 'do_' is a command).
        
        """
        lines = self.__doc__.split('\n')
        self.__doc__ = lines.pop(0).strip()
        for line in lines:
            self.__doc__ += '\n'
            self.__doc__ += line.strip()
        self.__doc__ += '\n\nCommands:'
        # Find all methods starting with 'do_'.
        _do_methods = (getattr(self, attr) for attr in dir(self)
                              if (attr.startswith('do_') and
                                 callable(getattr(self, attr))))
        # Get the first line of the docstring of every command.
        _do_docs = (m.__doc__.split('\n')[0] for m in _do_methods if m.__doc__)
        # Add those line to the docstring of this class
        for d in _do_docs:
            self.__doc__ += '\n'
            self.__doc__ += d

    def handle_key_down(self, ev_type, key, mod, unicode):
        """Define the basic functionality of a terminal.
        
        For now it is possible to type commands, delete characters by pressing
        backspace and browsing the command history with up and down keys.
        However, it is not yet possible to move the cursor left or right
        using arrows.
        
        """
        if key == PL.K_BACKSPACE:
            # Delete one character from the command line.
            self.cmd_line = self.cmd_line[:-1]
            self.hist[-1] = self.cmd_line
        elif key == PL.K_RETURN:
            # Try to execute a command.
            if not self.execute(self.cmd_line):
                # Command succeeds so update history and clear the command
                # line.
                self.hist[-1] = (self.cmd_line)
                self.hist.append('')
                self.hist_idx = len(self.hist) - 1
                self.cmd_line = ''
        elif key in (PL.K_UP, PL.K_DOWN):
            # Browse the command history.
            if key == PL.K_UP:
                idx = max(self.hist_idx - 1, 0)
            else:
                idx = min(self.hist_idx + 1, len(self.hist) - 1)
            self.cmd_line = self.hist[idx]
            self.hist_idx = idx
        else:
            self.cmd_line += unicode
            self.hist[-1] = self.cmd_line
        # Post an event with the current prompt saved as a string.
        self.post(Event('prompt', prompt=self.prompt + self.cmd_line))

    def parse_command(self, cmd):
        """Split a command using shlex."""
        try:
            return shlex.split(str(cmd))
        except ValueError:
            pass

    def execute(self, text):
        """Execute a command if the relative method if found.
        
        Returns True if the command fails.
        
        """
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

    def do_version(self, args):
        """version - display program version."""
        self.post(Event('print', text=__version__))

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

    def do_save(self, args):
        """save - save the state of the game to disk."""
        self.post(Event('game-save'))

    def do_boards(self, args):
        """boards - manage boards.
        Usage: board [commands] [args]
        boards - list all the boards
        boards 'uid' - change the active board
        boards add 'name' 'width' 'height' - add a board
        boards del 'uid' - delete a board from the current board
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
                if board["uid"] == self.state['active_board_uid']:
                    text += ' * '
                text += board['name'] + '    uid: ' + str(board['uid']) + '\n'
            self.post(Event('print', text=text))
        elif n == 1:
            try:
                uid = int(args.pop())
            except ValueError:
                return True
            self.post(Event('game-request-board-change', uid=uid))
        elif n >= 2:
            # Add a new board.
            cmd = args.pop(0)
            if cmd == 'add':
                if len(args) == 3:
                    self.post(Event('game-request-board-new', name=args[0],
                                    width=int(args[1]), height=int(args[2])))
            elif cmd == 'del':
                if len(args) == 1:
                    self.post(Event('game-event-board-del',
                                    uid=int(args.pop())))
        else:
            return True

    def do_pawns(self, args):
        """pawns - manage pawns.
        Usage: pawns [commands] [args]
        pawns - list all pawns
        pawns add 'name' 'x' 'y' 'width' 'height' - add a new pawn
        pawns del 'uid' - delete a pawn from the current board
        """
        n = len(args)
        if n == 0:
            text = ''
            try:
                board = self.uids[self.state['active_board_uid']]
                pawns = board['pawns']
            except KeyError:
                pawns = []
            for pawn in pawns:
                text += pawn['name'] + '    uid: ' + str(pawn['uid']) + '\n'
            self.post(Event('print', text=text))
        elif n >= 2:
            cmd = args.pop(0)
            if cmd == 'add':
                if len(args) == 6:
                    self.post(Event('game-request-pawn-new', name=args[0],
                                    initiative=int(args[1]), x=int(args[2]),
                                    y=int(args[3]), width=int(args[4]),
                                    height=int(args[5])))
            elif cmd == 'del':
                if len(args) == 1:
                    self.post(Event('game-event-pawn-del',
                                    uid=int(args.pop())))
        else:
            return True

    def do_tile(self, args):
        """tile - get or set a tile.
        Usage: tile 'x' 'y' [image]
        tile 'x' 'y' - show the name of the tile at x, y
        tile 'x' 'y' 'image' - set the tile at x, y to image
        """
        n = len(args)
        if n == 2:
            x, y = int(args[0]), int(args[1])
            board = self.uids[self.state['active_board_uid']]
            text = ''
            for tile in board["tiles"]:
                pos = (tile["x"], tile["y"])
                if (x, y) == pos:
                    text = tile["image"]
                    break
            self.post(Event('print', text=text))
        elif n == 3:
            x, y = int(args[0]), int(args[1])
            img = args[2]
            board = self.uids[self.state['active_board_uid']]
            text = ''
            for tile in board["tiles"]:
                pos = (tile["x"], tile["y"])
                if (x, y) == pos:
                    text = "Set tile " + str(x) + ", " + str(y) + " to: " + img
                    self.post(Event('update-tile', x=x, y=y, image=img))
                    break
            self.post(Event('print', text=text))
