# Copyright 2019 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import uuid

import mock
from django.test import Client
from django.test import TestCase
from rest_framework import status

from lcm.ns.biz.ns_heal import NSHealService
from lcm.pub.database.models import NSInstModel, NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION
from lcm.ns.tests import VNFD_MODEL_DICT, HEAL_NS_DICT, HEAL_VNF_DICT


class TestHealNsApi(TestCase):
    def setUp(self):
        self.url = "/api/nslcm/v1/ns_instances/%s/heal"
        self.ns_inst_id = str(uuid.uuid4())
        self.nf_inst_id = '1'
        self.nf_uuid = '1-1-1'
        self.job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.HEAL, self.ns_inst_id)
        self.client = Client()
        model = json.dumps(VNFD_MODEL_DICT)
        NSInstModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()
        NSInstModel(id=self.ns_inst_id, name="ns_name", status='null').save()
        NfInstModel.objects.create(
            nfinstid=self.nf_inst_id,
            nf_name='name_1',
            vnf_id='1',
            vnfm_inst_id='1',
            ns_inst_id=self.ns_inst_id,
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='null',
            mnfinstid=self.nf_uuid,
            package_id='pkg1',
            vnfd_model=model)

    def tearDown(self):
        pass

    @mock.patch.object(NSHealService, 'run')
    def test_heal_vnf_url(self, mock_run):
        data = HEAL_VNF_DICT.copy()
        data["healVnfData"]["vnfInstanceId"] = self.nf_inst_id
        response = self.client.post(self.url % self.ns_inst_id, data=data)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.data)
        self.assertIsNotNone(response.data)
        self.assertIsNotNone(response['Location'])
        response = self.client.get(response['Location'], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # add healNsData

    @mock.patch.object(NSHealService, 'run')
    def test_heal_ns_url(self, mock_run):
        data = HEAL_NS_DICT.copy()
        data["healNsData"]["vnfInstanceId"] = self.nf_inst_id
        response = self.client.post(self.url % self.ns_inst_id, data=data)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.data)
        self.assertIsNotNone(response['Location'])
        response = self.client.get(response['Location'], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch.object(NSHealService, "start")
    def test_heal_vnf_non_existing_ns(self, mock_start):
        mock_start.side_effect = NSLCMException("NS Not Found")
        ns_inst_id = "2"
        data = HEAL_VNF_DICT.copy()
        data["healVnfData"]["vnfInstanceId"] = self.nf_inst_id
        response = self.client.post(self.url % ns_inst_id, data=data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # add healNsData
    @mock.patch.object(NSHealService, "start")
    def test_heal_ns_heal_non_existing_ns(self, mock_start):
        mock_start.side_effect = NSLCMException("NS Not Found")
        ns_inst_id = "2"
        data = HEAL_NS_DICT.copy()
        data["healNsData"]["vnfInstanceId"] = self.nf_inst_id
        response = self.client.post(self.url % ns_inst_id, data=data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @mock.patch.object(NSHealService, "start")
    def test_heal_vnf_empty_post(self, mock_start):
        mock_start.side_effect = NSLCMException("healVnfData parameter does not exist or value is incorrect.")
        response = self.client.post(self.url % self.ns_inst_id, data={})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
