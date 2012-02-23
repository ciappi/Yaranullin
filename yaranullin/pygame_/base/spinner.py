# yaranullin/pygame_/base/controllers.py
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


import pygame

from ...event_system import Event
from ...spinner import CPUSpinner


class PygameCPUSpinner(CPUSpinner):

    def __init__(self, event_manager):
        CPUSpinner.__init__(self, event_manager)
        self.clock = pygame.time.Clock()

    def run(self):
        self.keep_going = True
        pygame.init()
        try:
            while self.keep_going:
                dt = self.clock.tick(30) / 1000.0
                event = Event('tick', dt=dt)
                self.event_manager.post(event)
                pygame.event.clear()
        except KeyboardInterrupt:
            event = Event('quit')
            self.event_manager.post(event)
            event = Event('tick')
            self.event_manager.post(event)
        pygame.quit()
