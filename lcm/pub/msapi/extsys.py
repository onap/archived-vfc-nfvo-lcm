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
    logger.debug("vims_info=%s", vims_info)
    return vims_info


def get_vim_by_id_vim_info(cloudowner, cloudregionid):
    cloud_owner = cloudowner
    cloud_regionid = cloudregionid
    ret = call_aai("/cloud-infrastructure/cloud-regions/cloud-region/%s/%s?depth=all"
                   % (cloud_owner, cloud_regionid), "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vim(%s__%s) from extsys." % (cloudowner, cloudregionid))
    # convert vim_info_aai to internal vim_info
    vim_info_aai = json.JSONDecoder().decode(ret[1])
    vim_info = convert_vim_info(vim_info_aai)
    logger.debug("cloud_owner=%s, cloud_regionid=%s, vim_info=%s", cloudowner, cloudregionid, vim_info)
    return vim_info


def get_vim_by_id(vim_id):
    # cloud_owner, cloud_region = split_vim_to_owner_region(vim_id)
    vim_id = json.JSONDecoder().decode(vim_id) if isinstance(vim_id, str) else vim_id
    cloud_owner = vim_id['cloud_owner']
    cloud_regionid = vim_id['cloud_regionid']
    ret = call_aai("/cloud-infrastructure/cloud-regions/cloud-region/%s/%s?depth=all"
                   % (cloud_owner, cloud_regionid), "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vim(%s) from extsys." % vim_id)
    # convert vim_info_aai to internal vim_info
    vim_info_aai = json.JSONDecoder().decode(ret[1])
    vim_info = convert_vim_info(vim_info_aai)
    logger.debug("vim_id=%s, vim_info=%s", vim_id, vim_info)
    return vim_info


def split_vim_to_owner_region(vim_id):
    split_vim = vim_id.split('_')
    cloud_owner = split_vim[0]
    cloud_region = "".join(split_vim[1:])
    return cloud_owner, cloud_region


def convert_vim_info(vim_info_aai):
    vim_id = vim_info_aai["cloud-owner"] + "_" + vim_info_aai["cloud-region-id"]
    vim_type_aai = vim_info_aai["cloud-type"]
    vim_type = vim_type_aai if vim_type_aai else "openstack"
    esr_system_info = ignore_case_get(ignore_case_get(vim_info_aai, "esr-system-info-list"), "esr-system-info")
    # tenants = ignore_case_get(vim_info_aai, "tenants")
    default_tenant = ignore_case_get(esr_system_info[0], "default-tenant")
    tenants = ignore_case_get(ignore_case_get(vim_info_aai, "tenants"), "tenant")
    tenant_id = ""
    for tenant_info in tenants:
        if tenant_info["tenant-name"] == default_tenant:
            tenant_id = tenant_info["tenant-id"]
            break
    vim_info = {
        "vimId": vim_id,
        "name": vim_id,
        "url": ignore_case_get(esr_system_info[0], "service-url"),
        "userName": ignore_case_get(esr_system_info[0], "user-name"),
        "password": ignore_case_get(esr_system_info[0], "password"),
        # "tenant": ignore_case_get(tenants[0], "tenant-id"),
        "tenantId": tenant_id,
        "tenant": default_tenant,
        "vendor": ignore_case_get(esr_system_info[0], "vendor"),
        "version": ignore_case_get(esr_system_info[0], "version"),
        "description": "vim",
        "domain": ignore_case_get(esr_system_info[0], "cloud-domain"),
        "type": vim_type,
        "createTime": "",
        "sslCacert": ignore_case_get(esr_system_info[0], "ssl-cacert"),
        "sslInsecure": str(ignore_case_get(esr_system_info[0], "ssl-insecure")),
        "status": ignore_case_get(esr_system_info[0], "system-status")
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
    logger.debug("sdn_ontroller_id=%s, sdnc_info=%s", sdn_ontroller_id, sdnc_info)
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
        "createTime": ""
    }
    return sdnc_info


def get_vnfm_by_id(vnfm_inst_id):
    uri = "/external-system/esr-vnfm-list/esr-vnfm/%s?depth=all" % vnfm_inst_id
    ret = call_aai(uri, "GET")
    if ret[0] > 0:
        logger.error('Send get VNFM information request to extsys failed.')
        raise NSLCMException('Send get VNFM information request to extsys failed.')
    # convert vnfm_info_aai to internal vnfm_info
    vnfm_info_aai = json.JSONDecoder().decode(ret[1])
    vnfm_info = convert_vnfm_info(vnfm_info_aai)
    logger.debug("vnfm_inst_id=%s, vnfm_info=%s", vnfm_inst_id, vnfm_info)
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
        "createTime": ""
    }
    return vnfm_info


def select_vnfm(vnfm_type, vim_id):
    uri = "/external-system/esr-vnfm-list"
    ret = call_aai(uri, "GET")
    if ret[0] > 0:
        logger.error("Failed to call %s: %s", uri, ret[1])
        raise NSLCMException('Failed to get vnfms from extsys.')
    vnfms = json.JSONDecoder().decode(ret[1])
    vnfms = ignore_case_get(vnfms, "esr-vnfm")
    for vnfm in vnfms:
        vnfm_info = get_vnfm_by_id(vnfm.get("vnfm-id"))
        logger.debug('LTX----------------------vnfm_info: %s', vnfm_info)
        vnfmtype = ignore_case_get(vnfm_info, "type")
        vimid = ignore_case_get(vnfm_info, "vimId")
        if vnfmtype == vnfm_type and vimid == vim_id:
            return vnfm_info
    raise NSLCMException('No vnfm found with %s in vim(%s)' % (vnfm_type, vim_id))


def get_ems_by_id(ems_inst_id):
    uri = "/external-system/esr-ems-list/esr-ems/%s?depth=all" % ems_inst_id
    ret = call_aai(uri, "GET")
    if ret[0] > 0:
        logger.error('Send get EMS information request to extsys failed.')
        raise NSLCMException('Send get EMS information request to extsys failed.')
    # convert vnfm_info_aai to internal vnfm_info
    ems_info_aai = json.JSONDecoder().decode(ret[1])
    ems_info = convert_ems_info(ems_info_aai)
    logger.debug("ems_inst_id=%s, ems_info=%s", ems_inst_id, ems_info)
    return ems_info


def convert_ems_info(ems_info_aai):
    esr_system_info = ignore_case_get(ignore_case_get(ems_info_aai, "esr-system-info-list"), "esr-system-info")
    ems_info_aai = {
        "emsId": ems_info_aai["ems-id"],
        "type": ignore_case_get(esr_system_info[0], "type"),
        "vendor": ignore_case_get(esr_system_info[0], "vendor"),
        "version": ignore_case_get(esr_system_info[0], "version"),
        "url": ignore_case_get(esr_system_info[0], "service-url"),
        "userName": ignore_case_get(esr_system_info[0], "user-name"),
        "password": ignore_case_get(esr_system_info[0], "password"),
        "createTime": ""
    }
    return ems_info_aai
