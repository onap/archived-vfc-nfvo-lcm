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
import math
import traceback
import logging
import json
import threading
import time
from lcm.ns.vnfs.wait_job import wait_job_finish
from lcm.pub.database.models import NSInstModel, VLInstModel, FPInstModel, NfInstModel
from lcm.pub.database.models import DefPkgMappingModel, InputParamMappingModel, ServiceBaseInfoModel
from lcm.pub.utils.jobutil import JOB_MODEL_STATUS, JobUtil
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.nslcm import call_from_ns_cancel_resource
from lcm.pub.utils.values import ignore_case_get

JOB_ERROR = 255
# [delete vnf try times]

logger = logging.getLogger(__name__)


class TerminateNsService(threading.Thread):
    def __init__(self, ns_inst_id, terminate_type, terminate_timeout, job_id):
        threading.Thread.__init__(self)
        self.ns_inst_id = ns_inst_id
        self.terminate_type = terminate_type
        self.terminate_timeout = terminate_timeout
        self.job_id = job_id
        self.vnfm_inst_id = ''

    def run(self):
        try:
            self.do_biz()
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_ERROR,  "ns terminate fail.", '')

    def do_biz(self):
        if not self.check_data():
            JobUtil.add_job_status(self.job_id, 100, "Need not terminate.", '')
            return

        self.cancel_sfc_list()
        self.cancel_vnf_list()
        time.sleep(4)
        self.cancel_vl_list()

        self.finaldata()

    def check_data(self):
        JobUtil.add_job_status(self.job_id, 0, "TERMINATING...", '')
        ns_inst = NSInstModel.objects.filter(id=self.ns_inst_id)
        if not ns_inst.exists():
            logger.warn('ns instance [%s] does not exist.' % self.ns_inst_id)
            return False
        JobUtil.add_job_status(self.job_id, 10, "Ns cancel: check ns_inst_id success", '')
        return True

    # delete VLINST
    def cancel_vl_list(self):
        array_vlinst = VLInstModel.objects.filter(ownertype='2', ownerid=self.ns_inst_id)
        if not array_vlinst:
            logger.error("[cancel_vl_list] no vlinst attatch to ns_inst_id:%s" % self.ns_inst_id)
            return
        step_progress = 20 / len(array_vlinst)
        cur_progress = 70
        for vlinst in array_vlinst:
            tmp_msg = vlinst.vlinstanceid
            try:
                ret = self.delete_vl(tmp_msg)
                if ret[0] == 0:
                    cur_progress += step_progress
                    result = json.JSONDecoder().decode(ret[1]).get("result", "")
                    if str(result) == '0':
                        JobUtil.add_job_status(self.job_id, cur_progress, "Delete vlinst:[%s] success." % tmp_msg, '')
                    else:
                        JobUtil.add_job_status(self.job_id, cur_progress, "Delete vlinst:[%s] failed." % tmp_msg, '')
                        return 'false'
                else:
                    NSInstModel.objects.filter(id=self.ns_inst_id).update(status='FAILED')
                    return 'false'
            except Exception as e:
                logger.error("[cancel_vl_list] error[%s]!" % e.message)
                logger.error(traceback.format_exc())
                JobUtil.add_job_status(self.job_id, cur_progress, "Delete vlinst:[%s] Failed." % tmp_msg, '')
                return 'false'
        return 'true'

    # delete SFC
    def cancel_sfc_list(self):
        array_sfcinst = FPInstModel.objects.filter(nsinstid=self.ns_inst_id)
        if not array_sfcinst:
            logger.error("[cancel_sfc_list] no sfcinst attatch to ns_inst_id:%s" % self.ns_inst_id)
            return
        step_progress = 20 / len(array_sfcinst)
        cur_progress = 30
        for sfcinst in array_sfcinst:
            tmp_msg = sfcinst.sfcid
            try:
                ret = self.delete_sfc(tmp_msg)
                if ret[0] == 0:
                    cur_progress += step_progress
                    result = json.JSONDecoder().decode(ret[1]).get("result", "")
                    if str(result) == '0':
                        JobUtil.add_job_status(self.job_id, cur_progress, "Delete sfcinst:[%s] success." % tmp_msg, '')
                    else:
                        JobUtil.add_job_status(self.job_id, cur_progress, "Delete sfcinst:[%s] failed." % tmp_msg, '')
                        return 'false'
                else:
                    NSInstModel.objects.filter(id=self.ns_inst_id).update(status='FAILED')
                    return 'false'
            except Exception as e:
                logger.error("[cancel_sfc_list] error[%s]!" % e.message)
                logger.error(traceback.format_exc())
                JobUtil.add_job_status(self.job_id, cur_progress, "Delete sfcinst:[%s] Failed." % tmp_msg, '')
                return 'false'
        return 'true'

    # delete Vnf
    def cancel_vnf_list(self):
        array_vnfinst = NfInstModel.objects.filter(ns_inst_id=self.ns_inst_id)
        if not array_vnfinst:
            logger.error("[cancel_vnf_list] no vnfinst attatch to ns_inst_id:%s" % self.ns_inst_id)
            return
        step_progress = 20 / len(array_vnfinst)
        cur_progress = 50
        for vnfinst in array_vnfinst:
            tmp_msg = vnfinst.nfinstid
            try:
                self.delete_vnf(tmp_msg)
                cur_progress += step_progress
                JobUtil.add_job_status(self.job_id, cur_progress, "Delete vnfinst:[%s] success." % tmp_msg, '')
            except Exception as e:
                logger.error("[cancel_vnf_list] error[%s]!" % e.message)
                logger.error(traceback.format_exc())
                JobUtil.add_job_status(self.job_id, cur_progress, "Delete vnfinst:[%s] Failed." % tmp_msg, '')
                return 'false'
        return 'true'

    def delete_vnf(self, nf_instid):
        ret = call_from_ns_cancel_resource('vnf', nf_instid)
        self.delete_resource(ret)

    def delete_sfc(self, sfc_instid):
        ret = call_from_ns_cancel_resource('sfc', sfc_instid)
        return ret

    def delete_vl(self, vl_instid):
        ret = call_from_ns_cancel_resource('vl', vl_instid)
        return ret

    def delete_resource(self, result):
        logger.debug("terminate_type=%s, result=%s", self.terminate_type, result)
        if result[0] == 0:
            job_info = json.JSONDecoder().decode(result[1])
            vnfm_job_id = ignore_case_get(job_info, "jobid")
            self.add_progress(5, "SEND_TERMINATE_REQ_SUCCESS")
            if self.terminate_type == 'forceful':
                ret = wait_job_finish(self.vnfm_inst_id, self.job_id, vnfm_job_id,
                                      progress_range=[10, 50],
                                      timeout=self.terminate_timeout,
                                      job_callback=TerminateNsService.wait_job_mode_callback, mode='1')
                if ret != JOB_MODEL_STATUS.FINISHED:
                    logger.error('[NS terminate] VNFM terminate ns failed')
                    NSInstModel.objects.filter(id=self.ns_inst_id).update(status='FAILED')
                    raise NSLCMException("DELETE_NS_RESOURCE_FAILED")
        else:
            logger.error('[NS terminate] VNFM terminate ns failed')
            NSInstModel.objects.filter(id=self.ns_inst_id).update(status='FAILED')
            raise NSLCMException("DELETE_NS_RESOURCE_FAILED")

    def exception(self):
        NSInstModel.objects.filter(id=self.ns_inst_id).update(status='FAILED')
        raise NSLCMException("DELETE_NS_RESOURCE_FAILED")

    def finaldata(self):
        NSInstModel.objects.filter(id=self.ns_inst_id).update(status='null')
        JobUtil.add_job_status(self.job_id, 100, "ns terminate ends.", '')

    # @staticmethod
    # def call_vnfm_to_cancel_resource(res_type, instid):
    #     ret = call_from_ns_cancel_resource(res_type, instid)
    #     return ret

    def add_progress(self, progress, status_decs, error_code=""):
        JobUtil.add_job_status(self.job_id, progress, status_decs, error_code)

    @staticmethod
    def wait_job_mode_callback(vnfo_job_id, vnfm_job_id, job_status, jobs, progress_range, **kwargs):
        for job in jobs:
            progress = TerminateNsService.calc_progress_over_100(job['progress'], progress_range)
            if 255 == progress and '1' == kwargs['mode']:
                break
            JobUtil.add_job_status(vnfo_job_id, progress, job.get('statusdescription', ''), job.get('errorcode', ''))

        latest_progress = TerminateNsService.calc_progress_over_100(job_status['progress'], progress_range)
        if 255 == latest_progress and '1' == kwargs['mode']:
            JobUtil.add_job_status(vnfo_job_id, progress_range[1], job_status.get('statusdescription', ''),
                                   job_status.get('errorcode', ''))
        else:
            JobUtil.add_job_status(vnfo_job_id, latest_progress, job_status.get('statusdescription', ''),
                                   job_status.get('errorcode', ''))
        if job_status['status'] in ('error', 'finished'):
            return True, job_status['status']
        return False, 'processing'

    @staticmethod
    def wait_job_finish_common_call_back(vnfo_job_id, vnfm_job_id, job_status, jobs, progress_range, **kwargs):
        error_254 = False
        for job in jobs:
            progress = TerminateNsService.calc_progress_over_100(job['progress'], progress_range)
            if 254 == progress:
                logger.debug("=========254==============")
                progress = 255
                error_254 = True
            JobUtil.add_job_status(vnfo_job_id, progress, job.get('statusdescription', ""), job.get('errorcode', ""))
        latest_progress = TerminateNsService.calc_progress_over_100(job_status['progress'], progress_range)
        if 254 == latest_progress:
            logger.debug("=========254==============")
            latest_progress = 255
            error_254 = True
        JobUtil.add_job_status(vnfo_job_id, latest_progress, job_status.get('statusdescription', ""),
                               job_status.get('errorcode', ""))
        # return error_254
        if error_254:
            logger.debug("return 254")
            return True, 'error_254'
        if job_status['status'] in ('error', 'finished'):
            return True, job_status['status']
        return False, 'processing'

    @staticmethod
    def calc_progress_over_100(vnfm_progress, target_range=None):
        if target_range is None:
            target_range = [0, 100]
        progress = int(vnfm_progress)
        if progress > 100:
            return progress
        floor_progress = int(math.floor(float(target_range[1] - target_range[0]) / 100 * progress))
        target_range = floor_progress + target_range[0]
        return target_range


class DeleteNsService(object):
    def __init__(self, ns_inst_id):
        self.ns_inst_id = ns_inst_id

    def do_biz(self):
        try:
            self.delete_ns()
        except:
            logger.error(traceback.format_exc())

    def delete_ns(self):
        logger.debug("delele NSInstModel(%s)", self.ns_inst_id)
        NSInstModel.objects.filter(id=self.ns_inst_id).delete()

        logger.debug("delele InputParamMappingModel(%s)", self.ns_inst_id)
        InputParamMappingModel.objects.filter(service_id=self.ns_inst_id).delete()

        logger.debug("delele DefPkgMappingModel(%s)", self.ns_inst_id)
        DefPkgMappingModel.objects.filter(service_id=self.ns_inst_id).delete()

        logger.debug("delele ServiceBaseInfoModel(%s)", self.ns_inst_id)
        ServiceBaseInfoModel.objects.filter(service_id=self.ns_inst_id).delete()
