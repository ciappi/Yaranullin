# yaranullin/run_server.py
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

# install_twisted_rector must be called before importing  and using the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()

from twisted.internet import reactor

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label

from yaranullin.config import CONFIG
from yaranullin.event_system import step
from yaranullin.game.game_wrapper import GameWrapper
from yaranullin.network.protocol import YaranullinServerFactory

HOST = ''
PORT = CONFIG.getint('network', 'port')
GAME = GameWrapper()


class TwistedServerApp(App):
    def build(self):
        self.label = Label(text="server started\n")
        reactor.listenTCP(PORT, YaranullinServerFactory())
        Clock.schedule_interval(step, 1 / 10.)
        return self.label


def run(args):
    ''' Main loop for the server '''
    #GAME.load_from_files(args.board)
    TwistedServerApp().run()
