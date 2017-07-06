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
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.msapi.extsys import get_vnfm_by_id

logger = logging.getLogger(__name__)


def send_nf_init_request(vnfm_inst_id, req_param):
    vnfm = get_vnfm_by_id(vnfm_inst_id)
    uri = '/openoapi/%s/v1/%s/vnfs' % (vnfm["type"], vnfm_inst_id)
    ret = req_by_msb(uri, "POST", req_param)
    if ret[0] != 0:
        logger.error("Failed to send nf init req:%s,%s", ret[2], ret[1])
        raise NSLCMException('Failed to send nf init request to VNFM(%s)' % vnfm_inst_id)
    return json.JSONDecoder().decode(ret[1])

def send_nf_terminate_request(vnfm_inst_id, vnf_inst_id, req_param):
    vnfm = get_vnfm_by_id(vnfm_inst_id)
    uri = '/openoapi/%s/v1/%s/vnfs/%s/terminate' % (vnfm["type"], vnfm_inst_id, vnf_inst_id)
    ret = req_by_msb(uri, "POST", req_param)
    if ret[0] > 0:
        logger.error("Failed to send nf terminate req:%s,%s", ret[2], ret[1])
        raise NSLCMException('Failed to send nf terminate request to VNFM(%s)' % vnfm_inst_id)
    return json.JSONDecoder().decode(ret[1]) if ret[1] else {}

def query_vnfm_job(vnfm_inst_id, job_id, response_id=0):
    vnfm = get_vnfm_by_id(vnfm_inst_id)
    retry_time = 3
    uri = '/openoapi/%s/v1/%s/jobs/%s?responseId=%s' % (vnfm["type"], 
        vnfm_inst_id, job_id, response_id)
    while retry_time > 0:
        rsp = req_by_msb(uri, "GET")
        if str(rsp[2]) == '404':
            return False, ''
        if rsp[0] != 0:
            logger.warning('retry_time=%s, detail message:%s' % (retry_time, rsp[1]))
            retry_time -= 1
        else:
            break
    if retry_time <= 0:
        logger.error(rsp[1])
        raise NSLCMException('Failed to query job from VNFM!')
    return True, json.JSONDecoder().decode(rsp[1])

def send_nf_scaling_request(vnfm_inst_id, vnf_inst_id, req_param):
    vnfm = get_vnfm_by_id(vnfm_inst_id)
    uri = '/openoapi/%s/v1/%s/vnfs/%s/scale' % (vnfm["type"], vnfm_inst_id, vnf_inst_id)
    ret = req_by_msb(uri, "POST", req_param)
    if ret[0] > 0:
        logger.error("Failed to send nf scale req:%s,%s", ret[2], ret[1])
        raise NSLCMException('Failed to send nf scale request to VNFM(%s)' % vnfm_inst_id)
    return json.JSONDecoder().decode(ret[1])
