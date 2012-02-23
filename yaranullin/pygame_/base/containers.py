# yaranullin/pygame_/base/containers.py
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

from ...event_system import EventManagerAndListener


class Container(EventManagerAndListener):

    """A container for widgets."""

    def __init__(self, main_window, rect=None):

        EventManagerAndListener.__init__(self, main_window)
        self.widgets = pygame.sprite.Group()
        self.ordered_widgets = []
        if rect is None:
            self.rect = pygame.rect.Rect(0, 0, 0, 0)
        else:
            self.rect = rect
        self.image = pygame.surface.Surface((self.rect.size)).convert()

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

    def append(self, widget):
        self.widgets.add(widget)
        self.ordered_widgets.append(widget)
        self.update_widgets_position()

    def remove(self, widget):
        self.widgets.remove(widget)
        self.ordered_widgets.remove(widget)
        self.update_widgets_position()

    def sort(self, *args, **kargs):
        self.ordered_widgets.sort(*args, **kargs)
        self.update_widgets_position()

    def update_widgets_position(self):
        pass

    def update(self, dt):
        """Updata the frame state."""
        self.widgets.update(dt)

    def draw(self):
        """Draw this container and its widgets."""
        # This is the destination surface on the screen.
        surf = pygame.display.get_surface().subsurface(self.abs_rect)
        # Draw the background image.
        surf.blit(self.image, (0, 0))
        # Draw all the widgets.
        self.widgets.draw(surf)

    def handle_tick(self, ev_type, dt):
        """Handle tick event."""
        self.update(dt)
        self.draw()


class OrderedContainer(Container):

    def __init__(self, event_manager, rect=None, gap=5):
        Container.__init__(self, event_manager, rect)
        self.gap = gap


class VContainer(OrderedContainer):

    def update_widgets_position(self):
        """First widget in self.widgets in the top element."""
        cx = self.rect.centerx
        top = self.rect.top + self.gap
        for widget in self.ordered_widgets:
            widget.rect.top = top
            widget.rect.centerx = cx
            b = widget.rect.bottom
            top = b + self.gap


class HContainer(OrderedContainer):

    def update_widgets_position(self):
        """First widget in self.widgets in the left element."""
        cy = self.rect.centery
        left = self.rect.left + self.gap
        for widget in self.ordered_widgets:
            widget.rect.left = left
            widget.rect.centery = cy
            r = widget.rect.right
            left = r + self.gap
