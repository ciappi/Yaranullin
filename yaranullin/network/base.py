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


import struct
import socket
import threading
import logging
import msgpack
from collections import deque

#from utils import encode, decode
from ..event_system import Listener, Event
from ..spinner import CPUSpinner


format = struct.Struct('!I')  # for messages up to 2**32 - 1 in length


class EndPoint(object):

    """Sends and receives messages across the network."""

    def setup(self):
        """Initialization stuff."""
        self.in_buffer = deque()
        self.out_buffer = deque()

    def recvall(self, length):
        """Read a message from the socket."""
        data = ''
        while len(data) < length:
            more = self.request.recv(length - len(data))
            if not more:
                raise EOFError('socket closed %d bytes into a %d-byte message'
                               % (len(data), length))
            data += more
        return data

    def pull(self):
        """Pull all data available from the socket."""
        try:
            while True:
                data = self.get()
                logging.debug('Pulling ' + repr(data) + ' from server.')
                self.in_buffer.append(data)
        except socket.error:
            pass

    def push(self):
        """Push all the data queue to the socket."""
        while len(self.out_buffer):
            data = self.out_buffer.popleft()
            logging.debug('Pushing ' + repr(data) + ' to server.')
            self.put(data)

    def get(self):
        """Get a single message from the socket.

        Returns the decompressed data.
        """
        lendata = self.recvall(format.size)
        (length,) = format.unpack(lendata)
        data = self.recvall(length)
        return data

    def put(self, message):
        """Send a single message to the socket."""
        self.request.sendall(format.pack(len(message)) + message)


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
            self.end_point.out_buffer.append(msgpack.dumps(data))


class NetworkController(Listener):

    """Process events from the network."""

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.end_point = None

    def handle_tick(self, ev_type):
        """Handle ticks."""
        self.consume_in_queue()

    def consume_in_queue(self):
        """Process the event queue.

        We trust we don't get stuck in this loop because the
        network is much slower to fill the queue than we are able to
        empty it.

        """
        if self.end_point is not None:
            while len(self.end_point.in_buffer):
                data = self.end_point.in_buffer.popleft()
                #event = loads(data, object_hook=decode)
                event = Event(**msgpack.loads(data))
                if self.check_event(event):
                    self.post(event)

    def check_event(self, event):
        """Check if an event can be posted on the local event manager."""
        return True


class NetworkSpinner(CPUSpinner):

    """Spinner for the network thread."""

    def run(self):
        """Main loop.

        Starts the regular CPUSpinner loop to process Yaranullin events as
        well as a loop regulary sending and receiving data from the network.

        """
        net_loop_thread = threading.Thread(target=self.run_network)
        net_loop_thread.start()
        CPUSpinner.run(self)
        net_loop_thread.join()

    def run_network(self):

        pass
