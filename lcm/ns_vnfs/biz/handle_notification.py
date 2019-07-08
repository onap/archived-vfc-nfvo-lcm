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

from lcm.ns_vnfs.enum import INST_TYPE
from lcm.pub.config.config import REPORT_TO_AAI
from lcm.pub.database.models import (CPInstModel, NfInstModel, PortInstModel,
                                     VLInstModel, VmInstModel, VNFCInstModel)
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.aai import (create_network_aai, create_vserver_aai,
                               delete_network_aai, delete_vserver_aai,
                               query_network_aai, query_vserver_aai)
from lcm.pub.msapi.extsys import get_vim_by_id, split_vim_to_owner_region
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class HandleVnfLcmOocNotification(object):
    def __init__(self, vnfmid, vnfInstanceId, data):
        logger.debug("[Notify LCM] vnfmid=%s, vnfInstanceId=%s, data=%s" % (vnfmid, vnfInstanceId, data))
        self.vnfmid = vnfmid
        self.m_vnfInstanceId = vnfInstanceId
        self.vnf_instid = get_vnfinstid(self.m_vnfInstanceId, self.vnfmid)
        self.operation = ignore_case_get(data, 'operation')
        self.affectedVnfcs = ignore_case_get(data, 'affectedVnfcs')
        self.affectedVls = ignore_case_get(data, 'affectedVirtualLinks')
        self.affectedCps = ignore_case_get(data, 'changedExtConnectivity')
        self.affectedVirtualStorage = ignore_case_get(data, 'affectedVirtualStorages')

    def do_biz(self):
        try:
            self.update_Vnfc()
            self.update_Vl()
            self.update_Cp()
            self.update_Storage()
            if REPORT_TO_AAI:
                self.update_network_in_aai()
            logger.debug("notify lcm end")
        except NSLCMException as e:
            exception(e.args[0])
        except Exception:
            logger.error(traceback.format_exc())
            exception('unexpected exception')

    def update_Vnfc(self):
        for vnfc in self.affectedVnfcs:
            vnfcInstanceId = ignore_case_get(vnfc, 'id')
            vduId = ignore_case_get(vnfc, 'vduId')
            changeType = ignore_case_get(vnfc, 'changeType')
            computeResource = ignore_case_get(vnfc, 'computeResource')
            vimId = ignore_case_get(computeResource, "vimConnectionId")
            vmId = ignore_case_get(computeResource, 'resourceId')
            vmName = ignore_case_get(computeResource, 'resourceId')  # replaced with resouceId temporarily

            if changeType == 'ADDED':
                VNFCInstModel(vnfcinstanceid=vnfcInstanceId, vduid=vduId,
                              nfinstid=self.vnf_instid, vmid=vmId).save()
                VmInstModel(vmid=vmId, vimid=vimId, resouceid=vmId, insttype=INST_TYPE.VNF,
                            instid=self.vnf_instid, vmname=vmName, hostid='1').save()
                if REPORT_TO_AAI:
                    self.create_vserver_in_aai(vimId, vmId, vmName)
            elif changeType == 'REMOVED':
                if REPORT_TO_AAI:
                    self.delete_vserver_in_aai(vimId, vmId, vmName)
                VNFCInstModel.objects.filter(vnfcinstanceid=vnfcInstanceId).delete()
            elif changeType == 'MODIFIED':
                VNFCInstModel.objects.filter(vnfcinstanceid=vnfcInstanceId).update(vduid=vduId,
                                                                                   nfinstid=self.vnf_instid,
                                                                                   vmid=vmId)
            else:
                exception('affectedVnfc struct error: changeType not in {ADDED, REMOVED, MODIFIED, TEMPORARY}')
        logger.debug("Success to update all vserver to aai.")

    def update_Vl(self):
        for vl in self.affectedVls:
            vlInstanceId = ignore_case_get(vl, 'id')
            vldid = ignore_case_get(vl, 'virtualLinkDescId')
            changeType = ignore_case_get(vl, 'changeType')
            networkResource = ignore_case_get(vl, 'networkResource')
            resourceType = ignore_case_get(networkResource, 'vimLevelResourceType')
            resourceId = ignore_case_get(networkResource, 'resourceId')
            resourceName = ignore_case_get(networkResource, 'resourceId')  # replaced with resouceId temporarily

            if resourceType != 'network':
                exception('affectedVl struct error: resourceType not euqal network')

            ownerId = self.vnf_instid

            if changeType == 'ADDED':
                VLInstModel(vlinstanceid=vlInstanceId, vldid=vldid, vlinstancename=resourceName, ownertype=0,
                            ownerid=ownerId, relatednetworkid=resourceId, vltype=0).save()
            elif changeType == 'REMOVED':
                VLInstModel.objects.filter(vlinstanceid=vlInstanceId).delete()
            elif changeType == 'MODIFIED':
                VLInstModel.objects.filter(vlinstanceid=vlInstanceId)\
                    .update(vldid=vldid, vlinstancename=resourceName, ownertype=0, ownerid=ownerId,
                            relatednetworkid=resourceId, vltype=0)
            else:
                exception('affectedVl struct error: changeType not in {ADDED, REMOVED, MODIFIED, TEMPORARY}')

    def update_Cp(self):
        for cp in self.affectedCps:
            virtualLinkInstanceId = ignore_case_get(cp, 'id')
            ownertype = 0
            ownerid = self.vnf_instid
            for extLinkPorts in ignore_case_get(cp, 'extLinkPorts'):
                cpInstanceId = ignore_case_get(extLinkPorts, 'cpInstanceId')
                cpdId = ignore_case_get(extLinkPorts, 'id')
                # changeType = ignore_case_get(cp, 'changeType')
                relatedportId = ''

                portResource = ignore_case_get(extLinkPorts, 'resourceHandle')
                if portResource:
                    vimId = ignore_case_get(portResource, 'vimConnectionId')
                    resourceId = ignore_case_get(portResource, 'resourceId')
                    resourceName = ignore_case_get(portResource, 'resourceId')  # replaced with resouceId temporarily
                    # tenant = ignore_case_get(portResource, 'tenant')
                    # ipAddress = ignore_case_get(portResource, 'ipAddress')
                    # macAddress = ignore_case_get(portResource, 'macAddress')
                    # instId = ignore_case_get(portResource, 'instId')
                    portid = str(uuid.uuid4())

                    PortInstModel(portid=portid, networkid='unknown', subnetworkid='unknown', vimid=vimId,
                                  resourceid=resourceId, name=resourceName, instid="unknown", cpinstanceid=cpInstanceId,
                                  bandwidth='unknown', operationalstate='active', ipaddress="unkown",
                                  macaddress='unknown',
                                  floatipaddress='unknown', serviceipaddress='unknown', typevirtualnic='unknown',
                                  sfcencapsulation='gre', direction='unknown', tenant="unkown").save()
                    relatedportId = portid

                CPInstModel(cpinstanceid=cpInstanceId, cpdid=cpdId, ownertype=ownertype, ownerid=ownerid,
                            vlinstanceid=virtualLinkInstanceId, relatedtype=2, relatedport=relatedportId,
                            status='active').save()

    def update_Storage(self):
        pass

    def update_network_in_aai(self):
        logger.debug("update_network_in_aai::begin to report network to aai.")
        try:
            for vl in self.affectedVls:
                vlInstanceId = ignore_case_get(vl, 'id')
                # vldid = ignore_case_get(vl, 'vldid')
                changeType = ignore_case_get(vl, 'changeType')
                networkResource = ignore_case_get(vl, 'networkResource')
                resourceType = ignore_case_get(networkResource, 'vimLevelResourceType')
                # resourceId = ignore_case_get(networkResource, 'resourceId')

                if resourceType != 'network':
                    logger.error('affectedVl struct error: resourceType not euqal network')
                    raise NSLCMException("affectedVl struct error: resourceType not euqal network")

                ownerId = self.vnf_instid

                if changeType in ['ADDED', 'MODIFIED']:
                    self.create_network_and_subnet_in_aai(vlInstanceId, ownerId)
                elif changeType == 'REMOVED':
                    self.delete_network_and_subnet_in_aai(vlInstanceId)
                else:
                    logger.error('affectedVl struct error: changeType not in {ADDED, REMOVED, MODIFIED, TEMPORARY}')
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


