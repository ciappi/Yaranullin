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

import sys

import pygame
import pygame.locals as PL

from ...event_system import Event, Listener
from ...config import CONFIG


class PygameKeyboard(Listener):
    """Handle Pygame Keyboard events.

    Translates a Pygame KEYDOWN event into a Yaranullin 'key-down' event and
    than post it to the event manager.
    """

    def handle_tick(self, ev_type, dt):
        for pygame_event in pygame.event.get([PL.KEYDOWN, PL.KEYUP]):
            event = None
            if pygame_event.type == PL.KEYDOWN:
                event = Event('key-down', key=pygame_event.key,
                              mod=pygame_event.mod,
                              unicode=pygame_event.unicode)

            if event:
                self.event_manager.post(event)


class PygameMouse(Listener):

    """Handle Pygame mouse events.

    Translate Pygame MOUSEMOTION, MOUSEBUTTONUP and MOUSEBUTTONDOWN into
    Yaranullin events. It implements a double click event since it is not
    automatically handled by pygame.
    """

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self.state = 'idle'
        self.timeout = CONFIG.getint('pygame', 'mouse-click-delay') / 1000.0

    def handle_tick(self, ev_type, dt):
        events = []
        if self.state == 'pressed':
            self.t += dt
            if self.t > self.timeout:
                self.state = 'idle'
        elif self.state == 'released':
            self.t += dt
            if self.t > self.timeout:
                self.state = 'idle'
                # fire single click
                events.append(Event('mouse-click-single-left',
                                    pos=self.pos))
        for pygame_event in pygame.event.get([PL.MOUSEMOTION,
                                             PL.MOUSEBUTTONUP,
                                             PL.MOUSEBUTTONDOWN]):
            if self.state == 'idle':
                if pygame_event.type == PL.MOUSEBUTTONDOWN:
                    if pygame_event.button == 1:
                        self.state = 'pressed'
                        self.t = 0
                        self.pos = pygame_event.pos
                elif pygame_event.type == PL.MOUSEMOTION:
                    if pygame_event.buttons == (True, False, False):
                        self.state = 'drag'
                    elif pygame_event.buttons == (False, False, False):
                        events.append(Event('mouse-motion',
                                            pos=pygame_event.pos,
                                            rel=pygame_event.rel))
            elif self.state == 'pressed':
                if pygame_event.type == PL.MOUSEBUTTONUP:
                    if pygame_event.button == 1:
                        self.state = 'released'
                elif pygame_event.type == PL.MOUSEMOTION:
                    self.state = 'idle'
            elif self.state == 'released':
                if pygame_event.type == PL.MOUSEBUTTONUP:
                    if pygame_event.button == 1:
                        self.state = 'idle'
                        # fire double click
                        events.append(Event('mouse-click-double-left',
                                            pos=pygame_event.pos))
                elif pygame_event.type == PL.MOUSEMOTION:
                    self.state = 'idle'
            elif self.state == 'drag':
                if pygame_event.type == PL.MOUSEBUTTONUP:
                    if pygame_event.button == 1:
                        self.state = 'idle'  # fire mouse drop event
                        events.append(Event('mouse-drop-left',
                                            pos=pygame_event.pos))
                else:
                    events.append(Event('mouse-drag-left',
                                        pos=pygame_event.pos,
                                        rel=pygame_event.rel))
            else:
                sys.exit('Unknown mouse button state')
        if events:
            self.post(*events)


class PygameSystem(Listener):
    """Handle pygame QUIT."""

    def handle_tick(self, ev_type, dt):
        for pygame_event in pygame.event.get(PL.QUIT):
            event = Event('quit')
            self.event_manager.post(event)
