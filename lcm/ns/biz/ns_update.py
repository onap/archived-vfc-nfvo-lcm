# Copyright (c) 2018, CMCC Technologies Co., Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import threading
import traceback
import datetime
import time

from lcm.ns.enum import NS_INST_STATUS, OPERATIONAL_STATE, STOP_TYPE
from lcm.pub.database.models import JobModel, NSInstModel
from lcm.ns_vnfs.biz.update_vnfs import NFOperateService
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_MODEL_STATUS, JOB_PROGRESS
from lcm.pub.utils.values import ignore_case_get
from lcm.ns.biz.ns_lcm_op_occ import NsLcmOpOcc

logger = logging.getLogger(__name__)


class NSUpdateService(threading.Thread):
    def __init__(self, ns_instance_id, request_data, job_id):
        super(NSUpdateService, self).__init__()
        self.ns_instance_id = ns_instance_id
        self.request_data = request_data
        self.job_id = job_id
        self.occ_id = NsLcmOpOcc.create(ns_instance_id, "SCALE", "PROCESSING", False, request_data)
        self.update_type = ''
        self.operate_vnf_data = ''

    def run(self):
        try:
            self.do_biz()
        except NSLCMException as e:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, e.args[0])
            NsLcmOpOcc.update(self.occ_id, operationState="FAILED", error=e.args[0])
        except Exception as e:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, 'ns update fail')
            NsLcmOpOcc.update(self.occ_id, operationState="FAILED", error=e.args[0])

    def do_biz(self):
        self.update_job(JOB_PROGRESS.STARTED, desc='ns update start')
        self.get_and_check_params()
        self.update_ns_status(NS_INST_STATUS.UPDATING)
        self.do_update()
        self.update_ns_status(NS_INST_STATUS.ACTIVE)
        self.update_job(JOB_PROGRESS.FINISHED, desc='ns update success')
        NsLcmOpOcc.update(self.occ_id, "COMPLETED")

    def get_and_check_params(self):
        ns_info = NSInstModel.objects.filter(id=self.ns_instance_id)
        if not ns_info:
            raise NSLCMException(
                'NS [id=%s] does not exist' % self.ns_instance_id)

        self.update_type = ignore_case_get(self.request_data, "updateType")
        if not self.update_type:
            raise NSLCMException(
                'UpdateType parameter does not exist or value incorrect.')

    def do_update(self):
        if self.update_type == "OPERATE_VNF":
            self.operate_vnf_data = ignore_case_get(
                self.request_data, "operateVnfData")
            if not self.operate_vnf_data:
                raise NSLCMException(
                    'OperateVnfData does not exist or value is incorrect.')
            for vnf_update_data in self.operate_vnf_data:
                vnf_update_params = self.prepare_update_params(vnf_update_data)
                status = self.do_vnf_update(vnf_update_params, 15)
                if status is JOB_MODEL_STATUS.FINISHED:
                    logger.info(
                        'nf[%s] update handle end' % vnf_update_params.get('vnfInstanceId'))
                    self.update_job(90,
                                    desc='nf[%s] update handle end'
                                         % vnf_update_params.get('vnfInstanceId'))
                else:
                    raise NSLCMException('nf update failed')
        else:
            raise NSLCMException('Method update.')

    def do_vnf_update(self, vnf_update_params, progress):
        vnf_instance_id = vnf_update_params.get('vnfInstanceId')
        nf_service = NFOperateService(vnf_instance_id, vnf_update_params)
        nf_service.start()
        self.update_job(progress, desc='nf[%s] update handle start' % vnf_instance_id)
        status = self.wait_job_finish(nf_service.job_id)
        return status

    @staticmethod
    def prepare_update_params(vnf_data):
        vnf_instance_id = ignore_case_get(vnf_data, 'vnfInstanceId')
        if not vnf_instance_id:
            raise NSLCMException(
                'VnfInstanceId does not exist or value is incorrect.')

        change_state_to = ignore_case_get(vnf_data, 'changeStateTo')
        if not change_state_to:
            raise NSLCMException(
                'ChangeStateTo does not exist or value is incorrect.')
        graceful_stop_timeout = ''
        operational_states = ignore_case_get(change_state_to, 'OperationalStates')
        if operational_states == OPERATIONAL_STATE.STOPPED:
            stop_type = ignore_case_get(vnf_data, 'stopType')
            if stop_type == STOP_TYPE.GRACEFUL:
                graceful_stop_timeout = ignore_case_get(vnf_data, 'gracefulStopTimeout')

        result = {
            "vnfInstanceId": vnf_instance_id,
            "changeStateTo": operational_states,
            "stopType": stop_type,
            "gracefulStopTimeout": graceful_stop_timeout if graceful_stop_timeout else 0
        }
        return result

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
            elif job_result.progress > JOB_PROGRESS.FINISHED:
                return JOB_MODEL_STATUS.ERROR
            else:
                continue
        return JOB_MODEL_STATUS.TIMEOUT

    def update_job(self, progress, desc=''):
        JobUtil.add_job_status(self.job_id, progress, desc)

    def update_ns_status(self, status):
        NSInstModel.objects.filter(id=self.ns_instance_id).update(status=status)
