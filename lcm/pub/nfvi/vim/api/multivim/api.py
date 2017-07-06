# Copyright 2017 ZTE Corporation.
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

from lcm.pub.nfvi.vim.lib.vimexception import VimException
from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.nfvi.vim import const

logger = logging.getLogger(__name__)

VIM_DRIVER_BASE_URL = "openoapi/multivim/v1"

def call(vim_id, tenant_id, res, method, data=''):
    if data and not isinstance(data, (str, unicode)):
        data = json.JSONEncoder().encode(data)
    url = "{base_url}/{vim_id}{tenant_id}/{res}".format(
        base_url=VIM_DRIVER_BASE_URL, 
        vim_id=vim_id,
        tenant_id="/" + tenant_id if tenant_id else "",
        res=res)
    ret = req_by_msb(url, method, data)
    if ret[0] > 0:
        raise VimException(ret[1], ret[2])
    return json.JSONDecoder().decode(ret[1]) if ret[1] else {}

######################################################################

def create_image(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "images", "POST", data)

def delete_image(vim_id, tenant_id, image_id):
    return call(vim_id, tenant_id, "images/%s" % image_id, "DELETE")
    
def get_image(vim_id, tenant_id, image_id):
    return call(vim_id, tenant_id, "images/%s" % image_id, "GET")
    
def list_image(vim_id, tenant_id):
    return call(vim_id, tenant_id, "images", "GET")

######################################################################

def create_network(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "networks", "POST", data)

def delete_network(vim_id, tenant_id, network_id):
    return call(vim_id, tenant_id, "networks/%s" % network_id, "DELETE")
    
def get_network(vim_id, tenant_id, network_id):
    return call(vim_id, tenant_id, "networks/%s" % network_id, "GET")
    
def list_network(vim_id, tenant_id):
    return call(vim_id, tenant_id, "networks", "GET")

######################################################################

def create_subnet(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "subnets", "POST", data)

def delete_subnet(vim_id, tenant_id, subnet_id):
    return call(vim_id, tenant_id, "subnets/%s" % subnet_id, "DELETE")
    
def get_subnet(vim_id, tenant_id, subnet_id):
    return call(vim_id, tenant_id, "subnets/%s" % subnet_id, "GET")
    
def list_subnet(vim_id, tenant_id):
    return call(vim_id, tenant_id, "subnets", "GET")

######################################################################

def create_port(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "ports", "POST", data)

def delete_port(vim_id, tenant_id, port_id):
    return call(vim_id, tenant_id, "ports/%s" % port_id, "DELETE")
    
def get_port(vim_id, tenant_id, port_id):
    return call(vim_id, tenant_id, "ports/%s" % port_id, "GET")
    
def list_port(vim_id, tenant_id):
    return call(vim_id, tenant_id, "ports", "GET")

######################################################################

def create_flavor(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "flavors", "POST", data)

def delete_flavor(vim_id, tenant_id, flavor_id):
    return call(vim_id, tenant_id, "flavors/%s" % flavor_id, "DELETE")
    
def get_flavor(vim_id, tenant_id, flavor_id):
    return call(vim_id, tenant_id, "flavors/%s" % flavor_id, "GET")
    
def list_flavor(vim_id, tenant_id):
    return call(vim_id, tenant_id, "flavors", "GET")

######################################################################

def create_vm(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "servers", "POST", data)

def delete_vm(vim_id, tenant_id, vm_id):
    return call(vim_id, tenant_id, "servers/%s" % vm_id, "DELETE")
    
def get_vm(vim_id, tenant_id, vm_id):
    return call(vim_id, tenant_id, "servers/%s" % vm_id, "GET")
    
def list_vm(vim_id, tenant_id):
    return call(vim_id, tenant_id, "servers", "GET")

######################################################################

def create_volume(vim_id, tenant_id, data):
    return call(vim_id, tenant_id, "volumes", "POST", data)

def delete_volume(vim_id, tenant_id, volume_id):
    return call(vim_id, tenant_id, "volumes/%s" % volume_id, "DELETE")
    
