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

from yaranullin.event_system import connect
from yaranullin.pygame_.utils import saturation
from yaranullin.pygame_.widgets import Widget


class Container(Widget):

    """A container for widgets."""

    def __init__(self, parent=None, rect=None):
        Widget.__init__(self, parent, rect)
        self.child_widgets = []

    def append(self, widget):
        self.child_widgets.append(widget)
        self.update_widgets_position()

    def remove(self, widget):
        self.child_widgets.remove(widget)
        self.update_widgets_position()

    def sort(self, *args, **kargs):
        self.child_widgets.sort(*args, **kargs)
        self.update_widgets_position()

    def update_widgets_position(self):
        pass

    def update(self, dt):
        """Updata the frame state."""
        for child in self.child_widgets:
            child.update(dt)
        self.update_widgets_position()

    def subsurface(self, surf):
        if not self.parent:
            return surf
        rect = self.abs_rect
        return surf.subsurface(rect)

    def draw(self, surf):
        """Draw this container and its widgets."""
        sub_surf = self.subsurface(surf)
        sub_surf.blit(self.image, (0, 0))
        for child in self.child_widgets:
            child.draw(sub_surf)


class OrderedContainer(Container):

    def __init__(self, parent=None, rect=None, gap=0):
        Container.__init__(self, parent, rect)
        self.gap = gap


class VContainer(OrderedContainer):

    def update_widgets_position(self):
        """First widget in self.child_widgets in the top element."""
        cx = self.rect.centerx
        top = self.rect.top + self.gap
        for widget in self.child_widgets:
            widget.rect.top = top
            widget.rect.centerx = cx
            b = widget.rect.bottom
            top = b + self.gap


class HContainer(OrderedContainer):

    def update_widgets_position(self):
        """First widget in self.child_widgets in the left element."""
        cy = self.rect.centery
        left = self.rect.left + self.gap
        for widget in self.child_widgets:
            widget.rect.left = left
            widget.rect.centery = cy
            r = widget.rect.right
            left = r + self.gap


class ScrollableContainer(Container):

    def __init__(self, parent, rect=None):
        Container.__init__(self, parent, rect)
        self.position = (0, 0)
        self.fullsize = self.rect.size
        connect('mouse-drag-left', self.handle_mouse_drag_left)

    def draw(self, surf):
        """Draw this container and its widgets."""
        sub_surf = self.subsurface(surf)
        temp_surf = pygame.surface.Surface(self.fullsize)
        for child in self.child_widgets:
            child.draw(temp_surf)
        sub_surf.blit(temp_surf, self.position)

    def handle_mouse_drag_left(self, ev_dict):
        pos = ev_dict['pos']
        rel = ev_dict['rel']
        if not self.abs_rect.collidepoint(pos):
            return
        new_pos = (self.position[0] + rel[0],
            self.position[1] + rel[1])
        high = (0, 0)
        low = (min(0, self.rect.width - self.fullsize[0]),
               min(0, self.rect.height - self.fullsize[1]))
        x = saturation(new_pos[0], low=low[0], high=high[0])
        y = saturation(new_pos[1], low=low[1], high=high[1])
        self.position = x, y
