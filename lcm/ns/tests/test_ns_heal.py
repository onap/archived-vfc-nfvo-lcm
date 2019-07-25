# Copyright 2017 Intel Corporation.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import mock
import time

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from lcm.jobs.enum import JOB_TYPE, JOB_ACTION, JOB_PROGRESS
from lcm.ns.biz.ns_heal import NSHealService
from lcm.ns.enum import NS_INST_STATUS
from lcm.ns_vnfs.biz.heal_vnfs import NFHealService
from lcm.ns.tests import HEAL_NS_DICT, HEAL_VNF_DICT, VNFD_MODEL_DICT
from lcm.pub.database.models import NSInstModel, NfInstModel, JobModel, VNFCInstModel, VmInstModel, NSLcmOpOccModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil


class TestHealNsViews(TestCase):
    def setUp(self):
        self.ns_inst_id = '1'
        self.nf_inst_id = '1'
        self.nf_uuid = '1-1-1'
        self.job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.HEAL, self.ns_inst_id)
        self.client = APIClient()
        NSInstModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()
        NSInstModel(id=self.ns_inst_id, name='ns_name', status='null').save()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id,
                                   nf_name='name_1',
                                   vnf_id='1',
                                   vnfm_inst_id='1',
                                   ns_inst_id=self.ns_inst_id,
                                   max_cpu='14',
                                   max_ram='12296',
                                   max_hd='101',
                                   max_shd='20',
                                   max_net=10,
                                   status='null',
                                   mnfinstid=self.nf_uuid,
                                   package_id='pkg1',
                                   vnfd_model=VNFD_MODEL_DICT)
        VNFCInstModel(nfinstid=self.nf_inst_id, vmid='vmid_01', vduid='vduid_01').save()
        VmInstModel(vmid='vmid_01', vmname='vmname_01').save()

    def tearDown(self):
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()
        VNFCInstModel.objects.all().delete()
        VmInstModel.objects.all().delete()

    @mock.patch.object(NSHealService, 'run')
    def test_heal_vnf_url(self, mock_run):
        heal_vnf_json = HEAL_VNF_DICT.copy()
        heal_vnf_json['healVnfData']['vnfInstanceId'] = self.nf_inst_id
        response = self.client.post('/api/nslcm/v1/ns/%s/heal' % self.ns_inst_id, data=heal_vnf_json, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.data)
        self.assertIsNotNone(response.data)
        self.assertIn('jobId', response.data)
        self.assertNotIn('error', response.data)
        response = self.client.delete('/api/nslcm/v1/ns/%s' % self.ns_inst_id)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    # add healNsData
    @mock.patch.object(NSHealService, 'run')
    def test_heal_ns_url(self, mock_run):
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json['healNsData']['vnfInstanceId'] = self.nf_inst_id
        response = self.client.post('/api/nslcm/v1/ns/%s/heal' % self.ns_inst_id, data=heal_ns_json, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.data)
        self.assertIsNotNone(response.data)
        self.assertIn('jobId', response.data)
        self.assertNotIn('error', response.data)
        response = self.client.delete('/api/nslcm/v1/ns/%s' % self.ns_inst_id)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    @mock.patch.object(NSHealService, 'start')
    def test_heal_vnf_non_existing_ns(self, mock_start):
        mock_start.side_effect = NSLCMException('NS Not Found')
        ns_inst_id = '2'
        heal_vnf_json = HEAL_VNF_DICT.copy()
        heal_vnf_json['healVnfData']['vnfInstanceId'] = self.nf_inst_id
        response = self.client.post('/api/nslcm/v1/ns/%s/heal' % ns_inst_id, data=heal_vnf_json, format='json')
        self.assertEqual(response.data['error'], 'NS Not Found')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

    # add healNsData
    @mock.patch.object(NSHealService, 'start')
    def test_heal_ns_heal_non_existing_ns(self, mock_start):
        mock_start.side_effect = NSLCMException('NS Not Found')
        ns_inst_id = '2'
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json['healNsData']['vnfInstanceId'] = self.nf_inst_id
        response = self.client.post('/api/nslcm/v1/ns/%s/heal' % ns_inst_id, data=heal_ns_json, format='json')
        self.assertEqual(response.data['error'], 'NS Not Found')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

    @mock.patch.object(NSHealService, 'start')
    def test_heal_vnf_empty_post(self, mock_start):
        mock_start.side_effect = NSLCMException('healVnfData parameter does not exist or value is incorrect.')
        response = self.client.post('/api/nslcm/v1/ns/%s/heal' % self.ns_inst_id, data={})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

    @mock.patch.object(NFHealService, 'run')
    @mock.patch.object(time, 'sleep')
    @mock.patch.object(JobModel.objects, 'get')
    def test_heal_vnf_thread(self, mock_get, mock_sleep, mock_run):
        mock_run.return_value = None
        mock_sleep.return_value = None
        mock_get.return_value = JobModel(progress=JOB_PROGRESS.FINISHED)
        heal_vnf_json = HEAL_VNF_DICT.copy()
        heal_vnf_json['healVnfData']['vnfInstanceId'] = self.nf_inst_id
        NSHealService(self.ns_inst_id, heal_vnf_json, self.job_id).run()
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)

    # add healNsData
    @mock.patch.object(NFHealService, 'run')
    @mock.patch.object(time, 'sleep')
    @mock.patch.object(JobModel.objects, 'get')
    def test_heal_ns_thread(self, mock_get, mock_sleep, mock_run):
        mock_run.return_value = None
        mock_sleep.return_value = None
        mock_get.return_value = JobModel(progress=JOB_PROGRESS.FINISHED)
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json['healNsData']['vnfInstanceId'] = self.nf_inst_id
        NSHealService(self.ns_inst_id, heal_ns_json, self.job_id).run()
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.ACTIVE)

    def test_heal_when_ns_does_not_exist(self):
        ns_inst_id = '2'
        ns_heal_service = NSHealService(ns_inst_id, {}, self.job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_heal_when_healnsdata_and_healvnfdata_parameters_does_not_exist(self):
        ns_heal_service = NSHealService(self.nf_inst_id, {}, self.job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_heal_when_healnsdata_and_healvnfdata_parameters_exist_together(self):
        data = {
            'healNsData': {'degreeHealing': 'HEAL_RESTORE'},
            'healVnfData': {'vnfInstanceId': 'default'}
        }
        ns_heal_service = NSHealService(self.nf_inst_id, data, self.job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    @mock.patch.object(NFHealService, 'run')
    @mock.patch.object(time, 'sleep')
    @mock.patch.object(JobModel.objects, 'get')
    def test_heal_vnf_thread_when_nf_heal_failed(self, mock_get, mock_sleep, mock_run):
        mock_run.return_value = None
        mock_sleep.return_value = None
        mock_get.return_value = JobModel(progress=JOB_PROGRESS.ERROR)
        heal_vnf_json = HEAL_VNF_DICT.copy()
        heal_vnf_json['healVnfData']['vnfInstanceId'] = self.nf_inst_id
        ns_heal_service = NSHealService(self.ns_inst_id, heal_vnf_json, self.job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    @mock.patch.object(NFHealService, 'run')
    @mock.patch.object(time, 'sleep')
    @mock.patch.object(JobModel.objects, 'get')
    def test_heal_ns_thread_when_nf_heal_failed(self, mock_get, mock_sleep, mock_run):
        mock_run.return_value = None
        mock_sleep.return_value = None
        mock_get.return_value = JobModel(progress=JOB_PROGRESS.ERROR)
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json['healNsData']['vnfInstanceId'] = self.nf_inst_id
        ns_heal_service = NSHealService(self.ns_inst_id, heal_ns_json, self.job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_heal_vnf_thread_when_vnfinstanceid_does_not_exist(self):
        heal_vnf_json = {'healVnfData': {'vnfInstanceId': ''}}
        ns_heal_service = NSHealService(self.ns_inst_id, heal_vnf_json, self.job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_heal_ns_thread_when_degreeHealing_does_not_exist(self):
        heal_ns_json = {'healNsData': {'degreeHealing': ''}}
        ns_heal_service = NSHealService(self.ns_inst_id, heal_ns_json, self.job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_heal_ns_thread_when_the_degree_of_healing_does_not_exist(self):
        heal_ns_json = {'healNsData': {'degreeHealing': 'xxx'}}
        ns_heal_service = NSHealService(self.ns_inst_id, heal_ns_json, self.job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_heal_ns_thread_when_nsinsts_does_not_exist(self):
        NSInstModel(id='text_nsinsts_does_not_exist', name='ns_name', status='null').save()
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json['healNsData']['vnfInstanceId'] = 'text_nsinsts_does_not_exist'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.HEAL, 'text_nsinsts_does_not_exist')
        ns_heal_service = NSHealService('text_nsinsts_does_not_exist', heal_ns_json, job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_heal_ns_thread_when_vnfcinsts_does_not_exist(self):
        NSInstModel(id='text_vnfcinsts_does_not_exist', name='ns_name', status='null').save()
        NfInstModel.objects.create(nfinstid='text_vnfcinsts_does_not_exist_nf_id',
                                   ns_inst_id='text_vnfcinsts_does_not_exist')
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json['healNsData']['vnfInstanceId'] = 'text_vnfcinsts_does_not_exist_nf_id'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.HEAL, 'text_vnfcinsts_does_not_exist')
        ns_heal_service = NSHealService('text_vnfcinsts_does_not_exist', heal_ns_json, job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_heal_ns_thread_when_vminstinfo_does_not_exist(self):
        ns_inst_id = 'text_vminstinfo_does_not_exist'
        NSInstModel(id=ns_inst_id, name='ns_name', status='null').save()
        NfInstModel.objects.create(nfinstid='text_vminstinfo_does_not_exist_nf_id',
                                   ns_inst_id=ns_inst_id)
        VNFCInstModel(nfinstid='text_vminstinfo_does_not_exist_nf_id', vmid='text_vminstinfo_does_not_exist_vm_id',
                      vduid='text_vminstinfo_does_not_exist_vdu_id').save()
        heal_ns_json = HEAL_NS_DICT.copy()
        heal_ns_json['healNsData']['vnfInstanceId'] = 'text_vminstinfo_does_not_exist_nf_id'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.HEAL, ns_inst_id)
        ns_heal_service = NSHealService(ns_inst_id, heal_ns_json, job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')
