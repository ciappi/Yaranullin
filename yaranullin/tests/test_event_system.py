# yaranullin/tests/test_event_system.py
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


import unittest

from ..event_system import Event, EventManager, Listener, \
                           EventManagerAndListener


class DummyListener(Listener):

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.events = []
        self.events2 = []

    def handle_test_event(self, ev_type, **kargs):
        self.events.append({ev_type: kargs})

    def handle_test_event2(self, ev_type, **kargs):
        self.events2.append({ev_type: kargs})


class TestEvent(unittest.TestCase):

    def test___init__(self):
        event = Event('test-event', arg1='test arg1', arg2=1)
        self.assertEqual('test-event', event.ev_type)
        self.assertEqual('test arg1', event.arg1)
        self.assertEqual(1, event.arg2)


class TestEventManager(unittest.TestCase):

    def setUp(self):
        self.em = EventManager()

    def test_post(self):
        event = Event('test-event')
        self.em.post(event)
        self.assertEqual(event, self.em.event_queue[0])
        self.em.event_queue.clear()

    def test_listener(self):
        dummy = DummyListener(self.em)
        self.assertEqual(self.em.events['test-event'][0], dummy)
        self.assertEqual(self.em.events['test-event2'][0], dummy)
        dummy.detach()
        self.assertNotIn('test-event', self.em.events)
        self.assertNotIn('test-event2', self.em.events)

    def test_consume_queue(self):
        dummy = DummyListener(self.em)
        event = Event('test-event')
        event2 = Event('test-event2')
        self.em.post(event, event2, event, event2, event2, Event('tick'))
        self.assertEqual(len(dummy.events), 2)
        self.assertEqual(len(dummy.events2), 3)


class TestListener(unittest.TestCase):

    def setUp(self):
        self.em = EventManager()

    def test_callback_dict(self):
        dummy = DummyListener(self.em)
        self.assertEqual(dummy.handle_test_event,
                         dummy.callbacks_dict['test-event'])
        self.assertEqual(dummy.handle_test_event2,
                         dummy.callbacks_dict['test-event2'])
        self.assertEqual(2, len(dummy.callbacks_dict))


class TestEventManagerAndListener(unittest.TestCase):

    def setUp(self):
        self.em = EventManager()
        self.emal = EventManagerAndListener(self.em)

    def test_attach_listener(self):
        dummy = DummyListener(self.emal)
        self.assertEqual(self.em.events['test-event'][0], self.emal)
        self.assertEqual(self.em.events['test-event2'][0], self.emal)
        dummy.detach()
        self.assertNotIn('test-event', self.em.events)
        self.assertNotIn('test-event2', self.em.events)
        self.assertNotIn('test-event', self.emal.events)
        self.assertNotIn('test-event2', self.emal.events)

    def test_event_propagation(self):
        dummy = DummyListener(self.emal)
        event = Event('test-event')
        event2 = Event('test-event2')
        self.em.post(event, event2, event, event2, event2)
        self.em.post(Event('tick'))
        self.assertEqual(len(dummy.events), 2)
        self.assertEqual(len(dummy.events2), 3)

    def test_event_propagation_upstream(self):
        dummy = DummyListener(self.emal)
        event = Event('test-event')
        dummy.event_manager.post(event)
        self.em.post(Event('tick'))
        self.assertEqual(len(dummy.events), 1)
