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
import mock
import uuid
from django.test import TestCase, Client
from lcm.pub.database.models import NSInstModel
from lcm.pub.utils import restcall
from rest_framework import status
from lcm.ns.tests import NS_INFO_AAI_DICT


class TestNsDelete(TestCase):
    def setUp(self):
        self.client = Client()
        self.ns_inst_id = str(uuid.uuid1())
        NSInstModel.objects.filter().delete()
        NSInstModel(id=self.ns_inst_id, nspackage_id="7", nsd_id="2", name='name',
                    nsd_invariant_id='123', description='description',
                    sdncontroller_id='456', flavour_id='789').save()

    def tearDown(self):
        NSInstModel.objects.all().delete()

    @mock.patch.object(restcall, 'call_req')
    def test_delete_ns_in_aai(self, mock_call_req):
        r1_query_ns_to_aai = [0, json.JSONEncoder().encode(NS_INFO_AAI_DICT), '200']
        r2_delete_ns_to_aai = [0, json.JSONEncoder().encode({}), '200']
        mock_call_req.side_effect = [r1_query_ns_to_aai, r2_delete_ns_to_aai]
        response = self.client.delete("/api/nslcm/v1/ns/%s" % self.ns_inst_id)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    @mock.patch.object(restcall, 'call_req')
    def test_delete_ns_in_databases(self, mock_call_req):
        data = NSInstModel.objects.filter()
        if data:
            data = NSInstModel.objects.filter().delete()
        else:
            data = {}
        delet_ns_in_database = [0, data, '200']
        query_data = NSInstModel.objects.filter()
        query_ns_in_database = [0, query_data, '200']
        mock_call_req.side_effect = [delet_ns_in_database, query_ns_in_database]
        response = self.client.delete("/api/nslcm/v1/ns/%s" % self.ns_inst_id)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
