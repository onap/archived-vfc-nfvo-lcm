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
import sys
import traceback

from neutronclient.common.exceptions import NeutronClientException
from neutronclient.common.exceptions import NetworkNotFoundClient
from neutronclient.common.exceptions import NotFound as SubnetNotFound

from lcm.pub.nfvi.vim.api.openstack import neutronbase
from lcm.pub.nfvi.vim.lib.syscomm import fun_name
from lcm.pub.nfvi.vim.api.openstack import project
from lcm.pub.nfvi.vim import const
from lcm.pub.nfvi.vim.lib.vimexception import VimException

logger = logging.getLogger(__name__)


def query_net(auth_info, net_id):
    neutron = neutronbase.get_neutron_default(fun_name(), auth_info)
    net = None
    try:
        net = neutron.show_network(net_id)["network"]
        keystone = auth_info["keystone"]
        tenant = keystone.tenants.get(tenant_id=net["tenant_id"])
    except NetworkNotFoundClient as e:
        logger.warn("NetworkNotFoundClient: %s", e.message)
        return [2, e.message]
    return [0, {
        "id": net["id"],
        "name": net["name"],
        "status": net["status"],
        "admin_state_up": net["admin_state_up"],
        "network_type": net["provider:network_type"],
        "physical_network": net["provider:physical_network"],
        "segmentation_id": net["provider:segmentation_id"],
        "tenant_id": net["tenant_id"],
        "tenant_name": tenant.name,
        "subnets": net["subnets"],
        "shared": net["shared"],
        "router_external": net["router:external"]
        }]


def query_nets(auth_info):
    neutron = neutronbase.get_neutron_default(fun_name(), auth_info)
    keystone = auth_info["keystone"]
    tenants_map = {}
    tenants = keystone.tenants.list()
    for tenant in tenants:
        tenants_map[tenant.id] = tenant.name

    nets = neutron.list_networks()
    return [0, {"networks": [{
        "id": net["id"],
        "name": net["name"],
        "status": net["status"],
        "admin_state_up": net["admin_state_up"],
        "network_type": net["provider:network_type"],
        "physical_network": net["provider:physical_network"],
        "segmentation_id": net["provider:segmentation_id"],
        "tenant_id": net["tenant_id"],
        "tenant_name": tenants_map[net["tenant_id"]] if net["tenant_id"] in tenants_map else "unknown",
        "subnets": net["subnets"],
        "shared": net["shared"],
        "router_external": net["router:external"]
        } for net in nets["networks"]]}]


def query_subnet(auth_info, subnet_id):
    neutron = neutronbase.get_neutron_default(fun_name(), auth_info)
    subnet_info = None
    try:
        subnet_info = neutron.show_subnet(subnet_id)["subnet"]
    except SubnetNotFound as e:
        logger.warn("SubnetNotFound: %s", e.message)
        return [2, e.message]
    ret = [0, {}]
    ret[1]["id"] = subnet_id
    ret[1]["name"] = subnet_info["name"]
    ret[1]["status"] = ""
    ret[1]["ip_version"] = subnet_info["ip_version"]
    ret[1]["cidr"] = subnet_info["cidr"]
    ret[1]["allocation_pools"] = subnet_info["allocation_pools"]
    ret[1]["enable_dhcp"] = subnet_info["enable_dhcp"]
    ret[1]["gateway_ip"] = subnet_info["gateway_ip"]
    ret[1]["host_routes"] = subnet_info["host_routes"]
    ret[1]["dns_nameservers"] = subnet_info["dns_nameservers"]
    return ret


def query_port(auth_info, port_id):
    neutron = neutronbase.get_neutron_default(fun_name(), auth_info)
    port_info = None
    try:
        port_info = neutron.show_port(port_id)["port"]
    except NeutronClientException as e:
        logger.warn("NeutronClientException: %s", e.message)
        return [2, e.message]
    ret = [0, {}]
    ret[1]["id"] = port_id
    ret[1]["name"] = port_info["name"]
    ret[1]["network_id"] = port_info["network_id"]
    ret[1]["tenant_id"] = port_info["tenant_id"]
    if "fixed_ips" in port_info and port_info["fixed_ips"]:
        ret[1]["ip"] = port_info["fixed_ips"][0]["ip_address"]
        ret[1]["subnet_id"] = port_info["fixed_ips"][0]["subnet_id"]
    else:
        ret[1]["ip"] = ""
        ret[1]["subnet_id"] = ""
    ret[1]["mac_address"] = port_info["mac_address"]
    ret[1]["status"] = port_info["status"]
    ret[1]["admin_state_up"] = port_info["admin_state_up"]
    ret[1]["device_id"] = port_info["device_id"]
    return ret


