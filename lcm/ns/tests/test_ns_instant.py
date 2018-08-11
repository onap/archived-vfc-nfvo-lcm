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

from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient
import mock
import json

from lcm.pub.database.models import NSInstModel
from lcm.ns.ns_instant import InstantNSService
from lcm.ns.ns_instant import BuildInWorkflowThread
from lcm.pub.utils import restcall


class TestNsInstant(TestCase):
    def setUp(self):
        self.client = APIClient()
        NSInstModel.objects.filter().delete()
        self.url = "/api/nslcm/v1/ns/2/instantiate"
        self.req_data = {
            "additionalParamForNs": {
                "sdnControllerId": "2"
            },
            "locationConstraints": [{
                "vnfProfileId": "vnfd1",
                "locationConstraints": {
                    "vimId": "3"
                }
            }]
        }
        self.nsd_model = json.dumps({
            "model": json.dumps({
                "vnfs": [{
                    "vnf_id": "vnf1",
                    "properties": {
                        "id": "vnfd1",
                        "nf_type": "xgw"
                    },
                    "dependencies": [{
                        "vl_id": "5"
                    }]
                }],
                "vls": [{
                    "vl_id": "5",
                    "properties": {}
                }]
            })
        })
        self.updated_nsd_model = {
            "vnfs": [{
                "dependencies": [{
                    "vl_id": "5"
                }],
                "vnf_id": "vnf1",
                "properties": {
                    "nf_type": "xgw",
                    "id": "vnfd1"
                }
            }],
            "vls": [{
                "vl_id": "5",
                "properties": {
                    "location_info": {
                        "vimid": "3"
                    }
                }
            }]
        }
        self.vnfms = json.dumps({
            "esr-vnfm": [{
                "vnfm-id": "4"
            }]
        })
        self.vnfm = json.dumps({
            "type": "xgw",
            "vim-id": "3",
            "vnfm-id": "4",
            "certificate-url": "http://127.0.0.0/ztevnfm/v1/auth",
            "esr-system-info-list": {
                "esr-system-info": [{
                    "type": "xgw",
                    "vendor": "zte",
                    "version": "1.0",
                    "service-url": "http://127.0.0.0/ztevnfm/v1",
                    "user-name": "admin",
                    "password": "admin123"
                }]
            }
        })
        NSInstModel(id="2", nspackage_id="7", nsd_id="2", status="active").save()

    def tearDown(self):
        pass

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(BuildInWorkflowThread, 'run')
    def test_ns_instantiate_when_succeed_to_enter_workflow(self, mock_run, mock_call_req):
        mock_run = None
        mock_call_req.side_effect = [
            [0, self.nsd_model, '200'],
            [0, self.vnfms, '200'],
            [0, self.vnfm, '200']
        ]
        resp = self.client.post(self.url, data=self.req_data, format='json')
        self.failUnlessEqual(status.HTTP_200_OK, resp.status_code)
        self.assertIn("jobId", resp.data)
        upd_nsd_model = NSInstModel.objects.filter(id="2").first().nsd_model
        self.assertEqual(self.updated_nsd_model, json.loads(upd_nsd_model))

    @mock.patch.object(InstantNSService, 'do_biz')
    def test_ns_instantiate_normal(self, mock_do_biz):
        mock_do_biz.return_value = dict(data={'jobId': "1"}, status=status.HTTP_200_OK)
        resp = self.client.post(self.url, data=self.req_data, format='json')
        self.failUnlessEqual(status.HTTP_200_OK, resp.status_code)
        self.assertEqual({'jobId': "1"}, resp.data)

    @mock.patch.object(restcall, 'call_req')
    def test_ns_instantiate_when_fail_to_parse_nsd(self, mock_call_req):
        mock_call_req.return_value = [1, "Failed to parse nsd", '500']
        resp = self.client.post(self.url, data=self.req_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", resp.data)
