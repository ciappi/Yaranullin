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

from yaranullin.event_system import Listener, Event, EventManagerAndListener
from yaranullin.spinner import CPUSpinner


FORMAT = struct.Struct('!I')  # for messages up to 2**32 - 1 in length

STATE_LEN, STATE_BODY = range(2)


class EndPointWrapper(Listener):

    """Interface EndPoint with Yaranullin's event system"""

    def __init__(self, event_manager, end_point):
        Listener.__init__(self, event_manager)
        self.end_point = end_point

    def handle_tick(self, ev_type):
        """Handle ticks."""
        self._consume_in_queue()

    def _add_to_out_queue(self, ev_type, **kargs):
        """Add an event to the queue of the end_point."""
        if not self.check_out_event(ev_type, **kargs):
            return
        data = {'ev_type': ev_type}
        data.update(kargs)
        self.end_point.add_to_out_buffer(bson.dumps(data))

    def _consume_in_queue(self):
        """Process the event queue."""
        # We trust we don't get stuck in this loop because the
        # network is much slower to fill the queue than we are able to
        # empty it.
        while True:
            data = self.end_point.get_from_in_buffer()
            if not data:
                break
            data = bson.loads(data)
            if not self.check_in_event(**data):
                continue
            self.post(Event(**data))

    def check_in_event(self, ev_type, **kargs):
        """Check if an event can be posted on the local event manager."""
        return True

    def check_out_event(self, ev_type, **kargs):
        """Check if an event can be sent over the network."""
        return True


class EndPoint(asyncore.dispatcher):

    """Sends and receives messages across the network."""

    wrapper_class = EndPointWrapper

    def __init__(self, event_manager, sock=None, sockets=None):
        asyncore.dispatcher.__init__(self, sock, sockets)
        self.wrapper = self.wrapper_class(event_manager, self)
        self._in_buffer = deque()
        self._out_buffer = deque()
        self.in_chunks = deque()
        self.len_in_chunks = 0
        self.state = STATE_LEN
        self.lendata = 0
        # XXX remember IPv6...
        if not sock:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.set_socket(sock)

    def add_to_out_buffer(self, message):
        self._out_buffer.append(FORMAT.pack(len(message)) + message)

    def get_from_in_buffer(self):
        if self._in_buffer:
            return self._in_buffer.popleft()

    def handle_connect(self):
        pass

    def handle_close(self):
        # Delete the wrapper when the connection is done
        self.wrapper = None
        self.close()

    def writable(self):
        return self._out_buffer

    def handle_write(self):
        num_sent = self.send(self._out_buffer[0])
        self._out_buffer[0] = self._out_buffer[0][num_sent:]
        if not self._out_buffer[0]:
            self._out_buffer.popleft()

    def _recvall(self, length):
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
            data = self._recvall(FORMAT.size)
            if data:
                (self.lendata, ) = FORMAT.unpack(data)
                self.state = STATE_BODY
        elif self.state == STATE_BODY:
            data = self._recvall(self.lendata)
            if data:
                self._in_buffer.append(data)
                self.state = STATE_LEN


class NetworkSpinner(CPUSpinner):

    def _run(self):
        """Dispatches network events"""
        while self.keep_going:
            self.post(Event('tick'))
            asyncore.poll(0.01)


class NetworkWrapper(EventManagerAndListener):

    """Wrapper for the network thread."""

    spinner = NetworkSpinner

    def __init__(self, event_manager):
        EventManagerAndListener.__init__(self, event_manager, independent=True)
        self.net_cpu_spinner = self.spinner(self)
        self.thread = threading.Thread(target=self.net_cpu_spinner.run)

    def handle_start(self, ev_type):
        """Run network loop"""
        self.thread.start()

