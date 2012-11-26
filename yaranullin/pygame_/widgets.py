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


"""Basic widgets."""

import os
import pygame

from yaranullin.event_system import connect
from yaranullin.config import YR_RES_DIR


class Frame(object):

    def __init__(self, parent=None, rect=None):
        self.parent = parent
        if rect is None:
            self.rect = pygame.rect.Rect(0, 0, 0, 0)
        else:
            self.rect = rect

    @property
    def abs_pos(self):
        x, y = self.rect.topleft
        if self.parent:
            rx, ry = self.parent.abs_pos
            x, y = x + rx, y + ry
        return x, y

    @property
    def abs_rect(self):
        rect = pygame.rect.Rect(self.rect)
        rect.topleft = self.abs_pos
        return rect


class Widget(Frame, pygame.sprite.Sprite):

    """The base widgets.

    It is a simple pygame sprite.

    """

    def __init__(self, parent):
        pygame.sprite.Sprite.__init__(self)
        Frame.__init__(self, parent)

    @property
    def image(self):
        return pygame.surface.Surface((self.rect.size)).convert()

    def update(self, dt):
        """Update the widget.

        This is useful to update parameters and create animation thanks to
        the input dt (time in seconds between two ticks).

        """
        pass


class Button(Widget):

    """A simple button that can be clicked."""

    def __init__(self, parent, image=None):
        Widget.__init__(self, parent)
        connect('mouse-click-single-left',
            self.handle_mouse_click_single_left())

    def on_mouse_click_single_left(self):
        pass

    def handle_mouse_click_single_left(self, ev_dict):
        pos = ev_dict['pos']
        if self.abs_rect.collidepoint(pos):
            self.on_mouse_click_single_left()


class TextLabel(Widget):
    """A text label."""

    def __init__(self, parent, text, font_name, font_size=20,
                 font_color=(255, 0, 0)):
        Widget.__init__(self, parent)
        self.text = text
        self.font_color = font_color
        self.font_size = font_size
        self.font_name = os.path.join(YR_RES_DIR, 'fonts', font_name)
        try:
            self.font = pygame.font.Font(self.font_name,
                                         self.font_size)
        except:
            default = pygame.font.get_default_font()
            self.font = pygame.font.SysFont(default, self.font_size)
        self.render_text()

    @property
    def image(self):
        return self._image

    def render_text(self):
        """Render the text using the given parameters."""
        text = self.text
        color = self.font_color
        # Fallback to default font if needed.
        self._image = self.font.render(text, True, color)
        self.rect.size = self.image.get_rect().size
