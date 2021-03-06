# Ductus
# Copyright (C) 2008  Jim Garrison <jim@garrison.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging

from ductus.utils import iterate_file_then_delete, iterator_to_tempfile

logger = logging.getLogger(__name__)

class CacheStorageBackend(object):
    """
    Caches a backend using another one as cache.

    Currently there is no limit to the cache size and nothing will be
    deleted from it automatically.
    """

    def __init__(self, backing_store, cache):
        self.__backing_store = backing_store
        self.__cache = cache

    def __attempt_cache_save(self, key, filename):
        try:
            self.__cache.put_file(key, filename)
            return True
        except Exception:
            return False

    def __contains__(self, key):
        return key in self.__cache or key in self.__backing_store

    def put_file(self, key, filename):
        self.__backing_store.put_file(key, filename)
        self.__attempt_cache_save(key, filename)

    def __getitem__(self, key):
        try:
            return self.__cache[key]
        except Exception:
            data_iterator = self.__backing_store[key]
            # Cache it
            tmpfile = iterator_to_tempfile(data_iterator)
            self.__attempt_cache_save(key, tmpfile)
            return iterate_file_then_delete(tmpfile)

    def __delitem__(self, key):
        del self.__backing_store[key]
        try:
            del self.__cache[key]
        except KeyError:
            logger.warning("Error while removing %s from cache." % key)

    def keys(self):
        # Assume all items in cache are in backing_store
        return self.__backing_store.keys()

    def iterkeys(self):
        # Assume all items in cache are in backing_store
        return iter(self.__backing_store)

    __iter__ = iterkeys

    def __len__(self):
        # Assume all items in cache are in backing_store
        return len(self.__backing_store)
