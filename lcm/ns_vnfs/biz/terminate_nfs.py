# Copyright 2016-2018 ZTE Corporation.
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

from lcm.pub.config.config import REPORT_TO_AAI
from lcm.pub.database.models import NfInstModel, VmInstModel, OOFDataModel, PortInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi import resmgr
from lcm.pub.msapi.aai import query_vnf_aai, delete_vnf_aai, query_vserver_aai, delete_vserver_aai
from lcm.pub.msapi.extsys import split_vim_to_owner_region, get_vim_by_id
from lcm.pub.msapi.vnfmdriver import send_nf_terminate_request
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_MODEL_STATUS
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.const import NFVO_VNF_INST_TIMEOUT_SECOND
from lcm.ns_vnfs.enum import VNF_STATUS, INST_TYPE
from lcm.ns_vnfs.biz.wait_job import wait_job_finish
from lcm.ns_vnfs.biz.subscribe import SubscriptionDeletion

logger = logging.getLogger(__name__)


class TerminateVnfs(threading.Thread):
    def __init__(self, data, vnf_inst_id, job_id):
        threading.Thread.__init__(self)
        self.vnf_inst_id = vnf_inst_id
        self.job_id = job_id
        self.vnfm_inst_id = ''
        self.vnf_uuid = ''
        self.vnfm_job_id = ''
        self.terminationType = data['terminationType']
        self.gracefulTerminationTimeout = data['gracefulTerminationTimeout']
        if not self.gracefulTerminationTimeout:
            self.gracefulTerminationTimeout = 120
        else:
            self.gracefulTerminationTimeout = int(self.gracefulTerminationTimeout)

        self.initdata()

    def run(self):
        try:
            self.check_nf_valid()
            self.send_nf_terminate_to_vnfmDriver()
            self.wait_vnfm_job_finish()
            self.send_terminate_vnf_to_resMgr()
            if REPORT_TO_AAI:
                self.delete_vserver_in_aai()
                self.delete_vnf_in_aai()
            self.delete_subscription()
            self.delete_data_from_db()
        except NSLCMException as e:
            self.set_job_err(e.args[0])
        except Exception as ex:
            logger.error(traceback.format_exc())
            self.set_job_err(ex.args[0])

    def set_vnf_status(self, vnf_inst_info):
        vnf_status = vnf_inst_info.status
        if (vnf_status == VNF_STATUS.TERMINATING):
            logger.info('[VNF terminate] VNF is dealing by other application,try again later.')
            raise NSLCMException('[VNF terminate] VNF is dealing by other application,try again later.')
        else:
            vnf_inst_info.status = VNF_STATUS.TERMINATING
            vnf_inst_info.save()

    def get_vnf_inst(self):
        vnf_inst = NfInstModel.objects.filter(nfinstid=self.vnf_inst_id)
        if not vnf_inst.exists():
            logger.warning('[VNF terminate] Vnf terminate [%s] does not exist.' % self.vnf_inst_id)
            return None
        return vnf_inst[0]

    def add_progress(self, progress, status_decs, error_code=""):
        JobUtil.add_job_status(self.job_id, progress, status_decs, error_code)

    def initdata(self):
        vnf_inst_info = self.get_vnf_inst()
        if not vnf_inst_info:
            self.add_progress(100, "TERM_VNF_NOT_EXIST_SUCCESS", "finished")
            return None
        self.add_progress(2, "GET_VNF_INST_SUCCESS")
        self.vnfm_inst_id = vnf_inst_info.vnfm_inst_id
        self.vnf_uuid = vnf_inst_info.mnfinstid
        if not self.vnf_uuid:
            self.add_progress(100, "TERM_VNF_NOT_EXIST_SUCCESS", "finished")

    def check_nf_valid(self):
        vnf_inst = NfInstModel.objects.filter(nfinstid=self.vnf_inst_id)
        if not vnf_inst.exists():
            logger.warning('[VNF terminate] Vnf instance [%s] is not exist.' % self.vnf_inst_id)
            raise NSLCMException('[VNF terminate] Vnf instance is not exist.')
        if not vnf_inst:
            self.add_progress(100, "TERM_VNF_NOT_EXIST_SUCCESS", "finished")
            raise NSLCMException('[VNF terminate] Vnf instance is not exist.')
        self.set_vnf_status(vnf_inst[0])

    def set_job_err(self, error_msg):
        logger.error('VNF Terminate failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.vnf_inst_id).update(status=VNF_STATUS.FAILED)
        JobUtil.add_job_status(self.job_id, 255, 'VNF Terminate failed, detail message: %s' % error_msg, 0)

    def send_nf_terminate_to_vnfmDriver(self):
        req_param = json.JSONEncoder().encode({
            'terminationType': self.terminationType,
            'gracefulTerminationTimeout': self.gracefulTerminationTimeout})
        rsp = send_nf_terminate_request(self.vnfm_inst_id, self.vnf_uuid, req_param)
        self.vnfm_job_id = ignore_case_get(rsp, 'jobId')

    def send_terminate_vnf_to_resMgr(self):
        resmgr.terminate_vnf(self.vnf_inst_id)

    def wait_vnfm_job_finish(self):
        if not self.vnfm_job_id:
            logger.warn("No Job, need not wait")
            return
        ret = wait_job_finish(vnfm_id=self.vnfm_inst_id,
                              vnfo_job_id=self.job_id,
                              vnfm_job_id=self.vnfm_job_id,
                              progress_range=[10, 90],
                              timeout=NFVO_VNF_INST_TIMEOUT_SECOND)

        if ret != JOB_MODEL_STATUS.FINISHED:
            logger.error('VNF terminate failed on VNFM side.')
            raise NSLCMException('VNF terminate failed on VNFM side.')

    def delete_subscription(self):
        try:
            SubscriptionDeletion(self.vnfm_inst_id, self.vnf_uuid).do_biz()
        except Exception as e:
            logger.error("delete_subscription failed: %s", e.args[0])

    def delete_data_from_db(self):
        PortInstModel.objects.filter(instid=self.vnf_inst_id).delete()
        NfInstModel.objects.filter(nfinstid=self.vnf_inst_id).delete()
        VmInstModel.objects.filter(instid=self.vnf_inst_id).delete()
        OOFDataModel.objects.filter(service_resource_id=self.vnf_inst_id).delete()
        JobUtil.add_job_status(self.job_id, 100, 'vnf terminate success', 0)

    def delete_vnf_in_aai(self):
        logger.debug("TerminateVnfs::delete_vnf_in_aai::delete vnf instance[%s] in aai." % self.vnf_inst_id)
        try:
            # query vnf instance in aai, get resource_version
            customer_info = query_vnf_aai(self.vnf_inst_id)
            resource_version = customer_info["resource-version"]

            # delete vnf instance from aai
            resp_data, resp_status = delete_vnf_aai(self.vnf_inst_id, resource_version)
            logger.debug(
                "Success to delete vnf[%s] from aai, resp_status: [%s]." % (self.vnf_inst_id, resp_status))
        except NSLCMException as e:
            logger.debug("Fail to delete vnf from aai[%s], detail message: %s" % (self.vnf_inst_id, e.args[0]))
        except:
            logger.error(traceback.format_exc())

    def delete_vserver_in_aai(self):
        logger.debug("delete_vserver_in_aai start!")
        try:
            vm_inst_infos = VmInstModel.objects.filter(insttype=INST_TYPE.VNF, instid=self.vnf_inst_id)
            for vm_inst_info in vm_inst_infos:
                vserver_id = vm_inst_info.resouceid
                vim_id = vm_inst_info.vimid
                cloud_owner, cloud_region_id = split_vim_to_owner_region(vim_id)
                # query vim_info from aai, get tenant
                vim_info = get_vim_by_id({"cloud_owner": cloud_owner, 'cloud_regionid': cloud_region_id})
                tenant_id = vim_info["tenantId"]

                # query vserver instance in aai, get resource_version
                vserver_info = query_vserver_aai(cloud_owner, cloud_region_id, tenant_id, vserver_id)
                resource_version = vserver_info["resource-version"]

                # delete vserver instance from aai
                resp_data, resp_status = delete_vserver_aai(cloud_owner, cloud_region_id,
                                                            tenant_id, vserver_id, resource_version)
                logger.debug(
                    "Success to delete vserver instance[%s] from aai, resp_status: [%s]." %
                    (vserver_id, resp_status))
            logger.debug("delete_vserver_in_aai end!")
        except NSLCMException as e:
            logger.debug("Fail to delete vserver from aai, detail message: %s" % e.args[0])
        except:
            logger.error(traceback.format_exc())
