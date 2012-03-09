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

from utils import sign, saturation
from ...event_system import EventManagerAndListener


class Container(EventManagerAndListener):

    """A container for widgets."""

    def __init__(self, main_window, rect=None):

        EventManagerAndListener.__init__(self, main_window)
        self.widgets = pygame.sprite.Group()
        self.ordered_widgets = []
        self.view = (0, 0)
        if rect is None:
            self.rect = pygame.rect.Rect(0, 0, 0, 0)
        else:
            self.rect = rect
        self.image = pygame.surface.Surface((self.rect.size)).convert()
        self._image = self.image.copy()

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
        # Clear the widgets.
        self.widgets.clear(self.image, self._image)
        # Draw all the widgets.
        self.widgets.draw(self.image)
        # Draw the background image.
        surf.blit(self.image, self.view)

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


class ScrollableContainer(Container):

    def __init__(self, main_window, rect=None):
        Container.__init__(self, main_window, rect)
        self.dragging = False
        self.position = (0, 0)
        self.velocity = (0, 0)
        self.deceleration = 2000

    def update(self, dt):
        """Animation sample."""
        if self.dragging == False:
            # Constant deceleration.
            d = (-abs(self.deceleration) * sign(self.velocity[0]),
                 -abs(self.deceleration) * sign(self.velocity[1]))
            xp = self.velocity[0] + d[0] * dt
            yp = self.velocity[1] + d[1] * dt
            x = self.position[0] + self.velocity[0] * dt
            y = self.position[1] + self.velocity[1] * dt
            # Put velocity to zero if necessary.
            if sign(xp) != sign(self.velocity[0]):
                xp = 0
            if sign(yp) != sign(self.velocity[1]):
                yp = 0
            self.velocity = xp, yp
            new_pos = x, y
        else:
            new_pos = self.view
            xp = (new_pos[0] - self.position[0]) / dt
            yp = (new_pos[1] - self.position[1]) / dt
            if (xp, yp) != (0, 0):
                self.velocity = xp, yp
        # Limit the position.
        high = (0, 0)
        low = (min(0, self.rect.width - self.image.get_width()),
               min(0, self.rect.height - self.image.get_height()))
        x = saturation(new_pos[0], low=low[0], high=high[0])
        y = saturation(new_pos[1], low=low[1], high=high[1])
        self.view = int(x), int(y)
        self.position = x, y

    def handle_mouse_drag_left(self, ev_type, rel, pos):
        if self.abs_rect.collidepoint(pos):
            self.dragging = True
            self.view = self.view[0] + rel[0], self.view[1] + rel[1]

    def handle_mouse_drop_left(self, ev_type, pos):
        if self.abs_rect.collidepoint(pos):
            self.dragging = False
