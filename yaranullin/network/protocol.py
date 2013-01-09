# -*- coding: utf-8 *-*
# yaranullin/network/protocol.py
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

import json
import collections

from twisted.internet import protocol
from twisted.protocols.basic import Int16StringReceiver

from yaranullin.event_system import post, connect


class YaranullinProtocol(Int16StringReceiver):

    def connectionMade(self):
        try:
            self.factory.endpoint = self
        except AttributeError:
            self.factory.endpoints.add(self)

    def stringReceived(self, string):
        '''Got an event message.'''
        self.factory.post(string)


class YaranullinClientFactory(protocol.ClientFactory):

    protocol = YaranullinProtocol
    endpoint = None
    from_yrn = collections.deque()

    def __init__(self):
        connect('tick', self.process_queue)
        connect('game-request-pawn-move', self.post)
        connect('game-request-pawn-place', self.post)
        connect('game-request-pawn-next', self.post)
        connect('game-request-update', self.post)
        connect('resource-request', self.post)

    def process_queue(self):
        '''Process the event queue from Yaranullin's event system.'''
        queue = self._from_yrn
        while queue:
            self.endpoint.sendString(queue.popleft())

    def post(self, event_dict):
        post(json.loads(event_dict))

    def send(self, event_dict):
        self._from_yrn.append(json.dumps(event_dict))


class YaranullinServerFactory(protocol.ClientFactory):

    protocol = YaranullinProtocol
    endpoints = set()
    from_yrn = collections.deque()

    def __init__(self):
        connect('tick', self.process_queue)
        connect('game-event-update', self.post)
        connect('game-event-pawn-next', self.post)
        connect('game-event-pawn-updated', self.post)
        connect('game-event-board-change', self.post)
        connect('resource-update', self.post)

    def process_queue(self):
        '''Process the event queue from Yaranullin's event system.'''
        queue = self._from_yrn
        while queue:
            for endpoint in self.endpoints:
                endpoint.sendString(queue.popleft())

    def post(self, string):
        post(json.loads(string))

    def send(self, event_dict):
        self._from_yrn.append(json.dumps(event_dict))