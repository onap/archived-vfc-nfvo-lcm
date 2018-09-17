# Copyright 2018 ZTE Corporation.
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
from lcm.pub.msapi.extsys import get_ems_by_id
from lcm.pub.utils.restcall import req_by_msb

logger = logging.getLogger(__name__)


def send_active_pnf_request(ems_inst_id, pnf_id, req_param):
    ems = get_ems_by_id(ems_inst_id)
    uri = '/api/%s/v1/%s/pnfs/%s/active' % (ems["type"], ems_inst_id, pnf_id)
    ret = req_by_msb(uri, "POST", req_param)
    if ret[0] != 0:
        logger.error("Failed to send nf init req:%s,%s", ret[2], ret[1])
        raise NSLCMException('Failed to send nf init request to VNFM(%s)' % ems_inst_id)
    return json.JSONDecoder().decode(ret[1])
