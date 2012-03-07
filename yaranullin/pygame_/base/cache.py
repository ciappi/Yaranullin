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
import zlib

import pygame

from ...event_system import Listener, Event
from ...config import YR_RES_DIR


class Cache(Listener):

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self._cache = {}

    def get(self, hash_):
        if 'value' in self._cache[hash_]:
            return self._cache[hash_]['value']

    def handle_resource_new(self, hash, width, height, format):
        self._cache[hash] = {}
        self._cache[hash]['size'] = width, height
        self._cache[hash]['format'] = format
        try:
            with open(os.path.join(YR_RES_DIR, hash + '.res')) as f:
                self._cache[hash]['value'] = zlib.decompress(f.read())
        except IOError:
            self.post(Event('resource-request', hash=hash))

    def handle_resource_update(self, ev_type, hash, resource):
        size = self._cache[hash]['size']
        format = self._cache[hash]['format']
        with open(os.path.join(YR_RES_DIR, hash + '.res'), 'w') as f:
            f.write(zlib.compress(resource))
        try:
            surf = pygame.image.fromstring(resource, size, format)
            self._cache[hash] = surf.convert()
        except pygame.error:
            logging.error('Error loading a resource.')


class CachedProperty(object):

    def __init__(self, default=None):
        self.hash = None
        self.default = default

    def __get__(self, instance, owner):
        value = instance.cache.get(self.hash)
        if value is not None:
            return value
        else:
            return self.default

    def __set__(self, instance, value):
        if value is not None:
            self.hash = value
