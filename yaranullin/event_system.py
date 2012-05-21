# yaranullin/event_system.py
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

'''The event system of Yaranullin.

This module is a simple implementation of an event pattern.

'''

import collections
import logging

LOGGER = logging.getLogger(__name__)

#
# WeakCallback is a singleton with respect to a callback (i.e. there is only
# one instance for a given callback).
#
from yaranullin.weakcallback import WeakCallback


_QUEUE = collections.deque()
_EVENTS = collections.defaultdict(set)


def connect(event, callback):
    ''' Connect a callback to an event '''
    if not isinstance(event, str):
        raise RuntimeError('event_system.connect(): invalid event type')
    wrapper = WeakCallback(callback)
    _EVENTS[event].add(wrapper)


def _disconnect(event, callback):
    ''' Disconnect a callback from an event '''
    wrapper = WeakCallback(callback)
    if wrapper in _EVENTS[event]:
        _EVENTS[event].remove(wrapper)


def disconnect(event=None, callback=None):
    ''' Disconnect callbacks '''
    if callback is None and event is None:
        # Remove all callbacks
        _EVENTS.clear()
    elif callback is not None and event is not None:
        # Remove at most one callback
        _disconnect(event, callback)
    elif event is None:
        # Remove a callback from all events
        for event in _EVENTS:
            _disconnect(event, callback)
    elif event in _EVENTS:
        # Delete all callbacks connected to an event
        _EVENTS.remove(event)


def post(event, attributes=None, queue=None, **kattributes):
    ''' Post an event '''
    if queue is None:
        queue = _QUEUE
    if not isinstance(event, str):
        raise RuntimeError('event_system.post(): invalid event type')
    if not _EVENTS[event] and not _EVENTS['any']:
        LOGGER.warning('No callback registered for event %s: dropping...',
                event)
        return
    event_dict = dict(kattributes)
    if attributes is not None:
        try:
            event_dict.update(attributes)
        except TypeError:
            LOGGER.error("Cannot update event dictionary with '%s' object",
                    str(type(attributes)))
    # Add the id of the dict to the object
    id_ = id(event_dict)
    event_dict['id'] = id_
    # Add a special attribute with the type of the event
    event_dict['event'] = event
    queue.append(event_dict) 
    return id_


def process_queue(queue=None):
    ''' Consume the event queue and call all handlers '''
    if queue is None:
        queue = _QUEUE
    stop = False
    garbage = set()
    while queue:
        event_dict = queue.popleft()
        event = event_dict['event']
        # Find all handler for this event
        handlers = set(_EVENTS[event])
        handlers |= _EVENTS['any']
        for handler in handlers:
            if handler() is None:
                garbage.add(handler)
                continue
            try:
                handler()(event_dict)
            except TypeError:
                # An handler can have no arguments
                handler()()
        # Garbage collect every dead WeakCallback
        if garbage:
            _EVENTS[event] -= garbage
            # 'garbage.clear()' takes about 80% of the time of 'garbage = set()'
            garbage.clear()
        if event == 'quit':
            stop = True 
            break
    return stop

