# Copyright 2016-2018 ZTE Corporation.
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
from django.test import TestCase
from lcm.pub.database.models import NSInstModel
from lcm.pub.database.models import NfInstModel
from lcm.pub.utils.timeutil import now_time
from lcm.ns.tests import VNFD_MODEL_DICT


class TestScaleAspect(TestCase):

    def setUp(self):
        self.initInstModel()

        self.init_scale_ns_data()

        self.vnf_scale_info_list = [
            {
                "vnfd_id": "nf_zte_cscf",
                "vnf_scaleAspectId": "mpu",
                "numberOfSteps": "1"
            },
            {
                "vnfd_id": "nf_zte_hss",
                "vnf_scaleAspectId": "gsu",
                "numberOfSteps": "2"
            }
        ]

    def init_scale_ns_data(self):
        self.ns_scale_aspect = "TIC_EDGE_IMS"
        self.ns_scale_steps = "1"
        self.ns_scale_direction = "SCALE_IN"
        self.scaleNsData = [{
            "scaleNsByStepsData": [
                {
                    "aspectId": self.ns_scale_aspect,
                    "numberOfSteps": self.ns_scale_steps,
                    "scalingDirection": self.ns_scale_direction
                }
            ]
        }]

        self.ns_scale_aspect2 = "TIC_EDGE_HW"
        self.ns_scale_steps2 = "4"
        self.scaleNsData2 = [{
            "scaleNsByStepsData": [
                {
                    "aspectId": self.ns_scale_aspect2,
                    "numberOfSteps": self.ns_scale_steps2,
                    "scalingDirection": self.ns_scale_direction
                }
            ]
        }]

    def initInstModel(self):
        self.nsd_id = "23"
        self.ns_inst_id = "1"
        self.ns_name = "ns_1"
        self.ns_package_id = "ns_zte"
        self.description = "ns_zte"
        self.global_customer_id = "global_customer_id"
        self.service_type = "service_role"

        NSInstModel(id=self.ns_inst_id,
                    name=self.ns_name,
                    nspackage_id=self.ns_package_id,
                    nsd_id=self.nsd_id,
                    description=self.description,
                    status='empty',
                    lastuptime=now_time(),
                    global_customer_id=self.global_customer_id,
                    service_type=self.service_type).save()

        self.nf_inst_id = "231"
        self.ns_inst_id = "1"
        self.nf_name = "name_1"
        self.vnf_id = "1"
        self.vnfm_inst_id = "1"
        self.package_id = "nf_zte_cscf"
        self.nf_uuid = "abc34-345a-de13-ab85-ijs9"

        NfInstModel.objects.create(
            nfinstid=self.nf_inst_id,
            nf_name=self.nf_name,
            vnf_id=self.vnf_id,
            vnfm_inst_id=self.vnfm_inst_id,
            ns_inst_id=self.ns_inst_id,
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='active',
            mnfinstid=self.nf_uuid,
            package_id=self.package_id,
            vnfd_model=json.dumps(VNFD_MODEL_DICT))

        # Create a second vnf instance
        self.nf_inst_id = "232"
        self.package_id = "nf_zte_hss"
        self.nf_uuid = "abc34-3g5a-de13-ab85-ijs3"

        NfInstModel.objects.create(
            nfinstid=self.nf_inst_id,
            nf_name=self.nf_name,
            vnf_id=self.vnf_id,
            vnfm_inst_id=self.vnfm_inst_id,
            ns_inst_id=self.ns_inst_id,
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='active',
            mnfinstid=self.nf_uuid,
            package_id=self.package_id,
            vnfd_model=json.dumps(VNFD_MODEL_DICT))

    def add_another_nf_instance(self):
        # Create a third vnf instance
        nf_inst_id = "233"
        package_id = "nf_zte_hss"
        nf_uuid = "ab34-3g5j-de13-ab85-ij93"

        NfInstModel.objects.create(
            nfinstid=nf_inst_id,
            nf_name=self.nf_name,
            vnf_id=self.vnf_id,
            vnfm_inst_id=self.vnfm_inst_id,
            ns_inst_id=self.ns_inst_id,
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='active',
            mnfinstid=nf_uuid,
            package_id=package_id,
            vnfd_model=json.dumps(VNFD_MODEL_DICT))

    def add_new_vnf_instance(self):
        # Create a third vnf instance
        nf_inst_id = "241"
        package_id = "nf_hw_cscf"
        nf_uuid = "ab34-3g5j-de13-aa85-ij93"

        NfInstModel.objects.create(
            nfinstid=nf_inst_id,
            nf_name=self.nf_name,
            vnf_id=self.vnf_id,
            vnfm_inst_id=self.vnfm_inst_id,
            ns_inst_id=self.ns_inst_id,
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='active',
            mnfinstid=nf_uuid,
            package_id=package_id,
            vnfd_model=json.dumps(VNFD_MODEL_DICT))

        # Create a third vnf instance
        nf_inst_id = "242"
        package_id = "nf_hw_hss"
        nf_uuid = "ab34-3g5j-de13-aa85-id93"

        NfInstModel.objects.create(
            nfinstid=nf_inst_id,
            nf_name=self.nf_name,
            vnf_id=self.vnf_id,
            vnfm_inst_id=self.vnfm_inst_id,
            ns_inst_id=self.ns_inst_id,
            max_cpu='14',
            max_ram='12296',
            max_hd='101',
            max_shd="20",
            max_net=10,
            status='active',
            mnfinstid=nf_uuid,
            package_id=package_id,
            vnfd_model=json.dumps(VNFD_MODEL_DICT))

    def tearDown(self):
        NSInstModel().clean()
        NfInstModel().clean()
