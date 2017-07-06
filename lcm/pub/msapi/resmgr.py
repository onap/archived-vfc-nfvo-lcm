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


def create_vl(req_param):
    ret = req_by_msb("/openoapi/resmgr/v1/vl", "POST", json.JSONEncoder().encode(req_param))
    if ret[0] != 0:
        logger.error("Failed to create vl to resmgr. detail is %s.", ret[1])
        #raise NSLCMException('Failed to create vl to resmgr.')
    #return json.JSONDecoder().decode(ret[1])


def delete_vl(vl_inst_id):
    ret = req_by_msb("/openoapi/resmgr/v1/vl/%s" % vl_inst_id, "DELETE")
    if ret[0] != 0:
        logger.error("Failed to delete vl(%s) to resmgr. detail is %s.", vl_inst_id, ret[1])
        #raise NSLCMException("Failed to delete vl(%s) to resmgr." % vl_inst_id)


def delete_sfc(sfc_inst_id):
    ret = req_by_msb("/openoapi/resmgr/v1/sfc/%s" % sfc_inst_id, "DELETE")
    if ret[0] != 0:
        logger.error("Failed to delete sfc(%s) to resmgr. detail is %s.", sfc_inst_id, ret[1])
        #raise NSLCMException("Failed to delete sfc(%s) to resmgr." % sfc_inst_id)


def grant_vnf(req_param):
    grant_data = json.JSONEncoder().encode(req_param)
    ret = req_by_msb("/openoapi/resmgr/v1/resource/grant", "PUT", grant_data)
    if ret[0] != 0:
        logger.error("Failed to grant vnf to resmgr. detail is %s.", ret[1])
        #raise NSLCMException('Failed to grant vnf to resmgr.')
        vim_id = ""
        if "vimId" in req_param:
            vim_id = req_param["vimId"]
        elif "additionalparam" in req_param and "vimid" in req_param["additionalparam"]:
            vim_id = req_param["additionalparam"]["vimid"]
        try:
            from lcm.pub.msapi import extsys
            vim = extsys.get_vim_by_id(vim_id)
            if isinstance(vim, list):
                vim = vim[0]
                vim_id = vim["vimId"]
            grant_rsp = {
                "vim": {
                    "vimid": vim_id,
                    "accessinfo": {
                        "tenant": vim["tenant"]
                    }
                }
            }
            logger.debug("grant_rsp=%s" % grant_rsp)
            return grant_rsp
        except:
            raise NSLCMException('Failed to grant vnf to resmgr.')
    return json.JSONDecoder().decode(ret[1])


def create_vnf(data):
    uri = '/openoapi/resmgr/v1/vnf'
    req_param = json.JSONEncoder().encode({
        'orchVnfInstanceId': data['nf_inst_id'],
        'vnfInstanceId': data['vnfm_nf_inst_id'],
        'vnfInstanceName': data['vnf_inst_name'],
        'nsId': data['ns_inst_id'],
        'nsName': data['ns_inst_name'],
        'vnfmId': data['vnfm_inst_id'],
        'vnfmName': data['vnfm_inst_name'],
        'vnfPackageName': data['vnfd_name'],
        'vnfDescriptorName': data['vnfd_id'],
        'jobId': data['job_id'],
        'vnfStatus': data['nf_inst_status'],
        'vnfType': data['vnf_type'],
        'onboardingId': data['nf_package_id'],
        'onboardingName': data['vnfd_name']})

    ret = req_by_msb(uri, "POST", req_param)
    if ret[0] != 0:
        logger.error('Send create VNF request to resmgr failed.')
        #raise NSLCMException('Send create VNF request to resmgr failed.')


def create_vnf_creation_info(data):
    uri = '/openoapi/resmgr/v1/vnfinfo'
    req_param = json.JSONEncoder().encode({
        'vnfInstanceId': data['nf_inst_id'],
        'nsId': data['ns_inst_id'],
        'vnfmId': data['vnfm_inst_id'],
        'vms': data['vms']})

    ret = req_by_msb(uri, "POST", req_param)
    if ret[0] > 0:
        logger.error('Send write vnf creation information to resmgr failed.')
        #raise NSLCMException('Send write vnf creation information to resmgr failed.')


def terminate_vnf(vnf_inst_id):
    uri = '/openoapi/resmgr/v1/vnf/%s' % vnf_inst_id
    req_param = {}
    ret = req_by_msb(uri, "DELETE", json.dumps(req_param))
    if ret[0] > 0:
        logger.error('Send terminate VNF request to resmgr failed.')
        #raise NSLCMException('Send terminate VNF request to resmgr failed.')