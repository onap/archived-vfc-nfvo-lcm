import mock
import time
import httplib2

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from lcm.jobs.enum import JOB_TYPE, JOB_ACTION, JOB_PROGRESS
from lcm.ns.biz.ns_terminate import TerminateNsService
from lcm.ns.enum import OWNER_TYPE, NS_INST_STATUS
from lcm.ns.tests import TERMINATE_NS_DICT
from lcm.ns_vnfs.biz.update_vnfs import NFOperateService
from lcm.pub.database.models import NSInstModel, JobModel, FPInstModel, NfInstModel, VLInstModel, PNFInstModel
from lcm.pub.utils.jobutil import JobUtil


class TestScaleAspect(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ns_inst_id = 'test_ns_terminate_001'
        self.url = '/api/nslcm/v1/ns/%s/terminate' % self.ns_inst_id
        NSInstModel(id=self.ns_inst_id).save()
        NSInstModel(id='test_ns_terminate_002').save()
        FPInstModel(nsinstid=self.ns_inst_id, sfcid='test_sfc_inst_001', fpname='xxx', status='zzz').save()
        NfInstModel(ns_inst_id=self.ns_inst_id).save()
        VLInstModel(ownertype=OWNER_TYPE.NS, ownerid=self.ns_inst_id).save()
        PNFInstModel(nsInstances=self.ns_inst_id).save()

    def tearDown(self):
        NSInstModel.objects.all().delete()
        FPInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()
        VLInstModel.objects.all().delete()
        PNFInstModel.objects.all().delete()
        JobModel.objects.all().delete()



    def test_ns_update_asynchronous_tasks_when_ns_does_not_exist(self):
        ns_instance_id = 'test_ns_terminate_not_exist'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.TERMINATE, ns_instance_id)
        TerminateNsService(ns_instance_id, job_id, TERMINATE_NS_DICT).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.FINISHED)

    def test_ns_update_asynchronous_tasks_with_none(self):
        ns_instance_id = 'test_ns_terminate_002'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.TERMINATE, ns_instance_id)
        TerminateNsService(ns_instance_id, job_id, TERMINATE_NS_DICT).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(httplib2.Http, 'request')
    def test_ns_update_asynchronous_tasks(self, mock_request, mock_sleep):
        mock_request.side_effect = [
            ({'status': '200'}, '{"result": "0"}'.encode('utf-8')),
            ({'status': '200'}, '{"jobId": "zzz"}'.encode('utf-8')),
            ({'status': '200'}, '{"responseDescriptor": {"progress": 100, "responseId": 1, '
                                '"statusDescription": ""}}'.encode('utf-8')),
            ({'status': '200'}, '{"result": "0"}'.encode('utf-8')),
            ({'status': '200'}, '{"result": "0"}'.encode('utf-8'))
        ]
        mock_sleep.return_value = None

        ns_instance_id = 'test_ns_terminate_001'
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.TERMINATE, ns_instance_id)
        TerminateNsService(ns_instance_id, job_id, TERMINATE_NS_DICT).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(httplib2.Http, 'request')
    def test_ns_update_asynchronous_tasks_when_cancel_vnf_no_vnfjobid(self, mock_request, mock_sleep):
        ns_instance_id = 'test_ns_terminate_when_cancel_vnf_no_vnfjobid'
        NSInstModel(id=ns_instance_id).save()
        NfInstModel(ns_inst_id=ns_instance_id).save()
        mock_request.side_effect = [
            ({'status': '200'}, '{"jobId": ""}'.encode('utf-8'))
        ]
        mock_sleep.return_value = None

        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.TERMINATE, ns_instance_id)
        TerminateNsService(ns_instance_id, job_id, TERMINATE_NS_DICT).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(httplib2.Http, 'request')
    def test_ns_update_asynchronous_tasks_when_terminate_vnf_failed(self, mock_request, mock_sleep):
        ns_instance_id = 'test_ns_terminate_when_terminate_vnf_failed'
        NSInstModel(id=ns_instance_id).save()
        NfInstModel(ns_inst_id=ns_instance_id).save()
        mock_request.side_effect = [
            ({'status': '404'}, '{"jobId": "zzz"}'.encode('utf-8'))
        ]
        mock_sleep.return_value = None

        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.TERMINATE, ns_instance_id)
        TerminateNsService(ns_instance_id, job_id, TERMINATE_NS_DICT).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(httplib2.Http, 'request')
    def test_ns_update_asynchronous_tasks_when_failed_to_query_job(self, mock_request, mock_sleep):
        ns_instance_id = 'test_ns_terminate_when_failed_to_query_job'
        NSInstModel(id=ns_instance_id).save()
        NfInstModel(ns_inst_id=ns_instance_id).save()
        mock_request.side_effect = [
            ({'status': '200'}, '{"jobId": "zzz"}'.encode('utf-8')),
            ({'status': '400'}),
            ({'status': '200'}, '{"responseDescriptor": {"progress": 100, "responseId": 1, '
                                '"statusDescription": ""}}'.encode('utf-8'))
        ]
        mock_sleep.return_value = None

        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.TERMINATE, ns_instance_id)
        TerminateNsService(ns_instance_id, job_id, TERMINATE_NS_DICT).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(httplib2.Http, 'request')
    def test_ns_update_asynchronous_tasks_when_no_new_progress(self, mock_request, mock_sleep):
        ns_instance_id = 'test_ns_terminate_when_no_new_progress'
        NSInstModel(id=ns_instance_id).save()
        NfInstModel(ns_inst_id=ns_instance_id).save()
        mock_request.side_effect = [
            ({'status': '200'}, '{"jobId": "zzz"}'.encode('utf-8')),
            ({'status': '200'}, '{}'.encode('utf-8')),
            ({'status': '200'}, '{"responseDescriptor": {"progress": 100, "responseId": 1, '
                                '"statusDescription": ""}}'.encode('utf-8'))
        ]
        mock_sleep.return_value = None

        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.TERMINATE, ns_instance_id)
        TerminateNsService(ns_instance_id, job_id, TERMINATE_NS_DICT).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.FINISHED)

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(httplib2.Http, 'request')
    def test_ns_update_asynchronous_tasks_when_job_failed(self, mock_request, mock_sleep):
        ns_instance_id = 'test_ns_terminate_when_job_failed'
        NSInstModel(id=ns_instance_id).save()
        NfInstModel(ns_inst_id=ns_instance_id).save()
        mock_request.side_effect = [
            ({'status': '200'}, '{"jobId": "zzz"}'.encode('utf-8')),
            ({'status': '200'}, '{"responseDescriptor": {"progress": 255, "responseId": 1, '
                                '"statusDescription": ""}}'.encode('utf-8'))
        ]
        mock_sleep.return_value = None

        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.TERMINATE, ns_instance_id)
        TerminateNsService(ns_instance_id, job_id, TERMINATE_NS_DICT).run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, JOB_PROGRESS.FINISHED)
