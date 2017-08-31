# Copyright 2017 Intel Corporation.
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
from lcm.pub.database.models import NSInstModel, NfInstModel
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE
from lcm.ns.const import NS_INST_STATUS
from lcm.pub.utils import restcall
from lcm.pub.exceptions import NSLCMException
from lcm.ns.ns_heal import NSHealService


class TestHealNsViews(TestCase):
    def setUp(self):

        self.ns_inst_id = '1'
        self.nf_inst_id = '1'
        self.nf_uuid = '1-1-1'

        self.job_id = JobUtil.create_job("NS", JOB_TYPE.HEAL_VNF, self.ns_inst_id)

        self.client = Client()

        model = '{"metadata": {"vnfdId": "1","vnfdName": "PGW001","vnfProvider": "zte","vnfdVersion": "V00001",' \
                '"vnfVersion": "V5.10.20","productType": "CN","vnfType": "PGW",' \
                '"description": "PGW VNFD description","isShared":true,"vnfExtendType":"driver"}}'
        NSInstModel(id=self.ns_inst_id, name="ns_name", status='null').save()
        NfInstModel.objects.create(nfinstid=self.nf_inst_id, nf_name='name_1', vnf_id='1',
                                   vnfm_inst_id='1', ns_inst_id=self.ns_inst_id,
                                   max_cpu='14', max_ram='12296', max_hd='101', max_shd="20", max_net=10,
                                   status='null', mnfinstid=self.nf_uuid, package_id='pkg1',
                                   vnfd_model=model)

    def tearDown(self):
        NSInstModel.objects.filter().delete()
        NfInstModel.objects.filter().delete()

    @mock.patch.object(NSHealService, 'run')
    def test_heal_vnf_url(self, mock_run):
        data = {
            "healVnfData": {
                "vnfInstanceId": self.nf_inst_id,
                "cause": "vm is down",
                "additionalParams": {
                    "action": "restartvm",
                    "actionvminfo": {
                        "vmid": "33",
                        "vmname": "xgw-smp11"
                    }
                }
            }
        }

        response = self.client.post("/api/nslcm/v1/ns/%s/heal" % self.ns_inst_id, data=data)
        self.assertEqual(status.HTTP_202_ACCEPTED, response.status_code)
        self.assertIsNotNone(response.data)
        self.assertIn("jobId", response.data)
        self.assertNotIn("error", response.data)

        response = self.client.delete("/api/nslcm/v1/ns/%s" % self.ns_inst_id)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    @mock.patch.object(NSHealService, 'start')
    @mock.patch.object(NSHealService, 'wait_job_finish')
    @mock.patch.object(NSHealService, 'update_job')
    def test_ns_manual_scale_thread(self, mock_start, mock_wait, mock_update):

        data = {
            "healVnfData": {
                "vnfInstanceId": self.nf_inst_id,
                "cause": "vm is down",
                "additionalParams": {
                    "action": "restartvm",
                    "actionvminfo": {
                        "vmid": "33",
                        "vmname": "xgw-smp11"
                    }
                }
            }
        }

        NSHealService(self.ns_inst_id, data, self.job_id).run()
        self.assertEqual(NSInstModel.objects.get(id=self.ns_inst_id).status, NS_INST_STATUS.HEALING)

    @mock.patch.object(NSHealService, "start")
    def test_ns_heal_non_existing_ns(self, mock_start):
        mock_start.side_effect = NSLCMException("NS Not Found")

        ns_inst_id = "2"

        data = {
            "healVnfData": {
                "vnfInstanceId": self.nf_inst_id,
                "cause": "vm is down",
                "additionalParams": {
                    "action": "restartvm",
                    "actionvminfo": {
                        "vmid": "33",
                        "vmname": "xgw-smp11"
                    }
                }
            }
        }

        response = self.client.post("/api/nslcm/v1/ns/%s/heal" % ns_inst_id, data=data)
        self.assertEqual(response.data["error"], "NS Not Found")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    @mock.patch.object(NSHealService, "start")
    def test_ns_heal_empty_post(self, mock_start):
        mock_start.side_effect = NSLCMException("healVnfData parameter does not exist or value is incorrect.")

        data = {}

        response = self.client.post("/api/nslcm/v1/ns/%s/heal" % self.ns_inst_id, data=data)
        self.assertEqual(response.data["error"], "healVnfData parameter does not exist or value is incorrect.")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
