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
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


def get_vims():
    ret = call_aai("/cloud-infrastructure/cloud-regions?depth=all", "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vims from extsys.")
    # convert vim_info_aai to internal vim_info
    vims_aai = json.JSONDecoder().decode(ret[1])
    vims_aai = ignore_case_get(vims_aai, "cloud-region")
    vims_info = []
    for vim in vims_aai:
        vim = convert_vim_info(vim)
        vims_info.append(vim)
    return vims_info


def get_vim_by_id(vim_id):
    cloud_owner, cloud_region = split_vim_to_owner_region(vim_id)
    ret = call_aai("/cloud-infrastructure/cloud-regions/cloud-region/%s/%s?depth=all"
                   % (cloud_owner, cloud_region), "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vim(%s) from extsys." % vim_id)
    # convert vim_info_aai to internal vim_info
    vim_info_aai = json.JSONDecoder().decode(ret[1])
    vim_info = convert_vim_info(vim_info_aai)
    return vim_info

def split_vim_to_owner_region(vim_id):
    split_vim = vim_id.split('_')
    cloud_owner = split_vim[0]
    cloud_region = "".join(split_vim[1:])
    return cloud_owner, cloud_region

def convert_vim_info(vim_info_aai):
    vim_id = vim_info_aai["cloud-owner"] + "_" + vim_info_aai["cloud-region-id"]
    esr_system_info = ignore_case_get(ignore_case_get(vim_info_aai, "esr-system-info-list"), "esr-system-info")
    # tenants = ignore_case_get(vim_info_aai, "tenants")
    vim_info = {
        "vimId": vim_id,
        "name": vim_id,
        "url": ignore_case_get(esr_system_info[0], "service-url"),
        "userName": ignore_case_get(esr_system_info[0], "user-name"),
        "password": ignore_case_get(esr_system_info[0], "password"),
        # "tenant": ignore_case_get(tenants[0], "tenant-id"),
        "tenant": ignore_case_get(esr_system_info[0], "default-tenant"),
        "vendor": ignore_case_get(esr_system_info[0], "vendor"),
        "version": ignore_case_get(esr_system_info[0], "version"),
        "description": "vim",
        "domain": "",
        "type": ignore_case_get(esr_system_info[0], "type"),
        "createTime": "2016-07-18 12:22:53"
    }
    return vim_info


def get_sdn_controller_by_id(sdn_ontroller_id):
    ret = call_aai("/external-system/esr-thirdparty-sdnc-list/esr-thirdparty-sdnc/%s?depth=all"
                   % sdn_ontroller_id, "GET")
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
    uri = '/external-system/esr-vnfm-list/esr-vnfm/%s?depth=all' % vnfm_inst_id
    ret = call_aai(uri, "GET")
    if ret[0] > 0:
        logger.error('Send get VNFM information request to extsys failed.')
        raise NSLCMException('Send get VNFM information request to extsys failed.')
    # convert vnfm_info_aai to internal vnfm_info
    vnfm_info_aai = json.JSONDecoder().decode(ret[1])
    vnfm_info = convert_vnfm_info(vnfm_info_aai)
    return vnfm_info


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
    uri = '/external-system/esr-vnfm-list?depth=all'
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
