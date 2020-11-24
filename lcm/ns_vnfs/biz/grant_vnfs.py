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
from lcm.ns_vnfs.const import SCALAR_UNIT_DICT

logger = logging.getLogger(__name__)


class GrantVnfs(object):
    def __init__(self, data, job_id):
        self.job_id = job_id
        self.vnfm_inst_id = ''
        self.vnf_uuid = ''
        self.vnfm_job_id = ''
        self.data = data

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
