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

from lcm.pub.database.models import NSInstModel, NSDModel
from lcm.pub.utils import restcall


class TestNsInstantiate(TestCase):
    def setUp(self):
        self.client = Client()
        self.nsd_id = str(uuid.uuid4())
        self.ns_package_id = str(uuid.uuid4())
        NSDModel(id=self.ns_package_id, nsd_id=self.nsd_id, name='name').save()

    def tearDown(self):
        NSDModel.objects.all().delete()
        NSInstModel.objects.all().delete()

    @mock.patch.object(restcall, 'call_req')
    def test_create_ns(self, mock_call_req):
        r1_create_ns_to_aai = [0, json.JSONEncoder().encode({}), '201']
        mock_call_req.side_effect = [r1_create_ns_to_aai]
        data = {
            'nsdid': self.nsd_id,
            'nsname': 'ns',
            'description': 'description'}
        response = self.client.post("/api/nslcm/v1/ns", data=data)
        self.failUnlessEqual(status.HTTP_201_CREATED, response.status_code)
