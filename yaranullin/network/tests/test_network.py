# yaranullin/network/tests/test_network.py
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


import unittest
import threading
from time import sleep

from ..server import ServerNetworkSpinner
from ..client import ClientNetworkSpinner
from ...event_system import EventManager, Event, Listener


class DummyListener(Listener):

    events = []

    def handle_game_request_pawn_next(self, ev_type, **kargs):

        event = Event(ev_type, **kargs)
        self.events.append(event)


class DummyListener2(Listener):

    events = []

    def handle_game_event_update(self, ev_type, **kargs):

        print 'dummy listener got event'
        event = Event(ev_type, **kargs)
        print event.__dict__
        self.events.append(event)


class test_network(unittest.TestCase):

    def setUp(self):

        # Server
        em = EventManager()
        self.dummy = DummyListener(em)
        spinner = ServerNetworkSpinner(em, ('', 44444))
        self.spinner_server_thread = threading.Thread(target=spinner.run)
        self.spinner_server_thread.start()
        self.event_manager_server = em
        self.server_spinner = spinner
        # Client
        em = EventManager()
        spinner = ClientNetworkSpinner(em)
        self.dummy2 = DummyListener2(em)
        self.spinner_client_thread = threading.Thread(target=spinner.run)
        self.spinner_client_thread.start()
        em.post(Event('join', host='127.0.0.1', port=44444))
        self.event_manager_client = em
        self.client_spinner = spinner

#    def test_client_to_server(self):
#        """Test the transmission of a simple 'test' event."""
#        test_event = Event('game-request-pawn-next', id=1024)
#        self.event_manager_client.post(test_event)
#        sleep(2)
#        self.assertEqual(1, len(self.dummy.events))
#        self.assertEqual(test_event.ev_type, self.dummy.events[0].ev_type)
#        self.assertEqual(test_event.id, self.dummy.events[0].id)

    def test_server_to_client(self):
        """Test the transmission of a simple 'test' event."""
        test_event = Event('game-event-update', id=2048)
        self.event_manager_server.post(test_event)
        sleep(2)
        self.assertEqual(1, len(self.dummy2.events))
        self.assertEqual(test_event.ev_type, self.dummy2.events[0].ev_type)
        self.assertEqual(test_event.id, self.dummy2.events[0].id)

    def tearDown(self):

        # Client
        em = self.event_manager_client
        spinner = self.spinner_client_thread
        em.post(Event('quit'))
        spinner.join()
        # Server
        em = self.event_manager_server
        spinner = self.spinner_server_thread
        em.post(Event('quit'))
        spinner.join()
