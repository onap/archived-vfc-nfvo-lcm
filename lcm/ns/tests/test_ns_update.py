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
from lcm.pub.database.models import NSInstModel, JobModel
from lcm.pub.utils.jobutil import JobUtil


class TestScaleAspect(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/nslcm/v1/ns/%s/update' % 'test_ns_update_001'
        NSInstModel(id='test_ns_update_001').save()

    def tearDown(self):
        NSInstModel.objects.all().delete()
        JobModel.objects.all().delete()

    def test_ns_update_when_require_is_not_valid(self):
        response = self.client.post(self.url, data={}, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch.object(NSUpdateService, 'run')
    def test_ns_update(self, mock_run):
        mock_run.return_value = None
        response = self.client.post(self.url, data=UPDATE_NS_DICT, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)

    @mock.patch.object(JobUtil, 'create_job')
    @mock.patch.object(NSUpdateService, 'run')
    def test_ns_update_nslcmexception(self, mock_run, mock_create_job):
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
        ns_instance_id = 'test_ns_update_001'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)
        NSUpdateService(ns_instance_id, UPDATE_NS_DICT, job_id).run()
        self.assertEqual(NSInstModel.objects.filter(id=ns_instance_id).first().status, NS_INST_STATUS.ACTIVE)
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(NFOperateService, 'run')
    @mock.patch.object(JobModel.objects, 'get')
    def test_ns_update_asynchronous_tasks_when_nf_update_error(self, mock_get, mock_run, mock_sleep):
        mock_sleep.return_value = None
        mock_run.return_value = None
        mock_get.return_value = JobModel(progress=JOB_PROGRESS.ERROR)
        ns_instance_id = 'test_ns_update_001'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)
        NSUpdateService(ns_instance_id, UPDATE_NS_DICT, job_id).run()
        self.assertEqual(NSInstModel.objects.filter(id=ns_instance_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)

    def test_ns_update_asynchronous_tasks_when_ns_does_not_exist(self):
        ns_instance_id = 'test_ns_update_002'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)
        NSUpdateService(ns_instance_id, UPDATE_NS_DICT, job_id).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)

    def test_ns_update_asynchronous_tasks_when_updatetype_parameter_does_not_exist(self):
        ns_instance_id = 'test_ns_update_001'
        request_data = {"updateType": ""}
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)
        NSUpdateService(ns_instance_id, request_data, job_id).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)

    def test_ns_update_asynchronous_tasks_when_updatetype_not_operate_vnf(self):
        ns_instance_id = 'test_ns_update_001'
        request_data = {"updateType": "ADD_VNF"}
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)
        NSUpdateService(ns_instance_id, request_data, job_id).run()
        self.assertEqual(NSInstModel.objects.filter(id=ns_instance_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)

    def test_ns_update_asynchronous_tasks_when_operatevnfdata_does_not_exist(self):
        ns_instance_id = 'test_ns_update_001'
        request_data = {"updateType": "OPERATE_VNF"}
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)
        NSUpdateService(ns_instance_id, request_data, job_id).run()
        self.assertEqual(NSInstModel.objects.filter(id=ns_instance_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)

    def test_ns_update_asynchronous_tasks_when_vnfinstanceid_does_not_exist(self):
        ns_instance_id = 'test_ns_update_001'
        request_data = {
            "updateType": "OPERATE_VNF",
            "OperateVnfData": [{}]
        }
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)
        NSUpdateService(ns_instance_id, request_data, job_id).run()
        self.assertEqual(NSInstModel.objects.filter(id=ns_instance_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)

    def test_ns_update_asynchronous_tasks_when_changestateto_does_not_exist(self):
        ns_instance_id = 'test_ns_update_001'
        request_data = {
            "updateType": "OPERATE_VNF",
            "OperateVnfData": [
                {
                    "vnfInstanceId": "test_vnf_001"
                }
            ]
        }
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)
        NSUpdateService(ns_instance_id, request_data, job_id).run()
        self.assertEqual(NSInstModel.objects.filter(id=ns_instance_id).first().status, NS_INST_STATUS.UPDATING)
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.ERROR)
