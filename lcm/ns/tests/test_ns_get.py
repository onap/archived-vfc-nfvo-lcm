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
from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import NSInstModel


class TestNsQuery(TestCase):
    def setUp(self):
        self.client = Client()
        NSInstModel(id=1, nsd_id=11, name='test01').save()
        NSInstModel(id=2, nsd_id=22, name='test02').save()

    def test_query_ns_by_nsinstance_id(self):
        response = self.client.get("/api/nslcm/v1/ns/1")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIsNotNone(response.data)

    def test_query_all_nsinstance(self):
        response = self.client.get("/api/nslcm/v1/ns")
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertIsNotNone(response.data)
        self.assertEqual(2, len(response.data))

    def test_query_ns_by_non_existing_nsinstance_id(self):
        response = self.client.get("/api/nslcm/v1/ns/200")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
