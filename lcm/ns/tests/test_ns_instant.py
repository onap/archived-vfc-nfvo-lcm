# Copyright 2016 ZTE Corporation.
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
import os
from mock import MagicMock
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from lcm.ns.biz.ns_instant import BuildInWorkflowThread
from lcm.ns.biz.ns_instant import InstantNSService
from lcm.pub.database.models import NSInstModel
from lcm.pub.utils import restcall, fileutil
from lcm.pub.config import config


class TestNsInstant(TestCase):

    cur_path = os.path.dirname(os.path.abspath(__file__))
    nsd_model = fileutil.read_json_file(cur_path + '/data/nsd_model.json')
    nsd_model_json = json.dumps({"model": json.dumps(nsd_model)})
    nsd_model_with_pnf_json = json.dumps(fileutil.read_json_file(cur_path + '/data/nsd_model_with_pnf.json'))
    vnfm_list_in_aai = fileutil.read_json_file(cur_path + '/data/vnfm_list_in_aai.json')
    vnfm_in_aai = fileutil.read_json_file(cur_path + '/data/vnfm_in_aai.json')
    job = fileutil.read_json_file(cur_path + '/data/job.json')
    instantiate_ns_with_pnf = fileutil.read_json_file(cur_path + '/data/instantiate_ns_with_pnf.json')
    instantiate_ns_json = fileutil.read_json_file(cur_path + '/data/instantiate_ns.json')
    vnfminfo = {"vnfmId": "1"}

    def setUp(self):
        self.client = APIClient()
        NSInstModel.objects.filter().delete()
        self.url = "/api/nslcm/v1/ns/%s/instantiate" % "2"
        NSInstModel(id="2", nspackage_id="7", nsd_id="2", status="active").save()

    def tearDown(self):
        pass

    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=nsd_model_json))
    @mock.patch.object(BuildInWorkflowThread, 'run')
    def test_ns_instantiate_when_succeed_to_enter_workflow(self, mock_run, mock_call_req):
        config.WORKFLOW_OPTION = "buildin"
        mock_call_req.side_effect = [
            [0, TestNsInstant.nsd_model_json, '200'],
            [0, TestNsInstant.vnfm_list_in_aai, '200'],
            [0, TestNsInstant.vnfm_in_aai, '200']
        ]
        instantiate_ns_json = fileutil.read_json_file(self.cur_path + '/data/instantiate_ns.json')
        resp = self.client.post(self.url, data=instantiate_ns_json, format='json')
        self.assertEqual(status.HTTP_200_OK, resp.status_code)
        self.assertIn("jobId", resp.data)

    @mock.patch.object(InstantNSService, 'do_biz')
    def test_ns_instantiate_normal(self, mock_do_biz):
        mock_do_biz.return_value = dict(data=TestNsInstant.job, status=status.HTTP_200_OK)
        instantiate_ns_json = fileutil.read_json_file(self.cur_path + '/data/instantiate_ns.json')
        resp = self.client.post(self.url, data=instantiate_ns_json, format='json')
        self.failUnlessEqual(status.HTTP_200_OK, resp.status_code)
        self.assertEqual(TestNsInstant.job, resp.data)

    @mock.patch.object(restcall, 'call_req')
    def test_ns_instantiate_when_fail_to_parse_nsd(self, mock_call_req):
        mock_call_req.return_value = [1, "Failed to parse nsd", '500']
        resp = self.client.post(self.url, data=TestNsInstant.instantiate_ns_json, format='json')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", resp.data)

    @mock.patch('lcm.ns.biz.ns_instantiate_flow.post_deal')
    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.ns.biz.ns_instantiate_flow.update_job')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=nsd_model_with_pnf_json))
    @mock.patch('lcm.pub.msapi.extsys.select_vnfm', MagicMock(return_value=vnfminfo))
    def test_ns_instantiate_with_pnf(self, mock_updata_job, mock_call_req, mock_post_deal):
        config.WORKFLOW_OPTION = "grapflow"
        NSInstModel(id="1", name="test_ns", nspackage_id="1", status="created").save()
        ret = [0, json.JSONEncoder().encode(TestNsInstant.job), '200']
        mock_call_req.side_effect = [ret for i in range(1, 20)]
        ack = InstantNSService(1, TestNsInstant.instantiate_ns_with_pnf).do_biz()
        self.assertEqual(ack['status'], status.HTTP_200_OK)

    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=nsd_model_with_pnf_json))
    @mock.patch('lcm.pub.msapi.extsys.select_vnfm', MagicMock(return_value=vnfminfo))
    def test_ns_instantiate_with_vimid_1(self, mock_call_req):
        config.WORKFLOW_OPTION = "grapflow"
        NSInstModel(id="1", name="test_ns", nspackage_id="1", status="created").save()
        ret = [0, json.JSONEncoder().encode(TestNsInstant.job), '200']
        mock_call_req.side_effect = [ret for i in range(1, 20)]
        ack = InstantNSService(1, TestNsInstant.instantiate_ns_with_pnf).do_biz()
        self.assertEqual(ack['status'], status.HTTP_200_OK)

    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=nsd_model_with_pnf_json))
    @mock.patch('lcm.pub.msapi.extsys.select_vnfm', MagicMock(return_value=vnfminfo))
    def test_ns_instantiate_with_different_vimid_2(self, mock_call_req):
        config.WORKFLOW_OPTION = "grapflow"
        NSInstModel(id="1", name="test_ns", nspackage_id="1", status="created").save()
        ret = [0, json.JSONEncoder().encode(TestNsInstant.job), '200']
        mock_call_req.side_effect = [ret for i in range(1, 20)]
        ack = InstantNSService(1, TestNsInstant.instantiate_ns_with_pnf).do_biz()
        self.assertEqual(ack['status'], status.HTTP_200_OK)
