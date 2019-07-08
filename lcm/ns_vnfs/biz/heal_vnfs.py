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

from lcm.pub.config.config import MR_IP
from lcm.pub.config.config import MR_PORT
from lcm.pub.database.models import NfInstModel, VNFCInstModel, VmInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.vnfmdriver import send_nf_heal_request
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_MODEL_STATUS, JOB_TYPE, JOB_PROGRESS, JOB_ACTION
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.enum import VNF_STATUS
from lcm.ns_vnfs.biz.wait_job import wait_job_finish


logger = logging.getLogger(__name__)


class NFHealService(threading.Thread):
    def __init__(self, vnf_instance_id, data):
        super(NFHealService, self).__init__()
        self.vnf_instance_id = vnf_instance_id
        self.data = data
        self.job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.HEAL, vnf_instance_id)
        self.nf_model = {}
        self.nf_additional_params = {}
        self.nf_heal_params = {}
        self.m_nf_inst_id = ''
        self.vnfm_inst_id = ''

    def run(self):
        try:
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.STARTED, 'vnf heal start')
            self.get_and_check_params()
            self.update_nf_status(VNF_STATUS.HEALING)
            self.send_nf_healing_request()
            self.update_nf_status(VNF_STATUS.ACTIVE)
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.FINISHED, 'vnf heal success')
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, e.args[0])
        except:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, 'vnf heal fail')

    def get_and_check_params(self):
        nf_info = NfInstModel.objects.filter(nfinstid=self.vnf_instance_id)
        if not nf_info:
            raise NSLCMException('VNF instance[id=%s] does not exist' % self.vnf_instance_id)
        logger.debug('vnfd_model = %s, vnf_instance_id = %s' % (nf_info[0].vnfd_model, self.vnf_instance_id))
        self.nf_model = nf_info[0].vnfd_model
        self.m_nf_inst_id = nf_info[0].mnfinstid
        self.vnfm_inst_id = nf_info[0].vnfm_inst_id
        self.nf_additional_params = ignore_case_get(self.data, 'additionalParams')
        if not self.nf_additional_params:
            raise NSLCMException('additionalParams parameter does not exist or value incorrect')

        actionvminfo = ignore_case_get(self.nf_additional_params, 'actionvminfo')
        vmid = ignore_case_get(actionvminfo, 'vmid')
        self.nf_heal_params = {
            "action": "vmReset",
            "affectedvm": {
                "vmid": vmid,
                "vduid": self.get_vudId(vmid),
                "vmname": self.get_vmname(vmid)
            }
        }
        retry_count = 10
        while (retry_count > 0):
            resp = restcall.call_req('http://%s:%s/events' % (MR_IP, MR_PORT),
                                     '',
                                     '',
                                     restcall.rest_no_auth,
                                     '/test/bins/1?timeout=15000',
                                     'GET')
            if resp[2] == '200' and resp[1] != '[]':
                for message in eval(resp[1]):
                    if 'powering-off' in message:
                        action = "vmReset"
                        vm_info = json.loads(message)
                        if vmid == vm_info['instance_id']:
                            vduid = self.get_vudId(vm_info['instance_id'])
                            self.nf_heal_params = {
                                "action": action,
                                "affectedvm": {
                                    "vmid": vm_info['instance_id'],
                                    "vduid": vduid,
                                    "vmname": vm_info['display_name']
                                }
                            }
                            retry_count = -1
            retry_count = retry_count - 1

    def send_nf_healing_request(self):
        req_param = json.JSONEncoder().encode(self.nf_heal_params)
        rsp = send_nf_heal_request(self.vnfm_inst_id, self.m_nf_inst_id, req_param)
        vnfm_job_id = ignore_case_get(rsp, 'jobId')
        if not vnfm_job_id:
            return
        ret = wait_job_finish(self.vnfm_inst_id, self.job_id, vnfm_job_id, progress_range=None, timeout=1200, mode='1')
        if ret != JOB_MODEL_STATUS.FINISHED:
            logger.error('[NF heal] nf heal failed')
            raise NSLCMException("nf heal failed")

    # Gets vdu id according to the given vm id.
    def get_vudId(self, vmid):
        vnfcInstances = VNFCInstModel.objects.filter(vmid=vmid, nfinstid=self.vnf_instance_id)
        if not vnfcInstances:
            raise NSLCMException('VDU [vmid=%s, vnfInstanceId=%s] does not exist' % (vmid, self.vnf_instance_id))

        return vnfcInstances.first().vduid

    def get_vmname(self, vmid):
        vms = VmInstModel.objects.filter(resouceid=vmid)
        if not vms:
            return vmid
        return vms.first().vmname

    def update_nf_status(self, status):
        NfInstModel.objects.filter(nfinstid=self.vnf_instance_id).update(status=status)
