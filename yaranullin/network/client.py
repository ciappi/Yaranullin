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

import logging

LOGGER = logging.getLogger(__name__)

from yaranullin.event_system import connect, post
from yaranullin.network.base import EndPoint


class ClientEndPoint(EndPoint):

    """End point wrapper for a client.

    The client can only move pawns and request the next pawn according to
    initiative order.

    """

    def __init__(self):
        EndPoint.__init__(self)
        connect('join', self.join)
        # Connect the events to send to the sever
        connect('game-request-pawn-move', self.post)
        connect('game-request-pawn-place', self.post)
        connect('game-request-pawn-next', self.post)
        connect('game-request-update', self.post)
        connect('resource-request', self.post)

    def join(self, event_dict):
        """Try to join a remote server."""
        # XXX We should reconnect if the connection goes down but
        # prevent a reconnection if connection is ok.
        host = event_dict['host']
        port = event_dict['port']
        self.connect((host, port))
        LOGGER.debug('Connecting to %s:%d', host, port)
        post('game-request-update')
