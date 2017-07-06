# Copyright 2016 ZTE Corporation.
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
import json

from lcm.pub.msapi import resmgr
from lcm.pub.database.models import NfPackageModel, NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class GrantVnfs(object):
    def __init__(self, data, job_id):
        self.job_id = job_id
        self.vnfm_inst_id = ''
        self.vnf_uuid = ''
        self.vnfm_job_id = ''
        self.data = data

    def send_grant_vnf_to_resMgr(self):
        logger.debug("grant data from vnfm:%s", self.data)
        if isinstance(self.data, (unicode, str)):
            self.data = json.JSONDecoder().decode(self.data)
        has_res_tpl = False
        grant_type = None
        if ignore_case_get(self.data, "addResource"):
            grant_type = "addResource"
        elif ignore_case_get(self.data, "removeResource"):
            grant_type = "removeResource"
        else:
            #raise NSLCMException("No grant resource is found.")
            has_res_tpl = True

        for res in ignore_case_get(self.data, grant_type):
            if "resourceTemplate" in res:
                has_res_tpl = True
                break

        if not has_res_tpl:
            m_vnf_inst_id = ignore_case_get(self.data, "vnfInstanceId")
            additional_param = ignore_case_get(self.data, "additionalparam")
            vnfm_inst_id = ignore_case_get(additional_param, "vnfmid")
            vim_id = ignore_case_get(additional_param, "vimid")

            vnfinsts = NfInstModel.objects.filter(
                mnfinstid=m_vnf_inst_id, vnfm_inst_id=vnfm_inst_id)
            if not vnfinsts:
                raise NSLCMException("Vnfinst(%s) is not found in vnfm(%s)" % (
                    m_vnf_inst_id, vnfm_inst_id))
                
            vnf_pkg_id = vnfinsts[0].package_id
            vnf_pkgs = NfPackageModel.objects.filter(nfpackageid=vnf_pkg_id)
            if not vnf_pkgs:
                raise NSLCMException("vnfpkg(%s) is not found" % vnf_pkg_id)

            vnfd = json.JSONDecoder().decode(vnf_pkgs[0].vnfdmodel)

            req_param = {
                "vnfInstanceId": m_vnf_inst_id, 
                "vimId": vim_id, 
                "additionalParam": additional_param,
                grant_type: []
            }
            for res in ignore_case_get(self.data, grant_type):
                vdu_name = ignore_case_get(res, "vdu")
                grant_res = {
                    "resourceDefinitionId": ignore_case_get(res, "resourceDefinitionId"),
                    "type": ignore_case_get(res,"type"),
                    "vdu": vdu_name
                }
                for vdu in vnfd["vdus"]:
                    if vdu_name in (vdu["vdu_id"], vdu["properties"].get("name", "")):
                        grant_res["resourceTemplate"] = self.get_res_tpl(vdu, vnfd)
                        break
                req_param[grant_type].append(grant_res)
            self.data = req_param
        return resmgr.grant_vnf(self.data)

    def get_res_tpl(self, vdu, vnfd):
        storage_size = 0
        for storage_id in vdu["local_storages"]:
            storage_size = storage_size + self.get_storage_size(storage_id, vnfd)
        resourceTemplate = {
            "virtualComputeDescriptor": {
                "virtualCpu": {
                    "numVirtualCpu": int(vdu["nfv_compute"]["num_cpus"])
                },
                "virtualMemory": {
                    "virtualMemSize": int(vdu["nfv_compute"]["mem_size"]) 
                }
            },
            "virtualStorageDescriptor": {
                "typeOfStorage": "",
                "sizeOfStorage": storage_size,
                "swImageDescriptor": ""
            }
        }
        return resourceTemplate

    def get_storage_size(self, storage_id, vnfd):
        for storage in vnfd["local_storages"]:
            if storage_id == storage["local_storage_id"]:
                return int(storage["properties"]["size"])
        return 0







