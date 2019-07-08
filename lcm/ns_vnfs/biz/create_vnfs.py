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
from threading import Thread
import traceback
import uuid

from lcm.ns.enum import OWNER_TYPE
from lcm.ns_vnfs.const import NFVO_VNF_INST_TIMEOUT_SECOND
from lcm.ns_vnfs.biz.subscribe import SubscriptionCreation
from lcm.ns_vnfs.biz.wait_job import wait_job_finish
from lcm.ns_vnfs.enum import VNF_STATUS, INST_TYPE
from lcm.pub.config.config import REPORT_TO_AAI
from lcm.pub.config.config import REG_TO_MSB_REG_PARAM, OOF_BASE_URL, OOF_PASSWD, OOF_USER
from lcm.pub.config.config import CUST_NAME, CUST_LAT, CUST_LONG
from lcm.pub.database.models import NfInstModel, NSInstModel, VmInstModel, VNFFGInstModel, VLInstModel, OOFDataModel
from lcm.jobs.enum import JOB_MODEL_STATUS, JOB_ACTION, JOB_PROGRESS, JOB_ERROR_CODE, JOB_TYPE
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.aai import create_vnf_aai
from lcm.pub.msapi.extsys import get_vnfm_by_id
from lcm.pub.msapi.resmgr import create_vnf, create_vnf_creation_info
from lcm.pub.msapi.sdc_run_catalog import query_vnfpackage_by_id
from lcm.pub.msapi.vnfmdriver import send_nf_init_request
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil
# from lcm.pub.utils.share_lock import do_biz_with_share_lock
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get


logger = logging.getLogger(__name__)


def prepare_create_params():
    nf_inst_id = str(uuid.uuid4())
    NfInstModel(
        nfinstid=nf_inst_id,
        status=VNF_STATUS.INSTANTIATING,
        create_time=now_time(),
        lastuptime=now_time()
    ).save()
    job_id = JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.CREATE, nf_inst_id)
    JobUtil.add_job_status(job_id, JOB_PROGRESS.STARTED, 'create vnf record in database.', JOB_ERROR_CODE.NO_ERROR)
    return nf_inst_id, job_id


