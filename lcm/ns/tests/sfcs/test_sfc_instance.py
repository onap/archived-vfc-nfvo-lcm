# Copyright 2018 ZTE Corporation.
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
# import json
# from rest_framework import status
# from test_data import nsd_model
from django.test import Client
from django.test import TestCase
from lcm.pub.database.models import FPInstModel, VNFFGInstModel


class TestSfc(TestCase):
    def setUp(self):
        self.client = Client()
        VNFFGInstModel.objects.all().delete()
        FPInstModel.objects.all().delete()
        VNFFGInstModel(vnffgdid="vnffg_id1", vnffginstid="vnffg_inst_1", nsinstid="ns_inst_1", endpointnumber=2,
                       vllist="vlinst1", cplist="cp1", vnflist="vnf1,vnf2").save()

    def tearDown(self):
        VNFFGInstModel.objects.all().delete()
        FPInstModel.objects.all().delete()

    # def test_sfc_instance_success(self):
    #    data = {
    #        "nsInstanceId": "ns_inst_1",
    #        "context": json.dumps(nsd_model),
    #        "fpindex": "fpd_1",
    #        "sdnControllerId": "sdnControllerId_1"
    #    }
    #    resp = self.client.post("/api/nslcm/v1/ns/sfc_instance", data, format='json')

    #    self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
    #    vnffg = VNFFGInstModel.objects.get(vnffginstid="vnffg_inst_1")
    #    ret = FPInstModel.objects.get(fpinstid=resp.data["fpinstid"])
    #    self.assertEqual(vnffg.fplist, resp.data["fpinstid"])
    #    self.assertIsNotNone(ret)
