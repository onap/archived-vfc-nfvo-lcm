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
import uuid

import mock
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIClient

from lcm.ns.biz.ns_create import CreateNSService
from lcm.pub.database.models import NSInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils import restcall


class TestNsInstantiate(TestCase):
    def setUp(self):
        self.client = Client()
        self.client1 = APIClient()
        self.nsd_id = str(uuid.uuid4())
        self.ns_package_id = str(uuid.uuid4())

    def tearDown(self):
        NSInstModel.objects.all().delete()

    @mock.patch.object(restcall, 'call_req')
    def test_create_ns(self, mock_call_req):
        nspackage_info = {
            "csarId": self.ns_package_id,
            "packageInfo": {}
        }
        r1_query_nspackage_from_catalog = [0, json.JSONEncoder().encode(nspackage_info), '201']
        r2_create_ns_to_aai = [0, json.JSONEncoder().encode({}), '201']
        mock_call_req.side_effect = [r1_query_nspackage_from_catalog, r2_create_ns_to_aai]
        data = {
            "context": {
                "globalCustomerId": "global-customer-id-test1",
                "serviceType": "service-type-test1"
            },
            "csarId": self.nsd_id,
            "nsName": "ns",
            "description": "description"
        }
        response = self.client1.post("/api/nslcm/v1/ns", data=data, format='json')
        self.failUnlessEqual(status.HTTP_201_CREATED, response.status_code)

    @mock.patch.object(CreateNSService, "do_biz")
    def test_create_ns_empty_data(self, mock_do_biz):
        mock_do_biz.side_effect = Exception("Exception in CreateNS.")
        data = {}
        response = self.client.post("/api/nslcm/v1/ns", data=data)
        self.assertEqual(response.data["error"], "Exception in CreateNS.")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    @mock.patch.object(CreateNSService, "do_biz")
    def test_create_ns_non_existing_nsd(self, mock_do_biz):
        mock_do_biz.side_effect = NSLCMException("nsd not exists.")
        new_nsd_id = '1'
        data = {
            'csarId': new_nsd_id,
            'nsName': 'ns',
            'description': 'description'
        }
        response = self.client.post("/api/nslcm/v1/ns", data=data)
        self.assertEqual(response.data["error"], "nsd not exists.")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    @mock.patch.object(restcall, 'call_req')
    def test_create_ns_when_fail_to_get_nsd(self, mock_call_req):
        mock_call_req.return_value = [1, "Failed to get nsd.", '500']
        data = {
            'csarId': '1',
            'nsName': 'ns',
            'description': 'description'
        }
        response = self.client.post("/api/nslcm/v1/ns", data=data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    @mock.patch.object(restcall, 'call_req')
    def test_create_ns_when_ns_name_exist(self, mock_call_req):
        nspackage_info = json.JSONEncoder().encode({
            "csarId": self.ns_package_id,
            "packageInfo": {}
        })
        mock_call_req.return_value = [0, nspackage_info, '200']
        NSInstModel(id="1", name="ns1").save()
        data = {
            'csarId': '1',
            'nsName': 'ns1',
            'description': 'description'
        }
        response = self.client.post("/api/nslcm/v1/ns", data=data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
