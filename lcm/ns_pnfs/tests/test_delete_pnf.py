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
from lcm.ns_pnfs.biz.delete_pnf import DeletePnf
from lcm.pub.database.models import PNFInstModel


class TestDeletePnfViews(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_do_biz(self):
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
        DeletePnf(pnfId).do_biz()
        pnfInst = PNFInstModel.objects.filter(pnfId=pnfId)
        self.assertEqual(0, len(pnfInst))

    def test_rest_api(self):
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
        response = self.client.delete("/api/nslcm/v1/pnfs/%s" % pnfId)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
