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

import os
import bz2

from StringIO import StringIO

from yaranullin.event_system import Listener, Event
from yaranullin.config import YR_CACHE_DIR


class Cache(Listener):

    """Cache holder.

    Try to load a file from the disk, otherwise ask the server for it.
    The returned object (through a 'cache-send' event) is a StringIO instance,
    thus the receiving class is responsible for load the data.

    """

    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)
        self._cache = {}

    def handle_cache_get(self, ev_type, name):
        """Handle a request for a cached value.

        Look for a key entry 'name' in the _cache dictionary, otherwise send
        a 'resource-request' event that will be hopefully handled by a server.

        """
        if name in self._cache:
            # The resource is already loaded in memory.
            value = self._cache[name]
        else:
            try:
                # Try to find the resource on the local disk.
                fname = os.path.join(YR_CACHE_DIR, name)
                with open(fname, 'rb') as f:
                    data = StringIO(f.read())
                self._cache[name] = data
                value = data
            except IOError:
                # No way, we have to ask the server...
                self.post(Event('resource-request', name=name))
                # Set a fake value to prevent multiple requests.
                self._cache[name] = None
                value = None
        if value:
            # Broadcast the resource to all local listeners.
            self.post(Event('cache-send', name=name, string_io=value))

    def handle_resource_update(self, ev_type, name, data):
        """Someone sent a resource."""
        fname = os.path.join(YR_CACHE_DIR, name)
        data = bz2.decompress(data)
        self.post(Event('cache-send', name=name, string_io=StringIO(data)))
        # Save a copy to disk.
        with open(fname, 'w+b') as f:
            f.write(data)


class CacheMixIn(object):

    """Cache facilities.

    A child class needs also Listener class.

    """

    def __init__(self):
        # property_name_from_cache -> data
        # The data inside the cache is not loaded yet.
        self._cache = {}
        # property_name_local -> property_name_from_cache
        self._properties = {}
        # property_name_from_cache -> load_func
        self._load_funcs = {}

    def get_from_cache(self, property_name_from_cache, load_func):
        """Get a value from the cache."""
        if not callable(load_func):
            return
        if property_name_from_cache in self._cache:
            # We already have this object in the cache
            return self._cache[property_name_from_cache]
        else:
            # We must retrive the property from the cache object
            self.post(Event('cache-get', name=property_name_from_cache))
            # Set the loading function.
            self._load_funcs[property_name_from_cache] = load_func
            # Prevent further requests
            self._cache[property_name_from_cache] = None

    def set_cached_property(self, property_name_local,
                            property_name_from_cache,
                            load_func, property_default_value=None):
        """Link a local property with a value from the cache."""
        if not callable(load_func):
            return
        if property_name_from_cache in self._cache:
            # We already have this object in the cache
            value = self._cache[property_name_from_cache]
            setattr(self, property_name_local, value)
        else:
            # We must retrive the property from the cache object
            self.post(Event('cache-get', name=property_name_from_cache))
            # Set the value to default until we get the real one from the cache
            setattr(self, property_name_local, property_default_value)
            # Set the loading function.
            self._load_funcs[property_name_from_cache] = load_func
            # Prevent further requests
            self._cache[property_name_from_cache] = None
        self._properties[property_name_local] = property_name_from_cache

    def handle_cache_send(self, ev_type, name, string_io):
        """Save received cached data if a loader is registered."""
        # Look if there is a loader registered.
        if name in self._load_funcs:
            # Preveng reloading a resource.
            if name in self._cache:
                if self._cache[name] is not None:
                    return
            load_func = self._load_funcs[name]
            # Load the file object
            value = load_func(string_io)
            self._cache[name] = value
            # Update local properties if any.
            for prop_name, prop_name_cache in self._properties.items():
                if name == prop_name_cache:
                    # If ther's is a cached property with this name,
                    # set its value.
                    setattr(self, prop_name, value)
