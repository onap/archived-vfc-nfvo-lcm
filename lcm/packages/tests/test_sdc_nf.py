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
import mock
from rest_framework import status
from django.test import TestCase
from django.test import Client

from lcm.pub.utils import restcall
from lcm.pub.utils import fileutil
from lcm.pub.database.models import NfPackageModel, NfInstModel
from lcm.pub.database.models import JobStatusModel, JobModel
from lcm.packages.sdc_nf_package import SdcNfDistributeThread, SdcNfPkgDeleteThread
from lcm.packages import sdc_nf_package


class TestNfPackage(TestCase):
    def setUp(self):
        self.client = Client()
        NfPackageModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()
        JobModel.objects.filter().delete()
        JobStatusModel.objects.filter().delete()

    def tearDown(self):
        pass

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail)
        self.assertEqual(1, len(jobs))

    @mock.patch.object(SdcNfDistributeThread, 'run')
    def test_nf_pkg_on_distribute_normal(self, mock_run):
        resp = self.client.post("/api/nslcm/v1/vnfpackage", {
            "csarId": "1",
            "vimIds": ["1"]
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
