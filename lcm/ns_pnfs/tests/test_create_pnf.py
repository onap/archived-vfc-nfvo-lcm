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

import uuid
import mock
import json
from django.test import TestCase, Client
from rest_framework import status
from lcm.ns_pnfs.biz.create_pnf import CreatePnf
from lcm.pub.utils import restcall


class TestCreatePnfViews(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @mock.patch.object(restcall, 'call_req')
    def test_do_biz(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            'id': str(uuid.uuid4()),
            'pnfdId': 'test',
            'pnfdName': 'test',
            'pnfdVersion': 'v1.1.0',
            'pnfdProvider': 'ZTE',
            'pnfdInvariantId': str(uuid.uuid4())
        }), '200']
        id = str(uuid.uuid4())
        data = {
            "pnfId": id,
            "pnfName": "Test PNF",
            "pnfdId": str(uuid.uuid4()),
            "pnfdInfoId": str(uuid.uuid4()),
            "pnfProfileId": str(uuid.uuid4()),
            "cpInfo": [
                {
                    "cpInstanceId": str(uuid.uuid4()),
                    "cpdId": "pnf_ext_cp01",
                    "cpProtocolData": []
                }
            ],
            "emsId": str(uuid.uuid4()),
            "nsInstances": str(uuid.uuid4()) + "," + str(uuid.uuid4())
        }
        ret = CreatePnf(data).do_biz()
        self.assertIsNotNone(ret)

    @mock.patch.object(restcall, 'call_req')
    def test_rest_api(self, mock_call_req):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            'id': str(uuid.uuid4()),
            'pnfdId': 'test',
            'pnfdName': 'test',
            'pnfdVersion': 'v1.1.0',
            'pnfdProvider': 'ZTE',
            'pnfdInvariantId': str(uuid.uuid4())
        }), '200']
        id = str(uuid.uuid4())
        data = {
            "pnfId": id,
            "pnfName": "Test PNF",
            "pnfdId": str(uuid.uuid4()),
            "pnfdInfoId": str(uuid.uuid4()),
            "pnfProfileId": str(uuid.uuid4()),
            "cpInfo": [
                {
                    "cpInstanceId": str(uuid.uuid4()),
                    "cpdId": "pnf_ext_cp01",
                    "cpProtocolData": []
                }
            ],
            "emsId": str(uuid.uuid4()),
            "nsInstances": str(uuid.uuid4())
        }

        response = self.client.post("/api/nslcm/v1/pnfs", data=data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        data = {
            "pnfId": id,
            "pnfName": "Test PNF",
            "pnfdId": str(uuid.uuid4()),
            "pnfdInfoId": str(uuid.uuid4()),
            "pnfProfileId": str(uuid.uuid4()),
            "cpInfo": [
                {
                    "cpInstanceId": str(uuid.uuid4()),
                    "cpdId": "pnf_ext_cp01",
                    "cpProtocolData": []
                }
            ],
            "emsId": str(uuid.uuid4()),
            "nsInstances": str(uuid.uuid4())
        }

        response = self.client.post("/api/nslcm/v1/pnfs", data=data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
