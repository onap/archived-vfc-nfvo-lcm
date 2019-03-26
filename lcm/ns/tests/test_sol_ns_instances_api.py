# Copyright 2019 ZTE Corporation.
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
import uuid

import mock
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIClient
from lcm.pub.database.models import NSInstModel
from lcm.pub.utils import restcall


class TestNsInstanceApi(TestCase):
    def setUp(self):
        self.client = Client()
        self.apiClient = APIClient()
        self.format = 'json'
        self.ns_instances_url = '/api/nslcm/v1/ns_instances'
        self.nsd_id = str(uuid.uuid4())
        self.ns_package_id = str(uuid.uuid4())

    def tearDown(self):
        NSInstModel.objects.all().delete()

    @mock.patch.object(restcall, 'call_req')
    def test_create_ns(self, mock_call_req):
        nspackage_info = {
            "csarId": self.ns_package_id,
            "packageInfo": {
                "nsPackageId": self.ns_package_id,
                "nsdId": self.nsd_id
            }
        }
        r1_query_nspackage_from_catalog = [0, json.JSONEncoder().encode(nspackage_info), '201']
        r2_create_ns_to_aai = [0, json.JSONEncoder().encode({}), '201']
        mock_call_req.side_effect = [r1_query_nspackage_from_catalog, r2_create_ns_to_aai]

        header = {
            'HTTP_GLOBALCUSTOMERID': 'global-customer-id-test1',
            'HTTP_SERVICETYPE': 'service-type-test1'
        }

        data = {
            "nsdId": self.nsd_id,
            "nsName": "ns",
            "nsDescription": "description"
        }
        response = self.apiClient.post(self.ns_instances_url, data=data, format=self.format, **header)

        self.failUnlessEqual(status.HTTP_201_CREATED, response.status_code)
