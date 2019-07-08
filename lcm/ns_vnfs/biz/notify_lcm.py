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
import traceback
import uuid

from rest_framework import status
from rest_framework.response import Response

from lcm.pub.config.config import REPORT_TO_AAI
from lcm.pub.database.models import VNFCInstModel, VLInstModel, NfInstModel, PortInstModel, CPInstModel, VmInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.aai import create_network_aai, query_network_aai, delete_network_aai, query_vserver_aai, \
    delete_vserver_aai
from lcm.pub.msapi.aai import create_vserver_aai
from lcm.pub.msapi.extsys import split_vim_to_owner_region, get_vim_by_id
from lcm.pub.utils.values import ignore_case_get
from lcm.ns_vnfs.enum import INST_TYPE

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
            if REPORT_TO_AAI:
                self.update_network_in_aai()
            logger.debug("notify lcm end")
        except NSLCMException as e:
            self.exception(e.args[0])
        except Exception:
            logger.error(traceback.format_exc())
            self.exception('unexpected exception')

    def get_vnfinstid(self, mnfinstid, vnfm_inst_id):
        logger.debug("vnfinstid in vnfm is:%s,vnfmid is:%s", mnfinstid, vnfm_inst_id)
        logger.debug("mnfinstid=%s, vnfm_inst_id=%s", mnfinstid, vnfm_inst_id)
        nfinst = NfInstModel.objects.filter(mnfinstid=mnfinstid, vnfm_inst_id=vnfm_inst_id).first()
        if nfinst:
            return nfinst.nfinstid
        raise NSLCMException("vnfinstid not exist")

    def exception(self, error_msg):
        logger.error('Notify Lcm failed, detail message: %s' % error_msg)
        return Response(data={'error': '%s' % error_msg}, status=status.HTTP_409_CONFLICT)

    def update_Vnfc(self):
        for vnfc in self.affectedVnfc:
            vnfcInstanceId = ignore_case_get(vnfc, 'vnfcInstanceId')
            vduId = ignore_case_get(vnfc, 'vduId')
            changeType = ignore_case_get(vnfc, 'changeType')
            vimId = ignore_case_get(vnfc, 'vimId')
            vmId = ignore_case_get(vnfc, 'vmId')
            vmName = ignore_case_get(vnfc, 'vmName')

            if changeType == 'added':
                VNFCInstModel(vnfcinstanceid=vnfcInstanceId, vduid=vduId,
                              nfinstid=self.vnf_instid, vmid=vmId).save()
                VmInstModel(vmid=vmId, vimid=vimId, resouceid=vmId, insttype=INST_TYPE.VNF,
                            instid=self.vnf_instid, vmname=vmName, hostid='1').save()
                if REPORT_TO_AAI:
                    self.create_vserver_in_aai(vimId, vmId, vmName)
            elif changeType == 'removed':
                if REPORT_TO_AAI:
                    self.delete_vserver_in_aai(vimId, vmId, vmName)
                VNFCInstModel.objects.filter(vnfcinstanceid=vnfcInstanceId).delete()
            elif changeType == 'modified':
                VNFCInstModel.objects.filter(vnfcinstanceid=vnfcInstanceId).update(vduid=vduId,
                                                                                   nfinstid=self.vnf_instid,
                                                                                   vmid=vmId)
            else:
                self.exception('affectedVnfc struct error: changeType not in {added,removed,modified}')
        logger.debug("Success to update all vserver to aai.")

    def delete_vserver_in_aai(self, vim_id, vserver_id, vserver_name):
        logger.debug("delete_vserver_in_aai start![%s]", vserver_name)
        try:
            cloud_owner, cloud_region_id = split_vim_to_owner_region(vim_id)
            # query vim_info from aai, get tenant
            vim_info = get_vim_by_id(vim_id)
            tenant_id = vim_info["tenantId"]

            # query vserver instance in aai, get resource_version
            vserver_info = query_vserver_aai(cloud_owner, cloud_region_id, tenant_id, vserver_id)
            resource_version = vserver_info["resource-version"]

            # delete vserver instance from aai
            resp_data, resp_status = delete_vserver_aai(cloud_owner, cloud_region_id,
                                                        tenant_id, vserver_id, resource_version)
            logger.debug(
                "Success to delete vserver instance[%s] from aai, resp_status: [%s]." %
                (vserver_id, resp_status))
            logger.debug("delete_vserver_in_aai end!")
        except NSLCMException as e:
            logger.debug("Fail to delete vserver from aai, detail message: %s" % e.args[0])
        except:
            logger.error(traceback.format_exc())

    def update_Vl(self):
        for vl in self.affectedVl:
            vlInstanceId = ignore_case_get(vl, 'vlInstanceId')
            vldid = ignore_case_get(vl, 'vldId')
            changeType = ignore_case_get(vl, 'changeType')
            networkResource = ignore_case_get(vl, 'networkResource')
            resourceType = ignore_case_get(networkResource, 'resourceType')
            resourceId = ignore_case_get(networkResource, 'resourceId')
            resourceName = ignore_case_get(networkResource, 'resourceName')

            if resourceType != 'network':
                self.exception('affectedVl struct error: resourceType not euqal network')

            ownerId = self.get_vnfinstid(self.m_vnfInstanceId, self.vnfmid)

            if changeType == 'added':
                VLInstModel(vlinstanceid=vlInstanceId, vldid=vldid, vlinstancename=resourceName, ownertype=0,
                            ownerid=ownerId, relatednetworkid=resourceId, vltype=0).save()
            elif changeType == 'removed':
                VLInstModel.objects.filter(vlinstanceid=vlInstanceId).delete()
            elif changeType == 'modified':
                VLInstModel.objects.filter(vlinstanceid=vlInstanceId)\
                    .update(vldid=vldid, vlinstancename=resourceName, ownertype=0, ownerid=ownerId,
                            relatednetworkid=resourceId, vltype=0)
            else:
                self.exception('affectedVl struct error: changeType not in {added,removed,modified}')

    def update_Cp(self):
        for cp in self.affectedCp:
            virtualLinkInstanceId = ignore_case_get(cp, 'virtualLinkInstanceId')
            ownertype = ignore_case_get(cp, 'ownerType')
            if not ownertype:
                ownertype = 0
            ownerid = self.vnf_instid if str(ownertype) == "0" else ignore_case_get(cp, 'ownerId')
            cpInstanceId = ignore_case_get(cp, 'cpInstanceId')
            cpdId = ignore_case_get(cp, 'cpdId')
            changeType = ignore_case_get(cp, 'changeType')
            relatedportId = ''
            portResource = ignore_case_get(cp, 'portResource')
            if portResource:
                vimId = ignore_case_get(portResource, 'vimId')
                resourceId = ignore_case_get(portResource, 'resourceId')
                resourceName = ignore_case_get(portResource, 'resourceName')
                tenant = ignore_case_get(portResource, 'tenant')
                ipAddress = ignore_case_get(portResource, 'ipAddress')
                macAddress = ignore_case_get(portResource, 'macAddress')
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

    def update_network_in_aai(self):
        logger.debug("update_network_in_aai::begin to report network to aai.")
        try:
            for vl in self.affectedVl:
                vlInstanceId = ignore_case_get(vl, 'vlInstanceId')
                # vldid = ignore_case_get(vl, 'vldid')
                changeType = ignore_case_get(vl, 'changeType')
                networkResource = ignore_case_get(vl, 'networkResource')
                resourceType = ignore_case_get(networkResource, 'resourceType')
                # resourceId = ignore_case_get(networkResource, 'resourceId')

                if resourceType != 'network':
                    logger.error('affectedVl struct error: resourceType not euqal network')
                    raise NSLCMException("affectedVl struct error: resourceType not euqal network")

                ownerId = self.get_vnfinstid(self.m_vnfInstanceId, self.vnfmid)

                if changeType in ['added', 'modified']:
                    self.create_network_and_subnet_in_aai(vlInstanceId, ownerId)
                elif changeType == 'removed':
                    self.delete_network_and_subnet_in_aai(vlInstanceId)
                else:
                    logger.error('affectedVl struct error: changeType not in {added,removed,modified}')
        except NSLCMException as e:
            logger.debug("Fail to create internal network to aai, detail message: %s" % e.args[0])
        except:
            logger.error(traceback.format_exc())

    def create_network_and_subnet_in_aai(self, vlInstanceId, ownerId):
        logger.debug("CreateVls::create_network_in_aai::report network[%s] to aai." % vlInstanceId)
        try:
            data = {
                "network-id": vlInstanceId,
                "network-name": vlInstanceId,
                "is-bound-to-vpn": False,
                "is-provider-network": True,
                "is-shared-network": True,
                "is-external-network": True,
                "relationship-list": {
                    "relationship": [
                        {
                            "related-to": "generic-vnf",
                            "relationship-data": [
                                {
                                    "relationship-key": "generic-vnf.vnf-id",
                                    "relationship-value": ownerId
                                }
                            ]
                        }
                    ]
                }
            }
            resp_data, resp_status = create_network_aai(vlInstanceId, data)
            logger.debug("Success to create network[%s] to aai: [%s].", vlInstanceId, resp_status)
        except NSLCMException as e:
            logger.debug("Fail to create network[%s] to aai, detail message: %s" % (vlInstanceId, e.args[0]))
        except:
            logger.error(traceback.format_exc())

    def delete_network_and_subnet_in_aai(self, vlInstanceId):
        logger.debug("DeleteVls::delete_network_in_aai::delete network[%s] in aai." % vlInstanceId)
        try:
            # query network in aai, get resource_version
            customer_info = query_network_aai(vlInstanceId)
            resource_version = customer_info["resource-version"]

            # delete network from aai
            resp_data, resp_status = delete_network_aai(vlInstanceId, resource_version)
            logger.debug("Success to delete network[%s] from aai, resp_status: [%s]."
                         % (vlInstanceId, resp_status))
        except NSLCMException as e:
            logger.debug("Fail to delete network[%s] to aai, detail message: %s" % (vlInstanceId, e.args[0]))
        except:
            logger.error(traceback.format_exc())

    def create_vserver_in_aai(self, vim_id, vserver_id, vserver_name):
        logger.debug("NotifyLcm::create_vserver_in_aai::report vserver instance to aai.")
        try:
            cloud_owner, cloud_region_id = split_vim_to_owner_region(vim_id)

            # query vim_info from aai
            vim_info = get_vim_by_id(vim_id)
            tenant_id = vim_info["tenantId"]
            data = {
                "vserver-id": vserver_id,
                "vserver-name": vserver_name,
                "prov-status": "ACTIVE",
                "vserver-selflink": "",
                "in-maint": True,
                "is-closed-loop-disabled": False,
                "relationship-list": {
                    "relationship": [
                        {
                            "related-to": "generic-vnf",
                            "relationship-data": [
                                {
                                    "relationship-key": "generic-vnf.vnf-id",
                                    "relationship-value": self.vnf_instid
                                }
                            ]
                        }
                    ]
                }
            }

            # create vserver instance in aai
            resp_data, resp_status = create_vserver_aai(cloud_owner, cloud_region_id, tenant_id, vserver_id, data)
            logger.debug("Success to create vserver[%s] to aai, vnf instance=[%s], resp_status: [%s]."
                         % (vserver_id, self.vnf_instid, resp_status))
        except NSLCMException as e:
            logger.debug("Fail to create vserver to aai, vnf instance=[%s], detail message: %s"
                         % (self.vnf_instid, e.args[0]))
        except:
            logger.error(traceback.format_exc())