class HandleVnfIdentifierCreationNotification(object):
    def __init__(self, vnfmId, vnfInstanceId, data):
        logger.debug("[Notify VNF Identifier Creation] vnfmId=%s, vnfInstanceId=%s, data=%s" % (vnfmId, vnfInstanceId, data))
        self.vnfm_id = vnfmId
        self.m_vnf_instance_id = vnfInstanceId
        self.time_stamp = ignore_case_get(data, 'timeStamp')
        # TODO: self.subscription_id = ignore_case_get(data, 'subscriptionId')
        # TODO: self._links = ignore_case_get(data, '_links')

    def do_biz(self):
        try:
            NfInstModel(
                nfinstid=str(uuid.uuid4()),
                mnfinstid=self.m_vnf_instance_id,
                vnfm_inst_id=self.vnfm_id,
                create_time=self.time_stamp
            ).save()
            logger.debug("Notify VNF identifier creation end.")
        except Exception:
            logger.error(traceback.format_exc())
            exception('unexpected exception')


class HandleVnfIdentifierDeletionNotification(object):
    def __init__(self, vnfmId, vnfInstanceId, data):
        logger.debug("[Notify VNF Identifier Deletion] vnfmId=%s, vnfInstanceId=%s, data=%s" % (vnfmId, vnfInstanceId, data))
        self.vnfm_id = vnfmId
        self.m_vnf_instance_id = vnfInstanceId
        self.vnf_instance_id = get_vnfinstid(self.m_vnf_instance_id, self.vnfm_id)
        self.time_stamp = ignore_case_get(data, 'timeStamp')
        # TODO: self.subscription_id = ignore_case_get(data, 'subscriptionId')
        # TODO: self._links = ignore_case_get(data, '_links')

    def do_biz(self):
        try:
            nf_insts = NfInstModel.objects.filter(
                mnfinstid=self.m_vnf_instance_id, vnfm_inst_id=self.vnfm_id)
            if nf_insts.exists():
                nf_insts.delete()
            logger.debug("Notify VNF identifier deletion end.")
        except Exception:
            logger.error(traceback.format_exc())
            exception('unexpected exception')


def get_vnfinstid(mnfinstid, vnfm_inst_id):
    logger.debug("vnfinstid in vnfm is:%s,vnfmid is:%s", mnfinstid, vnfm_inst_id)
    logger.debug("mnfinstid=%s, vnfm_inst_id=%s", mnfinstid, vnfm_inst_id)
    nfinst = NfInstModel.objects.filter(mnfinstid=mnfinstid, vnfm_inst_id=vnfm_inst_id).first()
    if nfinst:
        return nfinst.nfinstid
    raise NSLCMException("vnfinstid not exist")


def exception(error_msg):
    logger.error('Notify Lcm failed, detail message: %s' % error_msg)
    return Response(data={'error': '%s' % error_msg}, status=status.HTTP_409_CONFLICT)
