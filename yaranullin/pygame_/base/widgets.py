# yaranullin/pygame_/base/widgets.py
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

import os
import pygame

from yaranullin.config import YR_RES_DIR
from yaranullin.event_system import Listener


class Widget(Listener, pygame.sprite.Sprite):

    """The base widgets.

    It is a simple pygame sprite and a listener connected to the event manager.

    """

    def __init__(self, container, rect=None):
        pygame.sprite.Sprite.__init__(self)
        Listener.__init__(self, container)
        if rect is None:
            self.rect = pygame.rect.Rect(0, 0, 0, 0)
        else:
            self.rect = rect
        self.image = pygame.surface.Surface((self.rect.size)).convert()

    @property
    def cache(self):
        return self.event_manager.cache

    @property
    def abs_pos(self):
        rx, ry = self.event_manager.abs_pos
        x, y = self.rect.topleft
        return x + rx, y + ry

    @property
    def abs_rect(self):
        rect = pygame.rect.Rect(self.rect)
        rect.topleft = self.abs_pos
        return rect

    def update(self, dt):
        """Update the widget.

        This is useful to update parameters and create animation thanks to
        the input dt (time in seconds between two ticks).

        """
        pass


class ImageButton(Widget):

    """A simple image that can be clicked."""

    def __init__(self, container, image=None):
        Widget.__init__(self, container)

    def on_mouse_click_single_left(self):
        pass

    def handle_mouse_click_single_left(self, ev_type, pos):
        if self.abs_rect.collidepoint(pos):
            self.on_mouse_click_single_left()


class TextLabel(Widget):
    """A text label."""

    def __init__(self, event_manager, text, font_name, font_size=20,
                 font_color=(255, 0, 0)):
        Widget.__init__(self, event_manager)
        self.text = text
        self.font_color = font_color
        self.font_size = font_size
        self.font_name = os.path.join(YR_RES_DIR, font_name)
        try:
            self.font = pygame.font.Font(self.font_name,
                                         self.font_size)
        except:
            default = pygame.font.get_default_font()
            self.font = pygame.font.SysFont(default, self.font_size)
        self.render_text()

    def render_text(self):
        """Render the text using the given parameters."""
        text = self.text
        color = self.font_color
        # Fallback to default font if needed.
        self.image = self.font.render(text, True, color)
        self.rect.size = self.image.get_rect().size
