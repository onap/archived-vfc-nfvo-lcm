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
import uuid
import logging
import traceback

from rest_framework import status
from rest_framework.response import Response
from lcm.ns.vnfs.const import INST_TYPE
from lcm.pub.exceptions import NSLCMException
from lcm.pub.database.models import VNFCInstModel, VLInstModel, NfInstModel, PortInstModel, CPInstModel, VmInstModel
from lcm.pub.utils.values import ignore_case_get


logger = logging.getLogger(__name__)


class NotifyLcm(object):
    def __init__(self, vnfmid, vnfInstanceId, data):
        logger.debug("[Notify LCM] vnfmid=%s, vnfInstanceId=%s, data=%s" % (vnfmid, vnfInstanceId, data))
        self.vnf_instid = ''
        self.vnfmid = vnfmid
        self.m_vnfInstanceId = vnfInstanceId
        self.status = ignore_case_get(data, 'status')
        self.operation = ignore_case_get(data, 'operation')
        self.lcm_jobid = ignore_case_get(data, 'jobId')
        self.vnfdmodule = ignore_case_get(data, 'vnfdmodule')
        self.affectedVnfc = ignore_case_get(data, 'affectedVnfc')
        self.affectedVl = ignore_case_get(data, 'affectedVl')
        self.affectedCp = ignore_case_get(data, 'affectedCp')
        self.affectedVirtualStorage = ignore_case_get(data, 'affectedVirtualStorage')

    def do_biz(self):
        try:
            self.vnf_instid = self.get_vnfinstid(self.m_vnfInstanceId, self.vnfmid)
            self.update_Vnfc()
            self.update_Vl()
            self.update_Cp()
            self.update_Storage()
            #self.update_vnf_by_vnfdmodule()
            logger.debug("notify lcm end")
        except NSLCMException as e:
            self.exception(e.message)
        except Exception:
            logger.error(traceback.format_exc())
            self.exception('unexpected exception')

    def get_vnfinstid(self, mnfinstid, vnfm_inst_id):
        nfinst = NfInstModel.objects.filter(mnfinstid=mnfinstid, vnfm_inst_id=vnfm_inst_id).first()
        if nfinst:
            return nfinst.nfinstid
        else:
            self.exception('vnfinstid not exist')

    def exception(self, error_msg):
        logger.error('Notify Lcm failed, detail message: %s' % error_msg)
        return Response(data={'error': '%s' % error_msg}, status=status.HTTP_409_CONFLICT)

    def update_Vnfc(self):
        for vnfc in self.affectedVnfc:
            vnfcInstanceId = ignore_case_get(vnfc, 'vnfcInstanceId')
            vduId = ignore_case_get(vnfc, 'vduId')
            changeType = ignore_case_get(vnfc, 'changeType')
            vimId = ignore_case_get(vnfc, 'vimid')
            vmId = ignore_case_get(vnfc, 'vmid')
            vmName = ignore_case_get(vnfc, 'vmname')
            # resourceType = ignore_case_get(vmResource, 'resourceType')
            # resourceId = ignore_case_get(vmId, 'resourceId')


            # if resourceType != 'vm':
            #     self.exception('affectedVnfc struct error: resourceType not euqal vm')

            if changeType == 'added':
                VNFCInstModel(vnfcinstanceid=vnfcInstanceId, vduid=vduId,
                              nfinstid=self.vnf_instid, vmid=vmId).save()
                VmInstModel(vmid=vmId, vimid=vimId, resouceid=vmId, insttype=INST_TYPE.VNF,
                            instid=self.vnf_instid, vmname=vmName, hostid='1').save()
            elif changeType == 'removed':
                VNFCInstModel.objects.filter(vnfcinstanceid=vnfcInstanceId).delete()
            elif changeType == 'modified':
                VNFCInstModel.objects.filter(vnfcinstanceid=vnfcInstanceId).update(vduid=vduId,
                                                                                   nfinstid=self.vnf_instid,
                                                                                   vmid=vmId)
            else:
                self.exception('affectedVnfc struct error: changeType not in {added,removed,modified}')

    def update_Vl(self):
        for vl in self.affectedVl:
            vlInstanceId = ignore_case_get(vl, 'vlInstanceId')
            vldid = ignore_case_get(vl, 'vldid')
            changeType = ignore_case_get(vl, 'changeType')
            networkResource = ignore_case_get(vl, 'networkResource')
            resourceType = ignore_case_get(networkResource, 'resourceType')
            resourceId = ignore_case_get(networkResource, 'resourceId')

            if resourceType != 'network':
                self.exception('affectedVl struct error: resourceType not euqal network')

            ownerId = self.vnf_instid
            ownerId = self.get_vnfinstid(self.vnf_instid, self.vnfmid)

            if changeType == 'added':
                VLInstModel(vlInstanceId=vlInstanceId, vldId=vldid, ownerType=0, ownerId=ownerId,
                            relatedNetworkId=resourceId, vlType=0).save()
            elif changeType == 'removed':
                VLInstModel.objects.filter(vlInstanceId=vlInstanceId).delete()
            elif changeType == 'modified':
                VLInstModel.objects.filter(vlInstanceId=vlInstanceId)\
                    .update(vldId=vldid, ownerType=0, ownerId=ownerId, relatedNetworkId=resourceId, vlType=0)
            else:
                self.exception('affectedVl struct error: changeType not in {added,removed,modified}')

    def update_Cp(self):
        for cp in self.affectedCp:
            virtualLinkInstanceId = ignore_case_get(cp, 'virtualLinkInstanceId')
            #ownerid = ignore_case_get(cp, 'ownerid')
            ownertype = ignore_case_get(cp, 'ownertype')
            if not ownertype:
                ownertype = 0
            ownerid = self.vnf_instid if str(ownertype) == "0" else ignore_case_get(cp, 'ownerid')
            cpInstanceId = ignore_case_get(cp, 'cpinstanceid')
            cpdId = ignore_case_get(cp, 'cpdid')
            changeType = ignore_case_get(cp, 'changetype')
            relatedportId = ''
            portResource = ignore_case_get(cp, 'portResource')
            if portResource:
                vimId = ignore_case_get(portResource, 'vimid')
                resourceId = ignore_case_get(portResource, 'resourceid')
                resourceName = ignore_case_get(portResource, 'resourceName')
                tenant = ignore_case_get(portResource, 'tenant')
                ipAddress = ignore_case_get(portResource, 'ipAddress')
                macAddress = ignore_case_get(portResource, 'macAddress')
                sfcEncapsulation = ignore_case_get(portResource, 'sfcEncapsulation')
                instId = ignore_case_get(portResource, 'instId')
                portid = str(uuid.uuid4())
                PortInstModel(portid=portid, networkid='unknown', subnetworkid='unknown', vimid=vimId,
                              resourceid=resourceId, name=resourceName, instid=instId, cpinstanceid=cpInstanceId,
                              bandwidth='unknown', operationalstate='active', ipaddress=ipAddress, macaddress=macAddress,
                              floatipaddress='unknown', serviceipaddress='unknown', typevirtualnic='unknown',
                              sfcencapsulation='gre', direction='unknown', tenant=tenant).save()
                relatedportId = portid

            if changeType == 'added':
                CPInstModel(cpinstanceid=cpInstanceId, cpdid=cpdId, ownertype=ownertype, ownerid=ownerid,
                            relatedtype=2, relatedport=relatedportId, status='active').save()
            elif changeType == 'removed':
                CPInstModel.objects.filter(cpinstanceid=cpInstanceId).delete()
            elif changeType == 'changed':
                CPInstModel.objects.filter(cpinstanceid=cpInstanceId).update(cpdid=cpdId, ownertype=ownertype,
                                                                             ownerid=ownerid,
                                                                             vlinstanceid=virtualLinkInstanceId,
                                                                             relatedtype=2, relatedport=relatedportId)
            else:
                self.exception('affectedVl struct error: changeType not in {added,removed,modified}')

    def update_Storage(self):
        pass

    def update_vnf_by_vnfdmodule(self):
        NfInstModel.objects.filter(nfinstid=self.vnf_instid).update(vnfd_model=self.vnfdmodule)
