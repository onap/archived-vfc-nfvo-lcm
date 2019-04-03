# Copyright 2019 ZTE Corporation.
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

from django.test import TestCase, Client
from rest_framework import status


class TestSolHealthCheck(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_health_check(self):
        response = self.client.get("/api/nslcm/v1/health_check")
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.content)
        resp_data = json.loads(response.content)
        self.assertEqual({"status": "active"}, resp_data)
