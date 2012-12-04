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

import weakref

import pygame

from yaranullin.event_system import connect
from yaranullin.pygame_.utils import load_image, render_text


class Widget(object):

    """The base widgets."""

    def __init__(self, parent=None, rect=None):
        if rect is None:
            self.rect = pygame.rect.Rect(0, 0, 1, 1)
        else:
            self.rect = rect
        if parent is not None:
            self.parent = weakref.proxy(parent)
        else:
            self.parent = None
        self._image = 'black'
        self.alpha = False
        self.rotated = False

    @property
    def abs_rect(self):
        rect = pygame.rect.Rect(self.rect)
        if not self.parent:
            return rect
        rx, ry = rect.topleft
        x, y = self.parent.rect.topleft
        rect.topleft = rx + x, ry + y
        return rect

    def _get_image(self):
        '''Load the image'''
        return load_image(self._image, self.rect.size, self.alpha,
            self.rotated)

    def _set_image(self, image):
        '''Store the image name.'''
        self._image = image

    image = property(_get_image, _set_image)

    def update(self, dt):
        """Update the widget.

        This is useful to update parameters and create animation thanks to
        the input dt (time in seconds between two ticks).

        """
        pass

    def draw(self, surf):
        img = self.image
        if img:
            surf.blit(img, self.rect.topleft)


class Button(Widget):

    """A simple button that can be clicked."""

    def __init__(self, parent=None, rect=None):
        Widget.__init__(self, parent, rect)
        connect('mouse-click-single-left',
            self.handle_mouse_click_single_left)

    def on_mouse_click_single_left(self, ev_dict):
        pass

    def handle_mouse_click_single_left(self, ev_dict):
        pos = ev_dict['pos']
        if self.abs_rect.collidepoint(pos):
            self.on_mouse_click_single_left(ev_dict)


class TextLabel(Widget):

    def __init__(self, text, font_name, font_size=20,
                 font_color='red'):
        Widget.__init__(self)
        self.text = text
        self.font_color = font_color
        self.font_size = font_size
        self.font_name = font_name
        self.underline = False
        self.italic = False

    def _get_image(self):
        '''Render the text'''
        surf = render_text(self.text, self.font_name,
            self.font_size, self.font_color, self.underline, self.italic)
        self.rect.size = surf.get_size()
        #print self.rect
        return surf

    image = property(_get_image)
