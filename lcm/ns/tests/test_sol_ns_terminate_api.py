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
from lcm.ns.biz.ns_terminate import TerminateNsService
from lcm.pub.database.models import NfInstModel, NSInstModel
from lcm.ns.tests import VNFD_MODEL_DICT


class TestTerminateNsApi(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/api/nslcm/v1/ns_instances/%s/terminate"
        self.ns_inst_id = str(uuid.uuid4())
        self.nf_inst_id = '1'
        self.vnffg_id = str(uuid.uuid4())
        self.vim_id = str(uuid.uuid4())
        self.job_id = str(uuid.uuid4())
        self.nf_uuid = '1-1-1'
        self.tenant = "tenantname"
        NSInstModel(
            id=self.ns_inst_id,
            name="ns_name",
            status='null').save()
        NfInstModel.objects.create(
            nfinstid=self.nf_inst_id,
            nf_name='name_1',
            vnf_id='1',
            vnfm_inst_id='1',
            ns_inst_id='1-1-1,2-2-2',
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='null',
            mnfinstid=self.nf_uuid,
            package_id='pkg1',
            vnfd_model=json.dumps(VNFD_MODEL_DICT))

    def tearDown(self):
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()

    @mock.patch.object(TerminateNsService, 'run')
    def test_terminate_vnf(self, mock_run):
        mock_run.re.return_value = "1"
        req_data = {"terminationTime": "2019-03-25T09:10:35.610"}
        response = self.client.post(self.url % self.ns_inst_id, data=req_data)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertIsNotNone(response['Location'])
        response = self.client.get(response['Location'], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_not_allowed(self):
        response = self.client.put(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.patch(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.delete(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.get(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
