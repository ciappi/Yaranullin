# yaranullin/resources.py
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

import logging
import os
import bz2

import pygame

from ...event_system import Listener, Event
from ...config import YR_CACHE_DIR


class Cache(Listener):

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self._cache = {}

    def get(self, name):
        if name in self._cache:
            return self._cache[name]
        else:
            try:
                fname = os.path.join(YR_CACHE_DIR, name)
                surf = pygame.image.load(fname)
                surf = surf.convert()
                self._cache[name] = surf
                return surf
            except pygame.error:
                print 'requesting an image'
                self.post(Event('texture-request', name=name))
                self._cache[name] = None

    def handle_texture_update(self, ev_type, name, data):
        fname = os.path.join(YR_CACHE_DIR, name)
        with open(fname, 'w+b') as f:
            f.write(bz2.decompress(data))
        try:
            surf = pygame.image.load(fname)
            surf = surf.convert()
            self._cache[name] = surf
        except pygame.error:
            logging.error('Error loading a texture.')


class CachedProperty(object):

    def __init__(self, default=None):
        self.name = None
        self.default = default

    def __get__(self, instance, owner):
        if self.name is not None:
            value = instance.cache.get(self.name)
            if value is not None:
                return value
            else:
                return self.default

    def __set__(self, instance, value):
        if value is not None:
            self.name = value
