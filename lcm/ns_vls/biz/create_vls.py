# Copyright 2016-2017 ZTE Corporation.
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
import uuid

from lcm.ns.enum import OWNER_TYPE
from lcm.pub.config.config import REPORT_TO_AAI
from lcm.pub.database.models import VLInstModel, NSInstModel, VNFFGInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi import extsys, resmgr
from lcm.pub.msapi.aai import create_network_aai
from lcm.pub.nfvi.vim import const
from lcm.pub.nfvi.vim import vimadaptor
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class CreateVls(object):
    def __init__(self, data):
        self.owner_id = ignore_case_get(data, "nsInstanceId")
        self.index = int(float(ignore_case_get(data, "vlIndex")))
        self.context = ignore_case_get(data, "context")
        self.additionalParam = ignore_case_get(data, "additionalParamForNs")
        self.vl_inst_id = str(uuid.uuid4())
        self.owner_type = OWNER_TYPE.NS
        self.vld_id = ""
        self.vl_properties = ""
        self.vl_profile = ""
        self.vl_inst_name = ""
        self.related_network_id = ""
        self.related_subnetwork_id = ""
        self.vim_id = ""
        self.vim_name = ""
        self.tenant = ""
        self.description = ""
        self.route_external = ""
        self.ns_name = ""

    def do(self):
        try:
            self.get_data()
            self.create_vl_to_vim()
            self.create_vl_to_resmgr()
            self.save_vl_to_db()
            if REPORT_TO_AAI:
                self.create_network_and_subnet_in_aai()
            return {"result": 0, "detail": "instantiation vl success", "vlId": self.vl_inst_id}
        except NSLCMException as e:
            return self.exception_handle(e)
        except Exception as e:
            logger.error(traceback.format_exc())
            return self.exception_handle(e)

    def exception_handle(self, e):
        detail = "vl instantiation failed, detail message: %s" % e.args[0]
        logger.error(detail)
        return {"result": 1, "detail": detail, "vlId": self.vl_inst_id}

    def get_data(self):
        if isinstance(self.context, str):
            self.context = json.JSONDecoder().decode(self.context)
        vl_info = self.get_vl_info(ignore_case_get(self.context, "vls"))
        self.vld_id = ignore_case_get(vl_info, "vl_id")
        self.description = ignore_case_get(vl_info, "description")
        self.vl_properties = ignore_case_get(vl_info, "properties")
        self.vl_profile = ignore_case_get(self.vl_properties, "vl_profile")
        self.vl_inst_name = ignore_case_get(self.vl_profile, "networkName")
        self.route_external = ignore_case_get(vl_info, "route_external")
        ns_info = NSInstModel.objects.filter(id=self.owner_id)
        self.ns_name = ns_info[0].name if ns_info else ""

    def get_vl_info(self, vl_all_info):
        return vl_all_info[self.index - 1]

    def create_vl_to_vim(self):
        self.vim_id = self.vl_properties["location_info"]["vimid"]
        if not self.vim_id:
            if isinstance(self.additionalParam, str):
                self.additionalParam = json.JSONDecoder().decode(self.additionalParam)
            self.vim_id = ignore_case_get(self.additionalParam, "location")
        self.tenant = ignore_case_get(self.vl_properties["location_info"], "tenant")
        network_data = {
            "tenant": self.tenant,
            "network_name": self.vl_profile.get("networkName", ""),
            "shared": const.SHARED_NET,
            "network_type": self.vl_profile.get("networkType", ""),
            "segmentation_id": self.vl_profile.get("segmentationId", ""),
            "physical_network": self.vl_profile.get("physicalNetwork", ""),
            "mtu": self.vl_profile.get("mtu", const.DEFAULT_MTU),
            "vlan_transparent": self.vl_profile.get("vlanTransparent", False),
            "subnet_list": [{
                "subnet_name": self.vl_profile.get("networkName"),  # self.vl_profile.get("initiationParameters").get("name", ""),
                "cidr": self.vl_profile.get("cidr", "192.168.0.0/24"),
                "ip_version": self.vl_profile.get("ip_version", const.IPV4),
                "enable_dhcp": self.vl_profile.get("dhcpEnabled", False),
                "gateway_ip": self.vl_profile.get("gatewayIp", ""),
                "dns_nameservers": self.vl_profile.get("dns_nameservers", ""),
                "host_routes": self.vl_profile.get("host_routes", "")}]}
        startip = self.vl_profile.get("startIp", "")
        endip = self.vl_profile.get("endIp", "")
        if startip and endip:
            network_data["subnet_list"][0]["allocation_pools"] = [
                {"start": startip, "end": endip}]

        vl_resp = self.create_network_to_vim(network_data)
        self.related_network_id = vl_resp["id"]
        self.related_subnetwork_id = vl_resp["subnet_list"][0]["id"] if vl_resp["subnet_list"] else ""

    def create_network_to_vim(self, network_data):
        vim_resp_body = extsys.get_vim_by_id(self.vim_id)
        self.vim_name = vim_resp_body["name"]
        data = {
            "vimid": self.vim_id,
            "vimtype": vim_resp_body["type"],
            "url": vim_resp_body["url"],
            "user": vim_resp_body["userName"],
            "passwd": vim_resp_body["password"],
            "tenant": vim_resp_body["tenant"]}
        vim_api = vimadaptor.VimAdaptor(data)
        if not network_data["tenant"]:
            network_data["tenant"] = vim_resp_body["tenant"]
        vl_ret = vim_api.create_network(network_data)
        if vl_ret[0] != 0:
            logger.error("Send post vl request to vim failed, detail is %s" % vl_ret[1])
            raise NSLCMException("Send post vl request to vim failed.")
        return vl_ret[1]

    def create_vl_to_resmgr(self):
        self.vim_id = json.JSONDecoder().decode(self.vim_id) if isinstance(self.vim_id, str) else self.vim_id
        vim_id = self.vim_id['cloud_owner'] + self.vim_id['cloud_regionid']
        req_param = {
            "vlInstanceId": self.vl_inst_id,
            "name": self.vl_profile.get("networkName", ""),
            "backendId": str(self.related_network_id),
            "isPublic": "True",
            "dcName": "",
            "vimId": str(vim_id),
            "vimName": self.vim_name,
            "physicialNet": self.vl_profile.get("physicalNetwork", ""),
            "nsId": self.owner_id,
            "nsName": self.ns_name,
            "description": self.description,
            "networkType": self.vl_profile.get("networkType", ""),
            "segmentation": str(self.vl_profile.get("segmentationId", "")),
            "mtu": str(self.vl_profile.get("mtu", "")),
            "vlanTransparent": str(self.vl_profile.get("vlanTransparent", "")),
            "routerExternal": self.route_external,
            "resourceProviderType": "",
            "resourceProviderId": "",
            "subnet_list": [{
                "subnet_name": self.vl_profile.get("networkName", ""),  # self.vl_profile.get("initiationParameters").get("name", ""),
                "cidr": self.vl_profile.get("cidr", "192.168.0.0/24"),
                "ip_version": self.vl_profile.get("ip_version", const.IPV4),
                "enable_dhcp": self.vl_profile.get("dhcpEnabled", False),
                "gateway_ip": self.vl_profile.get("gatewayIp", ""),
                "dns_nameservers": self.vl_profile.get("dns_nameservers", ""),
                "host_routes": self.vl_profile.get("host_routes", "")
            }]
        }
        resmgr.create_vl(req_param)

    def create_vl_inst_id_in_vnffg(self):
        if "vnffgs" in self.context:
            for vnffg_info in self.context["vnffgs"]:
                vl_id_list = vnffg_info.get("properties", {}).get("dependent_virtual_link", "")
                if vl_id_list:
                    vl_inst_id_list = []
                    for vl_id in vl_id_list:
                        vl_inst_info = VLInstModel.objects.filter(vldid=vl_id)
                        if vl_inst_info:
                            vl_inst_id_list.append(vl_inst_info[0].vlinstanceid)
                        else:
                            vl_inst_id_list.append("")
                    vl_inst_id_str = ""
                    for vl_inst_id in vl_inst_id_list:
                        vl_inst_id_str += vl_inst_id + ","
                    vl_inst_id_str = vl_inst_id_str[:-1]
                    VNFFGInstModel.objects.filter(vnffgdid=vnffg_info["vnffg_id"], nsinstid=self.owner_id).update(
                        vllist=vl_inst_id_str)

    def save_vl_to_db(self):
        vim_id = json.JSONEncoder().encode(self.vim_id)
        VLInstModel(vlinstanceid=self.vl_inst_id, vldid=self.vld_id, vlinstancename=self.vl_inst_name,
                    ownertype=self.owner_type, ownerid=self.owner_id, relatednetworkid=self.related_network_id,
                    relatedsubnetworkid=self.related_subnetwork_id, vimid=vim_id, tenant=self.tenant).save()
        # do_biz_with_share_lock("create-vllist-in-vnffg-%s" % self.owner_id, self.create_vl_inst_id_in_vnffg)
        self.create_vl_inst_id_in_vnffg()

    def create_network_and_subnet_in_aai(self):
        logger.debug("CreateVls::create_network_in_aai::report network[%s] to aai." % self.vl_inst_id)
        try:
            ns_insts = NSInstModel.objects.filter(id=self.owner_id)
            self.global_customer_id = ns_insts[0].global_customer_id
            self.service_type = ns_insts[0].service_type
            data = {
                "network-id": self.vl_inst_id,
                "network-name": self.vl_inst_name,
                "is-bound-to-vpn": False,
                "is-provider-network": True,
                "is-shared-network": True,
                "is-external-network": True,
                "subnets": {
                    "subnet": [
                        {
                            "subnet-id": self.related_subnetwork_id,
                            "dhcp-enabled": False
                        }
                    ]
                },
                "relationship-list": {
                    "relationship": [
                        {
                            "related-to": "service-instance",
                            "relationship-data": [
                                {
                                    "relationship-key": "customer.global-customer-id",
                                    "relationship-value": self.global_customer_id
                                },
                                {
                                    "relationship-key": "service-subscription.service-type",
                                    "relationship-value": self.service_type
                                },
                                {
                                    "relationship-key": "service-instance.service-instance-id",
                                    "relationship-value": self.owner_id
                                }
                            ]
                        }
                    ]
                }
            }
            resp_data, resp_status = create_network_aai(self.vl_inst_id, data)
            logger.debug("Success to create network[%s] to aai: [%s].", self.vl_inst_id, resp_status)
        except NSLCMException as e:
            logger.debug("Fail to create network[%s] to aai, detail message: %s" % (self.vl_inst_id, e.args[0]))
        except:
            logger.error(traceback.format_exc())
