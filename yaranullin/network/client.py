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

from yaranullin.events import *

from yaranullin.framework import connect, post
from yaranullin.network.base import EventEndPoint


class ClientEventEndPoint(EventEndPoint):

    """End point wrapper for a client.

    The client can only move pawns and request the next pawn according to
    initiative order.

    """

    def __init__(self):
        EventEndPoint.__init__(self)
        self._connect_handlers()

    def _connect_handlers(self):
        ''' Connect the events to send to the sever '''
        connect(JOIN, self.join)
        connect(GAME-REQUEST-PAWN-MOVE, self.post)
        connect(GAME-REQUEST-PAWN-PLACE, self.post)
        connect(GAME-REQUEST-PAWN-NEXT, self.post)
        connect(GAME-REQUEST-UPDATE, self.post)
        #connect(RESOURCE-REQUEST, self.post)

    def join(self, host, port):
        """Try to join a remote server."""
        # We should reconnect if the connection goes down but
        # prevent a reconnection is connection is ok.
        self.connect((host, port))
        post(GAME-REQUEST-UPDATE)
