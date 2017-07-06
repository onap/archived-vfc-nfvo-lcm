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

import json
import logging

from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.restcall import req_by_msb

logger = logging.getLogger(__name__)


def delete_port_chain(req_param):
    url = "/openoapi/sdncdriver/v1/delchain"
    str = "delete port chain"
    delete_func(req_param, url, str)


def delete_flow_classifier(req_param):
    url = "/openoapi/sdncdriver/v1/delclassifier"
    str = "delete flow classifier"
    delete_func(req_param, url, str)


def delete_port_pair_group(req_param):
    url = "/openoapi/sdncdriver/v1/delportpairgroup"
    str = "delete port pair"
    delete_func(req_param, url, str)


def delete_port_pair(req_param):
    url = "/openoapi/sdncdriver/v1/delportpair"
    str = "delete port pair"
    delete_func(req_param, url, str)


def delete_func(req_param, url, str):
    ret = req_by_msb(url, "DELETE", json.JSONEncoder().encode(req_param))
    if ret[0] != 0:
        logger.error("Failed to %s to sdncdriver. detail is %s.", str, ret[1])
        raise NSLCMException('Failed to %s to sdncdriver.' % str)


def create_flow_classfier(data):
    url = "/openoapi/ztesdncdriver/v1/createflowclassfier"
    str = "create flow classfier"
    return create(data, url, str)


def create_port_pair(data):
    url = "/openoapi/ztesdncdriver/v1/createportpair"
    str = "create port pair"
    return create(data, url, str)


def create_port_pair_group(data):
    url = "/openoapi/ztesdncdriver/v1/createportpairgroup"
    str = "create port pair group"
    return create(data, url, str)


def create_port_chain(data):
    url = "/openoapi/ztesdncdriver/v1/createportchain"
    str = "create port chain"
    return create(data, url, str)


def create(req_param, url, str):
    ret = req_by_msb(url, "POST", json.dumps(req_param))
    if ret[0] != 0:
        logger.error("Failed to %s to sdncdriver. detail is %s.", str, ret[1])
        raise NSLCMException('Failed to %s to sdncdriver.' % str)
    resp_body = json.loads(ret[1])
    return resp_body["id"]
