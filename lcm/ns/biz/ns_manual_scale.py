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
import datetime
import logging
import threading
import time
import traceback

from lcm.ns.biz.scaleaspect import get_scale_vnf_data_info_list
from lcm.ns.enum import NS_INST_STATUS
from lcm.pub.database.models import JobModel, NSInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_MODEL_STATUS, JOB_PROGRESS
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.biz.scale_vnfs import NFManualScaleService
from lcm.ns.biz.ns_lcm_op_occ import NsLcmOpOcc

JOB_ERROR = 255
SCALE_TYPE = ("SCALE_NS", "SCALE_VNF")
logger = logging.getLogger(__name__)


class NSManualScaleService(threading.Thread):
    def __init__(self, ns_instance_id, request_data, job_id):
        super(NSManualScaleService, self).__init__()
        self.ns_instance_id = ns_instance_id
        self.request_data = request_data
        self.job_id = job_id
        self.occ_id = NsLcmOpOcc.create(ns_instance_id, "SCALE", "PROCESSING", False, request_data)
        self.scale_vnf_data = ''

    def run(self):
        try:
            self.do_biz()
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, e.args[0])
            NsLcmOpOcc.update(self.occ_id, operationState="FAILED", error=e.args[0])
        except Exception as e:
            logger.error(e.args[0])
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, 'ns scale fail')
            NsLcmOpOcc.update(self.occ_id, operationState="FAILED", error=e.args[0])
        finally:
            self.update_ns_status(NS_INST_STATUS.ACTIVE)

    def do_biz(self):
        self.update_job(1, desc='ns scale start')
        self.update_ns_status(NS_INST_STATUS.SCALING)
        self.check_and_set_params()
        self.do_vnfs_scale()
        self.update_job(JOB_PROGRESS.FINISHED, desc='ns scale success')
        NsLcmOpOcc.update(self.occ_id, "COMPLETED")

    def check_and_set_params(self):
        scale_type = ignore_case_get(self.request_data, 'scaleType')
        if scale_type != SCALE_TYPE[0]:
            raise NSLCMException('scaleType should be SCALE_NS.')

        scale_ns_data = ignore_case_get(self.request_data, 'scaleNsData')
        self.scale_vnf_data = get_scale_vnf_data_info_list(
            scale_ns_data, self.ns_instance_id)
        logger.debug('scale_vnf_data = %s' % self.scale_vnf_data)
        if not self.scale_vnf_data:
            raise NSLCMException('Failed to get scaleVnfData parameter')

    def do_vnfs_scale(self):
        for i in range(len(self.scale_vnf_data)):
            vnf_scale_params = self.prepare_vnf_scale_params(
                self.scale_vnf_data[i])
            count = len(self.scale_vnf_data)
            progress_range = [11 + 80 / count * i, 10 + 80 / count * (i + 1)]
            status = self.do_vnf_scale(vnf_scale_params, progress_range)
            if status is JOB_MODEL_STATUS.FINISHED:
                logger.info(
                    'nf[%s] scale handle end' %
                    vnf_scale_params.get('vnfInstanceId'))
                self.update_job(
                    progress_range[1],
                    desc='nf[%s] scale handle end' %
                    vnf_scale_params.get('vnfInstanceId'))
            else:
                raise NSLCMException('VNF scale failed')

    def prepare_vnf_scale_params(self, vnf_data):
        return {
            "vnfInstanceId": ignore_case_get(vnf_data, 'vnfInstanceId'),
            "scaleVnfData": ignore_case_get(vnf_data, 'scaleByStepData'),
            "nsInstanceId": self.ns_instance_id
        }

    def do_vnf_scale(self, vnf_scale_params, progress_range):
        nf_inst_id = vnf_scale_params.get('vnfInstanceId')
        nf_service = NFManualScaleService(nf_inst_id, vnf_scale_params)
        nf_service.start()
        self.update_job(
            progress_range[0],
            desc='nf[%s] scale handle start' %
            nf_inst_id)
        status = self.wait_job_finish(nf_service.job_id)
        return status

    @staticmethod
    def wait_job_finish(sub_job_id, timeout=3600):
        query_interval = 2
        start_time = end_time = datetime.datetime.now()
        while (end_time - start_time).seconds < timeout:
            job_result = JobModel.objects.get(jobid=sub_job_id)
            time.sleep(query_interval)
            end_time = datetime.datetime.now()
            if job_result.progress == JOB_PROGRESS.FINISHED:
                return JOB_MODEL_STATUS.FINISHED
            if job_result.progress > JOB_PROGRESS.FINISHED:
                return JOB_MODEL_STATUS.ERROR
        return JOB_MODEL_STATUS.TIMEOUT

    def update_job(self, progress, desc=''):
        JobUtil.add_job_status(self.job_id, progress, desc)

    def update_ns_status(self, status):
        NSInstModel.objects.filter(
            id=self.ns_instance_id).update(
            status=status)
