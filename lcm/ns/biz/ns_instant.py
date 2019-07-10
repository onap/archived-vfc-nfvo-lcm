# Copyright 2016-2017 ZTE Corporation.
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
import time
import traceback
import uuid
from threading import Thread

from rest_framework import status

from lcm.pub.config import config
from lcm.pub.database.models import DefPkgMappingModel, ServiceBaseInfoModel, InputParamMappingModel
from lcm.pub.database.models import NSInstModel, VNFFGInstModel, WFPlanModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi import activiti
from lcm.pub.msapi import sdc_run_catalog
from lcm.pub.msapi.catalog import get_process_id
from lcm.pub.msapi.catalog import get_servicetemplate_id, get_servicetemplate
from lcm.pub.msapi import extsys
from lcm.pub.msapi.wso2bpel import workflow_run
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.values import ignore_case_get
from lcm.workflows import build_in
from lcm.ns.biz.ns_instantiate_flow import run_ns_instantiate
from lcm.ns.biz.ns_lcm_op_occ import NsLcmOpOcc

logger = logging.getLogger(__name__)


class BuildInWorkflowThread(Thread):
    def __init__(self, plan_input, occ_id):
        Thread.__init__(self)
        self.plan_input = plan_input
        self.occ_id = occ_id

    def run(self):
        build_in.run_ns_instantiate(self.plan_input, self.occ_id)


