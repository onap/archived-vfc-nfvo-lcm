# Copyright (C) 2019 ZTE. All Rights Reserved
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
from django.test import Client
from rest_framework import status


class TestSwagger(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_swagger_json(self):
        pass

        # url = "/api/nslcm/v1/swagger.json"
        # response = self.client.get(url, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual("2.0", response.data.get("swagger"))
