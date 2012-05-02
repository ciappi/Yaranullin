# yaranullin/cmd_/command_prompt.py
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

import cmd
import collections
import threading
import time

from yaranullin.config import __version__
from yaranullin.event_system import Listener, Event
from yaranullin.game.state import State


class CommandPrompt(cmd.Cmd, State, Listener):

    """Yaranullin's shell.
    
    This class takes the Cmd framework of Python and fits it to
    Yaranullin's event system.

    Basically it defines a set of commands to modify the parameters of a game,
    i.e. adding/remove a board, adding/remove a pawn and so on.
    """

    prompt = 'yrn> '
    intro = ('Yaranullin\'s server, version %s\nType "?" or "help" for help;\n'
            'Type "q" to exit.' % __version__)

    def __init__(self, event_manager):
        cmd.Cmd.__init__(self)
        State.__init__(self)
        Listener.__init__(self, event_manager)
        self.cmdqueue = collections.deque()
        self.keep_going = True
        self.parsing_commands = False

    def cmdloop(self, intro=None):
        """cmdloop"""

        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            while True:
                if self.parsing_commands:
                    # Do not prompt the user for input because other threads
                    # are processing commands and printing stuff on the
                    # screen.
                    time.sleep(0.001)
                    continue
                if not self.keep_going:
                    # If we use 'while self.keep_going:', there could be a
                    # condition where the user gets the prompt after issuing a
                    # quit command.
                    break
                if self.use_rawinput:
                    try:
                        line = raw_input(self.prompt)
                    except EOFError:
                        line = 'EOF'
                else:
                    self.stdout.write(self.prompt)
                    self.stdout.flush()
                    line = self.stdin.readline()
                    if not len(line):
                        line = 'EOF'
                    else:
                        line = line.rstrip('\r\n')
                if line:
                    self.parsing_commands = True
                    self.cmdqueue.append(line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    def handle_start(self, ev_type):
        threading.Thread(target=self.cmdloop).start()

    def handle_quit(self, ev_type):
        self.keep_going = False

    def handle_tick(self, ev_type):
        while self.cmdqueue:
            line = self.cmdqueue.popleft()
            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop, line)
            if stop:
                self.post(Event('quit'))
                self.keep_going = False
                break
        self.parsing_commands = False

    def do_EOF(self, line):
        """Shutdown the server"""
        return True

    do_quit = do_q = do_exit = do_EOF

    def do_version(self):
        """Display version information"""
        print __version__

    def do_save(self):
        """Save the state of the game to disk"""
        self.post(Event('game-save'))

    def do_boards(self, args):
        """Manage boards
        Usage: board [commands] [args]
        boards - list all the boards
        boards 'uid' - change the active board
        boards add 'name' 'width' 'height' - add a board
        boards del 'uid' - delete a board from the current board
        """
        args = args.split()
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
            print text
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
            print 'Bad arguments'

    def do_pawns(self, args):
        """Manage pawns
        Usage: pawns [commands] [args]
        pawns - list all pawns
        pawns add 'name' 'x' 'y' 'width' 'height' - add a new pawn
        pawns del 'uid' - delete a pawn from the current board
        """
        args = args.split()
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
            print text
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
        """Manage tiles
        Usage: tile 'x' 'y' [image]
        tile 'x' 'y' - show the name of the tile at x, y
        tile 'x' 'y' 'image' - set the tile at x, y to image
        """
        args = args.split()
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
            print text
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
