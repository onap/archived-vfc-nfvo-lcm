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

import json
import mock
import uuid

from django.test import Client
from django.test import TestCase

from lcm.pub.database.models import FPInstModel
from lcm.pub.database.models import JobModel
from lcm.ns_sfcs.biz.create_sfc_worker import CreateSfcWorker
from lcm.ns_sfcs.tests.test_data import nsd_model
from lcm.ns_sfcs.biz.utils import get_fp_id
from lcm.ns_sfcs.biz.create_flowcla import CreateFlowClassifier
from lcm.ns_sfcs.biz.create_portpairgp import CreatePortPairGroup
from lcm.ns_sfcs.biz.create_port_chain import CreatePortChain


class TestCreateSfcWorker(TestCase):
    def setUp(self):
        self.client = Client()
        FPInstModel.objects.filter().delete()
        self.fpinstid = str(uuid.uuid4())
        FPInstModel(
            fpid="fpd_1",
            fpinstid=self.fpinstid,
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
            sdncontrollerid="sdn_controller_1",
            portpairgroups=json.JSONEncoder().encode([{"groupid": "1"}]),
            symmetric=1,
            flowclassifiers="test_flowclassifiers",

        ).save()

    def tearDown(self):
        FPInstModel.objects.filter().delete()

    @mock.patch.object(CreateFlowClassifier, 'do_biz')
    @mock.patch.object(CreatePortPairGroup, 'do_biz')
    @mock.patch.object(CreatePortChain, 'do_biz')
    def test_create_sfc_worker(self, mock_port_chain_do_biz, mock_port_pair_group_do_biz, mock_flow_classifier_do_biz):
        mock_port_chain_do_biz.return_value = None
        mock_port_pair_group_do_biz.return_value = None
        mock_flow_classifier_do_biz.return_value = None
        data = {
            'nsinstid': "ns_inst_1",
            "ns_model_data": nsd_model,
            'fpindex': get_fp_id("1", nsd_model),
            'fpinstid': self.fpinstid,
            'sdncontrollerid': "sdnControllerId_1"
        }

        create_sfc_worker = CreateSfcWorker(data)
        job_id = create_sfc_worker.init_data()
        create_sfc_worker.run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, 100)

    @mock.patch.object(CreatePortPairGroup, 'do_biz')
    @mock.patch.object(CreatePortChain, 'do_biz')
    def test_create_sfc_worker_when_error(self, mock_port_chain_do_biz, mock_port_pair_group_do_biz):
        mock_port_chain_do_biz.return_value = None
        mock_port_pair_group_do_biz.return_value = None
        data = {
            'nsinstid': "ns_inst_1",
            "ns_model_data": nsd_model,
            'fpindex': get_fp_id("1", nsd_model),
            'fpinstid': self.fpinstid,
            'sdncontrollerid': "sdnControllerId_1"
        }

        create_sfc_worker = CreateSfcWorker(data)
        job_id = create_sfc_worker.init_data()
        create_sfc_worker.run()
        self.assertEqual(JobModel.objects.filter(jobid=job_id).first().progress, 255)
        self.assertEqual(FPInstModel.objects.filter(fpinstid=self.fpinstid).first().status, 'failed')
