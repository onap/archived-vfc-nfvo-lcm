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

import uuid
from django.test import TestCase, Client
from rest_framework import status
from lcm.ns_pnfs.biz.get_pnf import GetPnf
from lcm.pub.database.models import PNFInstModel


class TestGetPnfViews(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_pnfid_filter(self):
        pnfId = str(uuid.uuid4())
        PNFInstModel(pnfId=pnfId,
                     pnfName="Test PNF",
                     pnfdId=str(uuid.uuid4()),
                     pnfdInfoId=str(uuid.uuid4()),
                     pnfProfileId=str(uuid.uuid4()),
                     cpInfo=[{
                         "cpInstanceId": str(uuid.uuid4()),
                         "cpdId": "pnf_ext_cp01",
                         "cpProtocolData": []
                     }]).save()
        pnfInst = GetPnf({"pnfId": pnfId}).do_biz()
        self.assertEqual("Test PNF", pnfInst[0].pnfName)

    def test_nsInstanceid_filter(self):
        pnfId = str(uuid.uuid4())
        nsInstanceId = str(uuid.uuid4())
        PNFInstModel(pnfId=pnfId,
                     pnfName="Test PNF",
                     pnfdId=str(uuid.uuid4()),
                     pnfdInfoId=str(uuid.uuid4()),
                     pnfProfileId=str(uuid.uuid4()),
                     cpInfo=[{
                         "cpInstanceId": str(uuid.uuid4()),
                         "cpdId": "pnf_ext_cp01",
                         "cpProtocolData": []
                     }],
                     emsId=str(uuid.uuid4()),
                     nsInstances=nsInstanceId
                     ).save()
        pnfInst = GetPnf({"nsInstanceId": nsInstanceId}).do_biz()
        self.assertEqual("Test PNF", pnfInst[0].pnfName)

    def test_get_instances_restapi(self):
        pnfId = str(uuid.uuid4())
        nsInstanceId = str(uuid.uuid4())
        PNFInstModel(pnfId=pnfId,
                     pnfName="Test PNF",
                     pnfdId=str(uuid.uuid4()),
                     pnfdInfoId=str(uuid.uuid4()),
                     pnfProfileId=str(uuid.uuid4()),
                     cpInfo=[{
                         "cpInstanceId": str(uuid.uuid4()),
                         "cpdId": "pnf_ext_cp01",
                         "cpProtocolData": []
                     }],
                     emsId=str(uuid.uuid4()),
                     nsInstances=nsInstanceId
                     ).save()
        response = self.client.get("/api/nslcm/v1/pnfs")
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_individual_instance_restapi(self):
        pnfId = str(uuid.uuid4())
        nsInstanceId = str(uuid.uuid4())
        PNFInstModel(pnfId=pnfId,
                     pnfName="Test PNF",
                     pnfdId=str(uuid.uuid4()),
                     pnfdInfoId=str(uuid.uuid4()),
                     pnfProfileId=str(uuid.uuid4()),
                     cpInfo=[{
                         "cpInstanceId": str(uuid.uuid4()),
                         "cpdId": "pnf_ext_cp01",
                         "cpProtocolData": []
                     }],
                     emsId=str(uuid.uuid4()),
                     nsInstances=nsInstanceId
                     ).save()
        response = self.client.get("/api/nslcm/v1/pnfs/%s" % pnfId)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_fileter_nsinstance_restapi(self):
        pnfId = str(uuid.uuid4())
        nsInstanceId = str(uuid.uuid4())
        PNFInstModel(pnfId=pnfId,
                     pnfName="Test PNF",
                     pnfdId=str(uuid.uuid4()),
                     pnfdInfoId=str(uuid.uuid4()),
                     pnfProfileId=str(uuid.uuid4()),
                     cpInfo=[{
                         "cpInstanceId": str(uuid.uuid4()),
                         "cpdId": "pnf_ext_cp01",
                         "cpProtocolData": []
                     }],
                     emsId=str(uuid.uuid4()),
                     nsInstances=nsInstanceId
                     ).save()
        response = self.client.get("/api/nslcm/v1/pnfs?nsInstanceId=%s" % nsInstanceId)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(pnfId, response.data[0]['pnfId'])
