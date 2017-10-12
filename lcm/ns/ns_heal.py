# Copyright 2017 Intel Corporation.
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
import threading
import traceback
import datetime
import time

from lcm.ns.const import NS_INST_STATUS
from lcm.pub.database.models import JobModel, NSInstModel
from lcm.ns.vnfs.heal_vnfs import NFHealService
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil, JOB_MODEL_STATUS
from lcm.pub.utils.values import ignore_case_get

JOB_ERROR = 255
logger = logging.getLogger(__name__)


class NSHealService(threading.Thread):
    def __init__(self, ns_instance_id, request_data, job_id):
        super(NSHealService, self).__init__()
        self.ns_instance_id = ns_instance_id
        self.request_data = request_data
        self.job_id = job_id

        self.heal_vnf_data = ''

    def run(self):
        try:
            self.do_biz()
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_ERROR, 'ns heal fail')

    def do_biz(self):
        self.update_job(1, desc='ns heal start')
        self.get_and_check_params()
        self.update_ns_status(NS_INST_STATUS.HEALING)
        self.do_vnfs_heal()
        self.update_ns_status(NS_INST_STATUS.ACTIVE)
        self.update_job(100, desc='ns heal success')

    def get_and_check_params(self):
        ns_info = NSInstModel.objects.filter(id=self.ns_instance_id)
        if not ns_info:
            logger.error('NS [id=%s] does not exist' % self.ns_instance_id)
            raise NSLCMException('NS [id=%s] does not exist' % self.ns_instance_id)
        self.heal_vnf_data = ignore_case_get(self.request_data, 'healVnfData')
        if not self.heal_vnf_data:
            logger.error('healVnfData parameter does not exist or value is incorrect.')
            raise NSLCMException('healVnfData parameter does not exist or value incorrect.')

    def do_vnfs_heal(self):
        vnf_heal_params = self.prepare_vnf_heal_params(self.heal_vnf_data)
        # count = len(self.heal_vnf_data)
        # Only one VNF is supported to heal.
        status = self.do_vnf_heal(vnf_heal_params, 15)
        if status is JOB_MODEL_STATUS.FINISHED:
            logger.info('nf[%s] heal handle end' % vnf_heal_params.get('vnfInstanceId'))
            self.update_job(90,
                            desc='nf[%s] heal handle end' % vnf_heal_params.get('vnfInstanceId'))
        else:
            logger.error('nf heal failed')
            raise NSLCMException('nf heal failed')

    def do_vnf_heal(self, vnf_heal_params, progress):
        vnf_instance_id = vnf_heal_params.get('vnfInstanceId')
        nf_service = NFHealService(vnf_instance_id, vnf_heal_params)
        nf_service.start()
        self.update_job(progress, desc='nf[%s] heal handle start' % vnf_instance_id)
        status = self.wait_job_finish(nf_service.job_id)
        return status

    def prepare_vnf_heal_params(self, vnf_data):
        vnf_instance_id = ignore_case_get(vnf_data, 'vnfInstanceId')
        cause = ignore_case_get(vnf_data, "cause")
        additional_params = ignore_case_get(vnf_data, "additionalParams")
        result = {
            "vnfInstanceId": vnf_instance_id,
            "cause": cause,
            "additionalParams": additional_params
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
            if job_result.progress == 100:
                return JOB_MODEL_STATUS.FINISHED
            elif job_result.progress > 100:
                return JOB_MODEL_STATUS.ERROR
            else:
                continue
        return JOB_MODEL_STATUS.TIMEOUT

    def update_job(self, progress, desc=''):
        JobUtil.add_job_status(self.job_id, progress, desc)

    def update_ns_status(self, status):
        NSInstModel.objects.filter(id=self.ns_instance_id).update(status=status)
