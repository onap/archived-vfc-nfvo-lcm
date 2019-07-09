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

from lcm.jobs.const import JOB_INSTANCE_RESPONSE_ID_URI
from lcm.pub.database.models import NSInstModel, VLInstModel, FPInstModel, NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.nslcm import call_from_ns_cancel_resource
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils import restcall
from lcm.ns.enum import OWNER_TYPE
from lcm.pub.database.models import PNFInstModel
from lcm.ns.biz.ns_lcm_op_occ import NsLcmOpOcc
from lcm.jobs.enum import JOB_PROGRESS

logger = logging.getLogger(__name__)


class TerminateNsService(threading.Thread):
    def __init__(self, ns_inst_id, job_id, request_data):
        threading.Thread.__init__(self)
        self.terminate_type = request_data.get('terminationType', 'GRACEFUL')
        self.terminate_timeout = request_data.get('gracefulTerminationTimeout', 600)
        self.job_id = job_id
        self.ns_inst_id = ns_inst_id
        self.occ_id = NsLcmOpOcc.create(ns_inst_id, "TERMINATE", "PROCESSING", False, request_data)

    def run(self):
        try:
            if not NSInstModel.objects.filter(id=self.ns_inst_id):
                JobUtil.add_job_status(self.job_id, JOB_PROGRESS.FINISHED, "Need not terminate.", '')
                NsLcmOpOcc.update(self.occ_id, "COMPLETED")
                return
            JobUtil.add_job_status(self.job_id, 10, "Starting terminate...", '')

            self.cancel_sfc_list()
            self.cancel_vnf_list()
            self.cancel_vl_list()
            self.cancel_pnf_list()

            NSInstModel.objects.filter(id=self.ns_inst_id).update(status='null')
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.FINISHED, "ns terminate ends.", '')
            NsLcmOpOcc.update(self.occ_id, "COMPLETED")
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, e.args[0])
            NsLcmOpOcc.update(self.occ_id, operationState="FAILED", error=e.args[0])
        except Exception as e:
            logger.error(e.args[0])
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, "ns terminate fail.")
            NsLcmOpOcc.update(self.occ_id, operationState="FAILED", error=e.args[0])

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
                logger.error("[cancel_vl_list] error[%s]!" % e.args[0])
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
                logger.error("[cancel_sfc_list] error[%s]!" % e.args[0])
                logger.error(traceback.format_exc())
            job_msg = "Delete sfcinst:[%s] %s." % (sfcinst.sfcid, delete_result)
            JobUtil.add_job_status(self.job_id, cur_progress, job_msg)

    def cancel_vnf_list(self):
        array_vnfinst = NfInstModel.objects.filter(ns_inst_id=self.ns_inst_id)
        if not array_vnfinst:
            logger.info("[cancel_vnf_list] no vnfinst attatch to ns_inst_id: %s" % self.ns_inst_id)
            return
        step_progress = 10 / len(array_vnfinst)
        cur_progress = 50
        vnf_jobs = []
        for vnfinst in array_vnfinst:
            cur_progress += step_progress
            delete_result = "failed"
            vnf_job_id = ''
            try:
                vnf_job_id = self.delete_vnf(vnfinst.nfinstid)
                if vnf_job_id:
                    delete_result = "deleting"
            except Exception as e:
                logger.error("[cancel_vnf_list] error[%s]!" % e.args[0])
                logger.error(traceback.format_exc())
            job_msg = "Delete vnfinst:[%s] %s." % (vnfinst.nfinstid, delete_result)
            JobUtil.add_job_status(self.job_id, cur_progress, job_msg)
            vnf_jobs.append((vnfinst.nfinstid, vnf_job_id))

        for vnfinstid, vnfjobid in vnf_jobs:
            try:
                cur_progress += step_progress
                if not vnfjobid:
                    continue
                is_job_ok = self.wait_delete_vnf_job_finish(vnfjobid)
                msg = "%s to delete VNF(%s)" % ("Succeed" if is_job_ok else "Failed", vnfinstid)
                logger.debug(msg)
                JobUtil.add_job_status(self.job_id, cur_progress, msg)
            except Exception as e:
                msg = "Exception occurs when delete VNF(%s)" % vnfinstid
                logger.debug(msg)
                JobUtil.add_job_status(self.job_id, cur_progress, msg)

    def delete_vnf(self, nf_instid):
        term_param = {
            "terminationType": self.terminate_type
        }
        if self.terminate_timeout:
            term_param["gracefulTerminationTimeout"] = int(self.terminate_timeout)
        ret = call_from_ns_cancel_resource('vnf', nf_instid, term_param)
        if ret[0] != 0:
            logger.error("Terminate VNF(%s) failed: %s", nf_instid, ret[1])
            return ''
        job_info = json.JSONDecoder().decode(ret[1])
        vnf_job_id = ignore_case_get(job_info, "jobId")
        return vnf_job_id

    def wait_delete_vnf_job_finish(self, vnf_job_id):
        count = 0
        retry_count = 400
        interval_second = 2
        response_id, new_response_id = 0, 0
        job_end_normal, job_timeout = False, True
        while count < retry_count:
            count = count + 1
            time.sleep(interval_second)
            uri = JOB_INSTANCE_RESPONSE_ID_URI % (vnf_job_id, response_id)
            ret = restcall.req_by_msb(uri, "GET")
            if ret[0] != 0:
                logger.error("Failed to query job: %s:%s", ret[2], ret[1])
                continue
            job_result = json.JSONDecoder().decode(ret[1])
            if "responseDescriptor" not in job_result:
                logger.debug("No new progress after response_id(%s) in job(%s)", response_id, vnf_job_id)
                continue
            progress = job_result["responseDescriptor"]["progress"]
            new_response_id = job_result["responseDescriptor"]["responseId"]
            job_desc = job_result["responseDescriptor"]["statusDescription"]
            if new_response_id != response_id:
                logger.debug("%s:%s:%s", progress, new_response_id, job_desc)
                response_id = new_response_id
                count = 0
            if progress == JOB_PROGRESS.ERROR:
                job_timeout = False
                logger.error("Job(%s) failed: %s", vnf_job_id, job_desc)
                break
            elif progress == JOB_PROGRESS.FINISHED:
                job_end_normal, job_timeout = True, False
                logger.info("Job(%s) ended normally", vnf_job_id)
                break
        if job_timeout:
            logger.error("Job(%s) timeout", vnf_job_id)
        return job_end_normal

    def cancel_pnf_list(self):
        pnfinst_list = PNFInstModel.objects.filter(nsInstances__contains=self.ns_inst_id)
        if len(pnfinst_list) > 0:
            cur_progress = 90
            step_progress = 5 / len(pnfinst_list)
            for pnfinst in pnfinst_list:
                delete_result = "fail"
                try:
                    ret = call_from_ns_cancel_resource('pnf', pnfinst.pnfId)
                    if ret[0] == 0:
                        delete_result = "success"
                except Exception as e:
                    logger.error("[cancel_pnf_list] error[%s]!" % e.args[0])
                    logger.error(traceback.format_exc())
                job_msg = "Delete pnfinst:[%s] %s" % (pnfinst.pnfId, delete_result)
                cur_progress += step_progress
                JobUtil.add_job_status(self.job_id, cur_progress, job_msg)
