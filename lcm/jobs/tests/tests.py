# Copyright 2016 ZTE Corporation.
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

from django.test import TestCase
from lcm.jobs.const import JOB_INSTANCE_URI
from lcm.jobs.enum import JOB_ACTION, JOB_STATUS, JOB_TYPE
from lcm.jobs.jobutil import JobUtil
from lcm.jobs.tests import UPDATE_JOB_DICT, UPDATE_JOB_BAD_REQ_DICT
from lcm.pub.database.models import JobModel, JobStatusModel
from rest_framework import status
from rest_framework.test import APIClient


class JobsViewTest(TestCase):
    def setUp(self):
        self.job_id = 'test_job_id'
        self.client = APIClient()
        JobModel.objects.all().delete()
        JobStatusModel.objects.all().delete()

    def tearDown(self):
        JobModel.objects.all().delete()
        JobStatusModel.objects.all().delete()

    def test_query_ns_job(self):
        JobModel(jobid=self.job_id,
                 jobtype=JOB_TYPE.NS,
                 jobaction=JOB_ACTION.INSTANTIATE,
                 resid='1').save()
        JobStatusModel(indexid=1,
                       jobid=self.job_id,
                       status=JOB_STATUS.PROCESSING,
                       progress=20,
                       descp='Finish to instantiate NS.',
                       errcode="0").save()
        response = self.client.get(JOB_INSTANCE_URI % self.job_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertIn('jobId', response.data)
        self.assertIn('responseDescriptor', response.data)
        self.assertEqual(20, response.data['responseDescriptor']['progress'])

    def test_query_ns_job_wrong_data(self):
        JobModel(jobid=self.job_id,
                 jobtype=JOB_TYPE.NS,
                 jobaction=JOB_ACTION.INSTANTIATE,
                 resid='1').save()
        JobStatusModel(indexid=1,
                       jobid=self.job_id,
                       status=JOB_STATUS.PROCESSING,
                       progress=20,
                       descp='Finish to instantiate NS.',
                       errcode="1").save()
        response = self.client.get(JOB_INSTANCE_URI % self.job_id)
        self.assertEqual(status.HTTP_500_INTERNAL_SERVER_ERROR, response.status_code)

    def test_query_ns_job_not_existed(self):
        job_id = 'test_job_id_not_existed'
        response = self.client.get(JOB_INSTANCE_URI % job_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('jobId', response.data)
        self.assertNotIn('responseDescriptor', response.data)

    def test_query_job_with_response_id(self):
        JobModel(jobid=self.job_id,
                 jobtype=JOB_TYPE.NS,
                 jobaction=JOB_ACTION.INSTANTIATE,
                 resid='1').save()
        JobStatusModel(indexid=1,
                       jobid=self.job_id,
                       status=JOB_STATUS.PROCESSING,
                       progress=20,
                       descp='NS instantiation progress is 20%.',
                       errcode="0").save()
        JobStatusModel(indexid=2,
                       jobid=self.job_id,
                       status=JOB_STATUS.PROCESSING,
                       progress=50,
                       descp='NS instantiation progress is 50%.',
                       errcode="0").save()
        JobStatusModel(indexid=3,
                       jobid=self.job_id,
                       status=JOB_STATUS.PROCESSING,
                       progress=80,
                       descp='NS instantiation progress is 80%.',
                       errcode="0").save()
        JobStatusModel(indexid=4,
                       jobid=self.job_id,
                       status=JOB_STATUS.FINISH,
                       progress=100,
                       descp='Finish to instantiate NS.',
                       errcode="0").save()
        url = JOB_INSTANCE_URI % self.job_id + "?responseId=2"
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.job_id, response.data.get('jobId'))
        self.assertIn('responseDescriptor', response.data)
        self.assertEqual(100, response.data['responseDescriptor']['progress'])
        self.assertEqual(1, len(response.data['responseDescriptor']['responseHistoryList']))

    def test_update_job(self):
        JobModel(
            jobid=self.job_id,
            jobtype=JOB_TYPE.NS,
            jobaction=JOB_ACTION.INSTANTIATE,
            resid='1').save()
        JobStatusModel(
            indexid=1,
            jobid=self.job_id,
            status=JOB_STATUS.PROCESSING,
            progress=20,
            descp='NS instantiation progress is 20%.',
            errcode="0").save()
        response = self.client.post(JOB_INSTANCE_URI % self.job_id, format='json', data=UPDATE_JOB_DICT)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)

    def test_update_job_not_existed(self):
        response = self.client.post(JOB_INSTANCE_URI % self.job_id, format='json', data=UPDATE_JOB_DICT)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_job_with_bad_req(self):
        JobModel(
            jobid=self.job_id,
            jobtype=JOB_TYPE.NS,
            jobaction=JOB_ACTION.INSTANTIATE,
            resid='1').save()
        JobStatusModel(
            indexid=1,
            jobid=self.job_id,
            status=JOB_STATUS.PROCESSING,
            progress=20,
            descp='NS instantiation progress is 20%.',
            errcode="0").save()
        response = self.client.post(JOB_INSTANCE_URI % self.job_id, format='json', data=UPDATE_JOB_BAD_REQ_DICT)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_query_job_status(self):
        job_id = "1"
        JobStatusModel.objects.filter().delete()
        JobStatusModel(
            indexid=1,
            jobid=job_id,
            status="success",
            progress=10
        ).save()
        JobStatusModel(
            indexid=2,
            jobid=job_id,
            status="success",
            progress=50
        ).save()
        JobStatusModel(
            indexid=3,
            jobid=job_id,
            status="success",
            progress=100
        ).save()
        jobs = JobUtil.query_job_status(job_id)
        self.assertEqual(1, len(jobs))
        self.assertEqual(3, jobs[0].indexid)
        jobs = JobUtil.query_job_status(job_id, 1)
        self.assertEqual(2, len(jobs))
        self.assertEqual(3, jobs[0].indexid)
        self.assertEqual(2, jobs[1].indexid)
        JobStatusModel.objects.filter().delete()

    def test_is_job_exists(self):
        job_id = "1"
        JobModel.objects.filter().delete()
        JobModel(
            jobid=job_id,
            jobtype="1",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        self.assertTrue(JobUtil.is_job_exists(job_id))
        JobModel.objects.filter().delete()

    def test_create_job(self):
        job_id = "5"
        JobModel.objects.filter().delete()
        JobUtil.create_job(
            job_type="1",
            job_action="2",
            inst_id="3",
            user="4",
            job_id=5,
            res_name="6")
        self.assertEqual(1, len(JobModel.objects.filter(jobid=job_id)))
        JobModel.objects.filter().delete()

    def test_clear_job(self):
        job_id = "1"
        JobModel.objects.filter().delete()
        JobModel(
            jobid=job_id,
            jobtype="1",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        JobUtil.clear_job(job_id)
        self.assertEqual(0, len(JobModel.objects.filter(jobid=job_id)))

    def test_add_job_status_when_job_is_not_created(self):
        JobModel.objects.filter().delete()
        self.assertRaises(
            Exception,
            JobUtil.add_job_status,
            job_id="1",
            progress=1,
            status_decs="2",
            error_code="0"
        )

    def test_add_job_status_normal(self):
        job_id = "1"
        JobModel.objects.filter().delete()
        JobStatusModel.objects.filter().delete()
        JobModel(
            jobid=job_id,
            jobtype="1",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        JobUtil.add_job_status(
            job_id="1",
            progress=1,
            status_decs="2",
            error_code="0"
        )
        self.assertEqual(1, len(JobStatusModel.objects.filter(jobid=job_id)))
        JobStatusModel.objects.filter().delete()
        JobModel.objects.filter().delete()

    def test_clear_job_status(self):
        job_id = "1"
        JobStatusModel.objects.filter().delete()
        JobStatusModel(
            indexid=1,
            jobid=job_id,
            status="success",
            progress=10
        ).save()
        JobUtil.clear_job_status(job_id)
        self.assertEqual(0, len(JobStatusModel.objects.filter(jobid=job_id)))

    def test_get_unfinished_jobs(self):
        JobModel.objects.filter().delete()
        JobModel(
            jobid="11",
            jobtype="InstVnf",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        JobModel(
            jobid="22",
            jobtype="InstVnf",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        JobModel(
            jobid="33",
            jobtype="InstVnf",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        progresses = JobUtil.get_unfinished_jobs(
            url_prefix="/vnfinst",
            inst_id="3",
            inst_type="InstVnf"
        )
        expect_progresses = ['/vnfinst/11', '/vnfinst/22', '/vnfinst/33']
        self.assertEqual(expect_progresses, progresses)
        JobModel.objects.filter().delete()
