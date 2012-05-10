# yaranullin/events.py
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

This module is an simple implementation of an event patter.

'''

import collections
import inspect
import time
import weakref


ANY, QUIT, TICK = range(3)

_QUEUE = collections.deque()

_EVENTS = {}

_EVENTS[ANY] = weakref.WeakValueDictionary()


def register(event, func):
    ''' Register an handler '''    
    if inspect.isfunction(func):
        func = {func: func}
    elif inspect.ismethod(func):
        func = {func.im_func: func.im_self}
    else:
        return
    if event not in _EVENTS:
        _EVENTS[event] = weakref.WeakValueDictionary()
    _EVENTS[event].update(func)


def unregister(event=None, func=None):
    ''' Unregister an handler '''
    if event is None and func is None:
        _EVENTS.clear()
        _EVENTS[ANY] = weakref.WeakValueDictionary()
        return
    if event not in _EVENTS:
        # XXX may raise an exception
        return
    if func is None and event is not ANY:
        # Delete all the events
        del _EVENTS[event]
        return
    if inspect.ismethod(func):
        func = func.im_func
    try:
        del _EVENTS[event][func]
    except KeyError:
        # XXX raise an exception
        return
    if not _EVENTS[event] and event is not ANY:
        del _EVENTS[event]


def post(event, **kargs):
    ''' Post an event '''
    if event not in _EVENTS and not _EVENTS[ANY]:
        return
    # Add the id of the dict to the object
    id_ = id(kargs)
    kargs['__id__'] = id_
    # Add a special attribute with the type of the event
    kargs['__event__'] = event
    # Post an event only if there is some handler registered.
    _QUEUE.append(kargs) 
    return id_


def _consume_event_queue():
    ''' Consume the event queue and call all handlers '''
    stop = False
    while _QUEUE:
        ekargs = _QUEUE.popleft()
        event = ekargs['__event__']
        # Find all handler for this event
        handlers = {}
        handlers.update(_EVENTS[event])
        handlers.update(_EVENTS[ANY])
        for handler, self in handlers.iteritems():
            hargs, _, hkeywords, _ = inspect.getargspec(handler)
            kargs = dict(ekargs)
            if 'self' in hargs:
                # We assume that this is a bound method
                kargs['self'] = self
            # Check if the handler has ** magic
            if not hkeywords:
                # Delete all arguments that the handler cannot take
                for key in kargs.keys():
                    if key not in hargs:
                        del kargs[key]
            handler(**kargs)
        if event == QUIT:
            stop = True 
            break
    return stop


def run():
    ''' Sample main loop of yaranullin '''
    stop = False
    while not stop:
        time.sleep(0.01)
        post(TICK)
        stop = _consume_event_queue()


class Pipe(object):

    ''' Used for communication between two processes.
    
    To allow sending and receiving events from two different processes,
    create an instance of Pipe for each one of them. The in_queue of the
    first Pipe must be the out_queue of the second and viceversa.

    The default implementation allows all events through the queues.
    
    '''

    def __init__(self, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.posted_events = set()
        register(ANY, self.handle)
        register(TICK, self.tick)

    def handle(self, **kargs):
        ''' Put given event to the out queue '''
        try:
            id_ = kargs['__id__']
            event = kargs['__event__']
        except KeyError:
            return
        if event == TICK:
            # Never post ticks between processes.
            return
        if id_ in self.posted_events:
            # This event was posted by the pipe, so do not have to post it
            # back or we will trigger an infinite loop.
            # Remove the event from the set (the event will be posted here
            # once) and return
            self.posted_events.remove(id_)
            return
        self.out_queue.put(kargs)

    def tick(self):
        ''' Get all the event from the in queue '''
        while not self.in_queue.empty():
            event = self.in_queue.get()
            self.posted_events.add(post(**event))
