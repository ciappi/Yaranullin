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


from yaranullin.event_system import Event
from yaranullin.network.base import EndPoint, EndPointWrapper, NetworkSpinner, \
                                    NetworkWrapper


class ClientEndPointWrapper(EndPointWrapper):

    """End point wrapper for a client.

    The client can only move pawns and request the next pawn according to
    initiative order.

    """

    handle_game_request_pawn_move = EndPointWrapper._add_to_out_queue
    handle_game_request_pawn_place = EndPointWrapper._add_to_out_queue
    handle_game_request_pawn_next = EndPointWrapper._add_to_out_queue
    handle_game_request_update = EndPointWrapper._add_to_out_queue
    handle_resource_request = EndPointWrapper._add_to_out_queue


class ClientEndPoint(EndPoint):

    """Client EndPoint."""

    wrapper_class = ClientEndPointWrapper

class ClientNetworkSpinner(NetworkSpinner):

    """Spinner for the client"""

    end_point = None

    def _run(self):
        self.end_point = ClientEndPoint(self.event_manager)
        NetworkSpinner._run(self)

    def handle_join(self, ev_type, host, port):
        """Try to join a remote server."""
        # We should reconnect if the connection goes down but
        # prevent a reconnection is connection is ok.
        self.end_point.connect((host, port))
        self.post(Event('game-request-update'))


class ClientNetworkWrapper(NetworkWrapper):

    """ Keeps client-side network running """

    spinner = ClientNetworkSpinner
