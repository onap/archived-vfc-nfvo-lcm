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
from lcm.pub.database.models import NfInstModel
from lcm.pub.utils import restcall


class VnfGrantViewTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        pass

    @mock.patch.object(restcall, 'call_req')
    def test_grant_vnf_normal(self, mock_call_req):
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
                    "resourceTemplate": {
                        "vimConnectionId": "4",
                        "resourceProviderId": "5",
                        "resourceId": "6",
                        "vimLevelResourceType": "7"
                    }
                }
            ],
            "placementConstraints": [
                {
                    "affinityOrAntiAffinity": "AFFINITY",
                    "scope": "NFVI_POP",
                    "resource": [
                        {
                            "idType": "RES_MGMT",
                            "resourceId": "1",
                            "vimConnectionId": "2",
                            "resourceProviderId": "3"
                        }
                    ]
                }
            ],
            "vimConstraints": [
                {
                    "sameResourceGroup": True,
                    "resource": [
                        {
                            "idType": "RES_MGMT",
                            "resourceId": "1",
                            "vimConnectionId": "2",
                            "resourceProviderId": "3"
                        }
                    ]
                }
            ],
            "additionalParams": {},
            "_links": {
                "vnfLcmOpOcc": {
                    "href": "1"
                },
                "vnfInstance": {
                    "href": "2"
                }
            }
        }
        vimConnections = {
            "id": "1",
            "vimId": "1",
        }
        mock_call_req.return_value = [0, json.JSONEncoder().encode(vimConnections), '200']
        response = self.client.post("/api/nslcm/v2/grants", data=data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content)
        resp_data = json.loads(response.content)
        expect_resp_data = {
            "id": resp_data.get("id"),
            "vnfInstanceId": "1",
            "vnfLcmOpOccId": "2",
            "vimConnections": [
                {
                    "id": "1",
                    "vimId": "1"
                }
            ]
        }
        self.assertEqual(expect_resp_data, resp_data)

    def test_grant_vnf_when_vnfinst_not_exist(self):
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
                }
            ],
            "placementConstraints": [
                {
                    "affinityOrAntiAffinity": "AFFINITY",
                    "scope": "NFVI_POP",
                    "resource": [
                        {
                            "idType": "RES_MGMT",
                            "resourceId": "1",
                            "vimConnectionId": "2",
                            "resourceProviderId": "3"
                        }
                    ]
                }
            ],
            "vimConstraints": [
                {
                    "sameResourceGroup": True,
                    "resource": [
                        {
                            "idType": "RES_MGMT",
                            "resourceId": "1",
                            "vimConnectionId": "2",
                            "resourceProviderId": "3"
                        }
                    ]
                }
            ],
            "additionalParams": {},
            "_links": {
                "vnfLcmOpOcc": {
                    "href": "1"
                },
                "vnfInstance": {
                    "href": "2"
                }
            }
        }
        response = self.client.post("/api/nslcm/v2/grants", data=data, format='json')
        self.failUnlessEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)

    def test_get_notify_vnf_normal(self):
        response = self.client.get("/api/nslcm/v2/ns/1/vnfs/1/Notify")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code, response.content)

    def test_notify_vnf_normal(self):
        data = {
            "id": "string",
            "notificationType": "string",
            "subscriptionId": "string",
            "timeStamp": "string",
            "notificationStatus": "START",
            "operationState": "STARTING",
            "vnfInstanceId": "string",
            "operation": "INSTANTIATE",
            "isAutomaticInvocation": True,
            "vnfLcmOpOccId": "string",
            "affectedVnfcs": [{
                "id": "string",
                "vduId": "string",
                "changeType": "ADDED",
                "computeResource": {
                    "vimConnectionId": "string",
                    "resourceProviderId": "string",
                    "resourceId": "string",
                    "vimLevelResourceType": "string"
                },
                "metadata": {},
                "affectedVnfcCpIds": [],
                "addedStorageResourceIds": [],
                "removedStorageResourceIds": [],
            }],
            "affectedVirtualLinks": [{
                "id": "string",
                "virtualLinkDescId": "string",
                "changeType": "ADDED",
                "networkResource": {
                    "vimConnectionId": "string",
                    "resourceProviderId": "string",
                    "resourceId": "string",
                    "vimLevelResourceType": "network",
                }
            }],
            "affectedVirtualStorages": [{
                "id": "string",
                "virtualStorageDescId": "string",
                "changeType": "ADDED",
                "storageResource": {
                    "vimConnectionId": "string",
                    "resourceProviderId": "string",
                    "resourceId": "string",
                    "vimLevelResourceType": "network",
                },
                "metadata": {}
            }],
            "changedInfo": {
                "vnfInstanceName": "string",
                "vnfInstanceDescription": "string",
                "vnfConfigurableProperties": {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string"
                },
                "metadata": {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string"
                },
                "extensions": {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string"
                },
                "vimConnectionInfo": [{
                    "id": "string",
                    "vimId": "string",
                    "vimType": "string",
                    "interfaceInfo": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string"
                    },
                    "accessInfo": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string"
                    },
                    "extra": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string"
                    }
                }],
                "vnfPkgId": "string",
                "vnfdId": "string",
                "vnfProvider": "string",
                "vnfProductName": "string",
                "vnfSoftwareVersion": "string",
                "vnfdVersion": "string"
            },
            "changedExtConnectivity": [{
                "id": "string",
                "resourceHandle": {
                    "vimConnectionId": "string",
                    "resourceProviderId": "string",
                    "resourceId": "string",
                    "vimLevelResourceType": "string"
                },
                "extLinkPorts": [{
                    "id": "string",
                    "resourceHandle": {
                        "vimConnectionId": "string",
                        "resourceProviderId": "string",
                        "resourceId": "string",
                        "vimLevelResourceType": "string"
                    },
                    "cpInstanceId": "string"
                }]
            }],
            "error": {
                "type": "string",
                "title": "string",
                "status": 0,
                "detail": "string",
                "instance": "string"
            },
            "_links": {
                "vnfInstance": {
                    "href": "string"
                },
                "subscription": {
                    "href": "string"
                },
                "vnfLcmOpOcc": {
                    "href": "string"
                }
            }
        }
        NfInstModel.objects.create(nfinstid='22',
                                   mnfinstid='2',
                                   vnfm_inst_id='1')
        response = self.client.post("/api/nslcm/v2/ns/1/vnfs/2/Notify", data=data, format='json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code, response.content)