def get_subnet_id(neutron, data, network_id):
    subnet_id = None
    if "subnet_name" in data and data["subnet_name"]:
        all_subnets = neutron.list_subnets()
        filter_subnets = [subnet for subnet in all_subnets["subnets"] if subnet["name"] == data["subnet_name"]
                          and subnet["network_id"] == network_id]
        count_filter_subnets = len(filter_subnets)
        if 1 > count_filter_subnets:
            logger.error("Subnet name(%s) does not exist" % data["subnet_name"])
            raise VimException("Subnet name(%s) does not exist" % data["subnet_name"])
        if 1 < count_filter_subnets:
            for subnet in filter_subnets:
                logger.error("subnet_id=%s", subnet["id"])
            raise VimException("%d subnet(%s) exist in network(%s)"
                               % (count_filter_subnets, data["subnet_name"], data["network_name"]))
        subnet_id = filter_subnets[0]['id']
    else:
        subnets = neutron.list_subnets()
        filter_subnets = [subnet for subnet in subnets["subnets"] if subnet["network_id"] == network_id]
        if filter_subnets:
            subnet_id = filter_subnets[0]["id"]
    return subnet_id


def create_port(auth_info, data):
    tenant_id = project.get_tenant_id(fun_name(), auth_info, data["tenant_name"])

    neutron_admin = neutronbase.get_neutron_default(fun_name(), auth_info)
    all_nets = neutron_admin.list_networks()
    filter_nets = [net for net in all_nets['networks'] if net['name'] == data["network_name"]]
    sel_nets = [net for net in filter_nets if net['tenant_id'] == tenant_id or
                (net['tenant_id'] != tenant_id and net['shared'])]
    count_sel_nets = len(sel_nets)
    if 1 > count_sel_nets:
        logger.error("Network(%s) does not exist" % data["network_name"])
        raise VimException("Network(%s) does not exist" % data["network_name"])
    if 1 < count_sel_nets:
        for net in sel_nets:
            logger.error("net_id=%s", net["id"])
        raise VimException("%d networks(%s) exist in tenant(%s)"
                           % (count_sel_nets, data["network_name"], data["tenant_name"]))
    network_id = sel_nets[0]['id']
    if tenant_id != sel_nets[0]['tenant_id']:
        neutron = neutronbase.get_neutron_by_tenant_id(fun_name(), auth_info, sel_nets[0]['tenant_id'])
    else:
        neutron = neutronbase.get_neutron(fun_name(), auth_info, data["tenant_name"])

    # get subnet id
    subnet_id = get_subnet_id(neutron_admin, data, network_id)

    # check port
    port_data = None
    ports = neutron.list_ports()
    sel_ports = [port for port in ports['ports'] if port['tenant_id'] == tenant_id
                 and port['network_id'] == network_id]
    filter_ports = []
    for port in sel_ports:
        if port['name'] == data["port_name"] and port['fixed_ips']:
            for fixed_ip in port['fixed_ips']:
                if fixed_ip['subnet_id'] == subnet_id:
                    filter_ports.append(port)
                    break
    count_filter_ports = len(filter_ports)
    if 1 < count_filter_ports:
        for port in filter_ports:
            logger.error("port_id=%s", port["id"])
        raise VimException("%d port(%s) exist in subnet(%s)"
                           % (count_filter_ports, data["port_name"], data["subnet_name"]))
    if 1 == len(filter_ports):
        logger.debug("Port(%s) is exist!" % data["port_name"])
        port_data = {'status': filter_ports[0]['status'],
                     'id': filter_ports[0]['id'],
                     'name': filter_ports[0]['name'],
                     'network_id': filter_ports[0]['network_id'],
                     const.RES_TYPE_KEY: const.RES_TYPE_EXIST}
        return [0, port_data]

    # create port
    create_param = {'port': {
            'name': data["port_name"],
            'admin_state_up': True,
            'network_id': network_id,
            'security_groups': [],
            'tenant_id': tenant_id}}
    if "mac_address" in data and data["mac_address"]:
        create_param['port']['mac_address'] = data["mac_address"]
    if "vnic_type" in data and data["vnic_type"]:
        create_param['port']['binding:vnic_type'] = data["vnic_type"]
    if "bandwidth" in data and data["bandwidth"]:
        create_param['port']['bandwidth'] = int(data["bandwidth"])
    if "bond" in data and data["bond"]:
        create_param['port']['bond'] = int(data["bond"])
    if "macbond" in data and data["macbond"]:
        if 'mac_address' in create_param['port']:
            create_param['port']['mac_address'] += (',' + data["macbond"])
        else:
            create_param['port']['mac_address'] = data["macbond"]
    if "ip" in data and data["ip"]:
        if subnet_id:
            create_param['port']['fixed_ips'] = [{"subnet_id": subnet_id, "ip_address": data["ip"]}]

    if "allowed_address_pairs" in data and data["allowed_address_pairs"]:
        create_param['port']['allowed_address_pairs'] = data["allowed_address_pairs"]
    logger.info("[%s]call neutron.create_port(%s)" % (fun_name(), str(create_param)))
    port_created = None
    try:
        port_created = neutron.create_port(create_param)
    except NeutronClientException as ex:
        logger.info("create_port exception: %s, %s", str(sys.exc_info()), ex.message)
        create_param['port'].pop('security_groups')
        if 'allowed_address_pairs' in create_param['port']:
            create_param['port'].pop('allowed_address_pairs')
        logger.info("[%s]recall neutron.create_port(%s)" % (fun_name(), str(create_param)))
        port_created = neutron.create_port(create_param)
    if port_created:
        port_data = {'status': port_created['port']['status'],
                     'id': port_created['port']['id'],
                     'name': port_created['port']['name'],
                     'network_id': port_created['port']['network_id'],
                     const.RES_TYPE_KEY: const.RES_TYPE_NEW}
    return [0, port_data]


