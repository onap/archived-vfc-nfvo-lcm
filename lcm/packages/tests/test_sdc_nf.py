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
import mock
from rest_framework import status
from django.test import TestCase
from django.test import Client

from lcm.pub.utils import restcall, toscaparser
from lcm.pub.utils import fileutil
from lcm.pub.database.models import NfPackageModel, NfInstModel
from lcm.pub.database.models import JobStatusModel, JobModel
from lcm.packages.sdc_nf_package import SdcNfDistributeThread, SdcNfPkgDeleteThread
from lcm.packages import sdc_nf_package
from lcm.pub.msapi import sdc

class TestNfPackage(TestCase):
    def setUp(self):
        self.client = Client()
        NfPackageModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()
        JobModel.objects.filter().delete()
        JobStatusModel.objects.filter().delete()
        self.vnfd_data = {
            "volume_storages": [
                {
                    "properties": {
                        "size_of_storage": {
                            "factor": 10,
                            "value": 10000000000,
                            "unit": "GB",
                            "unit_size": 1000000000
                        },
                        "type_of_storage": "volume",
                        "rdma_enabled": False,
                        "size": "10 GB"
                    },
                    "volume_storage_id": "vNAT_Storage_6wdgwzedlb6sq18uzrr41sof7",
                    "description": ""
                }
            ],
            "inputs": {},
            "vdus": [
                {
                    "volume_storages": [
                        "vNAT_Storage_6wdgwzedlb6sq18uzrr41sof7"
                    ],
                    "description": "",
                    "dependencies": [],
                    "vls": [],
                    "properties": {
                        "name": "vNat",
                        "configurable_properties": {
                            "test": {
                                "additional_vnfc_configurable_properties": {
                                    "aaa": "1",
                                    "bbb": "2",
                                    "ccc": "3"
                                }
                            }
                        },
                        "description": "the virtual machine of vNat",
                        "nfvi_constraints": [
                            "test"
                        ],
                        "boot_order": [
                            "vNAT_Storage"
                        ]
                    },
                    "vdu_id": "vdu_vNat",
                    "artifacts": [
                        {
                            "artifact_name": "vNatVNFImage",
                            "type": "tosca.artifacts.nfv.SwImage",
                            "properties": {
                                "operating_system": "linux",
                                "sw_image": "/swimages/vRouterVNF_ControlPlane.qcow2",
                                "name": "vNatVNFImage",
                                "container_format": "bare",
                                "min_ram": "1 GB",
                                "disk_format": "qcow2",
                                "supported_virtualisation_environments": [
                                    "test_0"
                                ],
                                "version": "1.0",
                                "checksum": "5000",
                                "min_disk": "10 GB",
                                "size": "10 GB"
                            },
                            "file": "/swimages/vRouterVNF_ControlPlane.qcow2"
                        }
                    ],
                    "nfv_compute": {
                        "flavor_extra_specs": {
                            "hw:cpu_sockets": "2",
                            "sw:ovs_dpdk": "true",
                            "hw:cpu_threads": "2",
                            "hw:numa_mem.1": "3072",
                            "hw:numa_mem.0": "1024",
                            "hw:numa_nodes": "2",
                            "hw:numa_cpus.0": "0,1",
                            "hw:numa_cpus.1": "2,3,4,5",
                            "hw:cpu_cores": "2",
                            "hw:cpu_threads_policy": "isolate"
                        },
                        "cpu_frequency": "2.4 GHz",
                        "num_cpus": 2,
                        "mem_size": "10 GB"
                    },
                    "local_storages": [],
                    "image_file": "vNatVNFImage",
                    "cps": []
                }
            ],
            "image_files": [
                {
                    "properties": {
                        "operating_system": "linux",
                        "sw_image": "/swimages/vRouterVNF_ControlPlane.qcow2",
                        "name": "vNatVNFImage",
                        "container_format": "bare",
                        "min_ram": "1 GB",
                        "disk_format": "qcow2",
                        "supported_virtualisation_environments": [
                            "test_0"
                        ],
                        "version": "1.0",
                        "checksum": "5000",
                        "min_disk": "10 GB",
                        "size": "10 GB"
                    },
                    "image_file_id": "vNatVNFImage",
                    "description": ""
                }
            ],
            "routers": [],
            "local_storages": [],
            "vnf_exposed": {
                "external_cps": [
                    {
                        "key_name": "sriov_plane",
                        "cp_id": "SRIOV_Port"
                    }
                ],
                "forward_cps": []
            },
            "vls": [
                {
                    "route_id": "",
                    "vl_id": "sriov_link",
                    "route_external": False,
                    "description": "",
                    "properties": {
                        "vl_flavours": {
                            "vl_id": "aaaa"
                        },
                        "connectivity_type": {
                            "layer_protocol": "ipv4",
                            "flow_pattern": "flat"
                        },
                        "description": "sriov_link",
                        "test_access": [
                            "test"
                        ]
                    }
                }
            ],
            "cps": [
                {
                    "vl_id": "sriov_link",
                    "vdu_id": "vdu_vNat",
                    "description": "",
                    "cp_id": "SRIOV_Port",
                    "properties": {
                        "address_data": [
                            {
                                "address_type": "ip_address",
                                "l3_address_data": {
                                    "ip_address_type": "ipv4",
                                    "floating_ip_activated": False,
                                    "number_of_ip_address": 1,
                                    "ip_address_assignment": True
                                }
                            }
                        ],
                        "description": "sriov port",
                        "layer_protocol": "ipv4",
                        "virtual_network_interface_requirements": [
                            {
                                "requirement": {
                                    "SRIOV": "true"
                                },
                                "support_mandatory": False,
                                "name": "sriov",
                                "description": "sriov"
                            },
                            {
                                "requirement": {
                                    "SRIOV": "False"
                                },
                                "support_mandatory": False,
                                "name": "normal",
                                "description": "normal"
                            }
                        ],
                        "role": "root",
                        "bitrate_requirement": 10
                    }
                }
            ],
            "metadata": {
                "vnfSoftwareVersion": "1.0.0",
                "vnfProductName": "zte",
                "localizationLanguage": [
                    "english",
                    "chinese"
                ],
                "vnfProvider": "zte",
                "vnfmInfo": "zte",
                "defaultLocalizationLanguage": "english",
                "vnfdId": "zte-hss-1.0",
                "id": "zte-hss-1.0",
                "vnfProductInfoDescription": "hss",
                "vnfdVersion": "1.0.0",
                "vnfProductInfoName": "hss"
            }
        }

    def tearDown(self):
        pass

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail)
        self.assertEqual(1, len(jobs))

    @mock.patch.object(SdcNfDistributeThread, 'run')
    def test_nf_pkg_distribute_normal(self, mock_run):
        resp = self.client.post("/api/nslcm/v1/vnfpackage", {
            "csarId": "1",
            "vimIds": ["1"]
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
    """
    def test_nf_pkg_distribute_when_csar_already_exist(self):
        NfPackageModel(uuid="1", nfpackageid="1", vnfdid="vcpe_vfw_zte_1_0").save()
        SdcNfDistributeThread(csar_id="1",
                           vim_ids=["1"],
                           lab_vim_id="",
                           job_id="2").run()
        self.assert_job_result("2", 255, "NF CSAR(1) already exists.")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(sdc, 'download_artifacts')
    @mock.patch.object(toscaparser, 'parse_vnfd')
    def test_nf_pkg_distribute_when_vnfd_already_exist(self,
    	mock_parse_vnfd, mock_download_artifacts, mock_call_req):
    	mock_parse_vnfd.return_value = json.JSONEncoder().encode(self.vnfd_data)
        mock_download_artifacts.return_value = "/home/hss.csar"
        mock_call_req.return_value = [0, json.JSONEncoder().encode([{
            "uuid": "1",
            "toscaModelURL": "https://127.0.0.1:1234/sdc/v1/hss.csar"
            }]), '200']
        NfPackageModel(uuid="2", nfpackageid="2", vnfdid="zte-hss-1.0").save()
        SdcNfDistributeThread(csar_id="1",
                           vim_ids=["1"],
                           lab_vim_id="",
                           job_id="2").run()
        self.assert_job_result("2", 255, "NFD(zte-hss-1.0) already exists.")
    
    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(sdc, 'download_artifacts')
    @mock.patch.object(toscaparser, 'parse_vnfd')
    def test_nf_pkg_distribute_successfully(self,
    	mock_parse_vnfd, mock_download_artifacts, mock_call_req):
    	mock_parse_vnfd.return_value = json.JSONEncoder().encode(self.vnfd_data)
        mock_download_artifacts.return_value = "/home/hss.csar"
        mock_call_req.return_value = [0, json.JSONEncoder().encode([{
            "uuid": "1",
            "toscaModelURL": "https://127.0.0.1:1234/sdc/v1/hss.csar"
            }]), '200']
        SdcNfDistributeThread(csar_id="1",
                           vim_ids=["1"],
                           lab_vim_id="",
                           job_id="4").run()
        self.assert_job_result("4", 100, "CSAR(1) distribute successfully.")
    """

    ###############################################################################################################

    @mock.patch.object(SdcNfPkgDeleteThread, 'run')
    def test_nf_pkg_delete_normal(self, mock_run):
        resp = self.client.delete("/api/nslcm/v1/vnfpackage/1")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
    """
    def test_nf_pkg_normal_delete(self):
        NfPackageModel(uuid="2", nfpackageid="2", vnfdid="vcpe_vfw_zte_1_0").save()
        SdcNfPkgDeleteThread(csar_id="2", job_id="2", force_delete=False).run()
        self.assert_job_result("2", 100, "Delete CSAR(2) successfully.")

    def test_nf_pkg_force_delete(self):
        NfPackageModel(uuid="1", nfpackageid="1", vnfdid="vcpe_vfw_zte_1_0").save()
        NfInstModel(nfinstid="1", package_id="1").save()
        SdcNfPkgDeleteThread(csar_id="1", job_id="2", force_delete=True).run()
        self.assert_job_result("2", 100, "Delete CSAR(1) successfully.")

    def test_nf_pkg_delete_when_pkg_in_using(self):
        NfPackageModel(uuid="3", nfpackageid="3", vnfdid="vcpe_vfw_zte_1_0").save()
        NfInstModel(nfinstid="3", package_id="3").save()
        SdcNfPkgDeleteThread(csar_id="3", job_id="2", force_delete=False).run()
        self.assert_job_result("2", 255, "NfInst by csar(3) exists, cannot delete.")
    """

    def test_nf_pkg_get_all(self):
        NfPackageModel(uuid="3", nfpackageid="3", vnfdid="4").save()

        resp = self.client.get("/api/nslcm/v1/vnfpackage")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual({"csars": [{"csarId":"3", "vnfdId": "4"}]}, resp.data)

    def test_nf_pkg_get_one(self):
        NfPackageModel(uuid="4", nfpackageid="4", vnfdid="5", 
        	vendor="6", vnfdversion="7", vnfversion="8").save()
        NfInstModel(nfinstid="1", package_id="4", nf_name="3").save()

        resp = self.client.get("/api/nslcm/v1/vnfpackage/4")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual({"csarId": "4", 
            "packageInfo": {
                "vnfdId": "5",
                "vnfdProvider": "6",
                "vnfdVersion": "7",
                "vnfVersion": "8"
            }, 
            "imageInfo": [],
            "vnfInstanceInfo": [{
                "vnfInstanceId": "1", "vnfInstanceName": "3"
            }]}, resp.data)







