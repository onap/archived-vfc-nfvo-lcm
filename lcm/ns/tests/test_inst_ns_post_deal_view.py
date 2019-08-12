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

from django.test import TestCase
from lcm.pub.database.models import NSInstModel, ServiceBaseInfoModel
from lcm.pub.utils import restcall
from rest_framework import status
from rest_framework.test import APIClient
from lcm.ns.tests import NSD_MODEL_DICT_INST_NS_POST_DEAL_VIEW


class NSInstPostDealView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/nslcm/v1/ns/test_ns_instance_id/postdeal"
        self.data = {"status": "true"}
        NSInstModel(id="test_ns_instance_id", name="test_ns_instance_name", nsd_id="test_nsd_id",
                    nsd_invariant_id="test_nsd_invariant_id",
                    nsd_model=json.dumps(NSD_MODEL_DICT_INST_NS_POST_DEAL_VIEW)).save()
        ServiceBaseInfoModel(service_id="test_ns_instance_id", service_name="service_name", service_type="service_type",
                             active_status="active_status", status="status", creator="creator", create_time="0").save()

    def tearDown(self):
        NSInstModel.objects.all().delete()

    @mock.patch.object(restcall, 'call_req')
    def test_inst_ns_post_deal_view(self, mock_call_req):
        ret = {"status": 1}
        mock_vals = {
            "api/polengine/v1/policyinfo":
                [0, json.JSONEncoder().encode(ret), "200"],
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect

        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
