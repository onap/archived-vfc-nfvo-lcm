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

import unittest
import json
import mock
import os
from django.test import Client
from rest_framework import status

from lcm.pub.utils import restcall
from lcm.pub.database.models import WFPlanModel

class WorkflowViewTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        WFPlanModel.objects.filter().delete()

    def tearDown(self):
        pass

    @mock.patch.object(restcall, 'upload_by_msb')
    def test_deploy_workflow(self, mock_upload_by_msb):
        mock_upload_by_msb.return_value = [0, json.JSONEncoder().encode({
            "status": "1",
            "message": "2",
            "deployedId": "3",
            "processId": "4"
            }), '202']
        response = self.client.post("/api/nslcm/v1/workflow", 
            {"filePath": os.path.abspath(__file__)}, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.content)
        self.assertEqual(1, len(WFPlanModel.objects.filter(deployed_id="3")))

    @mock.patch.object(restcall, 'upload_by_msb')
    @mock.patch.object(restcall, 'call_req')
    def test_force_deploy_workflow(self, mock_call_req, mock_upload_by_msb):
        mock_call_req.return_value = [0, json.JSONEncoder().encode({
            "status": "1",
            "message": "2"
            }), '202']
        mock_upload_by_msb.return_value = [0, json.JSONEncoder().encode({
            "status": "2",
            "message": "3",
            "deployedId": "4",
            "processId": "5"
            }), '202']
        WFPlanModel(deployed_id="1", process_id="2", status="3", message="4").save()
        response = self.client.post("/api/nslcm/v1/workflow", 
            {"filePath": os.path.abspath(__file__), "forceDeploy": "True"}, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.content)
        self.assertEqual(0, len(WFPlanModel.objects.filter(deployed_id="1")))
        self.assertEqual(1, len(WFPlanModel.objects.filter(deployed_id="4")))

    def test_deploy_workflow_when_already_deployed(self):
        WFPlanModel(deployed_id="1", process_id="2", status="3", message="4").save()
        response = self.client.post("/api/nslcm/v1/workflow", 
            {"filePath": os.path.abspath(__file__)}, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code, response.content)
        self.assertEqual({'msg': 'Already deployed.'}, json.loads(response.content))


