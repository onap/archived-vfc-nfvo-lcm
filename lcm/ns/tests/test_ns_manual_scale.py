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
from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework import status

from lcm.ns.biz.ns_manual_scale import NSManualScaleService
from lcm.ns.enum import NS_INST_STATUS
from lcm.pub.database.models import NSInstModel, JobModel, NfInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi import catalog
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_MODEL_STATUS, JOB_TYPE, JOB_ACTION
from lcm.ns.tests import SCALING_MAP_DICT, VNFD_MODEL_DICT, SCALE_NS_DICT


class TestNsManualScale(TestCase):

    def setUp(self):
        self.scaling_map_json = SCALING_MAP_DICT
        self.ns_inst_id = str(uuid.uuid4())
        self.job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.MANUAL_SCALE, self.ns_inst_id)
        self.client = APIClient()
        self.package_id = "7"
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
        self.vnfm_inst_id = "1"
        NfInstModel.objects.create(
            nfinstid="233",
            nf_name="name_1",
            vnf_id="1",
            vnfm_inst_id="1",
            ns_inst_id=self.ns_inst_id,
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='active',
            mnfinstid="ab34-3g5j-de13-ab85-ij93",
            package_id="nf_zte_hss",
            vnfd_model=json.dumps(VNFD_MODEL_DICT))

    @mock.patch.object(NSManualScaleService, 'run')
    def test_ns_manual_scale(self, mock_run):
        response = self.client.post("/api/nslcm/v1/ns/%s/scale" % self.ns_inst_id, data=SCALE_NS_DICT, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)

    def test_ns_manual_scale_error_scaletype(self):
        scale_ns_json = SCALE_NS_DICT.copy()
        scale_ns_json["scaleType"] = "SCALE_ERR"
        NSManualScaleService(self.ns_inst_id, scale_ns_json, self.job_id).run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(255, jobs[0].progress)

    def test_ns_manual_scale_error_nsd_id(self):
        scale_ns_json = SCALE_NS_DICT.copy()
        scale_ns_json["scaleNsData"][0]["scaleNsByStepsData"][0]["aspectId"] = "sss_zte"
        NSManualScaleService(self.ns_inst_id, scale_ns_json, self.job_id).run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(255, jobs[0].progress)

    def test_ns_manual_scale_error_aspect(self):
        scale_ns_json = SCALE_NS_DICT.copy()
        scale_ns_json["scaleNsData"][0]["scaleNsByStepsData"][0]["aspectId"] = "sss_zte"
        ns_inst_id, job_id = self.insert_new_ns()
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.MANUAL_SCALE, ns_inst_id)
        NSManualScaleService(ns_inst_id, scale_ns_json, job_id).run()
        jobs = JobModel.objects.filter(jobid=job_id)
        self.assertEqual(255, jobs[0].progress)

    @mock.patch.object(catalog, 'get_scalingmap_json_package')
    @mock.patch.object(NSManualScaleService, 'do_vnfs_scale')
    def test_ns_manual_scale_success(self, mock_do_vnfs_scale, mock_get_scalingmap_json_package):
        scale_ns_json = SCALE_NS_DICT.copy()
        scale_ns_json["scaleNsData"][0]["scaleNsByStepsData"][0]["aspectId"] = "TIC_EDGE_IMS"
        mock_get_scalingmap_json_package.return_value = self.scaling_map_json
        mock_do_vnfs_scale.return_value = JOB_MODEL_STATUS.FINISHED
        ns_inst_id, job_id = self.insert_new_ns()
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.MANUAL_SCALE, ns_inst_id)
        self.insert_new_nf()
        NSManualScaleService(ns_inst_id, scale_ns_json, job_id).run()
        jobs = JobModel.objects.filter(jobid=job_id)
        self.assertEqual(255, jobs[0].progress)

    @mock.patch.object(restcall, 'call_req')
    def test_ns_manual_scale_thread(self, mock_call):
        scale_ns_json = SCALE_NS_DICT.copy()
        NSManualScaleService(self.ns_inst_id, scale_ns_json, self.job_id).run()
        self.assertTrue(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)

    @mock.patch.object(NSManualScaleService, 'start')
    def test_ns_manual_scale_empty_data(self, mock_start):
        mock_start.side_effect = NSLCMException("NS scale failed.")
        response = self.client.post("/api/nslcm/v1/ns/%s/scale" % self.ns_inst_id, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @mock.patch.object(NSManualScaleService, 'start')
    def test_ns_manual_scale_when_ns_not_exist(self, mock_start):
        mock_start.side_effect = NSLCMException("NS scale failed.")
        scale_ns_json = SCALE_NS_DICT.copy()
        response = self.client.post("/api/nslcm/v1/ns/11/scale", data=scale_ns_json, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
