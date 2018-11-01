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
from lcm.pub.database.models import NfInstModel, VmInstModel


class GetVnf(object):
    def __init__(self, nf_inst_id):
        self.nf_inst_id = nf_inst_id

    def do_biz(self):
        nf_inst_info = NfInstModel.objects.filter(nfinstid=self.nf_inst_id)
        return nf_inst_info


class GetVnfVms(object):
    def __init__(self, nf_inst_id):
        self.nf_inst_id = nf_inst_id

    def do_biz(self):
        vnf_vms = VmInstModel.objects.filter(instid=self.nf_inst_id)
        return vnf_vms
