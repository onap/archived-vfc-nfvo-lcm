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

from lcm.ns.const import NS_INSTANCE_BASE_URI
from lcm.ns.enum import OWNER_TYPE
from lcm.pub.database.models import NSInstModel
from lcm.pub.database.models import NfInstModel
from lcm.pub.database.models import VLInstModel
from lcm.pub.database.models import CPInstModel
from lcm.pub.database.models import VNFFGInstModel
from lcm.pub.database.models import PNFInstModel

logger = logging.getLogger(__name__)


class GetNSInfoService(object):
    def __init__(self, ns_filter=None):
        self.ns_filter = ns_filter

    def get_ns_info(self, is_sol=False):
        if self.ns_filter and "ns_inst_id" in self.ns_filter:
            ns_inst_id = self.ns_filter["ns_inst_id"]
            ns_insts = NSInstModel.objects.filter(id=ns_inst_id)
        else:
            ns_insts = NSInstModel.objects.all()
        result = []
        for ns_inst in ns_insts:
            if ns_inst.status != 'null':
                result.append(self.get_single_ns_info(ns_inst, is_sol))
        return result

    def get_single_ns_info(self, ns_inst, is_sol=False):
        if is_sol:
            nsInstance = {}
            nsInstance['id'] = ns_inst.id
            nsInstance['nsInstanceName'] = ns_inst.name
            nsInstance['nsInstanceDescription'] = ns_inst.description
            nsInstance['nsdId'] = ns_inst.nsd_id
            nsInstance['nsdInfoId'] = ns_inst.nspackage_id
            nsInstance['nsState'] = ns_inst.status
            if ns_inst.nsd_invariant_id:
                nsInstance['nsdInvariantId'] = ns_inst.nsd_invariant_id
            if ns_inst.flavour_id:
                nsInstance['flavourId'] = ns_inst.flavour_id
                # todo 'nsScaleStatus':{}
                # todo  'additionalAffinityOrAntiAffinityRule':{}
            logger.debug(" test ")
            vnf_instance_list = self.get_vnf_infos(ns_inst.id, is_sol)
            if vnf_instance_list:
                nsInstance['vnfInstance'] = vnf_instance_list
                # todo 'pnfInfo': self.get_pnf_infos(ns_inst.id,is_sol),
            vl_list = self.get_vl_infos(ns_inst.id, is_sol)
            if vl_list:
                nsInstance['virtualLinkInfo'] = vl_list
                # todo 'vnffgInfo': self.get_vnffg_infos(ns_inst.id, ns_inst.nsd_model),
                # todo  'sapInfo':{},
                # todo  nestedNsInstanceId
            logger.debug(" test ")
            nsInstance['_links'] = {
                'self': {'href': NS_INSTANCE_BASE_URI % ns_inst.id},
                'instantiate': {'href': NS_INSTANCE_BASE_URI % ns_inst.id + '/instantiate'},
                'terminate': {'href': NS_INSTANCE_BASE_URI % ns_inst.id + '/terminate'},
                'update': {'href': NS_INSTANCE_BASE_URI % ns_inst.id + '/update'},
                'scale': {'href': NS_INSTANCE_BASE_URI % ns_inst.id + '/scale'},
                'heal': {'href': NS_INSTANCE_BASE_URI % ns_inst.id + '/heal'}
            }
            logger.debug(" test ")
            return nsInstance
        return {
            'nsInstanceId': ns_inst.id,
            'nsName': ns_inst.name,
            'description': ns_inst.description,
            'nsdId': ns_inst.nsd_id,
            'nsdInvariantId': ns_inst.nsd_invariant_id,
            'vnfInfo': self.get_vnf_infos(ns_inst.id, is_sol),
            'pnfInfo': self.get_pnf_infos(ns_inst.id),
            'vlInfo': self.get_vl_infos(ns_inst.id, is_sol),
            'vnffgInfo': self.get_vnffg_infos(ns_inst.id, ns_inst.nsd_model, is_sol),
            'nsState': ns_inst.status}

    @staticmethod
    def get_vnf_infos(ns_inst_id, is_sol):
        vnfs = NfInstModel.objects.filter(ns_inst_id=ns_inst_id)
        if is_sol:
            return [{
                'id': vnf.nfinstid,
                'vnfInstanceName': vnf.nf_name,
                'vnfdId': vnf.template_id,
                'vnfProvider': vnf.vendor,
                'vnfSoftwareVersion': vnf.version,
                'vnfProductName': vnf.nf_name,  # todo
                'vnfdVersion': vnf.version,  # todo
                'vnfPkgId': vnf.package_id,
                'instantiationState': vnf.status
            } for vnf in vnfs]
        return [{
            'vnfInstanceId': vnf.nfinstid,
            'vnfInstanceName': vnf.nf_name,
            'vnfProfileId': vnf.vnf_id} for vnf in vnfs]

    def get_vl_infos(self, ns_inst_id, is_sol):
        vls = VLInstModel.objects.filter(ownertype=OWNER_TYPE.NS, ownerid=ns_inst_id)
        if is_sol:
            return [
                {
                    'id': vl.vlinstanceid,
                    'nsVirtualLinkDescId': vl.vldid,
                    'nsVirtualLinkProfileId': vl.vldid,
                    'vlInstanceName': vl.vlinstancename,
                    'resourceHandle': [{
                        'vimConnectionId': vl.vimid,
                        'resourceId': vl.relatednetworkid,
                        'vimLevelResourceType': vl.vltype
                    }],
                    # todo 'linkPort': self.get_cp_infos(vl.vlinstanceid,is_sol),
                    'networkId': vl.relatednetworkid,
                    'subNetworkid': vl.relatedsubnetworkid
                } for vl in vls]

        return [{
            'vlInstanceId': vl.vlinstanceid,
            'vlInstanceName': vl.vlinstancename,
            'vldId': vl.vldid,
            'relatedCpInstanceId': self.get_cp_infos(vl.vlinstanceid)} for vl in vls]

    @staticmethod
    def get_cp_infos(vl_inst_id):
        cps = CPInstModel.objects.filter(relatedvl__icontains=vl_inst_id)
        return [{
            'cpInstanceId': cp.cpinstanceid,
            'cpInstanceName': cp.cpname,
            'cpdId': cp.cpdid} for cp in cps]

    def get_vnffg_infos(self, ns_inst_id, nsd_model, is_sol):
        vnffgs = VNFFGInstModel.objects.filter(nsinstid=ns_inst_id)
        return [{
            'vnffgInstanceId': vnffg.vnffginstid,
            'vnfId': self.convert_string_to_list(vnffg.vnflist),
            'pnfId': self.get_pnf_ids(nsd_model),
            'virtualLinkId': self.convert_string_to_list(vnffg.vllist),
            'cpId': self.convert_string_to_list(vnffg.cplist),
            'nfp': self.convert_string_to_list(vnffg.fplist)} for vnffg in vnffgs]

    @staticmethod
    def get_pnf_ids(nsd_model):
        context = json.loads(nsd_model)
        pnfs = context['pnfs']
        return [pnf['pnf_id'] for pnf in pnfs]

    @staticmethod
    def convert_string_to_list(detail_id_string):
        if not detail_id_string:
            return None
        return detail_id_string.split(',')

    @staticmethod
    def get_pnf_infos(ns_instance_id):
        pnfs = PNFInstModel.objects.filter(nsInstances__contains=ns_instance_id)
        return [pnf.__dict__ for pnf in pnfs]
