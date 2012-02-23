# yaranullin/pygame_/base/controllers.py
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

    def __init__(self, event_manager, *events):
        Listener.__init__(self, event_manager, *events)
        self.timeout = CONFIG.getint('pygame', 'mouse-click-delay')
        # This is the state of the left button, used to check for a double
        # click.
        self.left_button = {'first_click_time': 0,
                            'clicks_before_timeout': 0, 'pos': (0, 0)}

    def handle_tick(self, ev_type, dt):
        lB = self.left_button
        event = None
        if lB['first_click_time']:
            curr_time = pygame.time.get_ticks()
            if ((curr_time - lB['first_click_time']) > self.timeout):
                # We have to wait some amount of time before firing a single
                # click event, otherwise we cannot check a double click.
                if lB['clicks_before_timeout'] == 1:
                    event = Event('mouse-click-single-left',
                                  pos=lB['pos'])
                # We must reset the state alter the timeout has elapsed.
                lB['clicks_before_timeout'] = 0
                lB['first_click_time'] = 0

        for pygame_event in pygame.event.get([PL.MOUSEMOTION,
                                             PL.MOUSEBUTTONUP,
                                             PL.MOUSEBUTTONDOWN]):
            if pygame_event.type == PL.MOUSEBUTTONUP:
                # Adds a click to the state and, it there are 2 clicks
                # registered, fires a double click.
                if pygame_event.button == 1:
                    lB['clicks_before_timeout'] += 1
                    if lB['clicks_before_timeout'] == 2:
                        event = Event('mouse-click-double-left',
                                      pos=lB['pos'])
                        lB['clicks_before_timeout'] = 0
                        lB['first_click_time'] = 0
            elif pygame_event.type == PL.MOUSEBUTTONDOWN:
                reset_left_button = True
                if pygame_event.button == 1:
                    reset_left_button = False
                    # Save the time and the position of the first left click.
                    if lB['clicks_before_timeout'] == 0:
                        lB['first_click_time'] = pygame.time.get_ticks()
                        lB['pos'] = pygame_event.pos
                elif pygame_event.button == 3:
                    event = Event('mouse-click-single-right',
                                  pos=pygame_event.pos)
                elif pygame_event.button == 4:
                    event = Event('mouse-wheel-up', pos=pygame_event.pos)
                elif pygame_event.button == 5:
                    event = Event('mouse-wheel-down', pos=pygame_event.pos)
                # If we push another button (not the left one), we must reset
                # the state of the left button, like in every window manager.
                if reset_left_button:
                    lB['clicks_before_timeout'] = 0
                    lB['first_click_time'] = 0
            elif pygame_event.type == PL.MOUSEMOTION:
                # Moving the mouse should reset the state of the left button
                # as well.
                lB['clicks_before_timeout'] = 0
                lB['first_click_time'] = 0
                if pygame_event.buttons == (False, False, False):
                    event = Event('mouse-motion', pos=pygame_event.pos,
                                  rel=pygame_event.rel)
                # If needed it is very simple to add another event for a
                # mouse drag with another button (or more than one) pressed.
                elif pygame_event.buttons == (True, False, False):
                    event = Event('mouse-drag-left', pos=pygame_event.pos,
                                  rel=pygame_event.rel)

        if event:
            self.event_manager.post(event)


class PygameSystem(Listener):
    """Handle pygame QUIT."""

    def handle_tick(self, ev_type, dt):
        for pygame_event in pygame.event.get(PL.QUIT):
            event = Event('quit')
            self.event_manager.post(event)
