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
import traceback

from lcm.ns.const import OWNER_TYPE
from lcm.pub.database.models import NSInstModel, NfInstModel, VLInstModel, CPInstModel, VNFFGInstModel

logger = logging.getLogger(__name__)


class GetNSInfoService(object):
    def __init__(self, ns_inst_id=None):
        self.ns_inst_id = ns_inst_id

    def get_ns_info(self):
        try:
            if self.ns_inst_id:
                return self.get_single_ns_info(self.ns_inst_id)
            else:
                return self.get_total_ns_info()
        except:
            logger.error(traceback.format_exc())
            return None if self.ns_inst_id else []

    def get_total_ns_info(self):
        ns_inst_infos = NSInstModel.objects.all()
        ns_info_list = []
        for info in ns_inst_infos:
            ret = self.get_single_ns_info(info.id)
            if not ret:
                continue
            ns_info_list.append(ret)
        return ns_info_list

    def get_single_ns_info(self, ns_inst_id):
        ns_insts = NSInstModel.objects.filter(id=ns_inst_id)
        if not ns_insts:
            return None
        ns_inst_info = ns_insts[0]
        ret = {
            'nsInstanceId': ns_inst_info.id,
            'nsName': ns_inst_info.name,
            'description': ns_inst_info.description,
            'nsdId': ns_inst_info.nsd_id,
            'vnfInfoId': self.get_vnf_infos(ns_inst_id),
            'vlInfo': self.get_vl_infos(ns_inst_id),
            'vnffgInfo': self.get_vnffg_infos(ns_inst_id, ns_inst_info.nsd_model),
            'nsState': ns_inst_info.status}
        return ret

    @staticmethod
    def get_vnf_infos(ns_inst_id):
        ns_inst_infos = NfInstModel.objects.filter(ns_inst_id=ns_inst_id)
        vnf_info_list = []
        for info in ns_inst_infos:
            vnf_info = {
                'vnfInstanceId': info.nfinstid,
                'vnfInstanceName': info.nf_name,
                'vnfProfileId': info.vnf_id}
            vnf_info_list.append(vnf_info)
        return vnf_info_list

    def get_vl_infos(self, ns_inst_id):
        vl_inst_infos = VLInstModel.objects.filter(ownertype=OWNER_TYPE.NS, ownerid=ns_inst_id)
        vl_info_list = []
        for info in vl_inst_infos:
            vl_info = {
                'vlInstanceId': info.vlinstanceid,
                'vlInstanceName': info.vlinstancename,
                'vldId': info.vldid,
                'relatedCpInstanceId': self.get_cp_infos(info.vlinstanceid)}
            vl_info_list.append(vl_info)
        return vl_info_list

    @staticmethod
    def get_cp_infos(vl_inst_id):
        cp_inst_infos = CPInstModel.objects.filter(relatedvl__icontains=vl_inst_id)
        cp_info_list = []
        for info in cp_inst_infos:
            cp_info = {
                'cpInstanceId': info.cpinstanceid,
                'cpInstanceName': info.cpname,
                'cpdId': info.cpdid}
            cp_info_list.append(cp_info)
        return cp_info_list

    def get_vnffg_infos(self, ns_inst_id, nsd_model):
        vnffg_inst_infos = VNFFGInstModel.objects.filter(nsinstid=ns_inst_id)
        vnffg_info_list = []
        for info in vnffg_inst_infos:
            vnffg_info = {
                'vnffgInstanceId': info.vnffginstid,
                'vnfId': self.convert_string_to_list(info.vnflist),
                'pnfId': self.get_pnf_infos(nsd_model),
                'virtualLinkId': self.convert_string_to_list(info.vllist),
                'cpId': self.convert_string_to_list(info.cplist),
                'nfp': self.convert_string_to_list(info.fplist)}
            vnffg_info_list.append(vnffg_info)
        return vnffg_info_list

    @staticmethod
    def get_pnf_infos(nsd_model):
        context = json.loads(nsd_model)
        pnfs = context['pnfs']
        pnf_list = []
        for pnf in pnfs:
            pnf_list.append(pnf['pnf_id'])
        return pnf_list

    @staticmethod
    def convert_string_to_list(detail_id_string):
        if not detail_id_string:
            return None
        return detail_id_string.split(',')
