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

"""The event system of Yaranullin."""

import logging

from weakref import proxy
from collections import deque


class Event(object):

    """The class used for all events.

    This is used to broadcast messages to all listeners in all threads.

    """

    def __init__(self, ev_type, **kargs):

        self.__dict__.update(**kargs)
        # Ensure that the event type is corrent event if there is a
        # type keyword argument in kargs.
        self.ev_type = ev_type


class EventManager(object):
    """Broadcast events to registered listeners.

    Every listener will choose event types to get at creation time.
    There is just one EventManager at runtime.

    """

    def __init__(self):
        # Couple event types to listeners that want them.
        # {event_type: [listener_1, listener_2, ...], ...}
        self.events = dict()
        # Global event queue, thread safe thanks to deque.
        self.event_queue = deque()

    def attach_listener(self, listener, *wanted_events):
        """Register a Listener."""
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
            # Continue if there is no registered listeners.
            if event.ev_type not in self.events:
                continue
            # Avoid runtime errors for listeners created during
            # the following 'for' loop, by copying the list.
            listeners = tuple(self.events[event.ev_type])
            for listener in listeners:
                listener.notify(event)

    def __del__(self):
        """Ensure a clean exit for all listeners."""
        self.post(Event('quit'), Event('tick'))


class Listener(object):
    """Listen to events coming from the Event Manager.

    This is just an interface to be subclassed.

    """

    def __init__(self, event_manager):
        try:
            self.event_manager = proxy(event_manager)
        except TypeError:
            # This is already a proxy.
            self.event_manager = event_manager
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

    def post(self, *events):
        """Post events to the parent event manager."""
        self.event_manager.post(*events)

    def notify(self, event):
        """Handle events."""
        #self.callbacks_dict[event.ev_type](event)
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
    in another thread.
    It will register to its parent event manager with its own wanted events as
    well as listeners'.
    """

    def __init__(self, event_manager, independent=False):
        EventManager.__init__(self)
        Listener.__init__(self, event_manager)
        self.independent = independent

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
        # Post downstream only ticks.
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

        # Be notified about wanted events like a regular Listener.
        if event.ev_type in self.wanted_events:
            Listener.notify(self, event)
        # Downstream propagation of events.
        self.event_queue.append(event)
        if event.ev_type == 'tick':
            # Consume the event queue every tick.
            self.consume_event_queue()
