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


class TestNsInstant(TestCase):
    def setUp(self):
        self.client = Client()
        NSInstModel.objects.filter().delete()
        self.ns_inst_id = "2"
        NSInstModel(id="2", nspackage_id="7", nsd_id="2").save()

    def tearDown(self):
        pass

    @mock.patch.object(InstantNSService, 'do_biz')
    def testNsInstantNormal(self, mock_do_biz):
        mock_do_biz.return_value = dict(data={'jobId': "1"}, status=status.HTTP_200_OK)
        data = {
            "additionalParamForNs": {
                "location": "1",
                "sdnControllerId": "2"
            }
        }
        resp = self.client.post("/api/nslcm/v1/ns/%s/instantiate" % self.ns_inst_id, data=data)
        self.failUnlessEqual(status.HTTP_200_OK, resp.status_code)
        self.assertEqual({'jobId': "1"}, resp.data)
