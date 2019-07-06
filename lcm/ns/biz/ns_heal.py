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

import datetime
import logging
import threading
import time
import traceback

from lcm.ns.enum import NS_INST_STATUS
from lcm.pub.database.models import JobModel, NSInstModel, NfInstModel, VNFCInstModel, VmInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_MODEL_STATUS, JOB_PROGRESS
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.biz.heal_vnfs import NFHealService
from lcm.ns.biz.ns_lcm_op_occ import NsLcmOpOcc

logger = logging.getLogger(__name__)


class NSHealService(threading.Thread):
    def __init__(self, ns_instance_id, request_data, job_id):
        super(NSHealService, self).__init__()
        self.ns_instance_id = ns_instance_id
        self.request_data = request_data
        self.job_id = job_id
        self.occ_id = NsLcmOpOcc.create(ns_instance_id, "HEAL", "PROCESSING", False, request_data)
        self.heal_vnf_data = ''
        self.heal_ns_data = ''

    def run(self):
        try:
            self.do_biz()
        except NSLCMException as e:
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, e.args[0])
            NsLcmOpOcc.update(self.occ_id, operationState="FAILED", error=e.args[0])
        except Exception as e:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.ERROR, 'ns heal fail')
            NsLcmOpOcc.update(self.occ_id, operationState="FAILED", error=e.args[0])

    def do_biz(self):
        self.update_job(1, desc='ns heal start')
        self.get_and_check_params()
        self.update_ns_status(NS_INST_STATUS.HEALING)
        self.do_heal()
        self.update_ns_status(NS_INST_STATUS.ACTIVE)
        self.update_job(100, desc='ns heal success')
        NsLcmOpOcc.update(self.occ_id, "COMPLETED")

    def get_and_check_params(self):
        ns_info = NSInstModel.objects.filter(id=self.ns_instance_id)
        if not ns_info:
            errmsg = 'NS [id=%s] does not exist' % self.ns_instance_id
            raise NSLCMException(errmsg)

        self.heal_ns_data = ignore_case_get(self.request_data, 'healNsData')
        self.heal_vnf_data = ignore_case_get(self.request_data, 'healVnfData')

        if self.heal_ns_data and self.heal_vnf_data:
            errmsg = 'healNsData and healVnfData can not exist together'
            logger.error(errmsg)
            raise NSLCMException(errmsg)

        if not self.heal_ns_data and not self.heal_vnf_data:
            errmsg = 'healNsData and healVnfData parameters does not exist or value is incorrect.'
            raise NSLCMException(errmsg)

    def do_heal(self):
        if self.heal_vnf_data:
            vnf_heal_params = self.prepare_vnf_heal_params(self.heal_vnf_data)
            status = self.do_vnf_or_ns_heal(vnf_heal_params, 15)
            if status is JOB_MODEL_STATUS.FINISHED:
                logger.info('nf[%s] heal handle end' % vnf_heal_params.get('vnfInstanceId'))
                self.update_job(90, desc='nf[%s] heal handle end' % vnf_heal_params.get('vnfInstanceId'))
            else:
                errmsg = 'nf heal failed'
                raise NSLCMException(errmsg)
        else:
            ns_heal_params = self.prepare_ns_heal_params(self.heal_ns_data)
            for ns_heal_param in ns_heal_params:
                status = self.do_vnf_or_ns_heal(ns_heal_param, 15)
                if status is JOB_MODEL_STATUS.FINISHED:
                    logger.info('nf[%s] heal handle end' % ns_heal_param.get('vnfInstanceId'))
                    self.update_job(90, desc='nf[%s] heal handle end' % ns_heal_param.get('vnfInstanceId'))
                else:
                    errmsg = 'nf heal failed'
                    logger.error(errmsg)
                    raise NSLCMException(errmsg)

    def do_vnf_or_ns_heal(self, heal_param, progress):
        instance_id = heal_param.get('vnfInstanceId')
        nf_service = NFHealService(instance_id, heal_param)
        nf_service.start()
        self.update_job(
            progress, desc='nf[%s] heal handle start' % instance_id)
        status = self.wait_job_finish(nf_service.job_id)
        return status

    def prepare_ns_heal_params(self, ns_data):
        degree_healing = ignore_case_get(ns_data, 'degreeHealing')
        if not degree_healing:
            errmsg = 'degreeHealing does not exist.'
            logger.error(errmsg)
            raise NSLCMException(errmsg)
        ns_instance_id = self.ns_instance_id
        cause = 'vm is down'
        # action = ignore_case_get(ns_data, 'actionsHealing')
        if degree_healing == "HEAL_RESTORE":
            ns_inst_infos = NfInstModel.objects.filter(ns_inst_id=self.ns_instance_id)
            if not ns_inst_infos.exists():
                raise NSLCMException('NSInsts(%s) does not exist' % self.ns_instance_id)
            result_arr = []
            for ns_inst_info in ns_inst_infos:
                vnfc_insts = VNFCInstModel.objects.filter(nfinstid=ns_inst_info.nfinstid)
                # If a condition is not met, will it all terminate?
                if not vnfc_insts.exists():
                    raise NSLCMException('vnfcinsts(%s) does not exist' % ns_inst_info.nfinstid)
                for vnfc_inst in vnfc_insts:
                    vm_id = vnfc_inst.vmid
                    vdu_id = vnfc_inst.vduid
                    vm_inst_info = VmInstModel.objects.filter(vmid=vm_id)
                    if not vm_inst_info.exists():
                        raise NSLCMException('vminstinfo(%s) does not exist' % vm_id)
                    vm_name = vm_inst_info[0].vmname

                    result = {
                        "vnfInstanceId": ns_instance_id,
                        "cause": cause,
                        "additionalParams": {
                            "action": "restartvm",
                            "actionvminfo": {
                                "vmid": vm_id,
                                "vduid": vdu_id,
                                "vmname": vm_name
                            }
                        }
                    }
                    result_arr.append(result)
            return result_arr
        else:
            errmsg = 'The degree of healing dose not exist or value is incorrect.'
            logger.error(errmsg)
            raise NSLCMException(errmsg)

    def prepare_vnf_heal_params(self, vnf_data):
        vnf_instance_id = ignore_case_get(vnf_data, 'vnfInstanceId')
        if not vnf_instance_id:
            errmsg = 'vnfinstanceid does not exist or value is incorrect.'
            logger.error(errmsg)
            raise NSLCMException(errmsg)
        cause = ignore_case_get(vnf_data, 'cause')
        additional_params = ignore_case_get(vnf_data, 'additionalParams')
        action = ignore_case_get(additional_params, 'action')
        action_vm_info = ignore_case_get(additional_params, 'actionvminfo')
        vm_id = ignore_case_get(action_vm_info, 'vmid')
        vdu_id = ignore_case_get(action_vm_info, 'vduid')
        vm_name = ignore_case_get(action_vm_info, 'vmname')

        result = {
            "vnfInstanceId": vnf_instance_id,
            "cause": cause,
            "additionalParams": {
                "action": action,
                "actionvminfo": {
                    "vmid": vm_id,
                    "vduid": vdu_id,
                    "vmname": vm_name
                }
            }
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
        NSInstModel.objects.filter(
            id=self.ns_instance_id).update(status=status)
