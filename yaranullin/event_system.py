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

"""The event system of Yaranullin.

This is the fondation and main design pattern used in Yaranullin. The general
idea is taken from http://ezide.com/games/writing-games.html but the
implementation is different in a number of ways.

The design patter used here is a combination of MVC (Model View Controller)
and Mediator.

The aim of this desing is to decouple all the elements of the program (the
game logic, the gui, the network stack, etc...), such that everything is a
plugin (a Listener class to be specific) and, as such, it can be activated or
deactivated by simply adding or removing it from a specific global class
(EventManager) be activated or deactivated by simply adding or removing it
from a specific global class (EventManager).

Every Listener can send or recive events and so can communicate with other
Listeners without knowing anything about them.

"""

import sys
import logging

from copy import deepcopy
from random import choice
from weakref import proxy
from collections import deque


LISTENER_IDS_POOL = frozenset(range(2 ** 16))


class Event(object):

    """The class used for all events.

    An Event is composed by a mandatory type (a string) and by a variable
    number of optional arguments.

    A list of all the event types and their arguments can be found
    in docs/events.md along with a brief description.

    Creating a new event type is as simple as pick up a new name for it
    and define some handling function in a Listener.

    """

    def __init__(self, ev_type, **kargs):
        self.__dict__.update(**kargs)
        # Ensure that the event type is corrent event if there is a
        # type keyword argument in kargs.
        self.ev_type = ev_type


class EventManager(object):

    """Broadcast events to registered listeners.

    This class is the core of Yaranullin's framework and, as such, is
    responsible for dispatching all events to the listeners.  There should be
    only one EventManager in the main thread.

    """

    def __init__(self):
        # Couple event types to their listeners.
        # {'event_type': [listener_1, listener_2, ...], ...}
        self.events = dict()
        # Global event queue, thread safe thanks to deque.
        self.event_queue = deque()
        # Used ids.
        self.free_ids = set(LISTENER_IDS_POOL)

    def get_new_uid(self, uid):
        """Return an available uid.
        
        If the provided uid is available, then returns it unchanged. Otherwise
        returns an randomly chosen uid.
        """
        if uid in self.free_ids:
            self.free_ids.remove(uid)
            return uid
        if len(self.free_ids):
            new_uid = choice(list(self.free_ids))
            self.free_ids.remove(new_uid)
            return new_uid
        else:
            # This should never appen since there are 2^16 ids to choose from.
            sys.exit('Max number of listeners reached ('
                     + str(len(LISTENER_IDS_POOL)) + ')')

    def attach_listener(self, listener, *wanted_events):
        """Register a Listener to some events."""
        for event in wanted_events:
            if event in self.events:
                if listener not in self.events[event]:
                    self.events[event].append(listener)
            else:
                self.events[event] = [listener, ]

    def detach_listener(self, listener):
        """Unregister a Listener."""
        for listeners in self.events.values():
            if listener in listeners:
                listeners.remove(listener)
        # Purge events without listeners.
        events = {}
        for event, listeners in self.events.items():
            if len(listeners):
                events[event] = listeners
        self.events = events

    def post(self, *events):
        """Add an event to the event queue."""
        for event in events:
            self.event_queue.append(event)
            if event.ev_type == 'tick':
                # Consume the event queue every tick.
                self.consume_event_queue()
            else:
                # Log the event with INFO priority.
                logging.info("Event of type '%s' queued.", event.ev_type)

    def consume_event_queue(self):
        """Consume and clear the event queue."""
        while len(self.event_queue):
            event = self.event_queue.popleft()
            # Continue if there is no registered listeners for this type
            # of event.
            if event.ev_type not in self.events:
                continue
            # Avoid runtime errors for listeners created during
            # the following 'for' loop, by copying the list.
            listeners = tuple(self.events[event.ev_type])
            for listener in listeners:
                listener.notify(event)


