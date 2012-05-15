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

from yaranullin.events import GAME_EVENT_UPDATE, GAME_EVENT_PAWN_NEXT, \
        GAME_EVENT_PAWN_UPDATED, GAME_EVENT_BOARD_CHANGE, RESOURCE_UPDATE
from yaranullin.event_system import connect
from yaranullin.network.base import EndPoint


class ServerEndPoint(EndPoint):

    """End point wrapper for the server"""

    def __init__(self, sock):
        EndPoint.__init__(self, sock)
        self._connect_handlers()

    def _connect_handlers(self):
        connect(GAME_EVENT_UPDATE, self.post)
        connect(GAME_EVENT_PAWN_NEXT, self.post)
        connect(GAME_EVENT_PAWN_UPDATED, self.post)
        connect(GAME_EVENT_BOARD_CHANGE, self.post)
        connect(RESOURCE_UPDATE, self.post)


class EventServer(asyncore.dispatcher):

    """Handle server and create end points"""

    def __init__(self, server_address):
        asyncore.dispatcher.__init__(self)
        # XXX Remember IPv6
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(server_address)
        self.listen(5)

    def handle_accept(self):
        client_info = self.accept()
        if client_info is None:
            return
        ServerEndPoint(sock=client_info[0])
