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

"""
import unittest
from lcm.pub.nfvi.vim import vimadaptor
from lcm.pub.nfvi.vim.api.openstack import neutronbase
from lcm.pub.nfvi.vim.lib.syscomm import fun_name
from lcm.pub.nfvi.vim.test.openstack import pub
from lcm.pub.nfvi.vim import const

class TestNetwork(unittest.TestCase):
        def setUp(self):
        self.api = vimadaptor.VimAdaptor(pub.connect_info)
        self.network_data = {
            "tenant": "admin",
            "network_name": "testnet1",
            "shared": const.SHARED_NET,
            "network_type": "",
            "mtu": 1523,
            "subnet_list": [{
                "subnet_name": "subnet1",
                "cidr": "192.168.1.0/24",
                "ip_version": const.IPV4,
                "enable_dhcp": 0,
                "gateway_ip": "192.168.1.1",
                "dns_nameservers": [],
                "allocation_pools":[],
                "host_routes": []
            }]
        }

        self.port_data = {
            "port_name":"port_test",
            "tenant_name":"test",
            "network_name":"testnet1",
            "mac_address":"fa:16:3e:c9:cb:f5",
            "vnic_type":"normal",
            "bandwidth":"100",
            "bond":"0",
            "macbond":"",
            "ip":"192.168.1.10",
            "subnet_name":"subnet1",
            "allowed_address_pairs":[{'ip_address':'192.168.1.11','mac_address':'fa:16:3e:c9:cb:f6'}]
        }

        self.port_data_no_subname = {
            "port_name":"port_test_no_subname",
            "tenant_name":"admin",
            "network_name":"testnet1",
            "mac_address":"fa:16:3e:c9:cb:f7",
            "vnic_type":"normal",
            "bandwidth":"100",
            "bond":"0",
            "macbond":"",
            "ip":"192.168.1.12",
            "allowed_address_pairs":[{'ip_address':'192.168.1.13','mac_address':'fa:16:3e:c9:cb:f8'}]
        }

        self.network_data_rollback = {
            "tenant": "admin",
            "network_name": "testnet1",
            "shared": const.SHARED_NET,
            "network_type": "",
            "mtu": 1523,
            "subnet_list": [{
                "subnet_name": "subnet1",
                "cidr": "192.168.1.0/24",
                "ip_version": const.IPV4,
                "enable_dhcp": 0,
                "gateway_ip": "192.168.1.1",
                "dns_nameservers": [],
                "allocation_pools":[],
                "host_routes": []
            },
                            {
                "subnet_name": "subnet2",
                "cidr": "191.168.1.0/24",
                "ip_version": const.IPV6,
                "enable_dhcp": 0,
                "gateway_ip": "191.168.1.1",
                "dns_nameservers": [],
                "allocation_pools":[],
                "host_routes": []
            }]
        }
    def tearDown(self):
        pass

    def test_network_all(self):
        neutron = neutronbase.get_neutron_default(fun_name(), pub.connect_info)

        # create network
        ret = self.api.create_network(self.network_data)
        self.assertEqual(0, ret[0], ret[1])
        if ret[1][const.RES_TYPE_KEY] == const.RES_TYPE_EXIST:
            for subnet in ret[1]["subnet_list"]:
                ports = neutron.list_ports()
                for port in ports['ports']:
                    for fixed_ip in port['fixed_ips']:
                        if fixed_ip['subnet_id'] == subnet["id"]:
                            self.api.delete_port(port['id'])
                            break
                ret_del = self.api.delete_subnet(subnet_id = subnet["id"])
                self.assertEqual(0, ret_del[0])
            ret_del = self.api.delete_network(network_id = ret[1]["id"])
            self.assertEqual(0, ret_del[0])
            ret = self.api.create_network(self.network_data)
            self.assertEqual(0, ret[0])

        # network exist
        ret = self.api.create_network(self.network_data)
        self.assertEqual(0, ret[0])
        self.assertEqual(ret[1][const.RES_TYPE_KEY], const.RES_TYPE_EXIST)

        # query subnet
        q_subnet_ret = self.api.query_subnet(ret[1]["subnet_list"][0]["id"])
        self.assertEqual(0, q_subnet_ret[0])

        # query net
        q_net_ret = self.api.query_net(ret[1]["id"])
        self.assertEqual(0, q_net_ret[0])

        # query nets
        q_nets_ret = self.api.query_nets()
        self.assertEqual(0, q_nets_ret[0])
        flag = False
        for network in q_nets_ret[1]['networks']:
            if ret[1]["id"] == network["id"]:
                flag = True
                break
        self.assertTrue(flag)

        # create port
        create_port_ret = self.api.create_port(self.port_data)
        self.assertEqual(0, create_port_ret[0], create_port_ret[1])

        # port exist
        create_port_ret = self.api.create_port(self.port_data)
        self.assertEqual(0, create_port_ret[0])
        self.assertEqual(create_port_ret[1][const.RES_TYPE_KEY], const.RES_TYPE_EXIST)

        # create port no subname
        ret_no_subname = self.api.create_port(self.port_data_no_subname)
        self.assertEqual(0, ret_no_subname[0], ret_no_subname[1])
        self.api.delete_port(ret_no_subname[1]['id'])

        # create port except, networks not exist
        network_name = self.port_data["network_name"]
        self.port_data["network_name"] = "no_network"
        create_port_except_ret = self.api.create_port(self.port_data)
        self.assertEqual(1, create_port_except_ret[0])
        self.port_data["network_name"] = network_name

        # create port except, subnet not exist
        subnet_name = self.port_data["subnet_name"]
        self.port_data["subnet_name"] = "no_subnet"
        create_port_except_ret = self.api.create_port(self.port_data)
        self.assertEqual(1, create_port_except_ret[0])
        self.port_data["subnet_name"] = subnet_name

        # query port
        q_port_ret = self.api.query_port(create_port_ret[1]['id'])
        self.assertEqual(0, q_port_ret[0], q_port_ret[1])

        # delete port
        ret_port_del = self.api.delete_port(create_port_ret[1]['id'])
        self.assertEqual(0, ret_port_del[0])

        # delete network
        for subnet in ret[1]["subnet_list"]:
            ret_del = self.api.delete_subnet(subnet_id = subnet["id"])
            self.assertEqual(0, ret_del[0])
        ret_del = self.api.delete_network(network_id = ret[1]["id"])
        self.assertEqual(0, ret_del[0])

        # query net except
        q_net_ret = self.api.query_net(ret[1]["id"])
        self.assertEqual(2, q_net_ret[0])

        # query subnet except
        q_subnet_ret = self.api.query_subnet(ret[1]["subnet_list"][0]["id"])
        self.assertEqual(2, q_subnet_ret[0])

        # rollback test
        ret_roolback = self.api.create_network(self.network_data_rollback)
        self.assertEqual(1, ret_roolback[0])

        # delete except
        ret_del = self.api.delete_subnet(subnet_id = "11111")
        self.assertEqual(0, ret_del[0])

        ret_del = self.api.delete_network(network_id = "11111")
        self.assertEqual(0, ret_del[0])

        ret_del = self.api.delete_port(port_id = "11111")
        self.assertEqual(0, ret_del[0])

        # query except
        q_del = self.api.query_port(port_id = "11111")
        self.assertEqual(2, q_del[0])

        # multiple network except
        tenant = self.network_data["tenant"]
        network = self.network_data["network_name"]
        self.network_data["tenant"] = "test"
        self.network_data["network_name"] = "ut_test_network"
        ret = self.api.create_network(self.network_data)
        self.network_data["tenant"] = tenant
        self.network_data["network_name"] = network
        self.assertEqual(1, ret[0])

        tenant = self.port_data["tenant_name"]
        network = self.port_data["network_name"]
        self.port_data["tenant_name"] = "test"
        self.port_data["network_name"] = "ut_test_network"
        ret = self.api.create_port(self.port_data)
        self.port_data["tenant_name"] = tenant
        self.port_data["network_name"] = network
        self.assertEqual(1, ret[0])

        # multiple subnet except
        tenant = self.port_data["tenant_name"]
        network = self.port_data["network_name"]
        subnet = self.port_data["subnet_name"]
        self.port_data["tenant_name"] = "test"
        self.port_data["network_name"] = "ut_test_subnet_except"
        self.port_data["subnet_name"] = "ut_test_same_subnet"
        ret = self.api.create_port(self.port_data)
        self.port_data["tenant_name"] = tenant
        self.port_data["network_name"] = network
        self.port_data["subnet_name"] = subnet
        self.assertEqual(1, ret[0])
"""
