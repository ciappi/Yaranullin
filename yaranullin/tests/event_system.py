# yaranullin/tests/event_system.py
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

import sys
import unittest
import collections

if __name__ == '__main__':
    sys.path.insert(0, ".")

from yaranullin.weakcallback import WeakCallback
from yaranullin.event_system import connect, disconnect, post, _EVENTS, \
        _QUEUE, process_queue

Q = collections.deque()

def func_handler(ev):
    ''' Simple function handler '''
    del ev['id']
    del ev['event']
    Q.append(ev)


class Handler(object):

    ''' Class to test method handler '''

    def method_handler(self):
        ''' Simple method handler '''


class TestEvents(unittest.TestCase):

    def setUp(self):
        _QUEUE.clear()
        _EVENTS.clear()
        Q.clear()

    def test_connect(self):
        # Connect a single handler
        connect(10, func_handler)
        wrapper = WeakCallback(func_handler)
        self.assertTrue(10 in _EVENTS)
        self.assertTrue(wrapper in _EVENTS[10])

    def test_disconnect(self):
        # Disconnect a single handler
        connect(10, func_handler)
        disconnect(10, func_handler)
        wrapper = WeakCallback(func_handler)
        self.assertFalse(wrapper in _EVENTS[10])

    def test_post(self):
        # Post a single event
        connect(10, func_handler)
        event_dict = {'event': 10, 'id': post(10)}
        self.failUnlessEqual(event_dict, _QUEUE.popleft())

    def test_process_queue(self):
        connect(10, func_handler)
        event_dict = {'args1': 1, 'arg2':2}
        post(10, **event_dict)
        post(10, event_dict)
        process_queue()
        self.failUnlessEqual(event_dict, Q.popleft())
        self.failUnlessEqual(event_dict, Q.popleft())


if __name__ == '__main__':
    unittest.main()
