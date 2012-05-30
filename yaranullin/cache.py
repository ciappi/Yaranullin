# yaranullin/cache.py
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

from yaranullin.event_system import connect, post
from yaranullin.config import YR_CACHE_DIR


#
# The cache is never deleted
#
_CACHE = {}


def cache(func):
    ''' Cache decorator '''

    def _cache(resource_name):
        if not isinstance(resource_name, basestring):
            raise RuntimeError('cache._cache(): invalid name for a cached '
                    'object')
        try:
            return _CACHE[hash(func), resource_name]
        except KeyError:
            try:
                cached_obj = func(os.path.join(YR_CACHE_DIR, resource_name))
            except IOError as why:
                if why.errno == 2:
                    # The file is not available, ask the server...
                    post('resource-request', name=resource_name)
                else:
                    raise
            else:
                _CACHE[hash(func), resource_name] = cached_obj
                return cached_obj

    return _cache


def update_cache(event_dict):
    ''' Update the cache '''
    resource_name = event_dict['name']
    resource = event_dict['resource']
    with open(os.path.join(YR_CACHE_DIR, resource_name), 'w') as file_:
        file_.write(resource)

#
# As soon as this module is imported, function 'update_cache' is connected to
# the 'resource-update' event.
#
connect('resource-update', update_cache)
