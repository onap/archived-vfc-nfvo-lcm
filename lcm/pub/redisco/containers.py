#  Copyright (c) 2010 Tim Medina
#
#  Permission is hereby granted, free of charge, to any person
#  obtaining a copy of this software and associated documentation
#  files (the "Software"), to deal in the Software without
#  restriction, including without limitation the rights to use,
#  copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following
#  conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#
#  The original code link is https://github.com/iamteem/redisco/tree/master/redisco/containers.py

"""
This module contains the container classes to create objects
that persist directly in a Redis server.
"""

import collections
from functools import partial


class Container(object):
    """Create a container object saved in Redis.

    Arguments:
        key -- the Redis key this container is stored at
        db  -- the Redis client object. Default: None

    When ``db`` is not set, the gets the default connection from
    ``redisco.connection`` module.
    """

    def __init__(self, key, db=None, pipeline=None):
        self._db = db
        self.key = key
        self.pipeline = pipeline

    def clear(self):
        """Remove container from Redis database."""
        del self.db[self.key]

    def __getattribute__(self, att):
        if att in object.__getattribute__(self, 'DELEGATEABLE_METHODS'):
            return partial(getattr(object.__getattribute__(self, 'db'), att), self.key)
        else:
            return object.__getattribute__(self, att)

    @property
    def db(self):
        if self.pipeline:
            return self.pipeline
        if self._db:
            return self._db
        if hasattr(self, 'db_cache') and self.db_cache:
            return self.db_cache
        else:
            from redisco import connection
            self.db_cache = connection
            return self.db_cache

    DELEGATEABLE_METHODS = ()


class Hash(Container, collections.MutableMapping):

    def __getitem__(self, att):
        return self.hget(att)

    def __setitem__(self, att, val):
        self.hset(att, val)

    def __delitem__(self, att):
        self.hdel(att)

    def __len__(self):
        return self.hlen()

    def __iter__(self):
        return self.hgetall().__iter__()

    def __contains__(self, att):
        return self.hexists(att)

    def __repr__(self):
        return "<%s '%s' %s>" % (self.__class__.__name__, self.key, self.hgetall())

    def keys(self):
        return self.hkeys()

    def values(self):
        return self.hvals()

    def _get_dict(self):
        return self.hgetall()

    def _set_dict(self, new_dict):
        self.clear()
        self.update(new_dict)

    dict = property(_get_dict, _set_dict)

    DELEGATEABLE_METHODS = ('hlen', 'hset', 'hdel', 'hkeys', 'hgetall', 'hvals',
                            'hget', 'hexists', 'hincrby', 'hmget', 'hmset')
