# yaranullin/network/client.py
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

""" Network client """


import time
import asyncore

from yaranullin.event_system import Event
from yaranullin.network.base import EndPoint, NetworkView, NetworkController, \
                                    NetworkSpinner


STATE_DISCONNECTED, STATE_CONNECTING, STATE_CONNECTED = range(3)


class State(object):

    def __init__(self, state):
        self._state = state

    def get_state(self):
        """Return the current state"""
        return self._state

    def set_state(self, state):
        """Set the internal state to a new value"""
        self._state = state


STATE = State(STATE_DISCONNECTED)


class ClientNetworkController(NetworkController):
    """ Client-side network controller """


class ClientNetworkView(NetworkView):

    """Basic NetworkView for a client.

    The client can only move pawns and request the next pawn according to
    initiative order.

    """

    handle_game_request_pawn_move = NetworkView.add_to_out_queue
    handle_game_request_pawn_place = NetworkView.add_to_out_queue
    handle_game_request_pawn_next = NetworkView.add_to_out_queue
    handle_game_request_update = NetworkView.add_to_out_queue
    handle_resource_request = NetworkView.add_to_out_queue


class ClientEndPoint(EndPoint):

    """Client EndPoint."""

    def __init__(self, host, port, view, controller):
        """Setup the client end point."""
        EndPoint.__init__(self)
        # Connect to the server.
        self.connect((host, port))
        self.view = view
        self.controller = controller
        self.view.end_point = self
        self.controller.end_point = self

    def handle_close(self):
        # Delete every reference to view and controller so that they will be
        # garbage collected.
        EndPoint.handle_close(self)
        self.view.end_point = self.controller.end_point = None
        self.view = self.controller = None
        STATE.set_state(STATE_DISCONNECTED)


class ClientNetworkSpinner(NetworkSpinner):
    """ Keeps client-side network running """

    def __init__(self, event_manager):
        NetworkSpinner.__init__(self, event_manager)
        self.end_point = None
        self.host = None
        self.port = None
        self.view = None
        self.controller = None

    def handle_join(self, ev_type, host, port):
        """Try to join a remote server."""
        # We should reconnect if the connection goes down but
        # prevent a reconnection is connection is ok.
        state = STATE.get_state()
        if not self.end_point and state == STATE_DISCONNECTED:
            self.host = host
            self.port = port
            # Create the view for the network.
            self.view = ClientNetworkView(self.event_manager)
            # Create the controller for the network.
            self.controller = ClientNetworkController(self.event_manager)
            STATE.set_state(STATE_CONNECTING)
            event = Event('game-request-update')
            self.post(event)

    def run_network(self):
        """Network loop."""
        while self.keep_going:
            state = STATE.get_state()
            if state == STATE_CONNECTING:
                self.end_point = ClientEndPoint(self.host, self.port,
                        self.view, self.controller)
                self.controller = self.view = None
                STATE.set_state(STATE_CONNECTED)
            elif state == STATE_CONNECTED:
                # We cannot let asyncore loop forever, otherwise the flag
                # keep_going is useless.
                asyncore.poll(timeout=1)
            elif state == STATE_DISCONNECTED:
                # Ensure that an unused socket can be garbage collected
                self.end_point = None
                # Sleep a little to prevent a furious while loop 
                time.sleep(0.01)
            else:
                # XXX should raise an exception
                pass
