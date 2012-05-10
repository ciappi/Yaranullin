# yaranullin/tests/events.py
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

if __name__ == '__main__':
    sys.path.insert(0, ".")

from yaranullin.events import register, unregister, post, _EVENTS, _QUEUE, \
                              _consume_event_queue

Q = []

def func_handler(__id__):
    ''' Simple function handler '''
    Q.append(__id__)


def magic_handler(**kargs):
    Q.append(kargs)


class Handler(object):

    ''' Class to test method handler '''

    def method_handler(self):
        ''' Simple method handler '''


class TestEvents(unittest.TestCase):

    def test_register(self):
        # Test if a function handler is registered correctly
        register(10, func_handler)
        self.assertEqual(_EVENTS[10][func_handler], func_handler)
        # Test if a method is registered correctly
        h = Handler()
        register(20, h.method_handler)
        im_func = h.method_handler.im_func
        self.assertEqual(_EVENTS[20][im_func], h)
        # Function or method should register only once
        register(10, func_handler)
        register(20, h.method_handler)
        self.assertEqual(1, len(_EVENTS[10].keys()))
        self.assertEqual(1, len(_EVENTS[20].keys()))
        # Unregister the last handler for an event
        unregister(10, func_handler)
        self.assertFalse(10 in _EVENTS)
        unregister(20, h.method_handler)
        self.assertFalse(20 in _EVENTS)
        # Unregister an handler
        register(10, func_handler)
        register(10, h.method_handler)
        unregister(10, func_handler)
        self.assertFalse(func_handler in _EVENTS[10])
        self.assertTrue(im_func in _EVENTS[10])
        # Delete all 10's handlers
        unregister(10)
        self.assertFalse(10 in _EVENTS)

    def test_post(self):
        # Cannot post an event if there are no handler
        _QUEUE.clear()
        unregister()
        post(10)
        self.assertFalse(_QUEUE)
        # Register an handler and post an event
        register(10, func_handler)
        id_ = post(10)
        self.assertEqual(1, len(_QUEUE))
        # Check if the event if well formatted
        self.assertEqual({'__id__':id_, '__event__':10}, _QUEUE.popleft())

    def test_consume_event_queue(self):
        global Q
        register(10, func_handler)
        for _ in range(3):
            post(10)
        _QUEUE_ids = [el['__id__'] for el in _QUEUE]
        _consume_event_queue()
        self.assertEqual(_QUEUE_ids, Q)
        # Try magic handler function
        Q = []
        _QUEUE.clear()
        unregister()
        register(10, magic_handler)
        for _ in range(3):
            post(10, first='first arg', second='second arg')
        _QUEUE_events = list(_QUEUE)
        _consume_event_queue()
        self.assertEqual(_QUEUE_events, Q)



if __name__ == '__main__':
    unittest.main()
