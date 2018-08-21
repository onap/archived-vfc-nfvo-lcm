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
from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import JobModel, JobStatusModel


class JobsViewTest(TestCase):
    def setUp(self):
        self.job_id = 'test_job_id'
        self.client = Client()
        JobModel.objects.all().delete()
        JobStatusModel.objects.all().delete()

    def tearDown(self):
        JobModel.objects.all().delete()
        JobStatusModel.objects.all().delete()

    def test_job(self):
        JobModel(jobid=self.job_id, jobtype='VNF', jobaction='INST', resid='1').save()
        JobStatusModel(indexid=1, jobid=self.job_id, status='inst', progress=20, descp='inst', errcode="0").save()
        response = self.client.get("/api/nslcm/v1/jobs/%s" % self.job_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertIn('jobId', response.data)
        self.assertIn('responseDescriptor', response.data)
        self.assertEqual(20, response.data['responseDescriptor']['progress'])

    def test_non_exiting_job(self):
        job_id = 'test_new_job_id'
        JobModel(jobid=self.job_id, jobtype='VNF', jobaction='INST', resid='1').save()
        JobStatusModel(indexid=1, jobid=self.job_id, status='inst', progress=20, descp='inst', errcode="0").save()
        response = self.client.get("/api/nslcm/v1/jobs/%s" % job_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('jobId', response.data)
        self.assertNotIn('responseDescriptor', response.data)

    def test_query_job_with_response_id(self):
        JobModel(jobid=self.job_id, jobtype='VNF', jobaction='INST', resid='1').save()
        JobStatusModel(indexid=1, jobid=self.job_id, status='inst', progress=20, descp='inst', errcode="0").save()
        JobStatusModel(indexid=2, jobid=self.job_id, status='inst', progress=50, descp='inst', errcode="0").save()
        JobStatusModel(indexid=3, jobid=self.job_id, status='inst', progress=80, descp='inst', errcode="0").save()
        JobStatusModel(indexid=4, jobid=self.job_id, status='inst', progress=100, descp='inst', errcode="0").save()
        response = self.client.get("/api/nslcm/v1/jobs/%s?responseId=2" % job_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.job_id, response.data.get('jobId'))
        self.assertIn('responseDescriptor', response.data)
        self.assertEqual(100, response.data['responseDescriptor']['progress'])
        self.assertEqual(2, len(response.data['responseDescriptor']['responseHistoryList']))
