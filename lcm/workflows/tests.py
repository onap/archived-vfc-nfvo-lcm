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
from lcm.pub.database.models import WFPlanModel, JobStatusModel
from lcm.pub.utils.jobutil import JobUtil
from lcm.workflows import build_in

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

    @mock.patch.object(restcall, 'call_req')
    def test_buildin_workflow_normal(self, mock_call_req):
        ns_inst_id = "1"
        job_id = "1234"
        wf_input = {
            "jobId": job_id,
            "nsInstanceId": ns_inst_id,
            "object_context": '{"a": "b"}',
            "object_additionalParamForNs": '{"c": "d"}',
            "object_additionalParamForVnf": '{"e": "f"}',
            "vlCount": 1,
            "vnfCount": 1,
            "sfcCount": 1,
            "sdnControllerId": "2"
        }
        mock_vals = {
            "api/nslcm/v1/ns/vls":
                [0, json.JSONEncoder().encode({
                    "result": "0",
                    "detail": "vl1",
                    "vlId": "1"
                    }), '201'],
            "api/nslcm/v1/ns/vnfs":
                [0, json.JSONEncoder().encode({
                    "vnfInstId": "2",
                    "jobId": "11"
                    }), '201'],
            "api/nslcm/v1/ns/vnfs/2":
                [0, json.JSONEncoder().encode({
                    "vnfStatus": "active"
                    }), '201'],
            "api/nslcm/v1/ns/sfcs":
                [0, json.JSONEncoder().encode({
                    "sfcInstId": "3",
                    "jobId": "111"
                    }), '201'],
            "api/nslcm/v1/ns/sfcs/3":
                [0, json.JSONEncoder().encode({
                    "sfcStatus": "active"
                    }), '201'],
            "/api/nslcm/v1/jobs/11?responseId=0":
                [0, json.JSONEncoder().encode({"responseDescriptor": {
                    "responseId": "1",
                    "progress": 100,
                    "statusDescription": "ok"
                    }}), '200'],
            "/api/nslcm/v1/jobs/111?responseId=0":
                [0, json.JSONEncoder().encode({"responseDescriptor": {
                    "responseId": "1",
                    "progress": 100,
                    "statusDescription": "ok"
                    }}), '200'],
            "api/nslcm/v1/jobs/{jobId}".format(jobId=job_id): 
                [0, '{}', '201'],
            "api/nslcm/v1/ns/{nsInstanceId}/postdeal".format(nsInstanceId=ns_inst_id): 
                [0, '{}', '201']
        }

        def side_effect(*args):
            return mock_vals[args[4]]
        mock_call_req.side_effect = side_effect

        self.assertTrue(build_in.run_ns_instantiate(wf_input))


        









