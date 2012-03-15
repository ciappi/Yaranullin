# yaranullin/main.py
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


import sys
import threading

from yaranullin.config import CONFIG
from yaranullin.event_system import EventManager, Event
from yaranullin.game.game import Game
from yaranullin.game.state import ServerState, ClientState
from yaranullin.pygame_.gui import SimpleGUI
from yaranullin.pygame_.base.spinner import PygameCPUSpinner
from yaranullin.network.server import ServerNetworkSpinner
from yaranullin.network.client import ClientNetworkSpinner


class ServerRunner(object):

    """Yaranullin Server.

    setup a game model
    setup a server network spinner
    setup a file controller
    load a game if a file name is provided as a command line argument.

    """

    def __init__(self, args):
        self.main_event_manager = EventManager()
        if args.port:
            port = args.port
        else:
            port = CONFIG.getint('network', 'port')
        self.main_cpu_spinner = ServerNetworkSpinner(self.main_event_manager,
                                                     ('', port))
        self.game = Game(self.main_event_manager)
        self.state = ServerState(self.game)
        if args.game:
            event = Event('game-load', dname=args.game)
            self.main_event_manager.post(event)

    def run(self):
        self.main_cpu_spinner.run()


class ClientRunner(object):

    """Yaranullin Client.

    setup a client network spinner
    setup pygame controllers and views
    post a join event

    """

    def __init__(self, args):
        self.main_event_manager = EventManager()
        self.main_cpu_spinner = ClientNetworkSpinner(self.main_event_manager)
        self.mirror_state = ClientState(self.main_event_manager)
        self.pygame_gui = SimpleGUI(self.main_event_manager)
        self.pygame_spinner = PygameCPUSpinner(self.pygame_gui)
        self.pygame_thread = threading.Thread(target=self.pygame_spinner.run)
        if args.port:
            port = args.port
        else:
            port = CONFIG.getint('network', 'port')
        if args.host:
            host = args.host
        else:
            host = CONFIG.get('network', 'host')
        self.main_event_manager.post(Event('join', host=host, port=port))

    def run(self):
        self.pygame_thread.start()
        self.main_cpu_spinner.run()
        self.pygame_thread.join()


def main(args):

    runner = None
    mode = args.mode
    if mode == 'server':
        print 'Launching a server...'
        runner = ServerRunner(args)
    elif mode == 'client':
        print 'Launching a client...'
        runner = ClientRunner(args)
    if runner:
        if args.debug:
            runner.run()
        else:
            try:
                runner.run()
            except:
                sys.exit('Unexpected error.')
