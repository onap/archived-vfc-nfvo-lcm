#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

import redis

from lcm.pub.config.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWD


class SharedLock:
    def __init__(self, lock_key, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWD, db=9, lock_timeout=5 * 60):
        self.lock_key = lock_key
        self.lock_timeout = lock_timeout
        self.redis = redis.Redis(host=host, port=port, db=db, password=password)
        self.acquire_time = -1

    def acquire(self):
        begin = now = int(time.time())
        while (now - begin) < self.lock_timeout:

            result = self.redis.setnx(self.lock_key, now + self.lock_timeout + 1)
            if result == 1 or result is True:
                self.acquire_time = now
                return True

            current_lock_timestamp = self.redis.get(self.lock_key)
            if not current_lock_timestamp:
                time.sleep(1)
                continue

            current_lock_timestamp = int(current_lock_timestamp)

            if now > current_lock_timestamp:
                next_lock_timestamp = self.redis.getset(self.lock_key, now + self.lock_timeout + 1)
                if not next_lock_timestamp:
                    time.sleep(1)
                    continue
                next_lock_timestamp = int(next_lock_timestamp)

                if next_lock_timestamp == current_lock_timestamp:
                    self.acquire_time = now
                    return True
            else:
                time.sleep(1)
                continue
        return False

    def release(self):
        now = int(time.time())
        if now > self.acquire_time + self.lock_timeout:
            # key expired, do nothing and let other clients handle it
            return
        self.acquire_time = None
        self.redis.delete(self.lock_key)


def do_biz_with_share_lock(lock_name, callback):
    lock = SharedLock(lock_name)
    try:
        if not lock.acquire():
            raise Exception(lock_name + " timeout")
        callback()
    except Exception as e:
        raise e
    finally:
        lock.release()
