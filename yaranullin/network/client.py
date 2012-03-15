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


import socket
from time import sleep

from yaranullin.event_system import Event
from yaranullin.network.base import EndPoint, NetworkView, NetworkController, NetworkSpinner


class ClientNetworkController(NetworkController):
    pass


class ClientNetworkView(NetworkView):

    """Basic NetworkView for a client.

    The client can only move pawns and request the next pawn according to
    initiative order.

    """

    handle_game_request_pawn_move = NetworkView.add_to_out_queue
    handle_game_request_pawn_place = NetworkView.add_to_out_queue
    handle_game_request_pawn_next = NetworkView.add_to_out_queue
    handle_game_request_update = NetworkView.add_to_out_queue
    handle_texture_request = NetworkView.add_to_out_queue


class ClientEndPoint(EndPoint):

    def __init__(self, event_manager, host, port):
        self.request = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.request.connect((host, port))
        self.request.setblocking(False)
        self.setup(event_manager)

    def setup(self, event_manager):
        """Setup the client end point."""
        # Create the queues.
        EndPoint.setup(self)
        # Create the view for the network.
        view = ClientNetworkView(event_manager)
        view.end_point = self
        # Create the controller for the network.
        controller = ClientNetworkController(event_manager)
        controller.end_point = self
        # Save a reference for both of them.
        self.view = view
        self.controller = controller


class ClientNetworkSpinner(NetworkSpinner):

    def __init__(self, event_manager):
        NetworkSpinner.__init__(self, event_manager)
        self.end_point = None

    def handle_join(self, ev_type, host, port):
        """Try to join a remote server."""
        self.end_point = ClientEndPoint(self.event_manager, host, port)
        event = Event('game-request-update')
        self.post(event)

    def run_network(self):
        """Network loop.

        Simply pull and push from the socket.

        """
        while self.keep_going:
            if self.end_point is not None:
                self.end_point.pull()
                self.end_point.push()
            sleep(0.01)
