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


def get_vims():
    ret = req_by_msb("/openoapi/extsys/v1/vims", "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vims from extsys.")
    return json.JSONDecoder().decode(ret[1])


def get_vim_by_id(vim_id):
    ret = req_by_msb("/openoapi/extsys/v1/vims/%s" % vim_id, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vim(%s) from extsys." % vim_id)
    return json.JSONDecoder().decode(ret[1])


def get_sdn_controller_by_id(sdn_ontroller_id):
    ret = req_by_msb("/openoapi/extsys/v1/sdncontrollers/%s" % sdn_ontroller_id, "GET")
    if ret[0] != 0:
        logger.error("Failed to query sdn ontroller(%s) from extsys. detail is %s.", sdn_ontroller_id, ret[1])
        raise NSLCMException("Failed to query sdn ontroller(%s) from extsys." % sdn_ontroller_id)
    return json.JSONDecoder().decode(ret[1])


def get_vnfm_by_id(vnfm_inst_id):
    uri = '/openoapi/extsys/v1/vnfms/%s' % vnfm_inst_id
    ret = req_by_msb(uri, "GET")
    if ret[0] > 0:
        logger.error('Send get VNFM information request to extsys failed.')
        raise NSLCMException('Send get VNFM information request to extsys failed.')
    return json.JSONDecoder().decode(ret[1])

def select_vnfm(vnfm_type, vim_id):
    uri = '/openoapi/extsys/v1/vnfms'
    ret = req_by_msb(uri, "GET")
    if ret[0] > 0:
        logger.error("Failed to call %s: %s", uri, ret[1])
        raise NSLCMException('Failed to get vnfms from extsys.')
    vnfms = json.JSONDecoder().decode(ret[1])
    for vnfm in vnfms:
        if vnfm["type"] == vnfm_type and vnfm["vimId"] == vim_id:
            return vnfm
    raise NSLCMException('No vnfm found with %s in vim(%s)' % (vnfm_type, vim_id))

