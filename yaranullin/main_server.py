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

''' Implements command-line `server` command '''


from yaranullin.config import CONFIG
from yaranullin.event_system import EventManager, Event
from yaranullin.game.game import Game
from yaranullin.game.state import ServerState
from yaranullin.network.server import ServerNetworkWrapper
from yaranullin.spinner import CPUSpinner
from yaranullin.cmd_.command_prompt import CmdWrapper


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
        self.main_cpu_spinner = CPUSpinner(self.main_event_manager)
        self.cmd_wrapper = CmdWrapper(self.main_event_manager)
        self.network_wrapper = ServerNetworkWrapper(self.main_event_manager,
                                                    ('', port))
        self.game = Game(self.main_event_manager)
        self.state = ServerState(self.game)
        if args.game:
            event = Event('game-load', dname=args.game)
            self.main_event_manager.post(event)

    def run(self):
        ''' Run thread '''
        self.main_cpu_spinner.run()