class InstantNSService(object):
    def __init__(self, ns_inst_id, plan_content):
        self.ns_inst_id = ns_inst_id
        self.req_data = plan_content

    def do_biz(self):
        job_id = JobUtil.create_job("NS", "NS_INST", self.ns_inst_id)
        occ_id = NsLcmOpOcc.create(self.ns_inst_id, "INSTANTIATE", "PROCESSING", False, self.req_data)

        try:
            logger.debug('ns-instant(%s) workflow starting...' % self.ns_inst_id)
            logger.debug('req_data=%s' % self.req_data)
            ns_inst = NSInstModel.objects.get(id=self.ns_inst_id)
            vim_id = {}

            input_parameters = []
            if 'additionalParamForNs' in self.req_data:
                for key, val in list(self.req_data['additionalParamForNs'].items()):
                    input_parameters.append({"key": key, "value": val})

                if 'location' in self.req_data['additionalParamForNs']:
                    cloud_owner = self.req_data['additionalParamForNs']['location'].split('_')[0]
                    cloud_regionid = self.req_data["additionalParamForNs"]["location"].split('_')[1]
                    vim_id = {"cloud_owner": cloud_owner, "cloud_regionid": cloud_regionid}
                params_json = json.JSONEncoder().encode(self.req_data["additionalParamForNs"])
            else:
                params_json = json.JSONEncoder().encode({})

            location_constraints = []
            if 'locationConstraints' in self.req_data:
                location_constraints = self.req_data['locationConstraints']

            JobUtil.add_job_status(job_id, 5, 'Start query nsd(%s)' % ns_inst.nspackage_id)
            dst_plan = sdc_run_catalog.parse_nsd(ns_inst.nspackage_id, input_parameters)
            logger.debug('tosca plan dest: %s' % dst_plan)
            logger.debug('Start query nsd(%s)' % ns_inst.nspackage_id)
            NSInstModel.objects.filter(id=self.ns_inst_id).update(nsd_model=dst_plan)

            params_vnf = []
            plan_dict = json.JSONDecoder().decode(dst_plan)
            for vnf in ignore_case_get(plan_dict, "vnfs"):
                vnfd_id = vnf['properties']['id']
                vnfm_type_temp = vnf['properties'].get("vnfm_info", "undefined")
                logger.debug("vnfd_id: %s, vnfm_type : %s", vnfd_id, vnfm_type_temp)
                vnfm_type = vnfm_type_temp
                if isinstance(vnfm_type_temp, list):
                    vnfm_type = vnfm_type_temp[0]
                vimid = self.get_vnf_vim_id(vim_id, location_constraints, vnfd_id)
                s_vimid = "%s_%s" % (vimid["cloud_owner"], vimid["cloud_regionid"])
                vnfm_info = extsys.select_vnfm(vnfm_type=vnfm_type, vim_id=s_vimid)

                params_vnf.append({
                    "vnfProfileId": vnf["vnf_id"],
                    "additionalParam": {
                        "properties": json.JSONEncoder().encode(vnf['properties']),
                        "vimId": vimid,
                        "vnfmInstanceId": vnfm_info["vnfmId"],
                        "vnfmType": vnfm_type,
                        "inputs": params_json
                    }
                })

            self.set_vl_vim_id(vim_id, location_constraints, plan_dict)
            dst_plan = json.JSONEncoder().encode(plan_dict)
            logger.debug('tosca plan dest add vimid:%s' % dst_plan)
            NSInstModel.objects.filter(id=self.ns_inst_id).update(nsd_model=dst_plan)

            pnf_params_json = json.JSONEncoder().encode(self.init_pnf_para(plan_dict))

            vnf_params_json = json.JSONEncoder().encode(params_vnf)
            plan_input = {
                'jobId': job_id,
                'nsInstanceId': self.ns_inst_id,
                'object_context': dst_plan,
                'object_additionalParamForNs': params_json,
                'object_additionalParamForVnf': vnf_params_json,
                'object_additionalParamForPnf': pnf_params_json
            }
            plan_input.update(**self.get_model_count(dst_plan))

            if 'additionalParamForNs' in self.req_data:
                plan_input["sdnControllerId"] = ignore_case_get(
                    self.req_data['additionalParamForNs'], "sdncontroller")

            ServiceBaseInfoModel(service_id=self.ns_inst_id,
                                 service_name=ns_inst.name,
                                 service_type='NFVO',
                                 description=ns_inst.description,
                                 active_status='--',
                                 status=ns_inst.status,
                                 creator='--',
                                 create_time=int(time.time() * 1000)).save()

            if config.WORKFLOW_OPTION == "wso2":
                service_tpl = get_servicetemplate(ns_inst.nsd_id)
                DefPkgMappingModel(service_id=self.ns_inst_id,
                                   service_def_id=service_tpl['csarId'],
                                   template_name=service_tpl['templateName'],
                                   template_id=service_tpl['serviceTemplateId']).save()

                for key, val in list(self.req_data['additionalParamForNs'].items()):
                    InputParamMappingModel(service_id=self.ns_inst_id,
                                           input_key=key,
                                           input_value=val).save()

                for vnffg in ignore_case_get(plan_dict, "vnffgs"):
                    VNFFGInstModel(vnffgdid=vnffg["vnffg_id"],
                                   vnffginstid=str(uuid.uuid4()),
                                   nsinstid=self.ns_inst_id,
                                   endpointnumber=0).save()
            else:
                # TODO
                pass
            logger.debug("workflow option: %s" % config.WORKFLOW_OPTION)
            if config.WORKFLOW_OPTION == "wso2":
                return self.start_wso2_workflow(job_id, ns_inst, plan_input, occ_id=occ_id)
            elif config.WORKFLOW_OPTION == "activiti":
                return self.start_activiti_workflow(job_id, plan_input, occ_id=occ_id)
            elif config.WORKFLOW_OPTION == "grapflow":
                return self.start_buildin_grapflow(job_id, plan_input, occ_id=occ_id)
            else:
                return self.start_buildin_workflow(job_id, plan_input, occ_id=occ_id)

        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("ns-instant(%s) workflow error:%s" % (self.ns_inst_id, e.args[0]))
            NsLcmOpOcc.update(occ_id, operationState="FAILED", error=e.args[0])
            JobUtil.add_job_status(job_id, 255, 'NS instantiation failed')
            return dict(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def start_wso2_workflow(self, job_id, ns_inst, plan_input, occ_id):
        # todo occ_id
        servicetemplate_id = get_servicetemplate_id(ns_inst.nsd_id)
        process_id = get_process_id('init', servicetemplate_id)
        data = {"processId": process_id, "params": {"planInput": plan_input}}
        logger.debug('ns-instant(%s) workflow data:%s' % (self.ns_inst_id, data))

        ret = workflow_run(data)
        logger.info("ns-instant(%s) workflow result:%s" % (self.ns_inst_id, ret))
        JobUtil.add_job_status(job_id, 10, 'NS inst(%s) wso2 workflow started: %s' % (
            self.ns_inst_id, ret.get('status')))
        if ret.get('status') == 1:
            return dict(data={'jobId': job_id}, status=status.HTTP_200_OK, occ_id=occ_id)
        return dict(data={'error': ret['message']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def start_activiti_workflow(self, job_id, plan_input, occ_id):
        # todo occ_id
        plans = WFPlanModel.objects.filter()
        if not plans:
            raise NSLCMException("No plan is found, you should deploy plan first!")
        data = {
            "processId": plans[0].process_id,
            "params": plan_input
        }
        ret = activiti.exec_workflow(data)
        logger.info("ns-instant(%s) workflow result:%s" % (self.ns_inst_id, ret))
        JobUtil.add_job_status(job_id, 10, 'NS inst(%s) activiti workflow started: %s' % (
            self.ns_inst_id, ret.get('status')))
        if ret.get('status') == 1:
            return dict(data={'jobId': job_id}, status=status.HTTP_200_OK, occ_id=occ_id)
        return dict(data={'error': ret['message']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def start_buildin_workflow(self, job_id, plan_input, occ_id):
        JobUtil.add_job_status(job_id, 10, 'NS inst(%s) buildin workflow started.' % self.ns_inst_id)
        BuildInWorkflowThread(plan_input, occ_id).start()
        return dict(data={'jobId': job_id}, status=status.HTTP_200_OK, occ_id=occ_id)

    def start_buildin_grapflow(self, job_id, plan_input, occ_id):
        JobUtil.add_job_status(job_id, 10, 'NS inst(%s) buildin grap workflow started.' % self.ns_inst_id)
        run_ns_instantiate(plan_input, occ_id)
        return dict(data={'jobId': job_id}, status=status.HTTP_200_OK, occ_id=occ_id)

    @staticmethod
    def get_vnf_vim_id(vim_id, location_constraints, vnfdid):
        for location in location_constraints:
            if "vnfProfileId" in location and vnfdid == location["vnfProfileId"]:
                # if 'vimId' in location['locationConstraints']:
                if len(location['locationConstraints']) == 1:
                    cloud_owner = location['locationConstraints']["vimId"].split('_')[0]
                    cloud_regionid = location['locationConstraints']["vimId"].split('_')[1]
                    vim_id = {"cloud_owner": cloud_owner, "cloud_regionid": cloud_regionid}
                elif len(location['locationConstraints']) == 2:
                    cloud_owner = location['locationConstraints']["cloudOwner"]
                    cloud_regionid = location['locationConstraints']["cloudRegionId"]
                    vim_id = {"cloud_owner": cloud_owner, "cloud_regionid": cloud_regionid}
                return vim_id
        if vim_id:
            return vim_id
        raise NSLCMException("No Vim info is found for vnf(%s)." % vnfdid)

    @staticmethod
    def set_vl_vim_id(vim_id, location_constraints, plan_dict):
        if "vls" not in plan_dict:
            logger.debug("No vl is found in nsd.")
            return
        vl_vnf = {}
        for vnf in ignore_case_get(plan_dict, "vnfs"):
            if "dependencies" in vnf:
                for depend in vnf["dependencies"]:
                    vl_vnf[depend["vl_id"]] = vnf['properties']['id']
        vnf_vim = {}

        for location in location_constraints:
            if "vnfProfileId" in location:
                vnfd_id = location["vnfProfileId"]
                # if 'vimId' in location["locationConstraints"]:
                if len(location['locationConstraints']) == 1:
                    cloud_owner = location["locationConstraints"]["vimId"].split('_')[0]
                    cloud_regionid = location["locationConstraints"]["vimId"].split('_')[1]
                    vim_id = {"cloud_owner": cloud_owner, "cloud_regionid": cloud_regionid}
                    vnf_vim[vnfd_id] = vim_id
                elif len(location['locationConstraints']) == 2:
                    cloud_owner = location["locationConstraints"]["cloudOwner"]
                    cloud_regionid = location["locationConstraints"]["cloudRegionId"]
                    vim_id = {"cloud_owner": cloud_owner, "cloud_regionid": cloud_regionid}
                    vnf_vim[vnfd_id] = vim_id
        for vl in plan_dict["vls"]:
            vnfdid = ignore_case_get(vl_vnf, vl["vl_id"])
            vimid = ignore_case_get(vnf_vim, vnfdid)
            if not vimid:
                vimid = vim_id
            if "location_info" not in vl["properties"]:
                vl["properties"]["location_info"] = {}
            vl["properties"]["location_info"]["vimid"] = vimid

    @staticmethod
    def get_model_count(context):
        data = json.JSONDecoder().decode(context)
        vls = len(data.get('vls', []))
        sfcs = len(data.get('fps', []))
        vnfs = len(data.get('vnfs', []))
        pnfs = len(data.get('pnfs', []))
        return {'vlCount': str(vls), 'sfcCount': str(sfcs), 'vnfCount': str(vnfs), 'pnfCount': str(pnfs)}

    def init_pnf_para(self, plan_dict):
        pnfs_in_input = ignore_case_get(self.req_data, "addpnfData", [])
        pnfs_in_nsd = ignore_case_get(plan_dict, "pnfs", [])
        logger.debug("addpnfData ; %s" % pnfs_in_input)
        logger.debug("pnfs_in_nsd ; %s" % pnfs_in_nsd)
        pnfs = {}
        for pnf in pnfs_in_input:
            for pnfd in pnfs_in_nsd:
                if pnfd["properties"]["descriptor_id"] == pnf["pnfdId"]:
                    k = pnfd["pnf_id"]
                    pnf["nsInstances"] = self.ns_inst_id
                    pnfs[k] = {
                        "type": "CreatePnf",
                        "input": {
                            "content": pnf
                        }
                    }
        return pnfs
