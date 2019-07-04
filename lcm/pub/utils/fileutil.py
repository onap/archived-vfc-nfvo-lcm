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
import os
import shutil
import logging
import traceback
from urllib.request import Request, urlopen
import json

logger = logging.getLogger(__name__)


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path, 0o777)


def delete_dirs(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("Failed to delete %s:%s", path, e.args[0])


def download_file_from_http(url, local_dir, file_name):
    local_file_name = os.path.join(local_dir, file_name)
    is_download_ok = False
    try:
        make_dirs(local_dir)
        r = Request(url)
        req = urlopen(r)
        save_file = open(local_file_name, 'wb')
        save_file.write(req.read())
        save_file.close()
        req.close()
        is_download_ok = True
    except:
        logger.error(traceback.format_exc())
        logger.error("Failed to download %s to %s.", url, local_file_name)
    return is_download_ok, local_file_name


def read_json_file(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as json_file:
                data = json_file.read()
            return json.loads(data)
        except:
            logger.error(traceback.format_exc())
            logger.error("Failed to parse json file %s." % file_path)
    return None
