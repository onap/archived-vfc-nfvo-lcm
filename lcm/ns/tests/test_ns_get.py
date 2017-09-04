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
import uuid

from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import NSInstModel


class TestNsQuery(TestCase):
    def setUp(self):
        self.client = Client()
        self.nsd_id = str(uuid.uuid4())
        self.ns_package_id = str(uuid.uuid4())
        NSInstModel(id=1, nsd_id=1, name='test01').save()
        NSInstModel(id=2, nsd_id=1, name='test02').save()

    def test_query_ns_by_csarId(self):
        response = self.client.get("/api/nslcm/v1/ns?csarId=1")
        self.failUnlessEqual(status.HTTP_200_OK, response.status_code)


    def test_query_ns_by_nsinstance_id(self):
        response = self.client.get("/api/nslcm/v1/ns/1")
        self.failUnlessEqual(status.HTTP_200_OK, response.status_code)