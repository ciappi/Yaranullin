# yaranullin/run_client.py
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

import asyncore
try:
    import pygame
    import pygame.locals as PL
except ImportError:
    PYGAME = False
else:
    from yaranullin.pygame_.gui import PygameGui
    from yaranullin.pygame_.controllers import PygameKeyboard,\
        PygameMouse, PygameSystem
    PYGAME = True

from yaranullin.config import CONFIG
from yaranullin.event_system import post, process_queue
from yaranullin.network.client import ClientEndPoint
from yaranullin.game.game_wrapper import DummyGameWrapper


# Initialize network
ClientEndPoint()
HOST = CONFIG.get('network', 'host')
PORT = CONFIG.getint('network', 'port')
GAME = DummyGameWrapper()
if PYGAME:
    pygame.init()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([PL.QUIT, PL.MOUSEMOTION, PL.MOUSEBUTTONUP,
                              PL.MOUSEBUTTONDOWN, PL.KEYDOWN, PL.KEYUP])
    pygame.display.set_mode((0, 0))
    KEYBOARD = PygameKeyboard()
    MOUSE = PygameMouse()
    SYSTEM = PygameSystem()
    GUI = PygameGui()


def run(args):
    ''' Main loop for the client '''
    post('join', host=HOST, port=PORT)
    stop = False
    if PYGAME:
        clock = pygame.time.Clock()
    while not stop:
        if PYGAME:
            dt = clock.tick(60) / 1000.0
            post('tick', dt=dt)
            pygame.display.flip()
        else:
            post('tick')
        stop = process_queue()
        asyncore.poll(0.002)
    if PYGAME:
        pygame.quit()
