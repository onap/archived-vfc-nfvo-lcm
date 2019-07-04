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

import logging

logger = logging.getLogger(__name__)


def ignore_case_get(args, key, def_val=""):
    if not key:
        return def_val
    if key in args:
        return args[key]
    for old_key in args:
        if old_key.upper() == key.upper():
            return args[old_key]
    return def_val


def remove_none_key(data, none_list=None):
    none_list = none_list if none_list else [None, '', 'NULL', 'None', 'null', {}, '{}']
    if isinstance(data, dict):
        data = dict([(k, remove_none_key(v)) for k, v in list(data.items()) if v not in none_list])
    if isinstance(data, list):
        data = [remove_none_key(s) for s in data if s not in none_list]
    return data


def update_value(origin_data, new_data):
    logger.debug(origin_data)
    if not isinstance(origin_data, dict):
        str_data = origin_data.encode('utf-8')
        logger.debug(str_data)
        origin_data = eval(str_data)
    logger.debug(isinstance(origin_data, dict))
    logger.debug(new_data)
    for k, v in list(new_data.items()):
        if k not in origin_data:
            origin_data[k] = v
        else:
            if isinstance(origin_data[k], list):
                origin_data[k] = origin_data[k].extend(v)
            else:
                origin_data[k] = v
    return origin_data
