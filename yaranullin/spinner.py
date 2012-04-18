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

"""Event loop facilities.

There is one CPUSpinner attached to the main EventManager and there is one
more for every independent EventManagerAndListener. This means there there is
one CPUSpinner for every thread, included the main one.

Its tasks are to periodically generate a 'tick' event and to catch all
unhandled exceptions.

"""

import sys
import traceback
import time

from yaranullin.event_system import Event, Listener


class CPUSpinner(Listener):

    """Basic CPU Spinner class.

    It posts tick events periodically so that the parent event manager will
    process the event queue.

    """

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.keep_going = True

    def run(self):
        """Event loop.

        Periodically post a 'tick' event so than the corresponding event
        manager can process its event queue.

        """
        try:
            while self.keep_going:
                self.post(Event('tick'))
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            # Try to exit cleanly.
            self.post(Event('quit'), Event('tick'))

    def handle_quit(self, ev_type):
        """This will stop the while loop from running."""
        self.keep_going = False
