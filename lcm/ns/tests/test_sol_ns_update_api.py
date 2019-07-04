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

from django.test import TestCase
from rest_framework import status
from lcm.pub.database.models import NSInstModel, JobModel


class TestUpdateNsApi(TestCase):
    def setUp(self):
        self.url = "/api/nslcm/v1/ns_instances/%s/update"

    def tearDown(self):
        NSInstModel.objects.filter().delete()
        JobModel.objects.filter().delete()

    def test_method_not_allowed(self):
        response = self.client.put(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.patch(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.delete(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.get(self.url % '1', data={}, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
