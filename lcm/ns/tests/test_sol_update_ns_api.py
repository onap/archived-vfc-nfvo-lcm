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

import mock
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from lcm.pub.database.models import NSInstModel
from lcm.ns.biz.ns_update import NSUpdateService
from lcm.ns.tests import NSD_MODEL_DICT


class TestUpdateNSApi(TestCase):

    def setUp(self):
        self.apiClient = APIClient()
        self.format = "json"
        self.url = "/api/nslcm/v1/ns_instances/test_update_ns/update"
        self.data = {"updateType": "ADD_VNF"}
        NSInstModel(id="test_update_ns", name="test_ns_instance_name", nsd_id="test_nsd_id",
                    nsd_invariant_id="test_nsd_invariant_id", nsd_model=json.dumps(NSD_MODEL_DICT)).save()

    def tearDown(self):
        NSInstModel.objects.all().delete()

    @mock.patch.object(NSUpdateService, 'run')
    def test_create_ns(self, mock_run):
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
