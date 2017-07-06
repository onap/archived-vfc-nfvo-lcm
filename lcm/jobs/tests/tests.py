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

    def tearDown(self):
        JobModel.objects.all().delete()

    def test_job(self):
        JobModel(jobid=self.job_id, jobtype='VNF', jobaction='INST', resid='1').save()
        JobStatusModel(indexid=1, jobid=self.job_id, status='inst', progress=20, descp='inst').save()
        response = self.client.get("/openoapi/nslcm/v1/jobs/%s" % self.job_id)
        self.failUnlessEqual(status.HTTP_200_OK, response.status_code)
