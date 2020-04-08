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
import traceback
from threading import Thread
import time
from lcm.jobs.const import JOB_INSTANCE_URI, JOB_INSTANCE_RESPONSE_ID_URI
from lcm.jobs.enum import JOB_ERROR_CODE
from lcm.pub.utils.syscomm import fun_name
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils import restcall
from lcm.pub.exceptions import NSLCMException
from lcm.ns.biz.ns_lcm_op_occ import NsLcmOpOcc

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


def run_ns_instantiate(input_data, occ_id):
    logger.debug("Enter %s, input_data is %s", fun_name(), input_data)
    ns_instantiate_ok = False
    job_id = ignore_case_get(input_data, "jobId")
    ns_inst_id = ignore_case_get(input_data, "nsInstanceId")
    nsd_json = ignore_case_get(input_data, "object_context")
    ns_param_json = ignore_case_get(input_data, "object_additionalParamForNs")
    vnf_param_json = ignore_case_get(input_data, "object_additionalParamForVnf")
    pnf_param_json = ignore_case_get(input_data, "object_additionalParamForPnf")
    vl_count = int(ignore_case_get(input_data, "vlCount", 0))
    vnf_count = int(ignore_case_get(input_data, "vnfCount", 0))
    sfc_count = int(ignore_case_get(input_data, "sfcCount", 0))
    sdnc_id = ignore_case_get(input_data, "sdnControllerId")
    g_jobs_status[job_id] = [1 for i in range(vnf_count)] #为啥五次都为1
    try:
        update_job(job_id, 10, JOB_ERROR_CODE.NO_ERROR, "Start to create VL")
        for i in range(vl_count):
            create_vl(ns_inst_id, i + 1, nsd_json, ns_param_json)

        update_job(job_id, 30, JOB_ERROR_CODE.NO_ERROR, "Start to create VNF")
        jobs = [create_vnf(ns_inst_id, i + 1, vnf_param_json) for i in range(vnf_count)]
        wait_until_jobs_done(job_id, jobs)

        [confirm_vnf_status(inst_id) for inst_id, _, _ in jobs]

        update_job(job_id, 50, JOB_ERROR_CODE.NO_ERROR, "Start to create PNF")
        create_pnf(pnf_param_json)

        update_job(job_id, 70, JOB_ERROR_CODE.NO_ERROR, "Start to create SFC")
        g_jobs_status[job_id] = [1 for i in range(sfc_count)]
        jobs = [create_sfc(ns_inst_id, i + 1, nsd_json, sdnc_id) for i in range(sfc_count)]
        wait_until_jobs_done(job_id, jobs)

        [confirm_sfc_status(inst_id) for inst_id, _, _ in jobs]

        update_job(job_id, 90, JOB_ERROR_CODE.NO_ERROR, "Start to post deal")
        post_deal(ns_inst_id, "true")

        update_job(job_id, 100, JOB_ERROR_CODE.NO_ERROR, "Create NS successfully.")
        NsLcmOpOcc.update(occ_id, "COMPLETED")
        ns_instantiate_ok = True
    except NSLCMException as e:
        logger.error("Failded to Create NS: %s", e.args[0])
        update_job(job_id, JOB_ERROR, JOB_ERROR_CODE.ERROR, "Failded to Create NS.")
        NsLcmOpOcc.update(occ_id, operationState="FAILED", error=e.args[0])
        post_deal(ns_inst_id, "false")
    except Exception as e:
        logger.error(traceback.format_exc())
        update_job(job_id, JOB_ERROR, JOB_ERROR_CODE.ERROR, "Failded to Create NS.")
        NsLcmOpOcc.update(occ_id, operationState="FAILED", error=e.args[0])
        post_deal(ns_inst_id, "false")
    finally:
        g_jobs_status.pop(job_id)
    return ns_instantiate_ok


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
    ret[1] = json.JSONDecoder().decode(ret[1])

    result = str(ret[1]["result"])
    detail = ret[1]["detail"]
    vl_id = ret[1]["vlId"]
    if result != RESULT_OK:
        logger.error("Failed to create VL(%s): %s", vl_id, detail)
        raise NSLCMException("Failed to create VL(%s)" % vl_id)

    logger.debug("Create VL(%s) successfully.", vl_id)


def create_vnf(ns_inst_id, vnf_index, nf_param):
    uri = "api/nslcm/v1/ns/vnfs"
    data = json.JSONEncoder().encode({
        "nsInstanceId": ns_inst_id,
        "vnfIndex": vnf_index,
        "additionalParamForVnf": json.JSONDecoder().decode(nf_param)
    })

    ret = restcall.req_by_msb(uri, "POST", data)
    if ret[0] != 0:
        logger.error("Failed to call create_vnf(%s): %s", vnf_index, ret[1])
        raise NSLCMException("Failed to call create_vnf(index is %s)" % vnf_index)
    ret[1] = json.JSONDecoder().decode(ret[1])

    vnf_inst_id = ret[1]["vnfInstId"]
    job_id = ret[1]["jobId"]
    logger.debug("Create VNF(%s) started.", vnf_inst_id)
    return vnf_inst_id, job_id, vnf_index - 1


