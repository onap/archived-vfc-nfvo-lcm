# Copyright 2019 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import mock
import uuid
from mock import MagicMock
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from lcm.ns.biz.ns_instant import BuildInWorkflowThread
from lcm.ns.biz.ns_instant import InstantNSService
from lcm.pub.database.models import NSInstModel
from lcm.pub.utils import restcall
from lcm.pub.config import config
from lcm.ns.tests import NSD_MODEL_DICT, NSD_MODEL_WITH_PNF_DICT, VNFM_LIST_IN_AAI_DICT, VNFM_IN_AAI_DICT, VCPE_NS_MODEL_DICT, SOL_INSTANTIATE_NS_DICT, SOL_INSTANTIATE_NS_VCPE_DICT, SOL_INSTANTIATE_NS_WITH_PNF_DICT

nsd_model = json.dumps(NSD_MODEL_DICT)
nsd = json.dumps(NSD_MODEL_WITH_PNF_DICT)
vnfminfo = {"vnfmId": "1"}


class TestInstantiateNsApi(TestCase):

    def setUp(self):
        self.client = APIClient()
        NSInstModel.objects.filter().delete()
        self.url = "/api/nslcm/v1/ns_instances/%s/instantiate"
        self.req_data = SOL_INSTANTIATE_NS_DICT
        self.nsd_model = nsd_model
        self.vnfms = json.dumps(VNFM_LIST_IN_AAI_DICT)
        self.vnfm = json.dumps(VNFM_IN_AAI_DICT)
        self.nsInstanceId = str(uuid.uuid4())
        NSInstModel(id=self.nsInstanceId, nspackage_id="7", nsd_id="2", status="active").save()

    def tearDown(self):
        pass

    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=nsd_model))
    @mock.patch.object(BuildInWorkflowThread, 'run')
    def test_ns_instantiate_when_succeed_to_enter_workflow(self, mock_run, mock_call_req):
        config.WORKFLOW_OPTION = "buildin"
        mock_call_req.side_effect = [
            [0, self.vnfms, '200'],
            [0, self.vnfm, '200']
        ]
        response = self.client.post(self.url % self.nsInstanceId, data=self.req_data, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertIsNotNone(response['Location'])
        response = self.client.get(response['Location'], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch.object(InstantNSService, 'do_biz')
    def test_ns_instantiate_normal(self, mock_do_biz):
        mock_do_biz.return_value = {'occ_id': "1", 'data': {}}
        response = self.client.post(self.url % self.nsInstanceId, data=self.req_data, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)

    @mock.patch.object(restcall, 'call_req')
    def test_ns_instantiate_when_fail_to_parse_nsd(self, mock_call_req):
        mock_call_req.return_value = [1, "Failed to parse nsd", '500']
        resp = self.client.post(self.url % self.nsInstanceId, data=self.req_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @mock.patch('lcm.ns.biz.ns_instantiate_flow.post_deal')
    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.ns.biz.ns_instantiate_flow.update_job')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=nsd))
    @mock.patch('lcm.pub.msapi.extsys.select_vnfm', MagicMock(return_value=vnfminfo))
    def test_ns_instantiate_with_pnf(self, mock_updata_job, mock_call_req, mock_post_deal):
        config.WORKFLOW_OPTION = "grapflow"
        nsInstanceId = str(uuid.uuid4())
        NSInstModel(id=nsInstanceId, name="test_ns", nspackage_id="1", status="created").save()
        ret = [0, json.JSONEncoder().encode({'jobId': "1", "responseDescriptor": {"progress": 100}}), '200']
        mock_call_req.side_effect = [ret for i in range(1, 20)]
        response = self.client.post(self.url % nsInstanceId, data=SOL_INSTANTIATE_NS_WITH_PNF_DICT, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNotNone(response['Location'])
        response = self.client.get(response['Location'], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_not_allowed(self):
        response = self.client.put(self.url % self.nsInstanceId, data=self.req_data, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.patch(self.url % self.nsInstanceId, data=self.req_data, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.delete(self.url % self.nsInstanceId, data=self.req_data, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.client.get(self.url % self.nsInstanceId, data=self.req_data, format='json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=json.dumps({"model": json.dumps(VCPE_NS_MODEL_DICT)})))
    @mock.patch.object(BuildInWorkflowThread, 'run')
    def test_ns_instantiate_vcpe(self, mock_run, mock_call_req):
        config.WORKFLOW_OPTION = "buildin"
        mock_call_req.side_effect = [
            [0, self.vnfms, '200'],
            [0, self.vnfm, '200']
        ]
        response = self.client.post(self.url % self.nsInstanceId, data=SOL_INSTANTIATE_NS_VCPE_DICT, format='json')
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertIsNotNone(response['Location'])
        response = self.client.get(response['Location'], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