class CreateVnfs(Thread):
    def __init__(self, data, nf_inst_id, job_id):
        super(CreateVnfs, self).__init__()
        self.data = data
        self.nf_inst_id = nf_inst_id
        self.job_id = job_id
        self.ns_inst_id = ''
        self.vnf_id = ''
        self.vnfd_id = ''
        self.ns_inst_name = ''
        self.nsd_model = ''
        self.vnfd_model = ''
        self.vnf_inst_name = ''
        self.vnfm_inst_id = ''
        self.inputs = ''
        self.nf_package_info = ''
        self.vnfm_nf_inst_id = ''
        self.vnfm_job_id = ''
        self.vnfm_inst_name = ''
        self.vim_id = ''

    def run(self):
        try:
            self.get_params()
            self.check_nf_name_exist()
            self.get_vnfd_id()
            if REPORT_TO_AAI:
                self.create_vnf_in_aai()
            self.check_nf_package_valid()
            self.send_nf_init_request_to_vnfm()
            self.send_homing_request_to_OOF()
            self.send_get_vnfm_request_to_extsys()
            self.send_create_vnf_request_to_resmgr()
            self.wait_vnfm_job_finish()
            self.subscribe()
            self.write_vnf_creation_info()
            self.save_info_to_db()
            JobUtil.add_job_status(self.job_id, JOB_PROGRESS.FINISHED, 'vnf instantiation success', JOB_ERROR_CODE.NO_ERROR)
        except NSLCMException as e:
            self.vnf_inst_failed_handle(e.args[0])
        except Exception:
            logger.error(traceback.format_exc())
            self.vnf_inst_failed_handle('unexpected exception')

    def get_params(self):
        self.ns_inst_id = self.data['ns_instance_id']
        vnf_index = int(float(self.data['vnf_index'])) - 1
        additional_vnf_info = self.data['additional_param_for_vnf'][vnf_index]
        self.vnf_id = ignore_case_get(additional_vnf_info, 'vnfProfileId')
        additional_param = ignore_case_get(additional_vnf_info, 'additionalParam')
        self.properties = ignore_case_get(additional_param, 'properties')
        self.vnfm_inst_id = ignore_case_get(additional_param, 'vnfmInstanceId')
        para = ignore_case_get(additional_param, 'inputs')
        self.inputs = json.loads(para) if isinstance(para, str) else para
        self.vim_id = ignore_case_get(additional_param, 'vimId')
        self.vnfd_id = ignore_case_get(additional_param, 'vnfdId')

    def check_nf_name_exist(self):
        is_exist = NfInstModel.objects.filter(nf_name=self.vnf_inst_name).exists()
        if is_exist:
            raise NSLCMException('The name of VNF instance already exists.')

    def get_vnfd_id(self):
        if self.vnfd_id:
            logger.debug("need not get vnfd_id")
            self.nsd_model = {'vnfs': [], 'vls': [], 'vnffgs': []}
            self.vnf_inst_name = self.vnfd_id + str(uuid.uuid4())
            self.vnf_inst_name = self.vnf_inst_name[:30]
            return
        ns_inst_info = NSInstModel.objects.get(id=self.ns_inst_id)
        self.ns_inst_name = ns_inst_info.name
        self.nsd_model = json.loads(ns_inst_info.nsd_model)
        for vnf_info in self.nsd_model['vnfs']:
            if self.vnf_id == vnf_info['vnf_id']:
                self.vnfd_id = vnf_info['properties']['id']
                if 'name' not in vnf_info['properties']:
                    # HW vnf instance name must start with alphabet
                    self.vnf_inst_name = 'vnf' + self.vnfd_id[:10] + str(uuid.uuid4())
                else:
                    self.vnf_inst_name = vnf_info['properties']['name'] + str(uuid.uuid4())
                self.vnf_inst_name = self.vnf_inst_name[:30]
                self.vnf_inst_name = self.vnf_inst_name.replace("-", "_")
                return
        raise NSLCMException('Can not found vnf in nsd model')

    def check_nf_package_valid(self):
        nfpackage_info = query_vnfpackage_by_id(self.vnfd_id)
        self.nf_package_info = nfpackage_info["packageInfo"]
        self.vnfd_model = ignore_case_get(self.nf_package_info, "vnfdModel")
        self.vnfd_model = json.loads(self.vnfd_model)

    def get_virtual_link_info(self, vnf_id):
        virtual_link_list, ext_virtual_link = [], []
        for vnf_info in self.nsd_model['vnfs']:
            if vnf_info['vnf_id'] != vnf_id:
                continue
            for network_info in vnf_info['networks']:
                vl_instance = VLInstModel.objects.get(
                    vldid=network_info['vl_id'],
                    ownertype=OWNER_TYPE.NS,
                    ownerid=self.ns_inst_id)
                vl_instance_id = vl_instance.vlinstanceid
                network_name, subnet_name = self.get_network_info_of_vl(network_info['vl_id'])
                virtual_link_list.append({
                    'network_name': network_name,
                    'key_name': network_info['key_name'],
                    'subnetwork_name': subnet_name,
                    'vl_instance_id': vl_instance_id
                })
                vim_id = json.JSONDecoder().decode(vl_instance.vimid) if isinstance(vl_instance.vimid, str) \
                    else vl_instance.vimid
                ext_virtual_link.append({
                    "vlInstanceId": vl_instance_id,
                    "resourceId": vl_instance.relatednetworkid,
                    "resourceSubnetId": vl_instance.relatedsubnetworkid,
                    "cpdId": self.get_cpd_id_of_vl(network_info['key_name']),
                    "vim": {
                        "vimid": vim_id
                    },
                    # SOL 003 align
                    "id": vl_instance_id,
                    "vimConnectionId": vl_instance.vimid,
                    "extCps": self.get_cpds_of_vl(network_info['key_name'])
                })
        return virtual_link_list, ext_virtual_link

    def get_cpds_of_vl(self, vl_key):
        extCps = []
        logger.debug("vl_keya; %s" % vl_key)
        for cpd in self.vnfd_model["vnf_exposed"]["external_cps"]:
            logger.debug("exposed_cpd; %s" % cpd)
            if vl_key == cpd["key_name"]:
                cp = {"cpdId": cpd["cpd_id"], "cpConfig": []}
                extCps.append(cp)
        return extCps

    def get_cpd_id_of_vl(self, vl_key):
        for cpd in self.vnfd_model["vnf_exposed"]["external_cps"]:
            if vl_key == cpd["key_name"]:
                return cpd["cpd_id"]
        return ""

    def get_network_info_of_vl(self, vl_id):
        for vnf_info in self.nsd_model['vls']:
            if vnf_info['vl_id'] == vl_id:
                return vnf_info['properties']['vl_profile']['networkName'], vnf_info['properties']['vl_profile']['networkName']  # ['initiationParameters']['name']
        return '', ''

    def send_nf_init_request_to_vnfm(self):
        virtual_link_list, ext_virtual_link = self.get_virtual_link_info(self.vnf_id)
        req_param = json.JSONEncoder().encode({
            'vnfInstanceName': self.vnf_inst_name,
            'vnfPackageId': ignore_case_get(self.nf_package_info, "vnfPackageId"),
            'vnfDescriptorId': self.vnfd_id,
            'flavourId': "default",
            'extVirtualLink': ext_virtual_link,
            'additionalParam': {
                "properties": self.properties,
                "inputs": self.inputs,
                "vimId": self.vim_id,
                "extVirtualLinks": virtual_link_list
            }
        })
        rsp = send_nf_init_request(self.vnfm_inst_id, req_param)
        self.vnfm_job_id = ignore_case_get(rsp, 'jobId')
        self.vnfm_nf_inst_id = ignore_case_get(rsp, 'vnfInstanceId')

        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(
            mnfinstid=self.vnfm_nf_inst_id,
            nf_name=self.vnf_inst_name,
            vnf_id=self.vnf_id,
            package_id=ignore_case_get(self.nf_package_info, "vnfPackageId"),
            vnfm_inst_id=self.vnfm_inst_id,
            ns_inst_id=self.ns_inst_id,
            version=ignore_case_get(self.nf_package_info, "vnfdVersion"),
            vendor=ignore_case_get(self.nf_package_info, "vnfdProvider"),
            vnfd_model=self.vnfd_model,
            input_params=json.JSONEncoder().encode(self.inputs),
            lastuptime=now_time())

    def build_homing_request(self):
        id = str(uuid.uuid4())
        callback_uri = "http://{vfcBaseUrl}/api/nslcm/v1/ns/placevnf"
        IP = REG_TO_MSB_REG_PARAM["nodes"][0]["ip"]
        PORT = REG_TO_MSB_REG_PARAM["nodes"][0]["port"]
        vfcBaseUrl = IP + ':' + PORT
        callback_uri = callback_uri.format(vfcBaseUrl=vfcBaseUrl)
        modelInvariantId = "no-resourceModelInvariantId"
        modelVersionId = "no-resourceModelVersionId"
        nsInfo = NSInstModel.objects.filter(id=self.ns_inst_id)
        placementDemand = {
            "resourceModuleName": self.vnf_id,
            "serviceResourceId": self.vnfm_nf_inst_id,
            "resourceModelInfo": {
                "modelInvariantId": modelInvariantId,
                "modelVersionId": modelVersionId
            }
        }

        if self.vim_id:
            # vim_info = self.vim_id.split("_")
            # identifiers = list()
            # identifiers.append(vim_info[1])
            # cloudOwner = vim_info[0]
            identifiers = list()
            identifiers.append(self.vim_id['cloud_regionid'])
            cloudOwner = self.vim_id['cloud_owner']
            required_candidate = [
                {
                    "identifierType": "vimId",
                    "cloudOwner": cloudOwner,
                    "identifiers": identifiers
                }
            ]
            placementDemand["requiredCandidates"] = required_candidate

        req_body = {
            "requestInfo": {
                "transactionId": id,
                "requestId": id,
                "callbackUrl": callback_uri,
                "sourceId": "vfc",
                "requestType": "create",
                "numSolutions": 1,
                "optimizers": ["placement"],
                "timeout": 600
            },
            "placementInfo": {
                "requestParameters": {
                    "customerLatitude": CUST_LAT,
                    "customerLongitude": CUST_LONG,
                    "customerName": CUST_NAME
                },
                "subscriberInfo": {
                    "globalSubscriberId": "",
                    "subscriberName": "",
                    "subscriberCommonSiteId": "",
                },
                "placementDemands": []
            },
            "serviceInfo": {
                "serviceInstanceId": self.ns_inst_id,
                "serviceName": self.ns_inst_name,
                "modelInfo": {
                    "modelInvariantId": nsInfo[0].nsd_invariant_id,
                    "modelVersionId": nsInfo[0].nsd_id
                }
            }
        }
        req_body["placementInfo"]["placementDemands"].append(placementDemand)
        # Stored the init request info inside DB
        OOFDataModel.objects.create(
            request_id=id,
            transaction_id=id,
            request_status="init",
            request_module_name=self.vnf_id,
            service_resource_id=self.vnfm_nf_inst_id,
            vim_id="",
            cloud_owner="",
            cloud_region_id="",
            vdu_info="",
        )
        return req_body

    def send_homing_request_to_OOF(self):
        req_body = self.build_homing_request()
        base_url = OOF_BASE_URL
        resources = "/api/oof/v1/placement"
        resp = restcall.call_req(
            base_url=base_url,
            user=OOF_USER,
            passwd=OOF_PASSWD,
            auth_type=restcall.rest_no_auth,
            resource=resources,
            method="POST",
            content=json.dumps(req_body),
            additional_headers="")
        resp_body = resp[-2]
        resp_status = resp[-1]
        if resp_body:
            logger.debug("Got OOF sync response")
        else:
            logger.warn("Missing OOF sync response")
        logger.debug(("OOF sync response code is %s") % resp_status)
        if str(resp_status) != '202' or resp[0] != 0:
            OOFDataModel.objects.filter(
                request_id=req_body["requestInfo"]["requestId"],
                transaction_id=req_body["requestInfo"]["transactionId"]
            ).update(
                request_status="failed",
                vim_id="none",
                cloud_owner="none",
                cloud_region_id="none",
                vdu_info="none"
            )
            logger.error("Received a Bad Sync from OOF with response code %s" % resp_status)
        logger.info("Completed Homing request to OOF")

    def send_get_vnfm_request_to_extsys(self):
        resp_body = get_vnfm_by_id(self.vnfm_inst_id)
        self.vnfm_inst_name = ignore_case_get(resp_body, 'name')

    def send_create_vnf_request_to_resmgr(self):
        pkg_vnfd = self.vnfd_model
        data = {
            'nf_inst_id': self.nf_inst_id,
            'vnfm_nf_inst_id': self.vnfm_nf_inst_id,
            'vnf_inst_name': self.vnf_inst_name,
            'ns_inst_id': self.ns_inst_id,
            'ns_inst_name': self.ns_inst_name,
            'nf_inst_name': self.vnf_inst_name,
            'vnfm_inst_id': self.vnfm_inst_id,
            'vnfm_inst_name': self.vnfm_inst_name,
            'vnfd_name': pkg_vnfd['metadata'].get('name', 'undefined'),
            'vnfd_id': self.vnfd_id,
            'job_id': self.job_id,
            'nf_inst_status': VNF_STATUS.INSTANTIATING,
            'vnf_type': pkg_vnfd['metadata'].get('vnf_type', 'undefined'),
            'nf_package_id': ignore_case_get(self.nf_package_info, "vnfPackageId")
        }
        create_vnf(data)

    def wait_vnfm_job_finish(self):
        ret = wait_job_finish(
            vnfm_id=self.vnfm_inst_id,
            vnfo_job_id=self.job_id,
            vnfm_job_id=self.vnfm_job_id,
            progress_range=[10, 90],
            timeout=NFVO_VNF_INST_TIMEOUT_SECOND)

        if ret != JOB_MODEL_STATUS.FINISHED:
            raise NSLCMException('VNF instantiation failed from VNFM. The job status is %s' % ret)

    def subscribe(self):
        data = {
            'vnfInstanceId': self.vnfm_nf_inst_id,
            'vnfmId': self.vnfm_inst_id
        }
        try:
            SubscriptionCreation(data).do_biz()
        except Exception as e:
            logger.error("subscribe failed: %s", e.args[0])

    def write_vnf_creation_info(self):
        logger.debug("write_vnf_creation_info start")
        vm_inst_infos = VmInstModel.objects.filter(insttype=INST_TYPE.VNF, instid=self.nf_inst_id)
        data = {
            'nf_inst_id': self.nf_inst_id,
            'ns_inst_id': self.ns_inst_id,
            'vnfm_inst_id': self.vnfm_inst_id,
            'vms': [{'vmId': vm_inst_info.resouceid, 'vmName': vm_inst_info.vmname, 'vmStatus': 'ACTIVE'} for vm_inst_info in vm_inst_infos]
        }
        create_vnf_creation_info(data)
        logger.debug("write_vnf_creation_info end")

    def save_info_to_db(self):
        logger.debug("save_info_to_db start")
        # do_biz_with_share_lock("set-vnflist-in-vnffginst-%s" % self.ns_inst_id, self.save_vnf_inst_id_in_vnffg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.ACTIVE, lastuptime=now_time())
        logger.debug("save_info_to_db end")

    def vnf_inst_failed_handle(self, error_msg):
        logger.error('VNF instantiation failed, detail message: %s' % error_msg)
        NfInstModel.objects.filter(nfinstid=self.nf_inst_id).update(status=VNF_STATUS.FAILED, lastuptime=now_time())
        JobUtil.add_job_status(self.job_id, 255, 'VNF instantiation failed, detail message: %s' % error_msg, 0)

    def save_vnf_inst_id_in_vnffg(self):
        vnffgs = self.nsd_model['vnffgs']
        for vnffg in vnffgs:
            if self.vnf_id not in vnffg['members']:
                continue
            vnffg_inst_infos = VNFFGInstModel.objects.filter(vnffgdid=vnffg['vnffg_Id'], nsinstid=self.ns_inst_id)
            if not vnffg_inst_infos:
                raise NSLCMException('Vnffg instance not exist.')
            vnf_list = vnffg_inst_infos[0].vnflist
            vnffg_inst_infos.update(vnf_list=vnf_list + ',' + self.nf_inst_id if vnf_list else self.nf_inst_id)

    def create_vnf_in_aai(self):
        logger.debug("CreateVnfs::create_vnf_in_aai::report vnf instance[%s] to aai." % self.nf_inst_id)
        try:
            ns_insts = NSInstModel.objects.filter(id=self.ns_inst_id)
            self.global_customer_id = ns_insts[0].global_customer_id
            self.service_type = ns_insts[0].service_type
            data = {
                "vnf-id": self.nf_inst_id,
                "vnf-name": self.vnf_inst_name,
                "vnf-type": "vnf-type-test111",
                "service-id": self.ns_inst_id,
                "in-maint": True,
                "is-closed-loop-disabled": False,
                "relationship-list": {
                    "relationship": [
                        {
                            "related-to": "service-instance",
                            "relationship-data": [
                                {
                                    "relationship-key": "customer.global-customer-id",
                                    "relationship-value": self.global_customer_id
                                },
                                {
                                    "relationship-key": "service-subscription.service-type",
                                    "relationship-value": self.service_type
                                },
                                {
                                    "relationship-key": "service-instance.service-instance-id",
                                    "relationship-value": self.ns_inst_id
                                }
                            ]
                        }
                    ]
                }
            }
            resp_data, resp_status = create_vnf_aai(self.nf_inst_id, data)
            logger.debug("Success to create vnf[%s] to aai, ns instance=[%s], resp_status: [%s]."
                         % (self.nf_inst_id, self.ns_inst_id, resp_status))
        except NSLCMException as e:
            logger.debug("Fail to create vnf[%s] to aai, ns instance=[%s], detail message: %s"
                         % (self.nf_inst_id, self.ns_inst_id, e.args[0]))
        except:
            logger.error(traceback.format_exc())
