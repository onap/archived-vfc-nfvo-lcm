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

import unittest
import json

import mock
from rest_framework.test import APIClient
from rest_framework import status

from lcm.jobs.enum import JOB_TYPE, JOB_ACTION
from lcm.ns_vnfs.biz.terminate_nfs import TerminateVnfs
from lcm.ns_vnfs.tests.const import GRANT_DATA, VNF_LCM_OP_OCC_NOTIFICATION_DATA, \
    VNF_IDENTIFIER_CREATION_NOTIFICATION_DATA, VNF_IDENTIFIER_DELETION_NOTIFICATION_DATA
from lcm.pub.database.models import NfInstModel
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil


class VnfGrantViewTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        pass

    @mock.patch.object(restcall, 'call_req')
    def test_grant_vnf_normal(self, mock_call_req):
        vim_connections = {
            "vim": {
                "id": "1",
                "vimId": "1",
                "accessInfo": {}
            }
        }
        mock_call_req.return_value = [0, json.JSONEncoder().encode(vim_connections), '200']
        response = self.client.post("/api/nslcm/v2/grants", data=GRANT_DATA, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content)
        # resp_data = json.loads(response.content)
        # expect_resp_data = {
        #     "id": resp_data.get("id"),
        #     "vnfInstanceId": "1",
        #     "vnfLcmOpOccId": "2",
        #     "vimConnections": [
        #         {
        #             "id": "1",
        #             "vimId": "1"
        #         }
        #     ]
        # }
        # self.assertEqual(expect_resp_data, resp_data)

    def test_grant_vnf_when_vnfinst_not_exist(self):
        response = self.client.post("/api/nslcm/v2/grants", data=GRANT_DATA, format='json')
        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)

    @mock.patch.object(restcall, 'call_req')
    def test_grant_vnf(self, mock_call_req):
        data = {
            "vnfInstanceId": "1",
            "vnfLcmOpOccId": "2",
            "vnfdId": "3",
            "flavourId": "4",
            "operation": "INSTANTIATE",
            "isAutomaticInvocation": True,
            "instantiationLevelId": "5",
            "addResources": [
                {
                    "id": "1",
                    "type": "COMPUTE",
                    "vduId": "2",
                    "resourceTemplateId": "3",
                    "vdu": "1"
                }
            ],
            "additionalParams": {"vnfmid": "3"},
            "_links": {
                "vnfLcmOpOcc": {
                    "href": "1"
                },
                "vnfInstance": {
                    "href": "2"
                }
            }
        }
        vnfdModel = {
            "volume_storages": [],
            "vdus": [{
                "vdu_id": "1",
                "properties": {
                    "name": "1"
                },
                "local_storages": "2",
                "virtual_compute": {
                    "virtual_cpu": {
                        "num_virtual_cpu": "111"
                    },
                    "virtual_memory": {
                        "virtual_mem_size": "3 B"
                    }
                },
            }],
            "image_files": [],
            "routers": [],
            "local_storages": [{"local_storage_id": "1"}],
            "vnf_exposed": {
                "external_cps": [],
                "forward_cps": []
            },
            "vls": [],
            "cps": [],
            "metadata": {
                "designer": "sdno",
                "name": "underlayervpn",
                "csarVersion": "1.0",
                "csarType": "SSAR",
                "csarProvider": "huawei",
                "version": "1.0",
                "type": "SSAR",
                "id": "ns_underlayervpn_1_0"
            }
        }

        vnfpackage_info = {
            "imageInfo": [],
            "csarId": "vOpenNAT",
            "packageInfo": {
                "csarName": "vOpenNAT.csar",
                "vnfdModel": json.dumps(vnfdModel),
                "vnfdProvider": "Intel",
                "vnfdId": "openNAT_1.0",
                "downloadUrl": "http://10.96.33.39:8806/static/catalog/vOpenNAT/vOpenNAT.csar",
                "vnfVersion": "v1.0",
                "vnfdVersion": "v1.0",
                "vnfPackageId": "vOpenNAT"
            }
        }
        vimConnections = {
            "vim": {
                "id": "1",
                "vimId": "1",
                "accessInfo": {}
            }
        }
        NfInstModel.objects.create(nfinstid='1',
                                   mnfinstid='1',
                                   package_id="2",
                                   vnfm_inst_id='3')
        get_vnfpackage = [0, json.JSONEncoder().encode(vnfpackage_info), '200']
        get_vimConnections = [0, json.JSONEncoder().encode(vimConnections), '200']
        mock_call_req.side_effect = [get_vnfpackage, get_vimConnections]
        response = self.client.post("/api/nslcm/v2/grants", data=data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content)
        # resp_data = json.loads(response.content)
        # expect_resp_data = {
        #     "id": resp_data.get("id"),
        #     "vnfInstanceId": "1",
        #     "vnfLcmOpOccId": "2",
        #     "vimConnections": [
        #         {
        #             "id": "1",
        #             "vimId": "1"
        #         }
        #     ]
        # }
        # self.assertEqual(expect_resp_data, resp_data)

    def test_get_notify_vnf_normal(self):
        response = self.client.get("/api/nslcm/v2/ns/1/vnfs/1/Notify")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code, response.content)

    def test_notify_vnflcmopooc_normal(self):
        NfInstModel.objects.create(nfinstid='22',
                                   mnfinstid='2',
                                   vnfm_inst_id='1')
        response = self.client.post("/api/nslcm/v2/ns/1/vnfs/2/Notify",
                                    data=VNF_LCM_OP_OCC_NOTIFICATION_DATA,
                                    format='json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_notify_vnf_identifier_creation_normal(self):
        response = self.client.post("/api/nslcm/v2/ns/1/vnfs/2/Notify",
                                    data=VNF_IDENTIFIER_CREATION_NOTIFICATION_DATA,
                                    format='json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_notify_vnf_identifier_deletion_normal(self):
        NfInstModel.objects.create(nfinstid='22',
                                   mnfinstid='2',
                                   vnfm_inst_id='1')
        response = self.client.post("/api/nslcm/v2/ns/1/vnfs/2/Notify",
                                    data=VNF_IDENTIFIER_DELETION_NOTIFICATION_DATA,
                                    format='json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    @mock.patch.object(TerminateVnfs, 'run')
    def test_vnf_terminate(self, mock_run):
        vnf_instance_id = '628fd152-0089-4c20-b549-f35cb2fd4933'
        data = {
            'terminationType': 'FORCEFUL',
            'gracefulTerminationTimeout': 600
        }
        response = self.client.post("/api/nslcm/v1/ns/terminatevnf/%s" % vnf_instance_id, data=data)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.data)
