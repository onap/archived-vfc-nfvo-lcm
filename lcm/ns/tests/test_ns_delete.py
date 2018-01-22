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

from lcm.pub.database.models import NSInstModel
from lcm.pub.utils import restcall


class TestNsDelelete(TestCase):
    def setUp(self):
        self.client = Client()
        self.ns_inst_id = str(uuid.uuid1())
        NSInstModel.objects.filter().delete()
        NSInstModel(id=self.ns_inst_id, nspackage_id="7", nsd_id="2").save()

    def tearDown(self):
        NSInstModel.objects.all().delete()

    @mock.patch.object(restcall, 'call_req')
    def test_delete_ns(self, mock_call_req):
        ns_info = {
            "service-instance-id": "service-instance-id-9b9348f2-f75d-4559-823d-db7ac138ed34",
            "service-instance-name": "service-instance-name-9b9348f2-f75d-4559-823d-db7ac138ed34",
            "service-type": "service-type-9b9348f2-f75d-4559-823d-db7ac138ed34",
            "service-role": "service-role-9b9348f2-f75d-4559-823d-db7ac138ed34",
            "resource-version": "1505350720009"
        }
        r1_query_ns_to_aai = [0, json.JSONEncoder().encode(ns_info), '200']
        r2_delete_ns_to_aai = [0, json.JSONEncoder().encode({}), '200']
        mock_call_req.side_effect = [r1_query_ns_to_aai, r2_delete_ns_to_aai]
        response = self.client.delete("/api/nslcm/v1/ns/%s" % self.ns_inst_id)
        self.failUnlessEqual(status.HTTP_204_NO_CONTENT, response.status_code)
