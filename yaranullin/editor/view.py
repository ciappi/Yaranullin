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

import os

import pygame

from pygcurse import pygcurse
from yaranullin.config import YR_RES_DIR
from yaranullin.event_system import Listener
from yaranullin.pygame_.base.event_manager import PygameGUI
from yaranullin.editor.control import CommandPrompt


class PygcursesGUI(PygameGUI):

    def __init__(self, *args, **kargs):
        PygameGUI.__init__(self, *args, **kargs)
        self.set_display_mode((80, 24))
        self.win.font = pygame.font.Font(
            os.path.join(YR_RES_DIR, 'mono_font.ttf'), 28)
        self.win.autoupdate = False
        self.cmd_win = CommandPrompt(self)

    def set_display_mode(self, size, fullscreen=None):
        self.win = pygcurse.PygcurseWindow(size[0], size[1],
                                           "Yaranullin's editor")

    def handle_tick(self, ev_type, dt):
        self.win.update()

    def handle_print(self, ev_type, text):
        self.win.cursor = (0, 0)
        self.win.setscreencolors(clear=True)
        self.win.pygprint(text)

    def handle_print_append(self, ev_type, text):
        self.win.pygprint(text)
