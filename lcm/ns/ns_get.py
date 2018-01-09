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
import json
import logging

from lcm.ns.const import OWNER_TYPE
from lcm.pub.database.models import NSInstModel, NfInstModel, VLInstModel, CPInstModel, VNFFGInstModel

logger = logging.getLogger(__name__)


class GetNSInfoService(object):
    def __init__(self, nsfilter=None):
        self.ns_filter = nsfilter

    def get_ns_info(self):
        ns_insts = None
        if self.ns_filter and "ns_inst_id" in self.ns_filter:
            ns_inst_id = self.ns_filter["ns_inst_id"]
            ns_insts = NSInstModel.objects.filter(id=ns_inst_id)
        elif self.ns_filter and "csarId" in self.ns_filter:
            csar_id = self.ns_filter["csarId"]
            ns_insts = NSInstModel.objects.filter(nsd_id=csar_id)
        else:
            ns_insts = NSInstModel.objects.all()

        return [self.get_single_ns_info(ns_inst) for ns_inst in ns_insts]

    def get_single_ns_info(self, ns_inst):
        return {
            'nsInstanceId': ns_inst.id,
            'nsName': ns_inst.name,
            'description': ns_inst.description,
            'nsdId': ns_inst.nsd_id,
            'vnfInfoId': self.get_vnf_infos(ns_inst.id),
            'vlInfo': self.get_vl_infos(ns_inst.id),
            'vnffgInfo': self.get_vnffg_infos(ns_inst.id, ns_inst.nsd_model),
            'nsState': ns_inst.status
            }

    @staticmethod
    def get_vnf_infos(ns_inst_id):
        vnfs = NfInstModel.objects.filter(ns_inst_id=ns_inst_id)
        return [{
            'vnfInstanceId': vnf.nfinstid,
            'vnfInstanceName': vnf.nf_name,
            'vnfProfileId': vnf.vnf_id
            } for vnf in vnfs]

    def get_vl_infos(self, ns_inst_id):
        vls = VLInstModel.objects.filter(ownertype=OWNER_TYPE.NS, ownerid=ns_inst_id)
        return [{
            'vlInstanceId': vl.vlinstanceid,
            'vlInstanceName': vl.vlinstancename,
            'vldId': vl.vldid,
            'relatedCpInstanceId': self.get_cp_infos(vl.vlinstanceid)
            } for vl in vls]

    @staticmethod
    def get_cp_infos(vl_inst_id):
        cps = CPInstModel.objects.filter(relatedvl__icontains=vl_inst_id)
        return [{
            'cpInstanceId': cp.cpinstanceid,
            'cpInstanceName': cp.cpname,
            'cpdId': cp.cpdid
            } for cp in cps]

    def get_vnffg_infos(self, ns_inst_id, nsd_model):
        vnffgs = VNFFGInstModel.objects.filter(nsinstid=ns_inst_id)
        return [{
            'vnffgInstanceId': vnffg.vnffginstid,
            'vnfId': self.convert_string_to_list(vnffg.vnflist),
            'pnfId': self.get_pnf_infos(nsd_model),
            'virtualLinkId': self.convert_string_to_list(vnffg.vllist),
            'cpId': self.convert_string_to_list(vnffg.cplist),
            'nfp': self.convert_string_to_list(vnffg.fplist)
            } for vnffg in vnffgs]

    @staticmethod
    def get_pnf_infos(nsd_model):
        context = json.loads(nsd_model)
        pnfs = context['pnfs']
        return [pnf['pnf_id'] for pnf in pnfs]

    @staticmethod
    def convert_string_to_list(detail_id_string):
        if not detail_id_string:
            return None
        return detail_id_string.split(',')
