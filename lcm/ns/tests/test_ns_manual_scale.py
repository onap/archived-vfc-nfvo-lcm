# Copyright 2017 ZTE Corporation.
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

import mock
from django.test import Client
from django.test import TestCase
from rest_framework import status

from lcm.ns.const import NS_INST_STATUS
from lcm.ns.ns_manual_scale import NSManualScaleService
from lcm.pub.database.models import NSInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils import restcall
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE


SCALING_JSON = {
    "scale_options": [
        {
            "nsd_id": "ns_ims",
            "ns_scale_aspect": "TIC_CORE_IMS",
            "ns_scale_info": [
                {
                    "step": "1",
                    "scale_list": [
                        {
                            "vnfd_id": "zte_ims_cscf",
                            "vnf_scale_aspect": "mpu",
                            "numberOfSteps": "1"
                        },
                        {
                            "vnfd_id": "zte_ims_hss",
                            "vnf_scale_aspect": "fpu",
                            "numberOfSteps": "3"
                        }
                    ]
                },
                {
                    "step": "2",
                    "scale_list": [
                        {
                            "vnfd_id": "zte_ims_cscf",
                            "vnf_scale_aspect": "mpu",
                            "numberOfSteps": "2"
                        },
                        {
                            "vnfd_id": "zte_ims_hss",
                            "vnf_scale_aspect": "fpu",
                            "numberOfSteps": "6"
                        }
                    ]
                }
            ]
        },
        {
            "nsd_id": "ns_epc",
            "ns_scale_aspect": "TIC_EDGE_EPC",
            "ns_scale_info": [
                {
                    "step": "1",
                    "scale_list": [
                        {
                            "vnfd_id": "zte_epc_spgw",
                            "vnf_scale_aspect": "gpu",
                            "numberOfSteps": "1"
                        },
                        {
                            "vnfd_id": "zte_epc_tas",
                            "vnf_scale_aspect": "fpu",
                            "numberOfSteps": "2"
                        }
                    ]
                },
                {
                    "step": "2",
                    "scale_list": [
                        {
                            "vnfd_id": "zte_epc_spgw",
                            "vnf_scale_aspect": "mpu",
                            "numberOfSteps": "2"
                        },
                        {
                            "vnfd_id": "zte_epc_tas",
                            "vnf_scale_aspect": "fpu",
                            "numberOfSteps": "4"
                        }
                    ]
                }
            ]
        }
    ]
}


class TestNsManualScale(TestCase):
    def setUp(self):
        self.ns_inst_id = str(uuid.uuid4())
        self.job_id = JobUtil.create_job(
            "NS", JOB_TYPE.MANUAL_SCALE_VNF, self.ns_inst_id)

        self.client = Client()
        NSInstModel(
            id=self.ns_inst_id,
            name="abc",
            nspackage_id="7",
            nsd_id="111").save()

    def tearDown(self):
        NSInstModel.objects.filter().delete()

    @mock.patch.object(NSManualScaleService, 'run')
    def test_ns_manual_scale(self, mock_run):
        data = {
            "scaleType": "SCALE_NS",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "1",
                    "numberOfSteps": 1,
                    "scalingDirection": "0"
                }]
            }]
        }
        response = self.client.post(
            "/api/nslcm/v1/ns/%s/scale" %
            self.ns_inst_id, data=data)
        self.failUnlessEqual(status.HTTP_202_ACCEPTED, response.status_code)

    @mock.patch.object(restcall, 'call_req')
    def test_ns_manual_scale_thread(self, mock_call):
        data = {
            "scaleType": "SCALE_NS",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "1",
                    "numberOfSteps": 1,
                    "scalingDirection": "0"
                }]
            }]
        }
        NSManualScaleService(self.ns_inst_id, data, self.job_id).run()
        self.assertTrue(
            NSInstModel.objects.get(
                id=self.ns_inst_id).status,
            NS_INST_STATUS.ACTIVE)

    def test_swagger_ok(self):
        resp = self.client.get("/api/nslcm/v1/swagger.json", format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @mock.patch.object(NSManualScaleService, 'start')
    def test_ns_manual_scale_empty_data(self, mock_start):
        mock_start.side_effect = NSLCMException("NS scale failed.")
        response = self.client.post(
            "/api/nslcm/v1/ns/%s/scale" %
            self.ns_inst_id, data={})
        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    @mock.patch.object(NSManualScaleService, 'start')
    def test_ns_manual_scale_when_ns_not_exist(self, mock_start):
        mock_start.side_effect = NSLCMException("NS scale failed.")
        data = {
            "scaleType": "SCALE_NS",
            "scaleNsData": [{
                "scaleNsByStepsData": [{
                    "aspectId": "1",
                    "numberOfSteps": 1,
                    "scalingDirection": "0"
                }]
            }]
        }
        response = self.client.post("/api/nslcm/v1/ns/11/scale", data=data)
        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
