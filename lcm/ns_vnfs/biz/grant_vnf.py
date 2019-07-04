# Copyright 2018 ZTE Corporation.
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
import uuid
import time
from lcm.pub.database.models import NfInstModel, OOFDataModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.sdc_run_catalog import query_vnfpackage_by_id
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.msapi import resmgr
from lcm.ns_vnfs.const import SCALAR_UNIT_DICT

logger = logging.getLogger(__name__)


class GrantVnf(object):
    def __init__(self, grant_data):
        self.data = grant_data

    def exec_grant(self):
        logger.debug("grant data from vnfm:%s", self.data)
        if isinstance(self.data, str):
            self.data = json.JSONDecoder().decode(self.data)
        has_res_tpl = False
        grant_type = None
        action_type = ignore_case_get(self.data, "operation")
        vimConnections = []
        if ignore_case_get(self.data, "addResources"):
            grant_type = "addResources"
        elif ignore_case_get(self.data, "removeResources"):
            grant_type = "removeResources"
        else:
            has_res_tpl = True

        for res in ignore_case_get(self.data, grant_type):
            if "resourceTemplate" in res:
                has_res_tpl = True
                break

        if not has_res_tpl:
            m_vnf_inst_id = ignore_case_get(self.data, "vnfInstanceId")
            additional_param = ignore_case_get(self.data, "additionalparams")
            vnfm_inst_id = ignore_case_get(additional_param, "vnfmid")
            vim_id = ignore_case_get(additional_param, "vimid")
            if vnfm_inst_id and vnfm_inst_id != "":
                vnfinsts = NfInstModel.objects.filter(
                    mnfinstid=m_vnf_inst_id, vnfm_inst_id=vnfm_inst_id)
            else:
                vnfinsts = NfInstModel.objects.filter(
                    mnfinstid=m_vnf_inst_id)
            if not vnfinsts:
                raise NSLCMException("Vnfinst(%s) is not found in vnfm(%s)" % (
                    m_vnf_inst_id, vnfm_inst_id))

            vnf_pkg_id = vnfinsts[0].package_id
            nfpackage_info = query_vnfpackage_by_id(vnf_pkg_id)
            vnf_pkg = nfpackage_info["packageInfo"]
            vnfd = json.JSONDecoder().decode(vnf_pkg["vnfdModel"])

            req_param = {
                "vnfInstanceId": m_vnf_inst_id,
                "vimId": vim_id,
                "vnfLcmOpOccId": ignore_case_get(self.data, "vnfLcmOpOccId"),
                "additionalParams": additional_param,
                grant_type: []
            }
            for res in ignore_case_get(self.data, grant_type):
                vdu_name = ignore_case_get(res, "vdu")
                grant_res = {
                    "resourceDefinitionId": ignore_case_get(res, "resourceDefinitionId"),
                    "type": ignore_case_get(res, "type"),
                    "vdu": vdu_name
                }
                for vdu in vnfd["vdus"]:
                    if vdu_name in (vdu["vdu_id"], vdu["properties"].get("name", "")):
                        grant_res["resourceTemplate"] = self.get_res_tpl(vdu, vnfd)
                        break
                req_param[grant_type].append(grant_res)
            self.data = req_param
        tmp = resmgr.grant_vnf(self.data)
        vimConnections.append(
            {
                "id": tmp["vim"]["vimId"],
                "vimId": tmp["vim"]["vimId"],
                "vimType": None,
                "interfaceInfo": None,
                "accessInfo": tmp["vim"]["accessInfo"],
                "extra": None
            }
        )

        grant_resp = {
            "id": str(uuid.uuid4()),
            "vnfInstanceId": ignore_case_get(self.data, 'vnfInstanceId'),
            "vnfLcmOpOccId": ignore_case_get(self.data, "vnfLcmOpOccId"),
            "vimConnections": vimConnections
        }

        logger.debug("action_type=%s" % action_type)
        if action_type == 'INSTANTIATE':
            for i in range(18):
                offs = OOFDataModel.objects.filter(service_resource_id=ignore_case_get(self.data, "vnfInstanceId"))
                if not (offs.exists() and offs[0].vdu_info):
                    logger.debug("Cannot find oof data, retry%s" % (i + 1))
                    time.sleep(5)
                    continue
                try:
                    vdu_info = json.loads(offs[0].vdu_info)
                    grant_resp['vimAssets'] = {'computeResourceFlavours': []}
                    for vdu in vdu_info:
                        grant_resp['vimAssets']['computeResourceFlavours'].append({
                            'vimConnectionId': offs[0].vim_id,
                            'resourceProviderId': vdu.get("vduName"),
                            'vnfdVirtualComputeDescId': None,  # TODO: required
                            'vimFlavourId': vdu.get("flavorId")
                        })
                        # grant_resp['additionalparams'][off.vim_id] = off.directive
                except Exception:
                    logger.debug("Load OOF data error")
                break

        logger.debug("grant_resp=%s", grant_resp)
        return grant_resp

    def get_res_tpl(self, vdu, vnfd):
        storage_size = 0
        for storage_id in vdu["local_storages"]:
            storage_size = storage_size + self.get_storage_size(storage_id, vnfd)
        resourceTemplate = {
            "virtualComputeDescriptor": {
                "virtualCpu": {
                    "numVirtualCpu": int(vdu["virtual_compute"]["virtual_cpu"]["num_virtual_cpu"])
                },
                "virtualMemory": {
                    "virtualMemSize": parse_unit(vdu["virtual_compute"]["virtual_memory"]["virtual_mem_size"], "MB")
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
                return parse_unit(storage["properties"]["size"], "GB")
        return 0


def parse_unit(val, base_unit):
    # recognized_units = ["B", "kB", "KiB", "MB", "MiB", "GB", "GiB", "TB", "TiB"]
    # units_rate = [1, 1000, 1024, 1000000, 1048576, 1000000000, 1073741824, 1000000000000, 1099511627776]
    # unit_rate_map = {unit.upper(): rate for unit, rate in zip(recognized_units, units_rate)}
    num_unit = val.strip().split(" ")
    if len(num_unit) != 2:
        return val.strip()
    num, unit = num_unit[0], num_unit[1]
    return int(num) * SCALAR_UNIT_DICT[unit.upper()] / SCALAR_UNIT_DICT[base_unit.upper()]
