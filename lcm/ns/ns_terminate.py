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
import threading
import time
import traceback

from lcm.pub.database.models import NSInstModel, VLInstModel, FPInstModel, NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.nslcm import call_from_ns_cancel_resource
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils import restcall
from lcm.ns.const import OWNER_TYPE

JOB_ERROR = 255

logger = logging.getLogger(__name__)


class TerminateNsService(threading.Thread):
    def __init__(self, ns_inst_id, terminate_type, terminate_timeout, job_id):
        threading.Thread.__init__(self)
        self.ns_inst_id = ns_inst_id
        self.terminate_type = terminate_type
        self.terminate_timeout = terminate_timeout
        self.job_id = job_id

    def run(self):
        try:
            if not NSInstModel.objects.filter(id=self.ns_inst_id):
                JobUtil.add_job_status(self.job_id, 100, "Need not terminate.", '')
                return
            JobUtil.add_job_status(self.job_id, 10, "Starting terminate...", '')

            self.cancel_sfc_list()
            self.cancel_vnf_list()
            self.cancel_vl_list()

            NSInstModel.objects.filter(id=self.ns_inst_id).update(status='null')
            JobUtil.add_job_status(self.job_id, 100, "ns terminate ends.", '')
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_ERROR, "ns terminate fail.")

    def cancel_vl_list(self):
        array_vlinst = VLInstModel.objects.filter(ownertype=OWNER_TYPE.NS, ownerid=self.ns_inst_id)
        if not array_vlinst:
            logger.info("[cancel_vl_list] no vlinst attatch to ns_inst_id: %s" % self.ns_inst_id)
            return
        step_progress = 20 / len(array_vlinst)
        cur_progress = 70
        for vlinst in array_vlinst:
            delete_result = "failed"
            cur_progress += step_progress
            try:
                ret = call_from_ns_cancel_resource('vl', vlinst.vlinstanceid)
                if ret[0] == 0:
                    result = json.JSONDecoder().decode(ret[1]).get("result", "")
                    if str(result) == '0':
                        delete_result = "success"
            except Exception as e:
                logger.error("[cancel_vl_list] error[%s]!" % e.message)
                logger.error(traceback.format_exc())
            job_msg = "Delete vlinst:[%s] %s." % (vlinst.vlinstanceid, delete_result)
            JobUtil.add_job_status(self.job_id, cur_progress, job_msg)

    def cancel_sfc_list(self):
        array_sfcinst = FPInstModel.objects.filter(nsinstid=self.ns_inst_id)
        if not array_sfcinst:
            logger.info("[cancel_sfc_list] no sfcinst attatch to ns_inst_id: %s" % self.ns_inst_id)
            return
        step_progress = 20 / len(array_sfcinst)
        cur_progress = 30
        for sfcinst in array_sfcinst:
            cur_progress += step_progress
            delete_result = "failed"
            try:
                ret = call_from_ns_cancel_resource('sfc', sfcinst.sfcid)
                if ret[0] == 0:
                    result = json.JSONDecoder().decode(ret[1]).get("result", "")
                    if str(result) == '0':
                        delete_result = "success"
            except Exception as e:
                logger.error("[cancel_sfc_list] error[%s]!" % e.message)
                logger.error(traceback.format_exc())
            job_msg = "Delete sfcinst:[%s] %s." % (sfcinst.sfcid, delete_result)
            JobUtil.add_job_status(self.job_id, cur_progress, job_msg)

    def cancel_vnf_list(self):
        array_vnfinst = NfInstModel.objects.filter(ns_inst_id=self.ns_inst_id)
        if not array_vnfinst:
            logger.info("[cancel_vnf_list] no vnfinst attatch to ns_inst_id: %s" % self.ns_inst_id)
            return
        step_progress = 20 / len(array_vnfinst)
        cur_progress = 50
        for vnfinst in array_vnfinst:
            cur_progress += step_progress
            delete_result = "failed"
            try:
                if self.delete_vnf(vnfinst.nfinstid):
                    delete_result = "success"
            except Exception as e:
                logger.error("[cancel_vnf_list] error[%s]!" % e.message)
                logger.error(traceback.format_exc())
            job_msg = "Delete vnfinst:[%s] %s." % (vnfinst.nfinstid, delete_result)
            JobUtil.add_job_status(self.job_id, cur_progress, job_msg)

    def delete_vnf(self, nf_instid):
        ret = call_from_ns_cancel_resource('vnf', nf_instid)
        if ret[0] != 0:
            return False
        job_info = json.JSONDecoder().decode(ret[1])
        vnf_job_id = ignore_case_get(job_info, "jobid")
        return self.wait_delete_vnf_job_finish(vnf_job_id)

    def wait_delete_vnf_job_finish(self, vnf_job_id):
        count = 0
        retry_count = 400
        interval_second = 2
        response_id, new_response_id = 0, 0
        job_end_normal, job_timeout = False, True
        while count < retry_count:
            count = count + 1
            time.sleep(interval_second)
            uri = "/api/nslcm/v1/jobs/%s?responseId=%s" % (vnf_job_id, response_id)
            ret = restcall.req_by_msb(uri, "GET")
            if ret[0] != 0:
                logger.error("Failed to query job: %s:%s", ret[2], ret[1])
                continue
            job_result = json.JSONDecoder().decode(ret[1])
            if "responseDescriptor" not in job_result:
                logger.error("Job(%s) does not exist.", vnf_job_id)
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
                logger.error("Job(%s) failed: %s", vnf_job_id, job_desc)
                break
            elif progress == 100:
                job_end_normal, job_timeout = True, False
                logger.info("Job(%s) ended normally", vnf_job_id)
                break
        if job_timeout:
            logger.error("Job(%s) timeout", vnf_job_id)
        return job_end_normal
