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
import logging
import traceback

from lcm.pub.utils.syscomm import fun_name
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils import restcall
from lcm.pub.exceptions import NSLCMException

logger = logging.getLogger(__name__)

RESULT_OK, RESULT_NG = "0", "1"

"""
format of input_data
{
    "jobId": uuid of job, 
    "nsInstanceId": id of ns instance,
    "object_context": json format of nsd,
    "object_additionalParamForNs": json format of additional parameters for ns,
    "object_additionalParamForVnf": json format of additional parameters for vnf,
    "vlCount": int type of VL count,
    "vnfCount: int type of VNF count,
    "sfcCount": int type of SFC count, 
    "sdnControllerId": uuid of SDN controller
}
"""
def run_ns_instantiate(input_data):
    logger.debug("Enter %s, input_data is %s", fun_name(), input_data)
    job_id = ignore_case_get(input_data, "jobId")
    ns_inst_id = ignore_case_get(input_data, "nsInstanceId")
    nsd_json = ignore_case_get(input_data, "object_context")
    ns_param_json = ignore_case_get(input_data, "object_additionalParamForNs")
    vnf_param_json = ignore_case_get(input_data, "object_additionalParamForVnf")
    vl_count = ignore_case_get(input_data, "vlCount")
    vnf_count = ignore_case_get(input_data, "vnfCount")
    sfc_count = ignore_case_get(input_data, "sfcCount")
    sdnc_id = ignore_case_get(input_data, "sdnControllerId")
    
    update_job(job_id, 10, "0", "Start to create VL")
    for i in range(vl_count):
        create_vl(ns_inst_id, i + 1, nsd_json, ns_param_json)

    update_job(job_id, 30, "0", "Start to create VNF")
    for i in range(vnf_count):
        create_vnf()
    wait_until_job_done()

    update_job(job_id, 70, "0", "Start to create SFC")
    for i in range(sfc_count):
        create_sfc()
    wait_until_job_done()

    update_job(job_id, 90, "0", "Start to post deal")
    post_deal()

    update_job(job_id, 100, "0", "Create NS successfully.")

def create_vl(ns_inst_id, vl_index, nsd, ns_param):
    uri = "api/nslcm/v1/ns/vls"
    data = json.JSONEncoder().encode({
        "nsInstanceId": ns_inst_id,
        "vlIndex": vl_index,
        "context": nsd,
        "additionalParamForNs": ns_param
    })

    ret = restcall.req_by_msb(uri, "POST", data)
    if ret[0] != 0:
        logger.error("Failed to call create_vl(%s): %s", vl_index, ret[1])
        raise NSLCMException("Failed to call create_vl(index is %s)" % vl_index)

    result = str(ret[1]["result"])
    detail = ret[1]["detail"]
    vl_id = ret[1]["vlId"]
    if result != RESULT_OK:
        logger.error("Failed to create VL(%s): %s", vl_id, detail)
        raise NSLCMException("Failed to create VL(%s)" % vl_id)

    logger.debug("Create VL(%s) successfully.", vl_id)

def create_vnf():
    # TODO:
    pass

def create_sfc():
    # TODO:
    pass

def post_deal():
    # TODO:
    pass    

def update_job(job_id, progress, errcode, desc):
    uri = "api/nslcm/v1/jobs/{jobId}".format(jobId=job_id)
    data = json.JSONEncoder().encode({
        "progress": progress,
        "errcode": errcode,
        "desc": desc
    })
    restcall.req_by_msb(uri, "POST", data)  

def wait_until_job_done():
    # TODO:
    pass  
