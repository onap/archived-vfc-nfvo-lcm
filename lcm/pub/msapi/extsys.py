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
from lcm.pub.msapi.aai import call_aai
from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


def get_vims():
    ret = req_by_msb("/api/aai-esr-server/v1/vims", "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vims from extsys.")
    return json.JSONDecoder().decode(ret[1])


def get_vim_by_id(vim_id):
    ret = req_by_msb("/api/aai-esr-server/v1/vims/%s" % vim_id, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vim(%s) from extsys." % vim_id)
    return json.JSONDecoder().decode(ret[1])


def get_sdn_controller_by_id(sdn_ontroller_id):
    ret = call_aai("/external-system/esr-thirdparty-sdnc-list/esr-thirdparty-sdnc/%s" % sdn_ontroller_id, "GET")
    if ret[0] != 0:
        logger.error("Failed to query sdn ontroller(%s) from extsys. detail is %s.", sdn_ontroller_id, ret[1])
        raise NSLCMException("Failed to query sdn ontroller(%s) from extsys." % sdn_ontroller_id)
    # convert vim_info_aai to internal vim_info
    sdnc_info_aai = json.JSONDecoder().decode(ret[1])
    sdnc_info = convert_sdnc_info(sdnc_info_aai)
    return sdnc_info


def convert_sdnc_info(sdnc_info_aai):
    esr_system_info = ignore_case_get(ignore_case_get(sdnc_info_aai, "esr-system-info-list"), "esr-system-info")
    sdnc_info = {
        "sdnControllerId": sdnc_info_aai["thirdparty-sdnc-id"],
        "name": sdnc_info_aai["thirdparty-sdnc-id"],
        "url": ignore_case_get(esr_system_info[0], "service-url"),
        "userName": ignore_case_get(esr_system_info[0], "user-name"),
        "password": ignore_case_get(esr_system_info[0], "password"),
        "vendor": ignore_case_get(esr_system_info[0], "vendor"),
        "version": ignore_case_get(esr_system_info[0], "version"),
        "description": "",
        "protocol": ignore_case_get(esr_system_info[0], "protocal"),
        "productName": ignore_case_get(sdnc_info_aai, "product-name"),
        "type": ignore_case_get(esr_system_info[0], "type"),
        "createTime": "2016-07-18 12:22:53"
    }
    return sdnc_info


def get_vnfm_by_id(vnfm_inst_id):
    uri = '/api/aai-esr-server/v1/vnfms/%s' % vnfm_inst_id
    ret = req_by_msb(uri, "GET")
    if ret[0] > 0:
        logger.error('Send get VNFM information request to extsys failed.')
        raise NSLCMException('Send get VNFM information request to extsys failed.')
    return json.JSONDecoder().decode(ret[1])


def convert_vnfm_info(vnfm_info_aai):
    esr_system_info = ignore_case_get(ignore_case_get(vnfm_info_aai, "esr-system-info-list"), "esr-system-info")
    vnfm_info = {
        "vnfmId": vnfm_info_aai["vnfm-id"],
        "name": vnfm_info_aai["vnfm-id"],
        "type": ignore_case_get(esr_system_info[0], "type"),
        "vimId": vnfm_info_aai["vim-id"],
        "vendor": ignore_case_get(esr_system_info[0], "vendor"),
        "version": ignore_case_get(esr_system_info[0], "version"),
        "description": "vnfm",
        "certificateUrl": vnfm_info_aai["certificate-url"],
        "url": ignore_case_get(esr_system_info[0], "service-url"),
        "userName": ignore_case_get(esr_system_info[0], "user-name"),
        "password": ignore_case_get(esr_system_info[0], "password"),
        "createTime": "2016-07-06 15:33:18"
    }
    return vnfm_info


def select_vnfm(vnfm_type, vim_id):
    uri = '/external-system/esr-vnfm-list'
    ret = call_aai(uri, "GET")
    if ret[0] > 0:
        logger.error("Failed to call %s: %s", uri, ret[1])
        raise NSLCMException('Failed to get vnfms from extsys.')
    vnfms = json.JSONDecoder().decode(ret[1])
    vnfms = ignore_case_get(vnfms, "esr-vnfm")
    for vnfm in vnfms:
        esr_system_info = ignore_case_get(vnfm, "esr-system-info")
        type = ignore_case_get(esr_system_info, "type")
        vimId = vnfm["vnfm-id"]
        if type == vnfm_type and vimId == vim_id:
            # convert vnfm_info_aai to internal vnfm_info
            vnfm = convert_vnfm_info(vnfm)
            return vnfm
    raise NSLCMException('No vnfm found with %s in vim(%s)' % (vnfm_type, vim_id))
