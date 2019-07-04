# Copyright 2018 ZTE Corporation.
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
import mock
from django.test import Client
from django.test import TestCase
from rest_framework import status

from lcm.pub.database.models import FPInstModel, CPInstModel, PortInstModel, NfInstModel
from lcm.pub.database.models import VNFFGInstModel
from lcm.pub.msapi import extsys
from lcm.pub.msapi import sdncdriver
from lcm.pub.utils import restcall


class TestSfc(TestCase):
    def setUp(self):
        self.client = Client()
        FPInstModel.objects.filter().delete()
        VNFFGInstModel.objects.filter().delete()
        CPInstModel.objects.filter().delete()
        PortInstModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()

        self.save_vnffg_inst_data()
        self.save_vnf_inst_data()
        self.save_cp_inst_data()
        self.save_port_inst_data()
        self.save_fp_inst_data()

    def tearDown(self):
        pass

    @mock.patch.object(restcall, 'call_req')
    def test_sfc_instanciate(self, mock_call_req):
        pass
        # data = {
        #     "nsInstanceId": "ns_inst_1",
        #     "context": nsd_model,
        #     "fpindex": "fpd_1",
        #     "sdnControllerId": "sdnControllerId_1"
        # }
        # resp = self.client.post("/api/nslcm/v1/ns/sfc_instance", data, format='json')
        # self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)

    @mock.patch.object(extsys, "get_sdn_controller_by_id")
    @mock.patch.object(sdncdriver, "create_flow_classfier")
    @mock.patch.object(restcall, 'call_req')
    def test_create_flow_classfier(self, mock_call_req, mock_create_flow_classfier, mock_get_sdn_controller_by_id):
        data = {
            "fpinstid": "fp_inst_1",
            "context": json.dumps(nsd_model)
        }
        mock_create_flow_classfier.return_value = [0, json.dumps({'id': '1'})]
        mock_get_sdn_controller_by_id.return_value = json.loads('{"test":"test_name","url":"url_add"}')
        resp = self.client.post("/api/nslcm/v1/ns/create_flow_classifier", data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @mock.patch.object(extsys, "get_sdn_controller_by_id")
    @mock.patch.object(sdncdriver, 'create_port_pair_group')
    @mock.patch.object(sdncdriver, 'create_port_pair')
    @mock.patch.object(restcall, 'call_req')
    def test_create_port_pair_group(self, mock_call_req, mock_create_port_pair,
                                    mock_create_port_pair_group, mock_get_sdn_controller_by_id):
        data = {
            "nsinstanceid": "ns_inst_1",
            "fpinstid": "fp_inst_1",
            "context": json.dumps(nsd_model)
        }
        mock_create_port_pair.return_value = [0, json.dumps({'id': '1'})]
        mock_create_port_pair_group.return_value = [0, json.dumps({'id': '1'})]
        mock_get_sdn_controller_by_id.return_value = json.loads('{"test":"test_name","url":"url_add"}')
        resp = self.client.post("/api/nslcm/v1/ns/create_port_pair_group", data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @mock.patch.object(extsys, "get_sdn_controller_by_id")
    @mock.patch.object(sdncdriver, 'create_port_chain')
    @mock.patch.object(restcall, 'call_req')
    def test_create_port_chain(self, mock_call_req, mock_create_port_chain, mock_get_sdn_controller_by_id):
        data = {
            "nsinstanceid": "ns_inst_1",
            "fpinstid": "fp_inst_1",
            "context": json.dumps(nsd_model)
        }
        self.update_fp_inst_data()
        mock_create_port_chain.return_value = [0, json.dumps({'id': '1'})]
        mock_get_sdn_controller_by_id.return_value = json.loads('{"test":"test_name","url":"url_add"}')
        resp = self.client.post("/api/nslcm/v1/ns/create_port_chain", data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @mock.patch.object(restcall, 'call_req')
    def test_create_sfc(self, mock_call_req):
        pass
        # data = {
        #     "nsInstanceId": "ns_inst_1",
        #     "context": json.dumps(nsd_model),
        #     "fpindex": "1",
        #     'fpinstid': str(uuid.uuid4()),
        #     "sdnControllerId": "sdnControllerId_1"
        # }
        # resp = self.client.post("/api/nslcm/v1/ns/ns_sfcs", data, format='json')
        # self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)

    def update_fp_inst_data(self):
        FPInstModel.objects.filter(fpinstid="fp_inst_1").update(flowclassifiers="1",
                                                                portpairgroups=json.JSONEncoder().encode([{
                                                                    "groupid": "1",
                                                                    "portpair": ["2"]
                                                                }]))

    def save_vnffg_inst_data(self):
        VNFFGInstModel(
            vnffgdid="vnffg_id1",
            vnffginstid="vnffg_inst_1",
            nsinstid="ns_inst_1",
            endpointnumber=2,
            vllist="vlinst1",
            cplist="cp1",
            vnflist="vnf1,vnf2"
        ).save()

    def save_cp_inst_data(self):
        CPInstModel(
            cpinstanceid="cp_inst_1",
            cpdid="cpd_1",
            ownertype=0,
            ownerid="vnf_inst_1",
            relatedtype=1,
            relatedport="port_inst_1"
        ).save()

        CPInstModel(
            cpinstanceid="cp_inst_2",
            cpdid="cpd_2",
            ownertype=0,
            ownerid="vnf_inst_2",
            relatedtype=1,
            relatedport="port_inst_2"
        ).save()

    def save_fp_inst_data(self):
        FPInstModel(
            fpid="fpd_1",
            fpinstid="fp_inst_1",
            nsinstid="ns_inst_1",
            vnffginstid="vnffg_inst_1",
            policyinfo=[{
                "type": "ACL",
                "criteria": {
                    "dest_port_range": [80, 1024],
                    "source_port_range": [80, 1024],
                    "ip_protocol": "tcp",
                    "dest_ip_range": ["192.168.1.2", "192.168.1.100"],
                    "source_ip_range": ["192.168.1.2", "192.168.1.100"],
                    "dscp": 100,
                }
            }],
            status="enabled",
            sdncontrollerid="sdn_controller_1"

        ).save()

        FPInstModel(
            fpid="fpd_2",
            fpinstid="fp_inst_2",
            nsinstid="ns_inst_1",
            vnffginstid="vnffg_inst_1",
            policyinfo=[{
                "type": "ACL",
                "criteria": {
                    "dest_port_range": [80, 1024],
                    "source_port_range": [80, 1024],
                    "ip_protocol": "tcp",
                    "dest_ip_range": ["192.168.1.2", "192.168.1.100"],
                    "source_ip_range": ["192.168.1.2", "192.168.1.100"],
                    "dscp": 100,
                }
            }],
            status="enabled",
            sdncontrollerid="sdn_controller_1"
        ).save()

    def save_sdnc_inst_data(self):
        pass
        # SDNCModel(
        #     uuid="uuid_111",
        #     sdncontrollerid="sdn_controller_1",
        #     name="111",
        #     type="vnf",
        #     url="192.168.0.1:8080",
        #     username="admin",
        #     pwd="admin",
        #     ver="ver",
        #     longitude="longitude",
        #     latitude="latitude"
        # ).save()

    def save_port_inst_data(self):
        PortInstModel(
            portid="port_inst_1",
            networkid="network_inst_1",
            subnetworkid="subnetwork_inst_1",
            vimid="vim_1",
            resourceid="res_1",
            ipaddress="10.43.25.2",
            macaddress="EC-F4-BB-20-43-F1"
        ).save()

        PortInstModel(
            portid="port_inst_2",
            networkid="network_inst_1",
            subnetworkid="subnetwork_inst_1",
            vimid="vim_1",
            resourceid="res_1",
            ipaddress="10.43.25.3",
            macaddress="EC-F4-BB-20-43-F2"
        ).save()

    def save_vnf_inst_data(self):
        NfInstModel(
            nfinstid="vnf_inst_1",
            ns_inst_id="ns_inst_1",
            vnf_id="vnf_1",
            vnfd_model=json.dumps(vnfd_model_dict1)

        ).save()

        NfInstModel(
            nfinstid="vnf_inst_2",
            vnf_id="vnf_2",
            ns_inst_id="ns_inst_1",
            vnfd_model=json.dumps(vnfd_model_dict2)

        ).save()


vnfd_model_dict1 = {
    'vdus': [
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '2'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_omm.001',
            'image_file': 'opencos_sss_omm_img_release_20150723-1-disk1',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': 'omm.001',
                'manual_scale_select_vim': False
            },
            'description': 'singleommvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '4'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_1',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '1',
                'manual_scale_select_vim': False
            },
            'description': 'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_2',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '2',
                'manual_scale_select_vim': False
            },
            'description': 'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_3',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '3',
                'manual_scale_select_vim': False
            },
            'description': 'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '4'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_10',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '10',
                'manual_scale_select_vim': False
            },
            'description': 'ppvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_11',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '11',
                'manual_scale_select_vim': False
            },
            'description': 'ppvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_12',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '12',
                'manual_scale_select_vim': False
            },
            'description': 'ppvm'
        }
    ],
    'volumn_storages': [

    ],
    'policies': {
        'scaling': {
            'targets': {

            },
            'policy_id': 'policy_scale_sss-vnf-template',
            'properties': {
                'policy_file': '*-vnfd.zip/*-vnf-policy.xml'
            },
            'description': ''
        }
    },
    'image_files': [
        {
            'description': '',
            'properties': {
                'name': 'opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'checksum': '',
                'disk_format': 'VMDK',
                'file_url': './zte-cn-sss-main-image/OMM/opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': 'opencos_sss_omm_img_release_20150723-1-disk1'
        },
        {
            'description': '',
            'properties': {
                'name': 'sss.vmdk',
                'checksum': '',
                'disk_format': 'VMDK',
                'file_url': './zte-cn-sss-main-image/NE/sss.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': 'sss'
        }
    ],
    'vls': [

    ],
    'cps': [
        {'cp_id': 'cpd_1',
         "description": "",
         "properties": {
             "mac_address": "00:d9:00:82:11:e1",
             "ip_address": "10.43.25.2",
             "ip_range_start": "192.168.1.20",
             "ip_range_end": "192.168.1.29",
             "sfc_encapsulation": ""
         }
         },
    ],
    'metadata': {
        'vendor': 'zte',
        'is_shared': False,
        'description': '',
        'domain_type': 'CN',
        'version': 'v4.14.10',
        'vmnumber_overquota_alarm': False,
        'cross_dc': False,
        'vnf_type': 'SSS',
        'vnfd_version': 'V00000001',
        'id': 'vnfd_2',
        'name': 'sss-vnf-template'
    },

    'vnf_exposed': {
        "external_cps": [
            {
                "key_name": "virtualLink1",
                "cp_id": "cp1",
            },
        ],
        "forward_cps": [
            {
                "key_name": "forwarder1",
                "cp_id": "cpd_1",
            },
            {
                "key_name": "forwarder2",
                "cp_id": "cpd_2",
            },
        ],
    }
}

vnfd_model_dict2 = {
    'local_storages': [

    ],
    'vdus': [
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '2'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_omm.001',
            'image_file': 'opencos_sss_omm_img_release_20150723-1-disk1',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': 'omm.001',
                'manual_scale_select_vim': False
            },
            'description': 'singleommvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '4'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_1',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '1',
                'manual_scale_select_vim': False
            },
            'description': 'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_2',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '2',
                'manual_scale_select_vim': False
            },
            'description': 'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_3',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '3',
                'manual_scale_select_vim': False
            },
            'description': 'ompvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '4'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_10',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '10',
                'manual_scale_select_vim': False
            },
            'description': 'ppvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_11',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '11',
                'manual_scale_select_vim': False
            },
            'description': 'ppvm'
        },
        {
            'volumn_storages': [

            ],
            'nfv_compute': {
                'mem_size': '',
                'num_cpus': '14'
            },
            'local_storages': [

            ],
            'vdu_id': 'vdu_12',
            'image_file': 'sss',
            'dependencies': [

            ],
            'vls': [

            ],
            'cps': [

            ],
            'properties': {
                'key_vdu': '',
                'support_scaling': False,
                'vdu_type': '',
                'name': '',
                'storage_policy': '',
                'location_info': {
                    'vimId': '',
                    'availability_zone': '',
                    'region': '',
                    'dc': '',
                    'host': '',
                    'tenant': ''
                },
                'inject_data_list': [

                ],
                'watchdog': {
                    'action': '',
                    'enabledelay': ''
                },
                'local_affinity_antiaffinity_rule': {

                },
                'template_id': '12',
                'manual_scale_select_vim': False
            },
            'description': 'ppvm'
        }
    ],
    'volumn_storages': [

    ],
    'policies': {
        'scaling': {
            'targets': {

            },
            'policy_id': 'policy_scale_sss-vnf-template',
            'properties': {
                'policy_file': '*-vnfd.zip/*-vnf-policy.xml'
            },
            'description': ''
        }
    },
    'image_files': [
        {
            'description': '',
            'properties': {
                'name': 'opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'checksum': '',
                'disk_format': 'VMDK',
                'file_url': './zte-cn-sss-main-image/OMM/opencos_sss_omm_img_release_20150723-1-disk1.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': 'opencos_sss_omm_img_release_20150723-1-disk1'
        },
        {
            'description': '',
            'properties': {
                'name': 'sss.vmdk',
                'checksum': '',
                'disk_format': 'VMDK',
                'file_url': './zte-cn-sss-main-image/NE/sss.vmdk',
                'container_type': 'vm',
                'version': '',
                'hypervisor_type': 'kvm'
            },
            'image_file_id': 'sss'
        }
    ],
    'vls': [

    ],
    'cps': [
        {'cp_id': 'cpd_2',
         "description": "",
         "properties": {
             "mac_address": "00:d9:00:82:11:e2",
             "ip_address": "10.43.25.3",
             "ip_range_start": "192.168.1.20",
             "ip_range_end": "192.168.1.29",
             "sfc_encapsulation": ""
         }
         },
    ],
    'metadata': {
        'vendor': 'zte',
        'is_shared': False,
        'description': '',
        'domain_type': 'CN',
        'version': 'v4.14.10',
        'vmnumber_overquota_alarm': False,
        'cross_dc': False,
        'vnf_type': 'SSS',
        'vnfd_version': 'V00000001',
        'id': 'sss-vnf-template',
        'name': 'vnfd_2'
    },
    'vnf_exposed': {
        "external_cps": [
            {
                "key_name": "virtualLink1",
                "cp_id": "cp1",
            },
        ],
        "forward_cps": [
            {
                "key_name": "forwarder2",
                "cp_id": "cpd_2",
            },
            {
                "key_name": "forwarder3",
                "cp_id": "cpd_2",
            },
        ],
    }
}

