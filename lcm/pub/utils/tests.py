# Copyright 2018 ZTE Corporation.
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

import unittest
import mock
import enumutil
import fileutil
import urllib2
import syscomm
import timeutil
import values

from lcm.pub.database.models import JobStatusModel, JobModel
from lcm.pub.utils.jobutil import JobUtil


class MockReq():
    def read(self):
        return "1"

    def close(self):
        pass


class UtilsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_enum(self):
        MY_TYPE = enumutil.enum(SAMLL=0, LARGE=1)
        self.assertEqual(0, MY_TYPE.SAMLL)
        self.assertEqual(1, MY_TYPE.LARGE)

    def test_create_and_delete_dir(self):
        dirs = "abc/def/hij"
        fileutil.make_dirs(dirs)
        fileutil.make_dirs(dirs)
        fileutil.delete_dirs(dirs)

    @mock.patch.object(urllib2, 'urlopen')
    def test_download_file_from_http(self, mock_urlopen):
        mock_urlopen.return_value = MockReq()
        fileutil.delete_dirs("abc")
        is_ok, f_name = fileutil.download_file_from_http("1", "abc", "1.txt")
        self.assertTrue(is_ok)
        self.assertTrue(f_name.endswith("abc/1.txt"))
        fileutil.delete_dirs("abc")

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
            inst_type="1",
            jobaction="2",
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

    def test_fun_name(self):
        self.assertEqual("test_fun_name", syscomm.fun_name())

    def test_now_time(self):
        self.assertIn(":", timeutil.now_time())
        self.assertIn("-", timeutil.now_time())

    def test_ignore_case_get(self):
        data = {
            "Abc": "def",
            "HIG": "klm"
        }
        self.assertEqual("def", values.ignore_case_get(data, 'ABC'))
        self.assertEqual("def", values.ignore_case_get(data, 'abc'))
        self.assertEqual("klm", values.ignore_case_get(data, 'hig'))
        self.assertEqual("bbb", values.ignore_case_get(data, 'aaa', 'bbb'))
