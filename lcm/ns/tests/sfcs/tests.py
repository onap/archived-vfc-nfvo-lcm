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

import mock
from django.test import TestCase, Client
from rest_framework import status

from lcm.pub.database.models import FPInstModel, VNFFGInstModel
from lcm.pub.utils import restcall


class TestSfcDetailViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.ns_inst_id = str(uuid.uuid4())
        self.sfc_inst_id = str(uuid.uuid4())
        self.status = "active"
        self.sdn_controler_id = str(uuid.uuid4())
        sfc_id = str(uuid.uuid4())
        flow_classifiers = "flow1,flow2"
        port_pair_groups = json.JSONEncoder().encode(
            [{"groupid": "group1", "portpair": [str(uuid.uuid4()), str(uuid.uuid4())]},
             {"groupid": "group2", "portpair": [str(uuid.uuid4()), str(uuid.uuid4())]}])
        FPInstModel(fpid="", fpinstid=self.sfc_inst_id, nsinstid=self.ns_inst_id, vnffginstid="", policyinfo="",
                    status=self.status, sdncontrollerid=self.sdn_controler_id, sfcid=sfc_id,
                    flowclassifiers=flow_classifiers,
                    portpairgroups=port_pair_groups).save()
        VNFFGInstModel(vnffgdid="", vnffginstid="", nsinstid=self.ns_inst_id,
                       fplist="test1," + self.sfc_inst_id + ",test2,test3", endpointnumber=0, cplist="", vnflist="",
                       vllist="", status="").save()

    def tearDown(self):
        FPInstModel.objects.all().delete()
        VNFFGInstModel.objects.all().delete()

    @mock.patch.object(restcall, "call_req")
    def test_delete_sfc(self, mock_req_by_rest):
        mock_req_by_rest.return_value = [0, '{"test":"test_name","url":"url_add"}']
        response = self.client.delete("/openoapi/nslcm/v1/ns/sfcs/%s" % self.sfc_inst_id)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        expect_resp_data = {"result": 0, "detail": "delete sfc success"}
        self.assertEqual(expect_resp_data, response.data)

        for vnffg_info in VNFFGInstModel.objects.filter(nsinstid=self.ns_inst_id):
            self.assertEqual(vnffg_info.fplist, "test1,test2,test3")
        if FPInstModel.objects.filter(fpinstid=self.sfc_inst_id):
            self.fail()

        response = self.client.delete("/openoapi/nslcm/v1/ns/sfcs/%s" % "notExist")
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        expect_resp_data = {"result": 0, "detail": "sfc is not exist or has been already deleted"}
        self.assertEqual(expect_resp_data, response.data)

    def test_query_sfc(self):
        response = self.client.get("/openoapi/nslcm/v1/ns/sfcs/%s" % self.sfc_inst_id)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expect_resp_data = {'sfcInstId': self.sfc_inst_id,
                            'sfcStatus': self.status,
                            'sfcName': "xxx"}
        self.assertEqual(expect_resp_data, response.data)

        response = self.client.get("/openoapi/nslcm/v1/ns/sfcs/%s" % "notExist")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
