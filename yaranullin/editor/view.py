# yaranullin/editor/view.py
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

"""View class for the editor."""

import os
import textwrap

import pygame

from pygcurse import pygcurse
from yaranullin.event_system import Listener
from yaranullin.pygame_.base.event_manager import PygameGUI
from yaranullin.editor.control import CommandPrompt


class PygcursesGUI(PygameGUI):

    """This class is a very simple textual editor for a game.
    
    This class holds only the visual part of the editor.

    For now it displays an 80x24 ncurses like terminal with a command prompt
    at the bottom of it and a blinking cursor. On the remaining part of the
    window the outputs of the commands are displayed.

    This classes is build on top of pygcurse, a cross platform curses library
    build in turn atop pygame. This ensures support not only for all Unixes
    but also for Windows and Android platforms.
    
    """

    rate = 255/0.5
    color = 0

    def __init__(self, *args, **kargs):
        PygameGUI.__init__(self, *args, **kargs)
        self.set_display_mode((80, 24))
        self.win.font = pygame.font.SysFont('monospace', 18)
        self.win.autoupdate = False
        self.cmd_win = CommandPrompt(self)
        self.prompt = 0

    def set_display_mode(self, size, fullscreen=None):
        self.win = pygcurse.PygcurseWindow(size[0], size[1],
                                           "Yaranullin's editor")

    def handle_tick(self, ev_type, dt):
        """Update the screen and provides the cursor animation."""
        color = self.color + self.rate * dt
        if color > 255:
            color = 255
            self.rate = - self.rate
        elif color < 0:
            color = 0
            self.rate = - self.rate
        self.color = color
        col = int(self.color)
        col = col, col, col
        self.win.paint(x=self.prompt, y=23, bgcolor=col)
        self.win.update()

    def handle_print(self, ev_type, text):
        """Print something on the screen clearing any previous data.
        
        This is used to print the output of a command.
        
        """
        self.win.cursor = (0, 0)
        self.win.setscreencolors(clear=True)
        self.win.pygprint(text)

    def handle_print_append(self, ev_type, text):
        """Append some text to the screen."""
        self.win.pygprint(text)

    def handle_prompt(self, ev_type, prompt):
        """Print the prompt.
        
        There is support for multiline text.
        
        """
        prompt = str(prompt)
        if len(prompt) > 78:
            lines = textwrap.wrap(prompt, width=78)
        else:
            lines = [prompt, ]
        lines.reverse()
        self.prompt = len(lines[0])
        # Clear the prompt
        self.win.fill(' ', region=(0, 24 - len(lines) - 1, None, None))
        for n, line in zip(xrange(23, 23 - len(lines), -1), lines):
            self.win.putchars(line, x=0, y=n)
