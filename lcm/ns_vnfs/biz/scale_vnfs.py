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
import threading
import traceback

from lcm.pub.database.models import NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.vnfmdriver import send_nf_scaling_request
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_MODEL_STATUS, JOB_TYPE, JOB_PROGRESS, JOB_ACTION
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.enum import VNF_STATUS
from lcm.ns_vnfs.biz.wait_job import wait_job_finish

logger = logging.getLogger(__name__)


class NFManualScaleService(threading.Thread):
    def __init__(self, vnf_instance_id, data):
        super(NFManualScaleService, self).__init__()
        self.vnf_instance_id = vnf_instance_id
        self.data = data
        self.job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.MANUAL_SCALE, vnf_instance_id)
        self.nf_scale_params = []
        self.m_nf_inst_id = ''
        self.vnfm_inst_id = ''

    def run(self):
        try:
            self.do_biz()
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, e.args[0])
        except Exception as ex:
            logger.error(ex.args[0])
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, 'VNF scale failed')
        finally:
            self.update_nf_status()

    def do_biz(self):
        self.update_job(1, desc='VNF scale start')
        self.update_nf_status(VNF_STATUS.SCALING)
        self.get_and_check_params()
        self.send_nf_scaling_requests()
        self.update_nf_status(VNF_STATUS.ACTIVE)
        self.update_job(100, desc='VNF scale success')

    def get_and_check_params(self):
        nf_info = NfInstModel.objects.filter(nfinstid=self.vnf_instance_id)
        if not nf_info:
            raise NSLCMException(
                'NF instance[id=%s] does not exist' %
                self.vnf_instance_id)
        logger.debug('vnfd_model = %s, vnf_instance_id = %s' %
                     (nf_info[0].vnfd_model, self.vnf_instance_id))
        nf_model = nf_info[0].vnfd_model
        self.m_nf_inst_id = nf_info[0].mnfinstid
        self.vnfm_inst_id = nf_info[0].vnfm_inst_id
        scale_vnf_data = ignore_case_get(self.data, 'scaleVnfData')
        if not scale_vnf_data:
            raise NSLCMException('scaleVnfData parameter does not exist')

        self.nf_scale_params.append({
            'type': ignore_case_get(scale_vnf_data, 'type'),
            'aspectId': ignore_case_get(scale_vnf_data, 'aspectId'),
            'numberOfSteps': ignore_case_get(scale_vnf_data, 'numberOfSteps'),
            'additionalParam': {'vnfdModel': nf_model}
        })

    def send_nf_scaling_requests(self):
        nf_scale_num = len(self.nf_scale_params)
        for i in range(nf_scale_num):
            progress_range = [10 + 80 / nf_scale_num * i,
                              10 + 80 / nf_scale_num * (i + 1)]
            self.send_nf_scaling_request(
                self.nf_scale_params[i], progress_range)

    def send_nf_scaling_request(self, scale_param, progress_range):
        req_param = json.JSONEncoder().encode(scale_param)
        rsp = send_nf_scaling_request(
            self.vnfm_inst_id, self.m_nf_inst_id, req_param)
        vnfm_job_id = ignore_case_get(rsp, 'jobId')
        ret = wait_job_finish(
            self.vnfm_inst_id,
            self.job_id,
            vnfm_job_id,
            progress_range=progress_range,
            timeout=1200,
            mode='1')
        if ret != JOB_MODEL_STATUS.FINISHED:
            raise NSLCMException("VNF scale failed")

    def update_nf_status(self, status=VNF_STATUS.ACTIVE):
        NfInstModel.objects.filter(
            nfinstid=self.vnf_instance_id).update(
            status=status)

    def update_job(self, progress, desc=''):
        JobUtil.add_job_status(self.job_id, progress, desc)
