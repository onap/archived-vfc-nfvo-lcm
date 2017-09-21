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

import json
import logging
import threading
import traceback

from lcm.ns.vnfs.const import VNF_STATUS
from lcm.ns.vnfs.wait_job import wait_job_finish
from lcm.pub.database.models import NfInstModel, VNFCInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.vnfmdriver import send_nf_heal_request
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE, JOB_MODEL_STATUS
from lcm.pub.utils.values import ignore_case_get

JOB_ERROR = 255

logger = logging.getLogger(__name__)


class NFHealService(threading.Thread):
    def __init__(self, vnf_instance_id, data):
        super(NFHealService, self).__init__()
        self.vnf_instance_id = vnf_instance_id
        self.data = data
        self.job_id = JobUtil.create_job("NF", JOB_TYPE.HEAL_VNF, vnf_instance_id)

        self.nf_model = {}
        self.nf_additional_params = {}
        self.nf_heal_params = {}
        self.m_nf_inst_id = ''
        self.vnfm_inst_id = ''

    def run(self):
        try:
            self.do_biz()
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_ERROR, e.message)
        except:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_ERROR, 'nf heal fail')

    def do_biz(self):
        self.update_job(1, desc='nf heal start')
        self.get_and_check_params()
        self.update_nf_status(VNF_STATUS.HEALING)
        self.send_nf_healing_request()
        self.update_nf_status(VNF_STATUS.ACTIVE)
        self.update_job(100, desc='nf heal success')

    def get_and_check_params(self):
        nf_info = NfInstModel.objects.filter(nfinstid=self.vnf_instance_id)
        if not nf_info:
            logger.error('NF instance[id=%s] does not exist' % self.vnf_instance_id)
            raise NSLCMException('NF instance[id=%s] does not exist' % self.vnf_instance_id)
        logger.debug('vnfd_model = %s, vnf_instance_id = %s' % (nf_info[0].vnfd_model, self.vnf_instance_id))
        self.nf_model = json.loads(nf_info[0].vnfd_model)
        self.m_nf_inst_id = nf_info[0].mnfinstid
        self.vnfm_inst_id = nf_info[0].vnfm_inst_id
        self.nf_additional_params = ignore_case_get(self.data, 'additionalParams')

        if not self.nf_additional_params:
            logger.error('additionalParams parameter does not exist or value incorrect')
            raise NSLCMException('additionalParams parameter does not exist or value incorrect')

        action = ignore_case_get(self.nf_additional_params, 'action')
        if action is "restartvm":
            action = "vmReset"

        actionvminfo = ignore_case_get(self.nf_additional_params, 'actionvminfo')
        vmid = ignore_case_get(actionvminfo, 'vmid')
        vmname = ignore_case_get(actionvminfo, 'vmname')


        # Gets vduid
        vduid = self.get_vudId(vmid, self.vnf_instance_id)

        self.nf_heal_params = {
            "action": action,
            "affectedvm": {
                "vmid": vmid,
                "vduid": vduid,
                "vmname": vmname,
            }
        }

    def send_nf_healing_request(self):
        req_param = json.JSONEncoder().encode(self.nf_heal_params)
        rsp = send_nf_heal_request(self.vnfm_inst_id, self.m_nf_inst_id, req_param)
        vnfm_job_id = ignore_case_get(rsp, 'jobId')
        ret = wait_job_finish(self.vnfm_inst_id, self.job_id, vnfm_job_id, progress_range=None, timeout=1200,
                              mode='1')
        if ret != JOB_MODEL_STATUS.FINISHED:
            logger.error('[NF heal] nf heal failed')
            raise NSLCMException("nf heal failed")

    # Gets vdu id according to the given vm id.
    def get_vudId(self, vmid):
        vnfcInstances = VNFCInstModel.objects.filter(vmid = vmid, nfinstid=self.vnf_instance_id)
        if not vnfcInstances or len(vnfcInstances) > 1:
            raise NSLCMException('VDU [vmid=%s, vnfInstanceId=%s] does not exist' % (vmid, self.vnf_instance_id))

        vnfcInstance = VNFCInstModel.objects.filter(vmid = vmid,nfinstid=self.vnf_instance_id).first()
        return vnfcInstance.vduid

    def update_job(self, progress, desc=''):
        JobUtil.add_job_status(self.job_id, progress, desc)

    def update_nf_status(self, status):
        NfInstModel.objects.filter(nfinstid=self.vnf_instance_id).update(status=status)
