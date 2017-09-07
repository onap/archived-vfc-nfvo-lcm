# Copyright 2017 ZTE Corporation.
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
import uuid

from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils import restcall
from lcm.pub.config.config import AAI_BASE_URL, AAI_USER, AAI_PASSWD
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


def call_aai(resource, method, content=''):
    additional_headers = {
        'X-FromAppId': 'VFC-NFVO-LCM',
        'X-TransactionId': str(uuid.uuid1())
    }
    return restcall.call_req(base_url=AAI_BASE_URL,
        user=AAI_USER, 
        passwd=AAI_PASSWD, 
        auth_type=restcall.rest_no_auth, 
        resource=resource, 
        method=method, 
        content=content,
        additional_headers=additional_headers)

def create_ns_aai(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ns instance creation exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_ns_aai(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ns instance delete exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def query_ns_aai(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "GET", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Ns instance query exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def create_vnf_aai(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vnf instance creation exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_vnf_aai(vnf_id, data=''):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    ret = call_aai(resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vnf instance delete exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def query_vnf_aai(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s" % vnf_id
    ret = call_aai(resource, "GET", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vnf instance query exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def create_vserver_aai(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vserver creation exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def delete_vserver_aai(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "DELETE", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vserver delete exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def query_vserver_aai(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "GET", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Vserver query exception in AAI")
    return json.JSONDecoder().decode(ret[1])

def put_vserver_relationship(cloud_owner, cloud_region_id, tenant_id, vserver_id, data):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s/relationship-list/relationship" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Put or update vserver relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def delete_vserver_relationship(cloud_owner, cloud_region_id, tenant_id, vserver_id):
    resource = "/cloud-infrastructure/cloud-regions/cloud-region/%s/" \
               "%s/tenants/tenant/%s/vservers/vserver/%s/relationship-list/relationship" % \
               (cloud_owner, cloud_region_id, tenant_id, vserver_id)
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Delete vserver relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def put_vnf_relationship(vnf_id, data):
    resource = "/network/generic-vnfs/generic-vnf/%s/relationship-list/relationship" % vnf_id
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Put or update vnf instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def delete_vnf_relationship(vnf_id):
    resource = "/network/generic-vnfs/generic-vnf/%s/relationship-list/relationship" % vnf_id
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Delete vnf instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def put_ns_relationship(global_customer_id, service_type, service_instance_id, data):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s/relationship-list/relationship" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "PUT", data)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Put or update ns instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def delete_ns_relationship(global_customer_id, service_type, service_instance_id):
    resource = "/business/customers/customer/%s/service-subscriptions/service-subscription/" \
               "%s/service-instances/service-instance/%s/relationship-list/relationship" % \
               (global_customer_id, service_type, service_instance_id)
    ret = call_aai(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Delete ns instance relationship exception in AAI")
    return json.JSONDecoder().decode(ret[1])


def get_vnfm_by_id(vnfm_inst_id):
    uri = '/external-system/esr-vnfm-list/esr-vnfm/%s' % vnfm_inst_id
    ret = call_aai(uri, "GET")
    if ret[0] > 0:
        logger.error('Send get VNFM information request to extsys failed.')
        raise NSLCMException('Send get VNFM information request to extsys failed.')

    # convert vnfm_info_aai to internal vnfm_info
    vnfm_info_aai = json.JSONDecoder().decode(ret[1])
    vnfm_info = convert_vnfm_info(vnfm_info_aai)
    return vnfm_info

def convert_vnfm_info(vnfm_info_aai):
    esr_system_info = ignore_case_get(vnfm_info_aai, "esr-system-info")
    vnfm_info = {
        "vnfmId": vnfm_info_aai["vnfm-id"],
        "name": vnfm_info_aai["vnfm-id"],
        "type": ignore_case_get(esr_system_info, "type"),
        "vimId": vnfm_info_aai["vim-id"],
        "vendor": ignore_case_get(esr_system_info, "vendor"),
        "version": ignore_case_get(esr_system_info, "version"),
        "description": "vnfm",
        "certificateUrl": vnfm_info_aai["certificate-url"],
        "url": ignore_case_get(esr_system_info, "service-url"),
        "userName": ignore_case_get(esr_system_info, "service-url"),
        "password": ignore_case_get(esr_system_info, "service-url"),
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
    for vnfm in vnfms:
        esr_system_info = ignore_case_get(vnfm, "esr-system-info")
        type = ignore_case_get(esr_system_info, "type")
        vimId = vnfm["vnfm-id"]
        if type == vnfm_type and vimId == vim_id:
            # convert vnfm_info_aai to internal vnfm_info
            vnfm = convert_vnfm_info(vnfm)
            return vnfm
    raise NSLCMException('No vnfm found with %s in vim(%s)' % (vnfm_type, vim_id))


def get_vim_by_id(vim_id):
    cloud_owner, cloud_region = split_vim_to_owner_region(vim_id)
    ret = call_aai("/cloud-infrastructure/cloud-regions/cloud-region/%s/%s" % (cloud_owner, cloud_region), "GET")
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
    vim_id = vim_info_aai["cloud-owner"] + '_' + vim_info_aai["cloud-region-id"]
    esr_system_info = ignore_case_get(vim_info_aai, "esr-system-info")
    tenants = ignore_case_get(vim_info_aai, "tenants")
    vim_info = {
        "vimId": vim_id,
        "name": vim_id,
        "url": ignore_case_get(esr_system_info, "service-url"),
        "userName": ignore_case_get(esr_system_info, "service-url"),
        "password": ignore_case_get(esr_system_info, "service-url"),
        "tenant": ignore_case_get(tenants[0], "tenant-id"),
        "vendor": ignore_case_get(esr_system_info, "vendor"),
        "version": ignore_case_get(esr_system_info, "version"),
        "description": "vim",
        "domain": "",
        "type": "openstack",
        "createTime": "2016-07-18 12:22:53"
    }
    return vim_info


def get_vims():
    ret = call_aai("/cloud-infrastructure/cloud-regions", "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query vims from extsys.")

    # convert vim_info_aai to internal vim_info
    vims_aai = json.JSONDecoder().decode(ret[1])
    vims_info = []
    for vim in vims_aai:
        vim = convert_vim_info(vim)
        vims_info.append(vim)

    return vims_info
