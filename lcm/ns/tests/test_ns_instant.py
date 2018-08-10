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

from rest_framework import status
from django.test import TestCase
from django.test import Client
import mock

from lcm.pub.database.models import NSInstModel
from lcm.ns.ns_instant import InstantNSService
from lcm.pub.utils import restcall


class TestNsInstant(TestCase):
    def setUp(self):
        self.client = Client()
        NSInstModel.objects.filter().delete()
        self.url = "/api/nslcm/v1/ns/2/instantiate"
        self.req_data = {
            "additionalParamForNs": {
                "location": "1",
                "sdnControllerId": "2"
            }
        }
        NSInstModel(id="2", nspackage_id="7", nsd_id="2").save()

    def tearDown(self):
        pass

    @mock.patch.object(InstantNSService, 'do_biz')
    def test_ns_instantiate_normal(self, mock_do_biz):
        mock_do_biz.return_value = dict(data={'jobId': "1"}, status=status.HTTP_200_OK)
        resp = self.client.post(self.url, data=self.req_data)
        self.failUnlessEqual(status.HTTP_200_OK, resp.status_code)
        self.assertEqual({'jobId': "1"}, resp.data)

    @mock.patch.object(restcall, 'call_req')
    def test_ns_instantiate_when_fail_to_parse_nsd(self, mock_call_req):
        mock_call_req.return_value = [1, "Failed to parse nsd", '500']
        resp = self.client.post(self.url, data=self.req_data)
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", resp.data)
