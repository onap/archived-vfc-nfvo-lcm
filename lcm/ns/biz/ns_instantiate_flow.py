# Copyright 2018 ZTE Corporation.
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
from lcm.jobs.const import JOB_INSTANCE_URI
from lcm.pub.utils.syscomm import fun_name
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils import restcall
from lcm.jobs.enum import JOB_PROGRESS, JOB_ERROR_CODE
from lcm.pub.exceptions import NSLCMException
from lcm.workflows.graphflow.flow.flow import GraphFlow
from lcm.ns.biz.ns_lcm_op_occ import NsLcmOpOcc


logger = logging.getLogger(__name__)

config = {
    "CreateVnf": {"module": "lcm.ns_vnfs", "class": "CreateVnf"},
    "CreatePnf": {"module": "lcm.ns_pnfs", "class": "CreatePnf"},
    "CreateVl": {"module": "lcm.ns_vls", "class": "CreateVl"}
}


class NsInstantiateWorkflowThread(Thread):
    def __init__(self, plan_input, occ_id):
        Thread.__init__(self)
        self.plan_input = plan_input
        self.occ_id = occ_id

    def run(self):
        run_ns_instantiate(self.plan_input, self.occ_id)


def run_ns_instantiate(input_data, occ_id):
    """
    format of input_data
    {
        "jobId": uuid of job,
        "nsInstanceId": id of ns instance,
        "object_context": json format of nsd,
        "object_additionalParamForNs": json format of additional parameters for ns,
        "object_additionalParamForVnf": json format of additional parameters for vnf,
        "object_additionalParamForPnf": json format of additional parameters for pnf,
        "vlCount": int type of VL count,
        "vnfCount: int type of VNF count
    }
    """
    logger.debug("Enter %s, input_data is %s", fun_name(), input_data)
    ns_inst_id = ignore_case_get(input_data, "nsInstanceId")
    job_id = ignore_case_get(input_data, "jobId")
    update_job(job_id, 10, JOB_ERROR_CODE.NO_ERROR, "Start to prepare the NS instantiate workflow parameter")
    deploy_graph = build_deploy_graph(input_data)
    TaskSet = build_TaskSet(input_data)
    ns_instantiate_ok = False

    try:
        update_job(job_id, 15, "true", "Start the NS instantiate workflow")
        gf = GraphFlow(deploy_graph, TaskSet, config)
        logger.debug("NS graph flow run up!")
        gf.start()
        gf.join()
        gf.task_manager.wait_tasks_done(gf.sort_nodes)
        if gf.task_manager.is_all_task_finished():
            logger.debug("NS is instantiated!")
            update_job(job_id, 90, JOB_ERROR_CODE.NO_ERROR, "Start to post deal")
            post_deal(ns_inst_id, "true")
            update_job(job_id, JOB_PROGRESS.FINISHED, JOB_ERROR_CODE.NO_ERROR, "Create NS successfully.")
            NsLcmOpOcc.update(occ_id, "COMPLETED")
            ns_instantiate_ok = True
    except NSLCMException as e:
        logger.error("Failded to Create NS: %s", e.args[0])
        update_job(job_id, JOB_PROGRESS.ERROR, JOB_ERROR_CODE.ERROR, "Failded to Create NS.")
        NsLcmOpOcc.update(occ_id, operationState="FAILED", error=e.args[0])
        post_deal(ns_inst_id, "false")
    except Exception as e:
        logger.error(traceback.format_exc())
        update_job(job_id, JOB_PROGRESS.ERROR, JOB_ERROR_CODE.ERROR, "Failded to Create NS.")
        NsLcmOpOcc.update(occ_id, operationState="FAILED", error=e.args[0])
        post_deal(ns_inst_id, "false")
    return ns_instantiate_ok


def build_deploy_graph(input_data):
    nsd_json_str = ignore_case_get(input_data, "object_context")
    nsd_json = json.JSONDecoder().decode(nsd_json_str)
    deploy_graph = ignore_case_get(nsd_json, "graph")
    logger.debug("NS graph flow: %s" % deploy_graph)
    return deploy_graph


def build_vls(input_data):
    ns_inst_id = ignore_case_get(input_data, "nsInstanceId")
    nsd_json = json.JSONDecoder().decode(ignore_case_get(input_data, "object_context"))
    ns_param_json = ignore_case_get(input_data, "object_additionalParamForNs")
    vl_count = int(ignore_case_get(input_data, "vlCount", 0))

    vls = {}
    for i in range(vl_count):
        data = {
            "nsInstanceId": ns_inst_id,
            "vlIndex": i,
            "context": nsd_json,
            "additionalParamForNs": ns_param_json
        }
        key = nsd_json["vls"][i - 1]["vl_id"]
        vls[key] = {
            "type": "CreateVl",
            "input": {
                    "content": data
            }
        }
    return vls


def build_vnfs(input_data):
    ns_inst_id = ignore_case_get(input_data, "nsInstanceId")
    vnf_count = int(ignore_case_get(input_data, "vnfCount", 0))
    vnf_param_json = json.JSONDecoder().decode(ignore_case_get(input_data, "object_additionalParamForVnf"))
    vnfs = {}
    for i in range(vnf_count):
        data = {
            "nsInstanceId": ns_inst_id,
            "vnfIndex": i,
            "additionalParamForVnf": vnf_param_json
        }
        key = vnf_param_json[i - 1]["vnfProfileId"]
        vnfs[key] = {
            "type": "CreateVnf",
            "input": {
                    "content": data
            }
        }
    return vnfs


def build_pnfs(input_data):
    return json.JSONDecoder().decode(ignore_case_get(input_data, "object_additionalParamForPnf"))


def build_TaskSet(input_data):
    vls = build_vls(input_data)
    vnfs = build_vnfs(input_data)
    pnfs = build_pnfs(input_data)
    task_set = dict(dict(vls, **vnfs), **pnfs)
    return task_set


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
    logger.debug("job_id %s" % job_id)
    uri = JOB_INSTANCE_URI % job_id
    data = json.JSONEncoder().encode({
        "progress": progress,
        "errcode": errcode,
        "desc": desc
    })
    ret = restcall.req_by_msb(uri, "POST", data)
    return ret
