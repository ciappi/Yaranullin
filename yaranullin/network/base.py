# yaranullin/network/base.py
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

"""Base network classes."""

import asyncore
import struct
import socket
import threading
import bson
from collections import deque

#from utils import encode, decode
from yaranullin.event_system import Listener, Event


FORMAT = struct.Struct('!I')  # for messages up to 2**32 - 1 in length

STATE_LEN, STATE_BODY = range(2)


class EndPoint(asyncore.dispatcher):

    """Sends and receives messages across the network."""

    def __init__(self, sock=None, sockets=None):
        asyncore.dispatcher.__init__(self, sock, sockets)
        self.in_buffer = deque()
        self.out_buffer = deque()
        self.in_chunks = deque()
        self.len_in_chunks = 0
        self.state = STATE_LEN
        self.lendata = 0
        # XXX remember IPv6...
        if not sock:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.set_socket(sock)

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def writable(self):
        return self.out_buffer

    def handle_write(self):
        num_sent = self.send(self.out_buffer[0])
        self.out_buffer[0] = self.out_buffer[0][num_sent:]
        if not self.out_buffer[0]:
            self.out_buffer.popleft()

    def recvall(self, length):
        """ Receives a whole message """
        # Read at most 262144 bytes. Trying to read all (length -len(data))
        # has been reported to be an issue on Vista 32 bit because
        # this number has to be converted to a C long and sometimes it is
        # too big for that.
        to_read = min(length - self.len_in_chunks, 262144)
        data = self.recv(to_read)
        if not data:
            return
        self.in_chunks.append(data)
        self.len_in_chunks += len(data)
        if self.len_in_chunks == length:
            data = ''.join(self.in_chunks)
            self.len_in_chunks = 0
            self.in_chunks.clear()
            return data

    def handle_read(self):
        if self.state == STATE_LEN:
            data = self.recvall(FORMAT.size)
            if data:
                (self.lendata, ) = FORMAT.unpack(data)
                self.state = STATE_BODY
        elif self.state == STATE_BODY:
            data = self.recvall(self.lendata)
            if data:
                self.in_buffer.append(data)


class NetworkView(Listener):

    """The view of the network."""

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.end_point = None

    def add_to_out_queue(self, ev_type, **kargs):
        """Add an event to the queue of the end_point."""
        if self.end_point is not None:
            #data = dumps(event, default=encode)
            data = {'ev_type': ev_type}
            data.update(kargs)
            self.end_point.out_buffer.append(bson.dumps(data))


class NetworkController(Listener):

    """Process events from the network."""

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.end_point = None

    def handle_tick(self, ev_type):
        """Handle ticks."""
        self.consume_in_queue()

    def consume_in_queue(self):
        """Process the event queue."""
        if self.end_point is not None:
            # We trust we don't get stuck in this loop because the
            # network is much slower to fill the queue than we are able to
            # empty it.
            while len(self.end_point.in_buffer):
                data = self.end_point.in_buffer.popleft()
                #event = loads(data, object_hook=decode)
                event = Event(**bson.loads(data))
                if check_event(event):
                    self.post(event)


def check_event(event):
    """Check if an event can be posted on the local event manager."""
    return True


class NetworkWrapper(Listener):

    """Wrapper for the network thread."""

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.thread = None

    def handle_start(self, ev_type):
        """Run network loop"""
        self.thread = threading.Thread(target=self.run_network)
        self.thread.start()

    def handle_quit(self, ev_type):
        """Join network loop"""
        self.thread.join()

    def run_network(self):
        """Dispatches network events"""
