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
from django.test import Client
from rest_framework import status


class VnfGrantViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_grant_vnf_normal(self):
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
                    "resource": {
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
        response = self.client.post("/api/nslcm/v2/grants", data=data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code, response.content)
        resp_data = json.loads(response.content)
        expect_resp_data = {
            "id": resp_data.get("id"),
            "vnfInstanceId": "1",
            "vnfLcmOpOccId": "2"
        }
        self.assertEqual(expect_resp_data, resp_data)

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
                "changeType": "added",
                "computeResource": {
                    "vimConnectionId": "string",
                    "resourceProviderId": "string",
                    "resouceId": "string",
                    "vimLevelResourceType": "string"
                },
                "metadata": {},
                "affectedVnfcCpIds": [],
                "addedStorageResourceIds": [],
                "removedStorageResourceIds": [],
            }],
            "affectedVirtualLinks": [{
                "vlInstanceId": "string",
                "vldId": "string",
                "changeType": "added",
                "networkResource": {
                    "resourceType": "network",
                    "resourceId": "string",
                    "resourceName": "string"
                }
            }],
            "affectedVirtualStorages": [{}],
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
        response = self.client.post("/api/nslcm/v2/ns/1/vnfs/2/Notify", data=data, format='json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code, response.content)
