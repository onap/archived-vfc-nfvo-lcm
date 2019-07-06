# Copyright 2017 Intel Corporation.
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

from django.test import TestCase
import mock
from rest_framework.test import APIClient
from rest_framework import status
from lcm.ns.biz.ns_heal import NSHealService
from lcm.ns.enum import NS_INST_STATUS
from lcm.pub.database.models import NSInstModel, NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION
from lcm.ns_vnfs.biz.heal_vnfs import NFHealService
from lcm.ns.tests import HEAL_NS_DICT, HEAL_VNF_DICT, VNFD_MODEL_DICT


class TestHealNsViews(TestCase):
    def setUp(self):
        self.ns_inst_id = '1'
        self.nf_inst_id = '1'
        self.nf_uuid = '1-1-1'
        self.job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.HEAL, self.ns_inst_id)
        self.client = APIClient()
        NSInstModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()
        NSInstModel(id=self.ns_inst_id, name="ns_name", status='null').save()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id,
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
                                   vnfd_model=VNFD_MODEL_DICT)

    def tearDown(self):
        pass

    @mock.patch.object(NSHealService, 'run')
    def test_heal_vnf_url(self, mock_run):
        heal_vnf_json = HEAL_VNF_DICT.copy()
        heal_vnf_json["healVnfData"]["vnfInstanceId"] = self.nf_inst_id
        response = self.client.post("/api/nslcm/v1/ns/%s/heal" % self.ns_inst_id, data=heal_vnf_json, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.data)
        self.assertIsNotNone(response.data)
        self.assertIn("jobId", response.data)
        self.assertNotIn("error", response.data)
        response = self.client.delete("/api/nslcm/v1/ns/%s" % self.ns_inst_id)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    # add healNsData
    @mock.patch.object(NSHealService, 'run')
    def test_heal_ns_url(self, mock_run):
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json["healNsData"]["vnfInstanceId"] = self.nf_inst_id
        response = self.client.post("/api/nslcm/v1/ns/%s/heal" % self.ns_inst_id, data=heal_ns_json, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.data)
        self.assertIsNotNone(response.data)
        self.assertIn("jobId", response.data)
        self.assertNotIn("error", response.data)
        response = self.client.delete("/api/nslcm/v1/ns/%s" % self.ns_inst_id)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    @mock.patch.object(NFHealService, 'start')
    @mock.patch.object(NSHealService, 'wait_job_finish')
    @mock.patch.object(NSHealService, 'update_job')
    def test_heal_vnf_thread(self, mock_start, mock_wait, mock_update):
        heal_vnf_json = HEAL_VNF_DICT.copy()
        heal_vnf_json["healVnfData"]["vnfInstanceId"] = self.nf_inst_id
        NSHealService(self.ns_inst_id, heal_vnf_json, self.job_id).run()
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.HEALING)

    # add healNsData
    @mock.patch.object(NFHealService, 'start')
    @mock.patch.object(NSHealService, 'wait_job_finish')
    @mock.patch.object(NSHealService, 'update_job')
    def test_heal_ns_thread(self, mock_start, mock_wait, mock_update):
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json["healNsData"]["vnfInstanceId"] = self.nf_inst_id
        NSHealService(self.ns_inst_id, heal_ns_json, self.job_id).run()
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.HEALING)

    @mock.patch.object(NSHealService, "start")
    def test_heal_vnf_non_existing_ns(self, mock_start):
        mock_start.side_effect = NSLCMException("NS Not Found")
        ns_inst_id = "2"
        heal_vnf_json = HEAL_VNF_DICT.copy()
        heal_vnf_json["healVnfData"]["vnfInstanceId"] = self.nf_inst_id
        response = self.client.post("/api/nslcm/v1/ns/%s/heal" % ns_inst_id, data=heal_vnf_json, format='json')
        self.assertEqual(response.data["error"], "NS Not Found")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    # add healNsData
    @mock.patch.object(NSHealService, "start")
    def test_heal_ns_heal_non_existing_ns(self, mock_start):
        mock_start.side_effect = NSLCMException("NS Not Found")
        ns_inst_id = "2"
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json["healNsData"]["vnfInstanceId"] = self.nf_inst_id
        response = self.client.post("/api/nslcm/v1/ns/%s/heal" % ns_inst_id, data=heal_ns_json, format='json')
        self.assertEqual(response.data["error"], "NS Not Found")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    @mock.patch.object(NSHealService, "start")
    def test_heal_vnf_empty_post(self, mock_start):
        mock_start.side_effect = NSLCMException("healVnfData parameter does not exist or value is incorrect.")
        response = self.client.post("/api/nslcm/v1/ns/%s/heal" % self.ns_inst_id, data={})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
