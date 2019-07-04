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
from mock import MagicMock
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from lcm.ns.biz.ns_instant import BuildInWorkflowThread
from lcm.ns.biz.ns_instant import InstantNSService
from lcm.pub.database.models import NSInstModel
from lcm.pub.utils import restcall
from lcm.pub.config import config
from lcm.ns.tests import NSD_MODEL_DICT, NSD_MODEL_WITH_PNF_DICT, VNFM_LIST_IN_AAI_DICT, VNFM_IN_AAI_DICT, JOB_DICT, INSTANTIATE_NS_DICT, INSTANTIATE_NS_WITH_PNF_DICT


class TestNsInstant(TestCase):

    vnfminfo = {"vnfmId": "1"}

    def setUp(self):
        self.client = APIClient()
        NSInstModel.objects.filter().delete()
        self.url = "/api/nslcm/v1/ns/%s/instantiate" % "2"
        NSInstModel(id="2", nspackage_id="7", nsd_id="2", status="active").save()
        self._mock_get_auto_id()

    def tearDown(self):
        pass

    def _mock_get_auto_id(self):
        fake_auto_id = mock.Mock()
        fake_auto_id.return_value = 1
        patcher = mock.patch(
            'lcm.pub.utils.idutil.get_auto_id',
            fake_auto_id)
        patcher.start()

    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=json.dumps({"model": json.dumps(NSD_MODEL_DICT)})))
    @mock.patch.object(BuildInWorkflowThread, 'run')
    def test_ns_instantiate_when_succeed_to_enter_workflow(self, mock_run, mock_call_req):
        config.WORKFLOW_OPTION = "buildin"
        mock_call_req.side_effect = [
            [0, {"model": json.dumps(NSD_MODEL_DICT)}, '200'],
            [0, VNFM_LIST_IN_AAI_DICT, '200'],
            [0, VNFM_IN_AAI_DICT, '200']
        ]
        resp = self.client.post(self.url, data=INSTANTIATE_NS_DICT, format='json')
        self.assertEqual(status.HTTP_200_OK, resp.status_code)
        self.assertIn("jobId", resp.data)

    @mock.patch.object(InstantNSService, 'do_biz')
    def test_ns_instantiate_normal(self, mock_do_biz):
        mock_do_biz.return_value = dict(data=JOB_DICT, status=status.HTTP_200_OK)
        resp = self.client.post(self.url, data=INSTANTIATE_NS_DICT, format='json')
        self.assertEqual(status.HTTP_200_OK, resp.status_code)
        self.assertEqual(JOB_DICT, resp.data)

    @mock.patch.object(restcall, 'call_req')
    def test_ns_instantiate_when_fail_to_parse_nsd(self, mock_call_req):
        mock_call_req.return_value = [1, "Failed to parse nsd", '500']
        resp = self.client.post(self.url, data=INSTANTIATE_NS_DICT, format='json')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", resp.data)

    @mock.patch('lcm.ns.biz.ns_instantiate_flow.post_deal')
    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.ns.biz.ns_instantiate_flow.update_job')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=json.dumps(NSD_MODEL_WITH_PNF_DICT)))
    @mock.patch('lcm.pub.msapi.extsys.select_vnfm', MagicMock(return_value=vnfminfo))
    def test_ns_instantiate_with_pnf(self, mock_updata_job, mock_call_req, mock_post_deal):
        config.WORKFLOW_OPTION = "grapflow"
        NSInstModel(id="1", name="test_ns", nspackage_id="1", status="created").save()
        ret = [0, json.JSONEncoder().encode(JOB_DICT), '200']
        mock_call_req.side_effect = [ret for i in range(1, 20)]
        ack = InstantNSService(1, INSTANTIATE_NS_WITH_PNF_DICT).do_biz()
        self.assertEqual(ack['status'], status.HTTP_200_OK)

    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=json.dumps(NSD_MODEL_WITH_PNF_DICT)))
    @mock.patch('lcm.pub.msapi.extsys.select_vnfm', MagicMock(return_value=vnfminfo))
    def test_ns_instantiate_with_vimid_1(self, mock_call_req):
        config.WORKFLOW_OPTION = "grapflow"
        NSInstModel(id="1", name="test_ns", nspackage_id="1", status="created").save()
        ret = [0, json.JSONEncoder().encode(JOB_DICT), '200']
        mock_call_req.side_effect = [ret for i in range(1, 20)]
        ack = InstantNSService(1, INSTANTIATE_NS_WITH_PNF_DICT).do_biz()
        self.assertEqual(ack['status'], status.HTTP_200_OK)

    @mock.patch.object(restcall, 'call_req')
    @mock.patch('lcm.pub.msapi.sdc_run_catalog.parse_nsd', MagicMock(return_value=json.dumps(NSD_MODEL_WITH_PNF_DICT)))
    @mock.patch('lcm.pub.msapi.extsys.select_vnfm', MagicMock(return_value=vnfminfo))
    def test_ns_instantiate_with_different_vimid_2(self, mock_call_req):
        config.WORKFLOW_OPTION = "grapflow"
        NSInstModel(id="1", name="test_ns", nspackage_id="1", status="created").save()
        ret = [0, json.JSONEncoder().encode(JOB_DICT), '200']
        mock_call_req.side_effect = [ret for i in range(1, 20)]
        ack = InstantNSService(1, INSTANTIATE_NS_WITH_PNF_DICT).do_biz()
        self.assertEqual(ack['status'], status.HTTP_200_OK)
