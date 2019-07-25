import mock
import time

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from lcm.jobs.enum import JOB_TYPE, JOB_ACTION, JOB_PROGRESS
from lcm.ns.biz.ns_update import NSUpdateService
from lcm.ns.enum import NS_INST_STATUS
from lcm.ns.tests import UPDATE_NS_DICT
from lcm.ns_vnfs.biz.update_vnfs import NFOperateService
from lcm.pub.database.models import NSInstModel, JobModel, NSLcmOpOccModel
from lcm.pub.utils.jobutil import JobUtil


class TestScaleAspect(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ns_inst_id = 'test_ns_update_001'
        self.url = '/api/nslcm/v1/ns/%s/update' % self.ns_inst_id
        self.job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.HEAL, self.ns_inst_id)
        NSInstModel(id=self.ns_inst_id).save()

    def tearDown(self):
        NSInstModel.objects.all().delete()
        JobModel.objects.all().delete()

    def test_ns_update_when_require_is_not_valid(self):
        response = self.client.post(self.url, data={}, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch.object(NSUpdateService, 'run')
    def test_ns_update_url(self, mock_run):
        mock_run.return_value = None
        response = self.client.post(self.url, data=UPDATE_NS_DICT, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)

    @mock.patch.object(JobUtil, 'create_job')
    @mock.patch.object(NSUpdateService, 'run')
    def test_ns_update_url_nslcmexception(self, mock_run, mock_create_job):
        mock_run.return_value = None
        mock_create_job.return_value = None
        response = self.client.post(self.url, data=UPDATE_NS_DICT, format='json')
        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(NFOperateService, 'run')
    @mock.patch.object(JobModel.objects, 'get')
    def test_ns_update_asynchronous_tasks(self, mock_get, mock_run, mock_sleep):
        mock_sleep.return_value = None
        mock_run.return_value = None
        mock_get.return_value = JobModel(progress=JOB_PROGRESS.FINISHED)
        ns_heal_service = NSUpdateService(self.ns_inst_id, UPDATE_NS_DICT, self.job_id)
        ns_heal_service.run()
        self.assertEqual(NSInstModel.objects.filter(id=self.ns_inst_id).first().status, NS_INST_STATUS.ACTIVE)
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.FINISHED)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'COMPLETED')

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(NFOperateService, 'run')
    @mock.patch.object(JobModel.objects, 'get')
    def test_ns_update_asynchronous_tasks_when_nf_update_error(self, mock_get, mock_run, mock_sleep):
        mock_sleep.return_value = None
        mock_run.return_value = None
        mock_get.return_value = JobModel(progress=JOB_PROGRESS.ERROR)
        ns_heal_service = NSUpdateService(self.ns_inst_id, UPDATE_NS_DICT, self.job_id)
        ns_heal_service.run()
        self.assertEqual(NSInstModel.objects.filter(id=self.ns_inst_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_ns_update_asynchronous_tasks_when_ns_does_not_exist(self):
        ns_instance_id = 'test_ns_update_002'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)
        ns_heal_service = NSUpdateService(ns_instance_id, UPDATE_NS_DICT, job_id)
        ns_heal_service.run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_ns_update_asynchronous_tasks_when_updatetype_parameter_does_not_exist(self):
        request_data = {"updateType": ""}
        ns_heal_service = NSUpdateService(self.ns_inst_id, request_data, self.job_id)
        ns_heal_service.run()
        self.assertEqual(NSInstModel.objects.filter(id=self.ns_inst_id).first().status, None)
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_ns_update_asynchronous_tasks_when_updatetype_not_operate_vnf(self):
        request_data = {"updateType": "ADD_VNF"}
        ns_heal_service = NSUpdateService(self.ns_inst_id, request_data, self.job_id)
        ns_heal_service.run()
        self.assertEqual(NSInstModel.objects.filter(id=self.ns_inst_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_ns_update_asynchronous_tasks_when_operatevnfdata_does_not_exist(self):
        request_data = {"updateType": "OPERATE_VNF"}
        ns_heal_service = NSUpdateService(self.ns_inst_id, request_data, self.job_id)
        ns_heal_service.run()
        self.assertEqual(NSInstModel.objects.filter(id=self.ns_inst_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_ns_update_asynchronous_tasks_when_vnfinstanceid_does_not_exist(self):
        request_data = {
            "updateType": "OPERATE_VNF",
            "OperateVnfData": [{}]
        }
        ns_heal_service = NSUpdateService(self.ns_inst_id, request_data, self.job_id)
        ns_heal_service.run()
        self.assertEqual(NSInstModel.objects.filter(id=self.ns_inst_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')

    def test_ns_update_asynchronous_tasks_when_changestateto_does_not_exist(self):
        request_data = {
            "updateType": "OPERATE_VNF",
            "OperateVnfData": [
                {
                    "vnfInstanceId": "test_vnf_001"
                }
            ]
        }
        ns_heal_service = NSUpdateService(self.ns_inst_id, request_data, self.job_id)
        ns_heal_service.run()
        self.assertEqual(NSInstModel.objects.filter(id=self.ns_inst_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=self.job_id).first().progress, JOB_PROGRESS.ERROR)
        self.assertEqual(NSLcmOpOccModel.objects.filter(id=ns_heal_service.occ_id).first().operation_state, 'FAILED')