nsd_model = {
    "metadata": {
        "id": "nsd_demo",
        "vendor": "zte",
        "version": "1.1.0",
        "name": "testNSD",
        "description": "demo nsd",
    },

    "inputs": {
        "param1": "11",
        "param2": "22",
    },

    "vnfs": [
        {
            "type": "tosca.nodes.nfv.ext.VNF.FireWall",
            "vnf_id": "vnf_1",
            "description": "",
            "properties": {
                "id": "vnfd_1",
                "vendor": "zte",
                "version": "1.2.0",
                "vnfd_version": "1.1.0",
                "vnf_type": "vnf1",
                "domain_type": "CN",
                "name": "vnf1",
                "is_shared": False,
                "cross_dc": False,
                "request_reclassification": False,
                "nsh_aware": False,
                "custom_properties": {
                    "key1": "value1",
                    "keyN": "valueN",
                },
            },
            "dependencies": [
                "vnf_id1", "vnf_id2"
            ],
            "networks": [
                {
                    "key_name": "virtualLink1",
                    "vl_id": "vl_id1",
                },
            ],
        },
        {
            "type": "tosca.nodes.nfv.ext.VNF.FireWall",
            "vnf_id": "vnf_2",
            "description": "",
            "properties": {
                "id": "vnfd_2",
                "vendor": "zte",
                "version": "1.2.0",
                "vnfd_version": "1.1.0",
                "vnf_type": "vnf2",
                "domain_type": "CN",
                "name": "vnf1",
                "is_shared": False,
                "cross_dc": False,
                "request_reclassification": False,
                "nsh_aware": False,
                "custom_properties": {
                    "key1": "value1",
                    "keyN": "valueN",
                },
            },
            "dependencies": [
                "vnf_id1", "vnf_id2"
            ],
            "networks": [
                {
                    "key_name": "virtualLink1",
                    "vl_id": "vl_id1",
                },
            ],
        }
    ],

    "pnfs": [
        {
            "pnf_id": "pnf1",
            "description": "",
            "properties": {
                "id": "pnf1",
                "vendor": "zte",
                "version": "1.1.0",
                "pnf_type": "TTGW",
                "request_reclassification": False,
                "nsh_aware": False,
                "management_address": "10.44.56.78"
            },
            "cps": [
                "cpd_1", "cpd_22",
            ]
        }
    ],

    "nested_ns": [
        {
            "ns_id": "ns2",
            "description": "",
            "properties": {
                "id": "ns2_demo",
                "vendor": "zte",
                "version": "1.1.0",
                "name": "NSD2",
            },
            "networks": [
                {
                    "key_name": "virtualLink1",
                    "vl_id": "vl_id1",
                },
            ],
        }
    ],

    "vls": [
        {
            "vl_id": "vldId1",
            "description": "",
            "properties": {
                "name": "umac_241_control",
                "network_id": "fgdhsj434hfjdfd",
                "network_name": "umac_control",
                "vendor": "zte",
                "mtu": 1500,
                "network_type": "vlan",
                "physical_network": "phynet01",
                "segmentation_id": "30",
                "vlan_transparent": False,
                "vds_name": "vds1",
                "cidr": "192.168.199.0/24",
                "ip_version": 4,
                "gateway_ip": "192.168.199.1",
                "dhcp_enabled": False,
                "dns_nameservers": ["192.168.0.4", "192.168.0.10"],
                "start_ip": "192.168.199.2",
                "end_ip": "192.168.199.254",
                "host_routes": [
                    {
                        "destination": "10.43.26.0/24",
                        "nexthop": "10.41.23.1",
                    },
                ],
                "location_info": {
                    "vimId": "vimid",
                    "tenant": "tenantname",
                },
                "vlan_transparent": False,
            },
        },
    ],

    "cps": [
        {
            "cp_id": "cpd_1",
            "description": "",
            "properties": {
                "mac_address": "00:d9:00:82:11:e1",
                "ip_address": "192.168.1.21",
                "ip_range_start": "192.168.1.20",
                "ip_range_end": "192.168.1.29",
                "floating_ip_address": {
                    "external_network": "extnet01",
                    "ip_address": "10.43.53.23",
                },
                "service_ip_address": "192.168.1.23",
                "order": 1,
                "bandwidth": 1000,
                "vnic_type": "normal",
                "allowed_address_pairs": [
                    {
                        "ip": "192.168.1.13",
                        "mac": "00:f3:43:20:a2:a3"
                    },
                ],
                "bond": "none",
                "macbond": "00:d9:00:82:11:d1",
                "sfc_encapsulation": "",
                "direction": "",
            },
            "vl_id": "vlid1",
            "pnf_id": "pnf1",
        },

        {
            "cp_id": "forwarder_brasDP_dcPort",
            "description": "",
            "properties": {
                "mac_address": "00:d9:00:82:14:e1",
                "ip_address": "192.168.1.24",
                "ip_range_start": "192.168.1.20",
                "ip_range_end": "192.168.1.29",
                "floating_ip_address": {
                    "external_network": "extnet01",
                    "ip_address": "10.43.53.23",
                },
                "service_ip_address": "192.168.1.23",
                "order": 1,
                "bandwidth": 1000,
                "vnic_type": "normal",
                "allowed_address_pairs": [
                    {
                        "ip": "192.168.1.13",
                        "mac": "00:f3:43:20:a2:a3"
                    },
                ],
                "bond": "none",
                "macbond": "00:d9:00:82:11:d1",
                "sfc_encapsulation": "",
                "direction": "",
            },
            "vl_id": "vlid1",
            "pnf_id": "pnf1",
        },
        {
            "cp_id": "forwarder_brasDP_internetPort",
            "description": "",
            "properties": {
                "mac_address": "00:d9:00:82:15:e1",
                "ip_address": "192.168.1.25",
                "ip_range_start": "192.168.1.20",
                "ip_range_end": "192.168.1.29",
                "floating_ip_address": {
                    "external_network": "extnet01",
                    "ip_address": "10.43.53.23",
                },
                "service_ip_address": "192.168.1.23",
                "order": 1,
                "bandwidth": 1000,
                "vnic_type": "normal",
                "allowed_address_pairs": [
                    {
                        "ip": "192.168.1.13",
                        "mac": "00:f3:43:20:a2:a3"
                    },
                ],
                "bond": "none",
                "macbond": "00:d9:00:82:11:d1",
                "sfc_encapsulation": "",
                "direction": "",
            },
            "vl_id": "vlid1",
            "pnf_id": "pnf1",
        },

    ],

    "fps": [
        {
            "fp_id": "fpd_1",
            "description": "",
            "properties": {
                "policy": {
                    "type": "ACL",
                    "criteria": {
                        "dest_port_range": [80, 1024],
                        "source_port_range": [80, 1024],
                        "ip_protocol": "tcp",
                        "dest_ip_range": ["192.168.1.2", "192.168.1.100"],
                        "source_ip_range": ["192.168.1.2", "192.168.1.100"],
                        "dscp": 100,
                    },
                },
                "symmetric": True,
            },
            "forwarder_list": [
                {
                    "type": "cp",
                    "node_name": "cpd_1",
                    "capability": "",
                },
                {
                    "type": "cp",
                    "node_name": "forwarder_brasDP_dcPort",
                    "capability": "",
                },
                {
                    "type": "vnf",
                    "node_name": "vnf_1",
                    "capability": "forwarder1",
                },
                {
                    "type": "vnf",
                    "node_name": "vnf_2",
                    "capability": "forwarder2",
                },
                {
                    "type": "cp",
                    "node_name": "forwarder_brasDP_dcPort",
                    "capability": "",
                },
                {
                    "type": "cp",
                    "node_name": "forwarder_brasDP_internetPort",
                    "capability": "",
                },
            ],
        },

        {
            "fp_id": "fpd_2",
            "description": "",
            "properties": {
                "policy": {
                    "type": "ACL",
                    "criteria": {
                        "dest_port_range": [80, 1024],
                        "source_port_range": [80, 1024],
                        "ip_protocol": "tcp",
                        "dest_ip_range": ["192.168.1.2", "192.168.1.100"],
                        "source_ip_range": ["192.168.1.2", "192.168.1.100"],
                        "dscp": 100,
                    },
                },
                "symmetric": True,
            },
            "forwarder_list": [

                {
                    "type": "cp",
                    "node_name": "forwarder_brasDP_internetPort",
                    "capability": "",
                },
                {
                    "type": "cp",
                    "node_name": "forwarder_brasDP_dcPort",
                    "capability": "",
                },
                {
                    "type": "vnf",
                    "node_name": "vnf_2",
                    "capability": "forwarder2",
                },

            ],
        },
    ],

    "vnffgs": [
        {
            "vnffg_id": "vnffg_id1",
            "description": "",
            "properties": {
                "vendor": "zte",
                "version": "1.1.2",
                "number_of_endpoints": 7,
                "dependent_virtual_link": ["vldId1"],
                "connection_point": ["CP01", "CP02"],
                "constituent_vnfs": ["vnf_id1", "vnf_id2"],
                "constituent_pnfs": ["pnf1", "pnf2"],
            },
            "members": ["fpd_1", "fpd_2"],
        }
    ],

    "server_groups": [
        {
            "group_id": "",
            "description": "",
            "properties": {
                "name": "server_group1",
                "affinity_antiaffinity": "anti-affinity",
                "scope": "host",
            },
            "members": ["vnf1", "vnf2"],
        },
    ],

    "ns_exposed": {
        "external_cps": [
            {
                "key_name": "virtualLink1",
                "cp_id": "cp1",
            },
        ],
        "forward_cps": [
            {
                "key_name": "forwarder_brasDP_userPort",
                "cp_id": "cpd_1",
            },
            {
                "key_name": "forwarder_brasDP_internetPort",
                "cp_id": "cpd_4",
            },
            {
                "key_name": "forwarder_brasDP_dcPort",
                "cp_id": "cpd_5",
            },

        ],
    },

    "policies": [
        {
            "scaling": [
                {
                    "policy_id": "id1",
                    "description": "",
                    "properties": {
                        "policy_file": "Policies/ns1-policy.xml",
                    },
                    "targets": ['pfu_vm'],
                },
            ],
        },
    ],

    "ns_flavours": [
        {
            "flavour_id": "flavour1",
            "description": "",
            "vnf_profiles": [
                {
                    "vnf_id": "vnf1",
                    "flavour_id": "flavour1",
                    "instances_minimum_number": 1,
                    "instances_maximum_number": 4,
                    "local_affinity_antiaffinity_rule": [
                        {
                            "affinity_antiaffinity": "affinity",
                            "scope": "node",
                        }
                    ]
                },
            ],
            "pnf_profiles": [
                {
                    "pnf_id": "pnf1",
                },
            ],
            "vl_profiles": [
                {
                    "vl_id": "vlid1",
                    "bitrate_requirements": {
                        "root": 1000,
                        "leaf": 100
                    },
                    "qos": {
                        "maximum_latency": "1 ms",
                        "maximum_jitter": "10 ms",
                        "maximum_packet_loss_ratio": 0.5
                    },
                }
            ],
            "instantiation_levels": [
                {
                    "id": "instLevel1",
                    "description": "",
                    "vnf_levels": [
                        {
                            "vnf_id": "",
                            "vnf_instantiation_level": "small",
                            "instances_number": 1
                        },
                    ],
                    "scale_level_id": "scaleLevel1",
                }
            ],
            "default_instantiation_level": "instLevel1",
            "scale_levels": [
                {
                    "id": "scaleLevel1",
                    "order": 1,
                    "vnf_levels": [
                        {
                            "vnf_id": "",
                            "vnf_instantiation_level": "small",
                            "instances_number": 1
                        },
                    ],
                },
            ],
            "supported_operations": ["Scale", "Heal"],
            "affinity_antiaffinity_groups": [
                {
                    "group_id": "group1Id",
                    "name": "groupName",
                    "affinity_antiaffinity": "affinity",
                    "scope": "node",
                    "members": [
                        "vnfId1", "vnfIdN",
                    ],
                },
            ],
        },
    ],
}
