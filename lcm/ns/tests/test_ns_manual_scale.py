# Copyright 2017 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import mock
import time
import uuid
import copy

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from lcm.ns.biz.ns_manual_scale import NSManualScaleService
from lcm.ns.enum import NS_INST_STATUS
from lcm.pub.database.models import NSInstModel, JobModel, NfInstModel, NSLcmOpOccModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION, JOB_PROGRESS
from lcm.ns.tests import SCALING_MAP_DICT, SCALE_NS_THREAD_DICT, SCALE_NS_DICT
from lcm.ns_vnfs.enum import VNF_STATUS
from lcm.ns_vnfs.biz.scale_vnfs import NFManualScaleService


class TestNsManualScale(TestCase):

    def setUp(self):
        self.scaling_map_json = SCALING_MAP_DICT
        self.ns_inst_id = str(uuid.uuid4())
        self.job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.MANUAL_SCALE, self.ns_inst_id)
        self.client = APIClient()
        self.package_id = '7'
        NSInstModel(
            id=self.ns_inst_id,
            name='abc',
            nspackage_id=self.package_id,
            nsd_id='test_ns_manual_scale').save()
        NfInstModel(package_id='nf_001', status=VNF_STATUS.ACTIVE, nfinstid='nf_001').save()
        NfInstModel(package_id='nf_002', status=VNF_STATUS.ACTIVE, nfinstid='nf_002').save()

    def tearDown(self):
        NSInstModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()
        JobModel.objects.filter().delete()
        NSLcmOpOccModel.objects.filter().delete()

    @mock.patch.object(NSManualScaleService, 'run')
    def test_ns_manual_scale_url(self, mock_run):
        response = self.client.post('/api/nslcm/v1/ns/%s/scale' % self.ns_inst_id, data=SCALE_NS_DICT, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)

    @mock.patch.object(NSManualScaleService, 'run')
    def test_ns_manual_scale_url_when_require_data_is_not_valid(self, mock_run):
        response = self.client.post('/api/nslcm/v1/ns/%s/scale' % self.ns_inst_id, data={},
                                    format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn('error', response.data)

    @mock.patch.object(NSManualScaleService, 'start')
    def test_ns_manual_scale_url_when_ns_not_exist(self, mock_start):
        mock_start.side_effect = NSLCMException('NS scale failed.')
        scale_ns_json = SCALE_NS_DICT.copy()
        response = self.client.post('/api/nslcm/v1/ns/11/scale', data=scale_ns_json, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

    @mock.patch('lcm.ns.biz.ns_manual_scale.get_scale_vnf_data_info_list')
    @mock.patch.object(NFManualScaleService, 'run')
    @mock.patch.object(time, 'sleep')
    @mock.patch.object(JobModel.objects, 'get')
    def test_ns_manual_scale_asynchronous_tasks_success(self, mock_get, mock_sleep, mock_run, mock_vnf_data_info_list):
        mock_run.return_value = None
        mock_sleep.return_value = None
        mock_get.return_value = JobModel(progress=JOB_PROGRESS.FINISHED)
        mock_vnf_data_info_list.return_value = [
            {
                "vnfd_id": "nf_001",
                "vnf_scaleAspectId": "gpu",
                "numberOfSteps": "123"
            },
            {
                "vnfd_id": "nf_002",
                "vnf_scaleAspectId": "gpu",
                "numberOfSteps": "456"
            }
        ]
        scale_ns_json = SCALE_NS_THREAD_DICT.copy()
        ns_heal_service = NSManualScaleService(self.ns_inst_id, scale_ns_json, self.job_id)
        ns_heal_service.run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)
        self.assertEqual(JOB_PROGRESS.FINISHED, jobs[0].progress)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'COMPLETED')

    def test_ns_manual_scale_asynchronous_tasks_when_scale_ns_data_is_none(self):
        scale_ns_json = SCALE_NS_THREAD_DICT.copy()
        scale_ns_json['scaleNsData'] = None
        ns_heal_service = NSManualScaleService(self.ns_inst_id, scale_ns_json, self.job_id)
        ns_heal_service.run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs[0].progress)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_ns_manual_scale_asynchronous_tasks_when_scale_ns_by_steps_data_is_none(self):
        scale_ns_json = copy.deepcopy(SCALE_NS_THREAD_DICT)
        scale_ns_json['scaleNsData']["scaleNsByStepsData"] = None
        ns_heal_service = NSManualScaleService(self.ns_inst_id, scale_ns_json, self.job_id)
        ns_heal_service.run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs[0].progress)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    @mock.patch('lcm.ns.biz.ns_manual_scale.get_scale_vnf_data_info_list')
    @mock.patch.object(NFManualScaleService, 'run')
    @mock.patch.object(time, 'sleep')
    @mock.patch.object(JobModel.objects, 'get')
    def test_ns_manual_scale_asynchronous_tasks_when_vnf_scale_failed(self, mock_get, mock_sleep,
                                                                      mock_run, mock_vnf_data_info_list):
        scale_ns_json = SCALE_NS_THREAD_DICT.copy()
        mock_run.return_value = None
        mock_sleep.return_value = None
        mock_get.return_value = JobModel(progress=JOB_PROGRESS.ERROR)
        mock_vnf_data_info_list.return_value = [
            {
                "vnfd_id": "nf_001",
                "vnf_scaleAspectId": "gpu",
                "numberOfSteps": "123"
            },
            {
                "vnfd_id": "nf_002",
                "vnf_scaleAspectId": "gpu",
                "numberOfSteps": "456"
            }
        ]
        ns_heal_service = NSManualScaleService(self.ns_inst_id, scale_ns_json, self.job_id)
        ns_heal_service.run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs[0].progress)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_ns_manual_scale_asynchronous_tasks_when_error_scale_type(self):
        scale_ns_json = SCALE_NS_THREAD_DICT.copy()
        scale_ns_json['scaleType'] = 'SCALE_ERR'
        ns_heal_service = NSManualScaleService(self.ns_inst_id, scale_ns_json, self.job_id)
        ns_heal_service.run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs[0].progress)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    @mock.patch('lcm.ns.biz.ns_manual_scale.get_scale_vnf_data_info_list')
    def test_ns_manual_scale_asynchronous_tasks_when_failed_to_get_scale_vnf_data_parameter(self, mock_vnf_data_info):
        mock_vnf_data_info.return_value = []
        scale_ns_json = SCALE_NS_THREAD_DICT.copy()
        ns_heal_service = NSManualScaleService(self.ns_inst_id, scale_ns_json, self.job_id)
        ns_heal_service.run()
        jobs = JobModel.objects.filter(jobid=self.job_id)
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)
        self.assertEqual(JOB_PROGRESS.ERROR, jobs[0].progress)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')
