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
import pygame.locals as PL

from yaranullin.config import CONFIG
from yaranullin.event_system import post, connect


class PygameKeyboard(object):
    """Handle Pygame Keyboard events.

    Translates a Pygame KEYDOWN event into a Yaranullin 'key-down' event and
    than post it to the event manager.
    """

    def __init__(self):
        connect('tick', self.handle_tick)
        self.state = 'released'
        self.repeating_event = None
        self.t = 0
        self.delay = 0.5
        self.Dt = self.delay / 20

    def handle_tick(self, event_dict):
        dt = event_dict['dt']
        if self.state == 'pressed':
            self.t += dt
            if self.t >= self.delay:
                self.state = 'firing'
                post(self.repeating_event[0], self.repeating_event[1])
        elif self.state == 'firing':
            self.t += dt
            if (self.t - self.delay) > self.Dt:
                post(self.repeating_event[0], self.repeating_event[1])
                self.t = self.delay
        for pygame_event in pygame.event.get([PL.KEYDOWN, PL.KEYUP]):
            if pygame_event.type == PL.KEYDOWN:
                ev_name = 'key-down'
                ev_dict = {'key': pygame_event.key,
                    'mod': pygame_event.mod, 'unicode': pygame_event.unicode}
                post(ev_name, ev_dict)
                self.repeating_event = ev_name, ev_dict
                self.state = 'pressed'
                self.t = 0
            else:
                self.repeating_event = None
                self.state = 'released'
                self.t = 0


class PygameMouse(object):

    """Handle Pygame mouse events.

    Translate Pygame MOUSEMOTION, MOUSEBUTTONUP and MOUSEBUTTONDOWN into
    Yaranullin events. It implements a double click event since it is not
    automatically handled by pygame.
    """

    def __init__(self):
        connect('tick', self.handle_tick)
        self.state = 'idle'
        self.timeout = CONFIG.getint('pygame', 'mouse-click-delay') / 1000.0

    def handle_tick(self, event_dict):
        dt = event_dict['dt']
        if self.state == 'pressed':
            self.t += dt
            if self.t > self.timeout:
                self.state = 'idle'
        elif self.state == 'released':
            self.t += dt
            if self.t > self.timeout:
                self.state = 'idle'
                # fire single click
                post('mouse-click-single-left', pos=self.pos)
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
                        post('mouse-motion', pos=pygame_event.pos,
                            rel=pygame_event.rel)
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
                        post('mouse-click-double-left', pos=pygame_event.pos)
                elif pygame_event.type == PL.MOUSEMOTION:
                    self.state = 'idle'
            elif self.state == 'drag':
                if (pygame_event.type == PL.MOUSEMOTION and
                        pygame_event.buttons == (True, False, False)):
                    post('mouse-drag-left', pos=pygame_event.pos,
                        rel=pygame_event.rel)
                else:
                    self.state = 'idle'  # fire mouse drop event
                    post('mouse-drop-left', pos=pygame_event.pos)


class PygameSystem(object):
    """Handle pygame QUIT."""

    def __init__(self):
        connect('tick', self.handle_tick)

    def handle_tick(self):
        for pygame_event in pygame.event.get(PL.QUIT):
            post('quit')
