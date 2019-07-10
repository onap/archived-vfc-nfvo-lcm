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
from . import enumutil
from . import fileutil
from urllib import request
from . import syscomm
from . import timeutil
from . import values


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

    @mock.patch.object(request, 'urlopen')
    def test_download_file_from_http(self, mock_urlopen):
        mock_urlopen.return_value = MockReq()
        fileutil.delete_dirs("abc")
        is_ok, f_name = fileutil.download_file_from_http("https://git.onap.org/vfc/nfvo/lcm/tree/version.properties", "abc", "1.txt")
        self.assertTrue(is_ok)
        self.assertTrue(f_name.endswith("1.txt"))
        fileutil.delete_dirs("abc")

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
