# yaranullin/pipe.py
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

''' Communication between processes '''

from yaranullin.events import TICK, ANY
from yaranullin.event_system import post, connect


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
        connect(ANY, self.handle)
        connect(TICK, self.tick)

    def handle(self, **event_dict):
        ''' Put given event to the out queue '''
        try:
            id_ = event_dict['id']
            event = event_dict['event']
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
        self.out_queue.put(event_dict)

    def tick(self):
        ''' Get all the event from the in queue '''
        while not self.in_queue.empty():
            event_dict = self.in_queue.get()
            event = event_dict.pop('event')
            self.posted_events.add(post(event, event_dict))
