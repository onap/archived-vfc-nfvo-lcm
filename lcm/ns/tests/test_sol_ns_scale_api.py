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
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from lcm.ns.biz.ns_manual_scale import NSManualScaleService
from lcm.pub.database.models import NSInstModel, JobModel, NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION
from lcm.ns.tests import VNFD_MODEL_DICT, SCALE_NS_DICT


class TestScaleNsApi(TestCase):
    def setUp(self):
        self.url = "/api/nslcm/v1/ns_instances/%s/scale"
        self.ns_inst_id = str(uuid.uuid4())
        self.job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.MANUAL_SCALE, self.ns_inst_id)
        self.package_id = "7"
        self.client = APIClient()
        NSInstModel(
            id=self.ns_inst_id,
            name="abc",
            nspackage_id=self.package_id,
            nsd_id="111").save()

    def tearDown(self):
        NSInstModel.objects.filter().delete()
        JobModel.objects.filter().delete()

    def insert_new_ns(self):
        ns_inst_id = str(uuid.uuid4())
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.MANUAL_SCALE, self.ns_inst_id)
        package_id = "23"
        NSInstModel(
            id=ns_inst_id,
            name="abc",
            nspackage_id=package_id,
            nsd_id=package_id).save()
        return ns_inst_id, job_id

    def insert_new_nf(self):
        self.nf_name = "name_1"
        self.vnf_id = "1"
        self.vnfm_inst_id = "1"
        nf_inst_id = "233"
        package_id = "nf_zte_hss"
        nf_uuid = "ab34-3g5j-de13-ab85-ij93"
        NfInstModel.objects.create(
            nfinstid=nf_inst_id,
            nf_name=self.nf_name,
            vnf_id=self.vnf_id,
            vnfm_inst_id=self.vnfm_inst_id,
            ns_inst_id=self.ns_inst_id,
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='active',
            mnfinstid=nf_uuid,
            package_id=package_id,
            vnfd_model=json.dumps(VNFD_MODEL_DICT)
        )

    @mock.patch.object(NSManualScaleService, 'run')
    def test_ns_scale(self, mock_run):
        response = self.client.post(self.url % self.ns_inst_id, data=SCALE_NS_DICT)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertIsNotNone(response['Location'])
        response = self.client.get(response['Location'], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch.object(NSManualScaleService, 'start')
    def test_ns_manual_scale_empty_data(self, mock_start):
        mock_start.side_effect = NSLCMException("NS scale failed.")
        response = self.client.post(self.url % self.ns_inst_id, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch.object(NSManualScaleService, 'start')
    def test_ns_manual_scale_when_ns_not_exist(self, mock_start):
        mock_start.side_effect = NSLCMException("NS scale failed.")
        response = self.client.post(self.url % '11', data=SCALE_NS_DICT)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_method_not_allowed(self):
        response = self.client.put(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.patch(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.delete(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.get(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
