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
import json
import uuid
from lcm.pub.msapi import extsys
import mock
from django.test import TestCase, Client
from rest_framework import status
from lcm.pub.msapi import sdncdriver
from lcm.pub.database.models import FPInstModel


class TestSfcDetailViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.ns_inst_id = str(uuid.uuid4())
        self.sfc_inst_id = str(uuid.uuid4())
        self.status = "active"
        self.sdn_controler_id = str(uuid.uuid4())

    def tearDown(self):
        pass

    def test_sfc_delete_failed(self):
        response = self.client.delete("/api/nslcm/v1/ns/sfcs/%s" % "notExist")
        expect_resp_data = {"result": 0, "detail": "sfc is not exist or has been already deleted"}
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertEqual(expect_resp_data, response.data)

    def test_sfc_get_failed(self):
        sfc_inst_id = "10"
        response = self.client.get("/api/nslcm/v1/ns/sfcs/%s" % sfc_inst_id)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_sfc_get_success(self):
        sfc_inst_id = "10"
        FPInstModel(fpid="1", fpinstid="10", fpname="2", nsinstid="3", vnffginstid="4",
                    symmetric="5", policyinfo="6", forworderpaths="7", status="8", sdncontrollerid="9",
                    sfcid="10", flowclassifiers="11",
                    portpairgroups="12").save()
        response = self.client.get("/api/nslcm/v1/ns/sfcs/%s" % sfc_inst_id)
        expect_resp_data = {'sfcName': 'xxx', 'sfcInstId': '10', 'sfcStatus': '8'}
        self.assertEqual(expect_resp_data, response.data)
