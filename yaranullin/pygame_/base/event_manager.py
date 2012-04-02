# yaranullin/pygame_/base/event_manager.py
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
#import pygame.locals as PL

from yaranullin.event_system import EventManagerAndListener
from yaranullin.pygame_.base.controllers import PygameKeyboard, PygameMouse,\
                                                PygameSystem



class PygameGUI(EventManagerAndListener):

    """Used to test basic functionality of pygame.

    Pygames needs a working display in order to have a event system.

    """

    def __init__(self, event_manager):
        EventManagerAndListener.__init__(self, event_manager,
                                         independent=True)
        self.keyboard_controller = PygameKeyboard(self)
        self.mouse_controller = PygameMouse(self)
        self.system_controller = PygameSystem(self)

    def set_display_mode(self, size=(0, 0), fullscreen=False):
        if fullscreen:
            pygame.display.set_mode(size, PL.FULLSCREEN)
        else:
            pygame.display.set_mode(size)

    @property
    def abs_pos(self):
        return (0, 0)

    def handle_tick(self, ev_type, dt):
        """Update the display at every tick."""
        pygame.display.flip()
