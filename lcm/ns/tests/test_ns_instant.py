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
from rest_framework import status
from django.test import TestCase
from django.test import Client

from lcm.pub.database.models import NSInstModel
from lcm.pub.utils import restcall
from lcm.pub.utils import toscautil


class TestNsInstant(TestCase):
    def setUp(self):
        self.client = Client()
        NSInstModel.objects.filter().delete()
        self.context = '{"vnfs": ["a", "b"], "sfcs": ["c"], "vls": ["d", "e", "f"]}'
        NSInstModel(id="123", nspackage_id="7", nsd_id="2").save()

    def tearDown(self):
        pass

    """
    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(toscautil, 'convert_nsd_model')
    def test_ns_instant_ok(self, mock_convert_nsd_model, mock_call_req):
        mock_convert_nsd_model.return_value = self.context
        mock_vals = {
            "/openoapi/catalog/v1/csars/7/files?relativePath=abc.yaml":
                [0, '{"downloadUri":"http://test.yaml", "localPath":"./test.yaml"}', '200'],
            "/openoapi/tosca/v1/indirect/plan":
                [0, '{"description":"", "metadata":{}, "nodes":[]}', '200'],
            "/openoapi/catalog/v1/servicetemplates/2/operations":
                [0, '[{"name":"LCM", "processId":"{http://www.open-o.org/tosca/nfv/2015/12}init-16"}]', '200'],
            "/openoapi/wso2bpel/v1/process/instance":
                [0, '{"status": 1}', '200']}

        def side_effect(*args):
            return mock_vals[args[4]]

        mock_call_req.side_effect = side_effect

        data = {'iaUrl': "", 'vnfmId': "", 'context': "{\"e\":{\"f\":\"4\"}}", 'statusUrl': "",
                'serviceTemplateId': "", 'roUrl': "", 'containerapiUrl': "", 'flavor': "",
                'nsInstanceId': "123", 'instanceId': "234", 'resourceUrl': "", 'callbackId': "",
                'additionalParamForVnf': "[{\"b\":1},{\"c\":{\"d\":\"2\"}}]",
                'additionalParamForNs': "[{\"a\":3},{\"e\":{\"f\":\"4\"}}]", 'flavorParams': ""}
        resp = self.client.post("/openoapi/nslcm/v1/ns/123/instantiate", data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    """
    
    def test_swagger_ok(self):
        resp = self.client.get("/openoapi/nslcm/v1/swagger.json", format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
