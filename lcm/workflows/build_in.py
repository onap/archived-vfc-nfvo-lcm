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

logger = logging.getLogger(__name__)


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
    update_job()
    for i in range(vl_count):
        create_vl()
    wait_until_job_done()
    update_job()
    for i in range(vnf_count):
        create_vnf()
    wait_until_job_done()
    update_job()
    for i in range(sfc_count):
        create_sfc()
    wait_until_job_done()
    update_job()

def create_vl():
    # TODO:
    pass

def create_vnf():
    # TODO:
    pass

def create_sfc():
    # TODO:
    pass

def update_job():
    # TODO:
    pass

def wait_until_job_done():
    # TODO:
    pass  
