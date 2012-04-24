# yaranullin/network/server.py
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
import asyncore

from yaranullin.network.base import EndPoint, NetworkView, NetworkController, \
                                    NetworkSpinner


class ServerNetworkController(NetworkController):
    pass


class ServerNetworkView(NetworkView):

    handle_game_event_update = NetworkView.add_to_out_queue
    handle_game_event_pawn_next = NetworkView.add_to_out_queue
    handle_game_event_pawn_updated = NetworkView.add_to_out_queue
    handle_game_event_board_change = NetworkView.add_to_out_queue
    handle_resource_update = NetworkView.add_to_out_queue


class ServerEndPoint(EndPoint):

    def __init__(self, view, controller, sock=None, map=None):
        """Setup a server end point for every connected client."""
        EndPoint.__init__(self, sock=sock, map=map)
        # Create the view of the connected client.
        self.view = view
        self.view.end_point = self
        # Create the controller of the connected client.
        self.controller = controller
        self.controller.end_point = self

    def handle_close(self):
        self.view.end_point = self.controller.end_point = None
        self.view = self.controller = None
        EndPoint.handle_close(self)


class ServerNetworkSpinner(NetworkSpinner, asyncore.dispatcher):

    def __init__(self, event_manager, server_address):
        NetworkSpinner.__init__(self, event_manager)
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(server_address)
        self.listen(5)
        self.sockets = {}

    def handle_accept(self):
        client_info = self.accept()
        view = ServerNetworkView(self.event_manager)
        controller = ServerNetworkController(self.event_manager)
        ServerEndPoint(view, controller, sock=client_info[0],
                map=self.sockets)

    def run_network(self):

        """Network loop.

        Simply pull and push from the socket.

        """
        while self.keep_going:
            # We cannot let asyncore loop forever, otherwise the flag
            # keep_going is useless.
            asyncore.loop(timeout=1, count=1, map=self.sockets)
        else:
            # Probably we should call handle_close for each socket.
            for sock in self.sockets:
                sock.handle_close()
