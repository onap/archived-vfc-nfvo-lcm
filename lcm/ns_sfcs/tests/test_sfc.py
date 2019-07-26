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
import uuid
import time

from django.test import Client
from django.test import TestCase
from rest_framework import status

from lcm.pub.database.models import FPInstModel, CPInstModel, PortInstModel, NfInstModel
from lcm.pub.database.models import VNFFGInstModel
from lcm.pub.msapi import extsys
from lcm.pub.msapi import sdncdriver
from lcm.pub.utils import restcall
from lcm.ns_sfcs.biz.create_sfc_worker import CreateSfcWorker
from lcm.pub.utils.jobutil import JobUtil
from lcm.ns_sfcs.tests.test_data import nsd_model


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
        FPInstModel.objects.filter().delete()
        VNFFGInstModel.objects.filter().delete()
        CPInstModel.objects.filter().delete()
        PortInstModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()

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

    @mock.patch.object(CreateSfcWorker, 'run')
    @mock.patch.object(JobUtil, 'create_job')
    @mock.patch.object(time, 'sleep')
    def test_create_sfc(self, mock_sleep, mock_create_job, mock_run):
        mock_create_job.return_value = 'job_id_1'
        mock_sleep.return_value = None
        mock_run.return_value = None
        data = {
            'nsInstanceid': "ns_inst_1",
            "context": json.dumps(nsd_model),
            "fpindex": "1",
            'fpinstid': str(uuid.uuid4()),
            "sdnControllerId": "sdnControllerId_1"
        }
        resp = self.client.post("/api/nslcm/v1/ns/sfcs", data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['jobId'], 'job_id_1')

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
