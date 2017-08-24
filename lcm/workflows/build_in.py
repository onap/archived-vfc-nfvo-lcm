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
from threading import Thread
import time

from lcm.pub.utils.syscomm import fun_name
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils import restcall
from lcm.pub.exceptions import NSLCMException

logger = logging.getLogger(__name__)

RESULT_OK, RESULT_NG = "0", "1"
JOB_ERROR = 255

g_jobs_status = {}

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
    g_jobs_status[job_id] = [1 for i in range(vnf_count)]
    try:
        update_job(job_id, 10, "0", "Start to create VL")
        for i in range(vl_count):
            create_vl(ns_inst_id, i + 1, nsd_json, ns_param_json)

        update_job(job_id, 30, "0", "Start to create VNF")
        jobs = [create_vnf(ns_inst_id, i + 1, vnf_param_json) for i in range(vnf_count)] 
        wait_until_jobs_done(job_id, jobs)

        update_job(job_id, 70, "0", "Start to create SFC")
        jobs = [create_sfc(ns_inst_id, i + 1, nsd_json, sdnc_id) for i in range(sfc_count)] 
        wait_until_jobs_done(job_id, jobs)

        update_job(job_id, 90, "0", "Start to post deal")
        post_deal(ns_inst_id, "true")

        update_job(job_id, 100, "0", "Create NS successfully.")
    except NSLCMException as e:
        logger.error("Failded to Create NS: %s", e.message)
        update_job(job_id, JOB_ERROR, "255", "Failded to Create NS.")
        post_deal(ns_inst_id, "false")
    except:
        logger.error(traceback.format_exc())
        update_job(job_id, JOB_ERROR, "255", "Failded to Create NS.")
        post_deal(ns_inst_id, "false")
    finally:
        g_jobs_status.pop(job_id)


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

def create_vnf(ns_inst_id, vnf_index, nf_param):
    uri = "/ns/vnfs"
    data = json.JSONEncoder().encode({
        "nsInstanceId": ns_inst_id,
        "vnfIndex": vnf_index,
        "additionalParamForVnf": nf_param
    })

    ret = restcall.req_by_msb(uri, "POST", data)
    if ret[0] != 0:
        logger.error("Failed to call create_vnf(%s): %s", vnf_index, ret[1])
        raise NSLCMException("Failed to call create_vnf(index is %s)" % vnf_index)

    vnf_inst_id = ret[1]["vnfInstId"]
    job_id = ret[1]["jobId"]
    logger.debug("Create VNF(%s) started.", vnf_inst_id)
    return vnf_inst_id, job_id, vnf_index - 1

def create_sfc(ns_inst_id, fp_index, nsd_json, sdnc_id):
    uri = "/ns/sfcs"
    data = json.JSONEncoder().encode({
        "nsInstanceId": ns_inst_id,
        "context": nsd_json,
        "fpindex": fp_index,
        "sdnControllerId": sdnc_id
    })

    ret = restcall.req_by_msb(uri, "POST", data)
    if ret[0] != 0:
        logger.error("Failed to call create_sfc(%s): %s", fp_index, ret[1])
        raise NSLCMException("Failed to call create_sfc(index is %s)" % fp_index)

    sfc_inst_id = ret[1]["sfcInstId"]
    job_id = ret[1]["jobId"]
    logger.debug("Create SFC(%s) started.", sfc_inst_id)
    return sfc_inst_id, job_id, fp_index - 1

def post_deal(ns_inst_id, status):
    uri = "/ns/{nsInstanceId}/postdeal".format(nsInstanceId=ns_inst_id) 
    data = json.JSONEncoder().encode({
        "status": status
    })

    ret = restcall.req_by_msb(uri, "POST", data)
    if ret[0] != 0:
        logger.error("Failed to call post_deal(%s): %s", ns_inst_id, ret[1])
    logger.debug("Call post_deal(%s) successfully.", ns_inst_id)

def update_job(job_id, progress, errcode, desc):
    uri = "api/nslcm/v1/jobs/{jobId}".format(jobId=job_id)
    data = json.JSONEncoder().encode({
        "progress": progress,
        "errcode": errcode,
        "desc": desc
    })
    restcall.req_by_msb(uri, "POST", data)  

class JobWaitThread(Thread):
    """
    Job Wait 
    """

    def __init__(self, inst_id, job_id, index):
        Thread.__init__(self)
        self.inst_id = inst_id
        self.job_id = job_id
        self.index = index
        self.retry_count = 60
        self.interval_second = 3

    def run(self):
        count = 0
        response_id, new_response_id = 0, 0
        job_end_normal, job_timeout = False, True
        while count < self.retry_count:
            count = count + 1
            time.sleep(self.interval_second)
            uri = "/api/nslcm/v1/jobs/%s?responseId=%s" % (self.job_id, response_id)
            ret = restcall.req_by_msb(uri, "GET")
            if ret[0] != 0:
                logger.error("Failed to query job: %s:%s", ret[2], ret[1])
                continue
            job_result = json.JSONDecoder().decode(ret[1])
            if "responseDescriptor" not in job_result:
                logger.error("Job(%s) does not exist.", self.job_id)
                continue
            progress = job_result["responseDescriptor"]["progress"]
            new_response_id = job_result["responseDescriptor"]["responseId"]
            job_desc = job_result["responseDescriptor"]["statusDescription"]
            if new_response_id != response_id:
                logger.debug("%s:%s:%s", progress, new_response_id, job_desc)
                response_id = new_response_id
                count = 0
            if progress == JOB_ERROR:
                job_timeout = False
                logger.error("Job(%s) failed: %s", self.job_id, job_desc)
                break
            elif progress == 100:
                job_end_normal, job_timeout = True, False
                logger.info("Job(%s) ended normally", self.job_id)
                break
        if job_timeout:
            logger.error("Job(%s) timeout", self.job_id)
        if self.job_id in g_jobs_status:
            if job_end_normal:
                g_jobs_status[self.job_id][self.index] = 0

def wait_until_jobs_done(g_job_id, jobs):
    job_threads = []
    for inst_id, job_id, index in jobs:
        job_threads.append(JobWaitThread(inst_id, job_id, index))
    for t in job_threads:
        t.start()
    for t in job_threads:
        t.join()
    if g_job_id in g_jobs_status:
        if sum(g_jobs_status[g_job_id]) > 0:
            raise NSLCMException("Some jobs failed!")
      

