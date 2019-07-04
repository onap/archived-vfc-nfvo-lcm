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
import mock
import json
from .test_data import nsd_model, vnfd_model_dict1, vnfd_model_dict2
from rest_framework import status
from lcm.pub.utils import restcall
from lcm.pub.database.models import FPInstModel, NfInstModel
from django.test import Client
from django.test import TestCase


class TestSfc(TestCase):
    def setUp(self):
        self.client = Client()
        FPInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()
        NfInstModel(
            nfinstid="vnf_inst_1",
            ns_inst_id="ns_inst_1",
            vnf_id="vnf_1",
            vnfd_model=json.dumps(vnfd_model_dict1)).save()
        NfInstModel(
            nfinstid="vnf_inst_2",
            vnf_id="vnf_2",
            ns_inst_id="ns_inst_1",
            vnfd_model=json.dumps(vnfd_model_dict2)).save()
        FPInstModel(
            fpid="fpd_1",
            fpinstid="fp_inst_1",
            nsinstid="ns_inst_1",
            vnffginstid="vnffg_inst_1",
            policyinfo=[{
                "type": "ACL",
                "criteria": {
                    "dest_port_range": [80, 1024],
                    "source_port_range": [80, 1024],
                    "ip_protocol": "tcp",
                    "dest_ip_range": ["192.168.1.2", "192.168.1.100"],
                    "source_ip_range": ["192.168.1.2", "192.168.1.100"],
                    "dscp": 100,
                }
            }],
            status="enabled",
            sdncontrollerid="sdn_controller_1"
        ).save()

    def tearDown(self):
        FPInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()

    @mock.patch.object(restcall, 'call_req')
    def test_create_port_pair_group_success(self, mock_call_req):
        data = {
            "nsinstanceid": "ns_inst_1",
            "fpinstid": "fp_inst_1",
            "context": json.dumps(nsd_model)
        }
        mock_vals = {
            "/external-system/esr-thirdparty-sdnc-list/esr-thirdparty-sdnc/sdn_controller_1?depth=all":
                [0, json.JSONEncoder().encode({
                    "thirdparty-sdnc-id": "1",
                    "esr-system-info-list": {
                        "esr-system-info": [{
                            "service-url": "url_1",
                            "thirdparty-sdnc-id": "1",
                            "user-name": "aa",
                            "password": "123",
                            "vendor": "zte",
                            "version": "v1.0",
                            "protocal": "http",
                            "product-name": "bbb",
                            "type": "11"
                        }]
                    }
                }), '200'],
            "/api/ztesdncdriver/v1/createportpair":
                [0, json.JSONEncoder().encode({"id": "createportpair_id"}), '200'],
            "/api/ztesdncdriver/v1/createportpairgroup":
                [0, json.JSONEncoder().encode({"id": "createportpairgroup_id"}), '200'],
            "/api/microservices/v1/services":
                [0, None, '200']
        }

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect
        resp = self.client.post("/api/nslcm/v1/ns/create_port_pair_group", data)
        rest = json.loads(FPInstModel.objects.get(fpinstid="fp_inst_1").portpairgroups)[0]
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual("createportpairgroup_id", rest["groupid"])
