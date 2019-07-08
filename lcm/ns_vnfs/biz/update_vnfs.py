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

import json
import logging
import threading
import traceback

from lcm.pub.database.models import NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.vnfmdriver import send_nf_operate_request
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_MODEL_STATUS, JOB_TYPE, JOB_PROGRESS, JOB_ACTION
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.enum import VNF_STATUS
from lcm.ns_vnfs.biz.wait_job import wait_job_finish

logger = logging.getLogger(__name__)


class NFOperateService(threading.Thread):
    def __init__(self, vnf_instance_id, data):
        super(NFOperateService, self).__init__()
        self.vnf_instance_id = vnf_instance_id
        self.data = data
        self.job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.HEAL, vnf_instance_id)

        self.nf_model = {}
        self.nf_additional_params = {}
        self.nf_operate_params = data
        self.m_nf_inst_id = ''
        self.vnfm_inst_id = ''

    def run(self):
        try:
            self.do_biz()
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, e.args[0])
        except:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, 'nf update fail')

    def do_biz(self):
        self.update_job(1, desc='nf update start')
        self.get_and_check_params()
        self.update_nf_status(VNF_STATUS.UPDATING)
        self.send_nf_operating_request()
        self.update_nf_status(VNF_STATUS.ACTIVE)
        self.update_job(100, desc='nf update success')

    def get_and_check_params(self):
        nf_info = NfInstModel.objects.filter(nfinstid=self.vnf_instance_id)
        if not nf_info:
            logger.error('NF instance[id=%s] does not exist' % self.vnf_instance_id)
            raise NSLCMException('NF instance[id=%s] does not exist' % self.vnf_instance_id)
        logger.debug('vnfd_model = %s, vnf_instance_id = %s' % (nf_info[0].vnfd_model, self.vnf_instance_id))
        self.nf_model = nf_info[0].vnfd_model
        self.m_nf_inst_id = nf_info[0].mnfinstid
        self.vnfm_inst_id = nf_info[0].vnfm_inst_id
        self.nf_additional_params = ignore_case_get(self.data, 'additionalParams')

    def send_nf_operating_request(self):
        req_param = json.JSONEncoder().encode(self.nf_operate_params)
        # rsp = send_nf_heal_request(self.vnfm_inst_id, self.m_nf_inst_id, req_param)
        rsp = send_nf_operate_request(self.vnfm_inst_id, self.m_nf_inst_id, req_param)
        vnfm_job_id = ignore_case_get(rsp, 'jobId')
        ret = wait_job_finish(self.vnfm_inst_id, self.job_id, vnfm_job_id, progress_range=None, timeout=1200,
                              mode='1')
        if ret != JOB_MODEL_STATUS.FINISHED:
            logger.error('[NF update] nf update failed')
            raise NSLCMException("nf update failed")

    def update_job(self, progress, desc=''):
        JobUtil.add_job_status(self.job_id, progress, desc)

    def update_nf_status(self, status):
        NfInstModel.objects.filter(nfinstid=self.vnf_instance_id).update(status=status)
