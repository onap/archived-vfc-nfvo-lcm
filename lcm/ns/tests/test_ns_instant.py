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

# from rest_framework import status
from django.test import TestCase
from django.test import Client

from lcm.pub.database.models import NSInstModel


class TestNsInstant(TestCase):
    def setUp(self):
        self.client = Client()
        NSInstModel.objects.filter().delete()
        self.context = '{"vnfs": ["a", "b"], "sfcs": ["c"], "vls": ["d", "e", "f"]}'
        NSInstModel(id="123", nspackage_id="7", nsd_id="2").save()

    def tearDown(self):
        pass
