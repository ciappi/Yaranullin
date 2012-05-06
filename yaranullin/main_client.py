# yaranullin/main_client.py
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

''' Implements command-line `client` command '''


import threading

from yaranullin.config import CONFIG
from yaranullin.event_system import EventManager, Event
from yaranullin.cache import Cache
from yaranullin.game.state import ClientState
from yaranullin.pygame_.gui import SimpleGUI
from yaranullin.pygame_.base.spinner import PygameCPUSpinner
from yaranullin.network.client import ClientNetworkWrapper
from yaranullin.spinner import CPUSpinner


class ClientRunner(object):

    """Yaranullin Client.

    setup a client network spinner
    setup pygame controllers and views
    post a join event

    """

    def __init__(self, args):
        self.main_event_manager = EventManager()
        self.main_cpu_spinner = CPUSpinner(self.main_event_manager)
        self.network_wrapper = ClientNetworkWrapper(self.main_event_manager)
        self.mirror_state = ClientState(self.main_event_manager)
        self.cache = Cache(self.main_event_manager)
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
        ''' Run thread '''
        self.pygame_thread.start()
        self.main_cpu_spinner.run()
        self.pygame_thread.join()