class Listener(object):
    """Listen to events coming from the Event Manager.

    This is just an interface to be subclassed.
    For example to handle an event called 'this-is-a-test', a method called
    'handle_this_is_a_test' must be defined in the subclass, taking as
    arguments the properties of the event.

    For example if the event is defined as:

    e = Event('this-is-a-test', prop=3)

    than the handling function must be:

    def handle_this_is_a_test(ev_type, prop):
        ...

    Note that the char '-' is always translated to '_'.

    """

    def __init__(self, event_manager):
        try:
            self.event_manager = proxy(event_manager)
        except TypeError:
            # This is already a proxy.
            self.event_manager = event_manager
        self._uid = None
        # Only methods starting with 'handle_' will be taken into account.
        # For exemple the callback 'handle_sample_event' will be paired
        # with the event 'sample-event'.
        prefix = 'handle_'
        callbacks = [(e[len(prefix):].replace('_', '-'), getattr(self, e))
                     for e in dir(self) if e.startswith(prefix)]
        # Generate a dictionary which pair events to their callbacks.
        self.callbacks_dict = dict(callbacks)
        # Save wanted events.
        wanted_events = self.callbacks_dict.keys()
        self.wanted_events = set(wanted_events)
        # Attach to event manager.
        self.attach()

    def __set_uid(self, new_uid):
        """Get a unique id."""
        if self._uid is None:
            self._uid = self.event_manager.get_new_uid(new_uid)

    def __get_uid(self):
        return self._uid

    uid = property(__get_uid, __set_uid)

    def post(self, *events):
        """Post events to the parent event manager."""
        self.event_manager.post(*events)

    def notify(self, event):
        """Handle events."""
        kargs = dict(event.__dict__)
        ev_type = kargs.pop('ev_type')
        self.callbacks_dict[event.ev_type](ev_type, **kargs)

    def attach(self):
        """Register to the event manager."""
        self.event_manager.attach_listener(self, *self.wanted_events)

    def detach(self):
        """Detach from event manager."""
        self.event_manager.detach_listener(self)


class EventManagerAndListener(EventManager, Listener):

    """Used as listener and event manager.

    Used to isolate some parts of Yaranullin (i.e. network listeners,
    pygame listeners...).
    If independent is True, this class is used to group listeners that goes
    in the same thread.
    It will register to its parent event manager with its own wanted events as
    well as listeners'.
    """

    def __init__(self, event_manager, independent=False):
        EventManager.__init__(self)
        Listener.__init__(self, event_manager)
        self.independent = independent

    def get_new_uid(self, uid):
        return self.event_manager.get_new_uid(uid)

    def upgrade_wanted_events(self):
        """Upgrade wanted events avoiding duplicates.

        It is used when other listeners connects to this event manager.

        """
        self.detach()
        events = set(self.wanted_events)
        events |= set(self.events.keys())
        if self.independent:
            # We don't want to listen to ticks coming from the parent
            # event manager.
            events -= set(('tick',))
        else:
            # We want to receive ticks otherwise the event queue will never
            # be emptied.
            events |= set(('tick',))
        self.event_manager.attach_listener(self, *events)

    def attach_listener(self, listener, *wanted_events):
        EventManager.attach_listener(self, listener, *wanted_events)
        self.upgrade_wanted_events()

    def detach_listener(self, listener):
        EventManager.detach_listener(self, listener)
        self.upgrade_wanted_events()

    def post(self, *events):
        """Add an event to the event queue."""
        # Post downstream only ticks, all the other events must go up until
        # they reach the main EventManager.
        for event in events:
            if event.ev_type == 'tick':
                if 'tick' in self.wanted_events:
                    Listener.notify(self, event)
                self.event_queue.append(event)
                self.consume_event_queue()
            else:
                # Post upstream, up to the main event manager.
                self.event_manager.post(event)

    def notify(self, event):

        # If this EventManager is independent (means it runs on its own
        # thread),then copy the event before using it any further.
        if self.independent:
            # For some reason deepcopy fails if one of the attributes of the
            # event is a cStringIO.SringIO class. This is fixed using
            # StringIO.StringIO instead, but I don't know why.
            event = deepcopy(event)
        # Be notified about wanted events like a regular Listener.
        if event.ev_type in self.wanted_events:
            Listener.notify(self, event)
        # Downstream propagation of events.
        self.event_queue.append(event)
        if event.ev_type == 'tick':
            # Consume the event queue every tick.
            self.consume_event_queue()
