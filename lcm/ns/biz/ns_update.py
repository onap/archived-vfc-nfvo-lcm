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
import threading
import traceback
import datetime
import time

from lcm.ns.const import NS_INST_STATUS
from lcm.pub.database.models import JobModel, NSInstModel
from lcm.ns.vnfs.update_vnfs import NFUpdateService
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil, JOB_MODEL_STATUS
from lcm.pub.utils.values import ignore_case_get

JOB_ERROR = 255
logger = logging.getLogger(__name__)


class NSUpdateService(threading.Thread):

    def __init__(self, ns_instance_id, request_data, job_id):
        super(NSUpdateService, self).__init__()
        self.ns_instance_id = ns_instance_id
        self.request_data = request_data
        self.job_id = job_id

        self.update_type = ''
        self.operate_vnf_data = ''

    def run(self):
        try:
            self.do_biz()
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_ERROR, 'ns update fail')

    def do_biz(self):
        self.update_job(1, desc='ns update start')
        self.get_and_check_params()
        self.update_ns_status(NS_INST_STATUS.UPDATING)
        self.do_update()
        self.update_ns_status(NS_INST_STATUS.ACTIVE)
        self.update_job(100, desc='ns update success')

    def get_and_check_params(self):
        ns_info = NSInstModel.objects.filter(id=self.ns_instance_id)
        if not ns_info:
            logger.error('NS [id=%s] does not exist' % self.ns_instance_id)
            raise NSLCMException(
                'NS [id=%s] does not exist' %
                self.ns_instance_id)

        self.update_type = ignore_case_get(self.request_data, "updateType")
        if not self.update_type:
            logger.error(
                'UpdateType parameter does not exist or value is incorrect.')
            raise NSLCMException(
                'UpdateType parameter does not exist or value incorrect.')

    def do_update(self):
        if self.update_type == "OPERATE_VNF":
            self.operate_vnf_data = ignore_case_get(
                self.request_data, "operateVnfData")
            ns_update_params = self.prepare_update_params(
                self.operate_vnf_data)
            status = self.do_ns_update(ns_update_params, 15)
            if status is JOB_MODEL_STATUS.FINISHED:
                logger.info(
                    'nf[%s] update handle end' %
                    ns_update_params.get('nsInstanceId'))
                self.update_job(90,
                                desc='nf[%s] update handle end' % ns_update_params.get('nsInstanceId'))
            else:
                logger.error('nf update failed')
                raise NSLCMException('nf update failed')
        else:
            logger.error('Method update.')
            raise NSLCMException('Method update.')

    def do_ns_update(self, ns_update_params, progress):
        ns_instance_id = ns_update_params.get('nsInstanceId')
        nf_service = NFUpdateService(ns_instance_id, ns_update_params)
        nf_service.start()
        self.update_job(
            progress,
            desc='nf[%s] update handle start' %
            ns_instance_id)
        status = self.wait_job_finish(nf_service.job_id)
        return status

    @staticmethod
    def prepare_update_params(vnf_data):
        ns_instance_id = ignore_case_get(vnf_data, 'nsInstanceId')
        if not ns_instance_id:
            logger.error('NsInstanceId does not exist or value is incorrect.')
            raise NSLCMException(
                'NsInstanceId does not exist or value is incorrect.')

        change_state_to = ignore_case_get(vnf_data, 'changeStateTo')
        if not change_state_to:
            logger.error('ChangeStateTo does not exist or value is incorrect.')
            raise NSLCMException(
                'ChangeStateTo does not exist or value is incorrect.')

        stop_type = ''
        graceful_stop_timeout = ''
        operational_states = ignore_case_get(
            change_state_to, 'OperationalStates')
        if operational_states == "STARTED":
            pass
        elif operational_states == "STOPPED":
            stop_type = ignore_case_get(vnf_data, 'stopType')
            if stop_type == "GRACEFUL":
                graceful_stop_timeout = ignore_case_get(
                    vnf_data, 'gracefulStopTimeout')
                if not graceful_stop_timeout:
                    logger.error(
                        'gracefulStopTimeout does not exist or value is incorrect.')
                    raise NSLCMException(
                        'gracefulStopTimeout does not exist or value is incorrect.')
            elif stop_type == "FORCEFUL":
                graceful_stop_timeout = ''
            else:
                logger.error('StopType should be GRACEFUL or FORCEFUL')
                raise NSLCMException('StopType should be GRACEFUL or FORCEFUL')
        else:
            logger.error('OperationalStates should be started or stopped')
            raise NSLCMException(
                'OperationalStates should be started or stopped')

        result = {
            "nsInstanceId": ns_instance_id,
            "changeStateTo": {
                "OperationalStates": operational_states
            },
            "stopType": stop_type,
            "gracefulStopTimeout": graceful_stop_timeout
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
        NSInstModel.objects.filter(
            id=self.ns_instance_id).update(
                status=status)
