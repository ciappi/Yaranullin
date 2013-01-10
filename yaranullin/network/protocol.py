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
        self.factory.add(self)

    def connectionLost(self, reason):
        self.factory.remove(self)

    def stringReceived(self, string):
        '''Got an event message.'''
        self.factory.post(string)


class YaranullinClientFactory(protocol.ClientFactory):

    protocol = YaranullinProtocol
    endpoint = None
    from_yrn = collections.deque()

    def __init__(self):
        connect('tick', self.process_queue)
        connect('game-request-pawn-move', self.send)
        connect('game-request-pawn-place', self.send)
        connect('game-request-pawn-next', self.send)

    def add(self, prot):
        self.endpoint = prot

    def remove(self, prot):
        if prot is self.endpoint:
            self.endpoint = None

    def process_queue(self):
        '''Process the event queue from Yaranullin's event system.'''
        queue = self.from_yrn
        while queue:
            self.endpoint.sendString(queue.popleft())

    def post(self, event_dict):
        post(json.loads(event_dict))

    def send(self, event_dict):
        self.from_yrn.append(json.dumps(event_dict))


class YaranullinServerFactory(protocol.ServerFactory):

    protocol = YaranullinProtocol
    endpoints = set()
    from_yrn = collections.deque()

    def __init__(self):
        connect('tick', self.process_queue)
        connect('game-event-pawn-next', self.send)
        connect('game-event-pawn-moved', self.send)

    def add(self, prot):
        self.endpoints.add(prot)

    def remove(self, prot):
        if prot in self.endpoints:
            self.endpoints.remove(prot)

    def process_queue(self):
        '''Process the event queue from Yaranullin's event system.'''
        queue = self.from_yrn
        while queue:
            for endpoint in self.endpoints:
                endpoint.sendString(queue.popleft())

    def post(self, string):
        post(json.loads(string))

    def send(self, event_dict):
        self.from_yrn.append(json.dumps(event_dict))