def get_volume(vim_id, tenant_id, volume_id):
    return call(vim_id, tenant_id, "volumes/%s" % volume_id, "GET")
    
def list_volume(vim_id, tenant_id):
    return call(vim_id, tenant_id, "volumes", "GET")

######################################################################

def list_tenant(vim_id, tenant_name=""):
    res = "tenants"
    if tenant_name:
        res = "%s?name=%s" % (res, tenant_name)
    return call(vim_id, "", res, "GET")

######################################################################


class MultiVimApi:

    def login(self, connect_info):
        self.vim_id = connect_info["vimid"]
        self.tenant_name = connect_info["tenant"]
        tenants = list_tenant(self.vim_id)
        for tenant in tenants["tenants"]:
            if self.tenant_name == tenant["name"]:
                self.tenant_id = tenant["id"]
                return [0, connect_info]
        raise VimException(1, "Tenant(%s) not exist" % self.tenant_name)

    def query_net(self, auth_info, net_id):
        net = get_network(self.vim_id, self.tenant_id, net_id)
        return [0, {
            "id": net.get("id", ""),
            "name": net.get("name", ""),
            "status": net.get("status", ""),
            "admin_state_up": net.get("admin_state_up", True),
            "network_type": net.get("networkType", ""),
            "physical_network": net.get("physicalNetwork", ""),
            "segmentation_id": net.get("segmentationId", ""),
            "tenant_id": self.tenant_id,
            "tenant_name": self.tenant_name,
            "subnets": net.get("subnets", []),
            "shared": net.get("shared", True),
            "router_external": net.get("routerExternal", "")
        }]

    def query_nets(self, auth_info):
        nets = list_network(self.vim_id, self.tenant_id)
        return [0, {"networks": [{
            "id": net.get("id", ""),
            "name": net.get("name", ""),
            "status": net.get("status", ""),
            "admin_state_up": net.get("admin_state_up", True),
            "network_type": net.get("networkType", ""),
            "physical_network": net.get("physicalNetwork", ""),
            "segmentation_id": net.get("segmentationId", ""),
            "tenant_id": self.tenant_id,
            "tenant_name": self.tenant_name,
            "subnets": net.get("subnets", []),
            "shared": net.get("shared", True),
            "router_external": net.get("routerExternal", "")
        } for net in nets["networks"]]}]      

    def query_subnet(self, auth_info, subnet_id):
        subnet_info = get_subnet(self.vim_id, self.tenant_id, subnet_id)
        ret = [0, {}]
        ret[1]["id"] = subnet_id
        ret[1]["name"] = subnet_info.get("name", "")
        ret[1]["status"] = ""
        ret[1]["ip_version"] = subnet_info.get("ipVersion", 4)
        ret[1]["cidr"] = subnet_info.get("cidr", "")
        ret[1]["allocation_pools"] = subnet_info.get("allocationPools", [])
        ret[1]["enable_dhcp"] = subnet_info.get("enableDhcp", False)
        ret[1]["gateway_ip"] = subnet_info.get("gatewayIp", "")
        ret[1]["host_routes"] = subnet_info.get("hostRoutes", [])
        ret[1]["dns_nameservers"] = subnet_info.get("dnsNameservers", [])
        return ret

    def query_port(self, auth_info, port_id):
        port_info = get_port(self.vim_id, self.tenant_id, port_id)
        ret = [0, {}]
        ret[1]["id"] = port_id
        ret[1]["name"] = port_info.get("name", "")
        ret[1]["network_id"] = port_info.get("networkId", "")
        ret[1]["tenant_id"] = self.tenant_id,
        ret[1]["ip"] = port_info.get("ip", "")
        ret[1]["subnet_id"] = port_info.get("subnetId", "")
        ret[1]["mac_address"] = port_info.get("macAddress", "")
        ret[1]["status"] = port_info.get("status", "")
        ret[1]["admin_state_up"] = port_info.get("admin_state_up", True)
        ret[1]["device_id"] = port_info.get("device_id", "")
        return ret

    def create_port(self, auth_info, data):
        return [0, data]

    def delete_port(self, auth_info, port_id):
        return [0, ""]

    def create_image(self, auth_info, data):
        image_data = {
            "name": data["image_name"],
            "imagePath": data["image_url"],
            "imageType": data["image_type"],
            "containerFormat": "bare",
            "visibility": "public",
            "properties": [] 
        }
        image = create_image(self.vim_id, self.tenant_id, image_data)
        return [0, {
            "id": image["id"], 
            "name": image["name"], 
            const.RES_TYPE_KEY: image["returnCode"]}]

    def get_image(self, auth_info, image_id):
        image = get_image(self.vim_id, self.tenant_id, image_id)
        return [0, {
            "id": image["id"], 
            "name": image["name"], 
            "size": image["size"], 
            "status": image["status"]}]      

    def get_images(self, auth_info):
        images = list_image(self.vim_id, self.tenant_id)
        return [0, {"image_list": [{
            "id": img["id"], 
            "name": img["name"], 
            "size": img["size"], 
            "status": img["status"]
            } for img in images["images"]]}]

    def delete_image(self, auth_info, image_id):
        return [0, ""]

    def create_network(self, auth_info, data):
        net_data = {
            "name": data["network_name"],
            "shared": True,
            "networkType": data["network_type"]
        }
        if "physical_network" in data and data['physical_network']:
            net_data["physicalNetwork"] = data['physical_network']
        if "vlan_transparent" in data and data["vlan_transparent"]: 
            net_data["vlanTransparent"] = data["vlan_transparent"]
        if "segmentation_id" in data and data['segmentation_id']:
            net_data["segmentationId"] = data["segmentation_id"]
        if "routerExternal" in data and data['routerExternal']:
            net_data["routerExternal"] = data["routerExternal"]
        net = create_network(self.vim_id, self.tenant_id, net_data)
        network_id = net["id"]
        ret_net = {
            "status": net.get("status", ""),
            "id": network_id,
            "name": net.get("name", ""),
            "provider:segmentation_id": net.get("segmentationId", ""),
            "provider:network_type": net.get("networkType", ""),
            const.RES_TYPE_KEY: net["returnCode"],
            "subnet_list": []
        }
        if "subnet_list" in data and data["subnet_list"]:
            subnet = data["subnet_list"][0]           
            subnet_data = {
                "networkId": network_id,
                "name": subnet["subnet_name"],
                "cidr": subnet["cidr"],
                "ipVersion": const.IPV4,
                "enableDhcp": False           
            }
            if "ip_version" in subnet and subnet["ip_version"]:
                subnet_data["ipVersion"] = int(subnet["ip_version"])
            if "enable_dhcp" in subnet and subnet["enable_dhcp"]:
                subnet_data["enableDhcp"] = int(subnet["enable_dhcp"]) == const.ENABLE_DHCP
            if "gateway_ip" in subnet and subnet["gateway_ip"]:
                subnet_data["gatewayIp"] = subnet["gateway_ip"]
            if "dns_nameservers" in subnet and subnet["dns_nameservers"]:
                subnet_data["dnsNameservers"] = subnet["dns_nameservers"]
            if "allocation_pools" in subnet and subnet["allocation_pools"]:
                subnet_data["allocationPools"] = subnet["allocation_pools"]
            if "host_routes" in subnet and subnet["host_routes"]:
                subnet_data["hostRoutes"] = subnet["host_routes"]
            subnet_create = create_subnet(self.vim_id, self.tenant_id, subnet_data)
            ret_net["subnet_list"].append({
                "id": subnet_create["id"],
                "name": subnet_create["name"],
                const.RES_TYPE_KEY: net["returnCode"]})
        return [0, ret_net]

    def delete_network(self, auth_info, network_id):
        return delete_network(self.vim_id, self.tenant_id, network_id)

    def delete_subnet(self, auth_info, subnet_id):
        return delete_subnet(self.vim_id, self.tenant_id, subnet_id)
