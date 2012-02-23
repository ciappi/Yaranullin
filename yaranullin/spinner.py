# yaranullin/spinner.py
#
# Copyright (c) 2011 Marco Scopesi <marco.scopesi@gmail.com>
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
from time import sleep, time

from event_system import Event, Listener


class CPUSpinner(Listener):

    """Basic CPU Spinner class.

    It posts tick events periodically so that the parent event manager will
    process the event queue.

    """

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.keep_going = True

    def run(self):
        """This is the main loop."""
        state = 'waiting'
        waiting_starts = int(time())
        try:
            while self.keep_going:
                self.post(Event('tick'))
                if state == 'waiting':
                    sleep(0.1)
                    if len(self.event_manager.event_queue):
                        state == 'running'
                    elif ((int(time()) - waiting_starts) > 10):
                        # After a certain amount of time go to sleep.
                        state == 'sleeping'
                elif state == 'running':
                    sleep(0.01)
                    if not len(self.event_manager.event_queue):
                        state == 'waiting'
                        waiting_starts = int(time())
                elif state == 'sleeping':
                    sleep(0.5)
                    if len(self.event_manager.event_queue):
                        state == 'running'
                else:
                    sys.exit('Unknown spinner state.')  # Log something as well.
        except KeyboardInterrupt:
            self.post(Event('quit'))
            self.post(Event('tick'))

    def handle_quit(self, ev_type):
        # this will stop the while loop from running
        self.keep_going = False