def create_network(auth_info, data):
    neutron = neutronbase.get_neutron(fun_name(), auth_info, data["tenant"])
    tenant_id = project.get_tenant_id(fun_name(), auth_info, data["tenant"])

    neutron_admin = neutronbase.get_neutron_default(fun_name(), auth_info)
    all_nets = neutron_admin.list_networks()
    filter_nets = [net for net in all_nets['networks'] if net['name'] == data["network_name"]]
    sel_nets = [net for net in filter_nets if net['tenant_id'] == tenant_id or
                (net['tenant_id'] != tenant_id and net['shared'])]
    count_sel_nets = len(sel_nets)
    if 1 < count_sel_nets:
        for sel_net in sel_nets:
            logger.info("net_id=%s, net_tenant_id=%s", sel_net["id"], sel_net['tenant_id'])
        raise VimException("Already %d networks are found with name %s" % (count_sel_nets, data["network_name"]))

    network_data = None
    if sel_nets:
        if sel_nets[0]['tenant_id'] != tenant_id:
            neutron = neutronbase.get_neutron_by_tenant_id(fun_name(), auth_info, sel_nets[0]['tenant_id'])
        all_subnets = neutron_admin.list_subnets()
        filter_subnets = [subnet for subnet in all_subnets["subnets"] if subnet["network_id"] == sel_nets[0]["id"]]
        network_data = {"status": sel_nets[0]["status"],
                        "id": sel_nets[0]["id"],
                        "name": data["network_name"],
                        "provider:segmentation_id": sel_nets[0]["provider:segmentation_id"],
                        "provider:network_type": sel_nets[0]["provider:network_type"],
                        const.RES_TYPE_KEY: const.RES_TYPE_EXIST,
                        "subnet_list": [{
                                            "id": subnet["id"],
                                            "name": subnet["name"],
                                            const.RES_TYPE_KEY: const.RES_TYPE_EXIST
                                        } for subnet in filter_subnets]}
    else:
        create_params = {
            'network': {
                'name': data["network_name"],
                'admin_state_up': True,
                'tenant_id': tenant_id,
                'shared': "shared" in data and int(data["shared"]) == const.SHARED_NET}}
        if "mtu" in data and int(data["mtu"]) != const.DEFAULT_MTU:
            create_params['network']['mtu'] = int(data["mtu"])
        if "vlan_transparent" in data and int(data["vlan_transparent"]) == const.SUPPORT_VLAN_TRANSPARENT:
            create_params['network']['vlan-transparent'] = True
        if "network_type" in data and data['network_type']:
            create_params['network']['provider:network_type'] = data['network_type']
        if "segmentation_id" in data and data['segmentation_id']:
            create_params['network']['provider:segmentation_id'] = int(data['segmentation_id'])
        if "physical_network" in data and data['physical_network']:
            create_params['network']['provider:physical_network'] = data['physical_network']

        logger.info("[%s]call neutron.create_network(%s)" % (fun_name(), str(create_params)))
        network_created = neutron.create_network(create_params)
        network_data = {"status": network_created['network']['status'],
                        "id": network_created['network']['id'],
                        "name": data["network_name"],
                        "provider:segmentation_id": network_created['network']['provider:segmentation_id'],
                        "provider:network_type": network_created['network']['provider:network_type'],
                        const.RES_TYPE_KEY: const.RES_TYPE_NEW,
                        "subnet_list": []}

    # subnet create
    exist_subnet_names = [subnet["name"] for subnet in network_data["subnet_list"]]
    need_rollback, ret_error = False, None
    if "subnet_list" in data and data["subnet_list"]:
        for subnet_data in data["subnet_list"]:
            if subnet_data["subnet_name"] in exist_subnet_names:
                continue
            ret = create_subnet(neutron, network_data["id"], subnet_data)
            if ret[0] != 0:
                need_rollback, ret_error = True, ret
                break
            network_data["subnet_list"].append(ret[1])

    # rollback when failed to create subnet
    if need_rollback:
        rollback(neutron_admin, network_data)
        return ret_error

    return [0, network_data]


