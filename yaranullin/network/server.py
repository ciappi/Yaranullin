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

from yaranullin.network.base import EndPoint, EndPointWrapper, NetworkSpinner, \
                                    NetworkWrapper


class ServerEndPointWrapper(EndPointWrapper):

    """End point wrapper for the server"""

    handle_game_event_update = EndPointWrapper._add_to_out_queue
    handle_game_event_pawn_next = EndPointWrapper._add_to_out_queue
    handle_game_event_pawn_updated = EndPointWrapper._add_to_out_queue
    handle_game_event_board_change = EndPointWrapper._add_to_out_queue
    handle_resource_update = EndPointWrapper._add_to_out_queue


class ServerEndPoint(EndPoint):

    """End point for the server"""

    wrapper_class = ServerEndPointWrapper


class Server(asyncore.dispatcher):

    """Handle server and create end points"""

    def __init__(self, event_manager, server_address):
        asyncore.dispatcher.__init__(self)
        self.event_manager = event_manager
        # XXX Remember IPv6
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(server_address)
        self.listen(5)

    def handle_accept(self):
        client_info = self.accept()
        if client_info is None:
            return
        ServerEndPoint(self.event_manager, sock=client_info[0])


class ServerNetworkSpinner(NetworkSpinner):

    """Spinner for the server"""

    def _run(self):
        # FIXME take address from config file
        Server(self.event_manager, ('', 60000))
        NetworkSpinner._run(self)


class ServerNetworkWrapper(NetworkWrapper):

    """Wrap asyncore loop"""

    spinner = ServerNetworkSpinner

