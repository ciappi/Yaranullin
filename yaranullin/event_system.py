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
import inspect

LOGGER = logging.getLogger(__name__)

#
# WeakCallback is a singleton with respect to a callback (i.e. there is only
# one instance for a given callback).
#
from yaranullin.weakcallback import WeakCallback


_QUEUE = collections.deque()
_EVENTS = collections.defaultdict(set)


def connect(event, callback, events=None):
    ''' Connect a callback to an event '''
    if events is None:
        events = _EVENTS
    if not isinstance(event, basestring):
        raise RuntimeError('event_system.connect(): invalid event type')
    wrapper = WeakCallback(callback)
    LOGGER.debug("Connecting callback %s with event '%s'", repr(callback),
        event)
    events[event].add(wrapper)


def _disconnect(event, callback, events=None):
    ''' Disconnect a callback from an event '''
    if events in None:
        events = _EVENTS
    wrapper = WeakCallback(callback)
    if wrapper in events[event]:
        events[event].remove(wrapper)
        LOGGER.debug("Disconnecting callback %s from event '%s'",
                repr(callback), event)
    else:
        LOGGER.debug("Callback %s was not connected to event '%s'",
                repr(callback), event)


def disconnect(event=None, callback=None, events=None):
    ''' Disconnect callbacks '''
    if events is None:
        events = _EVENTS
    if callback is None and event is None:
        # Remove all callbacks
        LOGGER.debug("Disconnecting all callbacks")
        events.clear()
    elif callback is not None and event is not None:
        # Remove at most one callback
        _disconnect(event, callback, events)
    elif event is None:
        # Remove a callback from all events
        for event in events:
            _disconnect(event, callback, events)
    elif event in events:
        # Delete all callbacks connected to an event
        LOGGER.debug("Disconnecting all callbacks from event '%s'", event)
        events.remove(event)


def post(event, attributes=None, queue=None, events=None, **kattributes):
    ''' Post an event '''
    if queue is None:
        queue = _QUEUE
    if events is None:
        events = _EVENTS
    if not isinstance(event, basestring):
        raise RuntimeError('event_system.post(): invalid event type')
    if not events[event] and not events['any']:
        if event != 'tick':
            LOGGER.debug("No callback connected to event '%s': dropping...",
                    event)
        if event != 'quit':
            return
    event_dict = dict(kattributes)
    if attributes is not None:
        try:
            event_dict.update(attributes)
        except TypeError:
            LOGGER.exception("Cannot update event dictionary with object '%s'",
                    str(type(attributes)))
            raise
    # Add the id of the dict to the object
    id_ = id(event_dict)
    event_dict['id'] = id_
    # Add a special attribute with the type of the event
    event_dict['event'] = event
    queue.append(event_dict)
    if event != 'tick':
        LOGGER.debug("Appended event '%s' to the queue, with args %s", event,
                repr(event_dict))
    return id_


def process_queue(queue=None, events=None):
    ''' Consume the event queue and call all handlers '''
    if queue is None:
        queue = _QUEUE
    if events is None:
        events = _EVENTS
    stop = False
    garbage = set()
    while queue:
        event_dict = queue.popleft()
        event = event_dict['event']
        # Find all handler for this event
        handlers = set(events[event])
        handlers |= events['any']
        if event != 'tick':
            LOGGER.debug("Calling handlers for event '%s'...", event)
        for handler_ in handlers:
            handler = handler_()
            if handler is None:
                garbage.add(handler_)
                continue
            if event != 'tick':
                LOGGER.debug("Calling callback '%s'...", repr(handler))
            args, _, _, _ = inspect.getargspec(handler)
            if inspect.ismethod(handler):
                len_args = len(args) - 1
            else:
                len_args = len(args)
            if len_args == 0:
                handler()
            elif len_args == 1:
                handler(event_dict)
            else:
                raise TypeError("Bad number of arguments for callback '%s'" %
                        repr(handler))
            if event != 'tick':
                LOGGER.debug("Calling callback '%s'... done", repr(handler))
        if event != 'tick':
            LOGGER.debug("Calling handlers for event '%s'... done", event)
        # Garbage collect every dead WeakCallback
        if garbage:
            events[event] -= garbage
            # 'garbage.clear()' takes about 80% of the time
            # of 'garbage = set()'
            garbage.clear()
            LOGGER.debug("Purged dead handlers for event '%s'", event)
        if event == 'quit':
            stop = True
            break
    return stop