def create_subnet(neutron, network_id, data):
    all_subnets = neutron.list_subnets()
    filter_subnets = [subnet for subnet in all_subnets["subnets"]
                      if subnet["network_id"] == network_id and subnet["name"] == data["subnet_name"]]
    if filter_subnets:
        return [0, {
                    "id": filter_subnets[0]["id"],
                    "name": data["subnet_name"],
                    const.RES_TYPE_KEY: const.RES_TYPE_EXIST}]
    try:
        create_params = {
            'subnet': {
                'network_id': network_id,
                'name': data["subnet_name"],
                'cidr': data["cidr"],
                'ip_version': int(data["ip_version"]) if "ip_version" in data else const.IPV4, }}
        create_params["subnet"]["enable_dhcp"] = ("enable_dhcp" in data
                                                  and int(data["enable_dhcp"]) == const.ENABLE_DHCP)
        if "gateway_ip" in data and data["gateway_ip"]:
            create_params["subnet"]["gateway_ip"] = data["gateway_ip"]
        else:
            create_params["subnet"]["gateway_ip"] = None
        if "dns_nameservers" in data and data["dns_nameservers"]:
            create_params["subnet"]["dns_nameservers"] = data["dns_nameservers"]
        if "allocation_pools" in data and data["allocation_pools"]:
            create_params["subnet"]["allocation_pools"] = data["allocation_pools"]
        if "host_routes" in data and data["host_routes"]:
            create_params["subnet"]["host_routes"] = data["host_routes"]

        logger.info("[%s]call neutron.create_subnet(%s)" % (fun_name(), str(create_params)))
        subnet_created = neutron.create_subnet(create_params)
        return [0, {"id": subnet_created["subnet"]["id"],
                    "name": data["subnet_name"],
                    const.RES_TYPE_KEY: const.RES_TYPE_NEW}]
    except Exception as ex:
        logger.error(traceback.format_exc())
        logger.error(str(sys.exc_info()))
        return [1, ex.message if ex.message else str(sys.exc_info())]


def rollback(neutron, network_data):
    for subnet_data in network_data["subnet_list"]:
        if subnet_data[const.RES_TYPE_KEY] == const.RES_TYPE_NEW:
            try:
                logger.info("[%s]call neutron.delete_subnet(%s)" % (fun_name(), subnet_data["id"]))
                neutron.delete_subnet(subnet_data["subnet_id"])
            except:
                logger.error("[%s]%s", fun_name(), str(sys.exc_info()))

    if network_data and network_data[const.RES_TYPE_KEY] == const.RES_TYPE_NEW:
        try:
            logger.info("[%s]call neutron.delete_network(%s)" % (fun_name(), network_data["id"]))
            neutron.delete_network(network_data["id"])
        except:
            logger.error("[%s]%s", fun_name(), str(sys.exc_info()))


def delete_network(auth_info, network_id):
    neutron = neutronbase.get_neutron_default(fun_name(), auth_info)
    try:
        neutron.delete_network(network_id)
    except Exception as ex:
        logger.error(traceback.format_exc())
        msg = ex.message if ex.message else str(sys.exc_info())
        logger.error(msg)
        if 404 == ex.status_code:
            return [0, ex.message]
        return [1, "Vim exception."]
    return [0, "Network(%s) is deleted" % network_id]


def delete_subnet(auth_info, subnet_id):
    neutron = neutronbase.get_neutron_default(fun_name(), auth_info)
    try:
        neutron.delete_subnet(subnet_id)
    except NeutronClientException as e:
        logger.warn("[%s]NetworkNotFoundClient: %s", fun_name(), e.message)
        return [0, e.message]
    return [0, "Subnet(%s) is deleted" % subnet_id]


def delete_port(auth_info, port_id):
    neutron = neutronbase.get_neutron_default(fun_name(), auth_info)
    try:
        neutron.delete_port(port_id)
    except NeutronClientException as e:
        logger.warn("[%s]NeutronClientException: %s", fun_name(), e.message)
        return [0, e.message]
    return [0, "Port(%s) is deleted" % port_id]
