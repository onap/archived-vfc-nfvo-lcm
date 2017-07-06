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

from lcm.pub.utils.restcall import req_by_msb

logger = logging.getLogger(__name__)

def call_from_ns_cancel_resource(res_type, instid):
    method = "DELETE"
    if res_type == 'vl':
        uri = '/openoapi/nslcm/v1/ns/vls/%s' % instid

    elif res_type == 'sfc':
        uri = '/openoapi/nslcm/v1/ns/sfcs/%s' % instid
    else:
        # vnf
        method = "POST"
        uri = '/openoapi/nslcm/v1/ns/vnfs/%s' % instid
    req_param = {}
    ret = req_by_msb(uri, method, json.dumps(req_param))
    logger.info("[NS terminate] call vnfm [%s] result:%s" % (res_type, ret))
    return ret