def create_sfc(ns_inst_id, fp_index, nsd_json, sdnc_id):
    uri = "api/nslcm/v1/ns/sfcs"
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
    ret[1] = json.JSONDecoder().decode(ret[1])

    sfc_inst_id = ret[1]["sfcInstId"]
    job_id = ret[1]["jobId"]
    logger.debug("Create SFC(%s) started.", sfc_inst_id)
    return sfc_inst_id, job_id, fp_index - 1


def post_deal(ns_inst_id, status):
    uri = "api/nslcm/v1/ns/{nsInstanceId}/postdeal".format(nsInstanceId=ns_inst_id)
    data = json.JSONEncoder().encode({
        "status": status
    })

    ret = restcall.req_by_msb(uri, "POST", data)
    if ret[0] != 0:
        logger.error("Failed to call post_deal(%s): %s", ns_inst_id, ret[1])
    logger.debug("Call post_deal(%s, %s) successfully.", ns_inst_id, status)


def update_job(job_id, progress, errcode, desc):
    uri = JOB_INSTANCE_URI % job_id
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

    def __init__(self, inst_id, job_id, ns_job_id, index):
        Thread.__init__(self)
        self.inst_id = inst_id
        self.job_id = job_id
        self.ns_job_id = ns_job_id
        self.index = index
        self.retry_count = 600
        self.interval_second = 3

    def run(self):
        count = 0
        response_id, new_response_id = 0, 0
        job_end_normal, job_timeout = False, True
        while count < self.retry_count:
            count = count + 1
            time.sleep(self.interval_second)
            uri = JOB_INSTANCE_RESPONSE_ID_URI % (self.job_id, response_id)
            ret = restcall.req_by_msb(uri, "GET")
            if ret[0] != 0:
                logger.error("Failed to query job: %s:%s", ret[2], ret[1])
                continue
            job_result = json.JSONDecoder().decode(ret[1])
            if "responseDescriptor" not in job_result:
                logger.debug("No new progress after response_id(%s) in job(%s)", response_id, self.job_id)
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
        if self.ns_job_id in g_jobs_status:
            if job_end_normal:
                g_jobs_status[self.ns_job_id][self.index] = 0


def wait_until_jobs_done(g_job_id, jobs):
    job_threads = []
    for inst_id, job_id, index in jobs:
        job_threads.append(JobWaitThread(inst_id, job_id, g_job_id, index))
    for t in job_threads:
        t.start()
    for t in job_threads:
        t.join()
    if g_job_id in g_jobs_status:
        if sum(g_jobs_status[g_job_id]) > 0:
            logger.error("g_jobs_status[%s]: %s", g_job_id, g_jobs_status[g_job_id])
            raise NSLCMException("Some jobs failed!")


def confirm_vnf_status(vnf_inst_id):
    uri = "api/nslcm/v1/ns/vnfs/{vnfInstId}".format(vnfInstId=vnf_inst_id)
    ret = restcall.req_by_msb(uri, "GET")
    if ret[0] != 0:
        raise NSLCMException("Failed to call get_vnf(%s)" % vnf_inst_id)
    ret[1] = json.JSONDecoder().decode(ret[1])

    vnf_status = ret[1]["vnfStatus"]
    if vnf_status != "active":
        raise NSLCMException("Status of VNF(%s) is not active" % vnf_inst_id)


def confirm_sfc_status(sfc_inst_id):
    uri = "api/nslcm/v1/ns/sfcs/{sfcInstId}".format(sfcInstId=sfc_inst_id)
    ret = restcall.req_by_msb(uri, "GET")
    if ret[0] != 0:
        raise NSLCMException("Failed to call get_sfc(%s)" % sfc_inst_id)
    ret[1] = json.JSONDecoder().decode(ret[1])

    sfc_status = ret[1]["sfcStatus"]
    if sfc_status != "active":
        raise NSLCMException("Status of SFC(%s) is not active" % sfc_inst_id)


def create_pnf(pnf_param_json):
    if pnf_param_json and len(pnf_param_json) > 0:
        pnfs = json.JSONDecoder().decode(pnf_param_json)
        for pnf in list(pnfs.values()):
            uri = "/api/nslcm/v1/pnfs"
            method = "POST"
            content = json.JSONEncoder().encode(pnf["input"]["content"])
            ret = restcall.req_by_msb(uri, method, content)
            if ret[0] != 0:
                logger.error("Failed to call create_pnf(%s) result %s", content, ret)
                raise NSLCMException("Failed to call create_pnf(%s)" % content)
