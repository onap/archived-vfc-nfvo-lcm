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

from django.test import TestCase
from lcm.pub.utils.scaleaspect import get_json_data
from lcm.pub.database.models import NfInstModel
from lcm.pub.database.models import NSInstModel
from lcm.pub.utils.timeutil import now_time
import os


class TestScaleAspect(TestCase):

    def setUp(self):
        self.init_scaling_map_json()
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

    def init_scaling_map_json(self):
        curdir_path = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__))))
        filename = curdir_path + "/ns/data/scalemapping.json"
        self.scaling_map_json = get_json_data(filename)

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
            vnfd_model='{"metadata": {"vnfdId": "1","vnfdName": "PGW001",'
            '"vnfProvider": "zte","vnfdVersion": "V00001","vnfVersion": "V5.10.20",'
            '"productType": "CN","vnfType": "PGW",'
            '"description": "PGW VNFD description",'
            '"isShared":true,"vnfExtendType":"driver"}}')

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
            vnfd_model='{"metadata": {"vnfdId": "1","vnfdName": "PGW001",'
                       '"vnfProvider": "zte","vnfdVersion": "V00001","vnfVersion": "V5.10.20",'
                       '"productType": "CN","vnfType": "PGW",'
                       '"description": "PGW VNFD description",'
                       '"isShared":true,"vnfExtendType":"driver"}}')

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
            vnfd_model='{"metadata": {"vnfdId": "1","vnfdName": "PGW001",'
                       '"vnfProvider": "zte","vnfdVersion": "V00001","vnfVersion": "V5.10.20",'
                       '"productType": "CN","vnfType": "PGW",'
                       '"description": "PGW VNFD description",'
                       '"isShared":true,"vnfExtendType":"driver"}}')

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
            vnfd_model='{"metadata": {"vnfdId": "1","vnfdName": "PGW001",'
                       '"vnfProvider": "zte","vnfdVersion": "V00001","vnfVersion": "V5.10.20",'
                       '"productType": "CN","vnfType": "PGW",'
                       '"description": "PGW VNFD description",'
                       '"isShared":true,"vnfExtendType":"driver"}}')

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
            vnfd_model='{"metadata": {"vnfdId": "1","vnfdName": "PGW001",'
                       '"vnfProvider": "zte","vnfdVersion": "V00001","vnfVersion": "V5.10.20",'
                       '"productType": "CN","vnfType": "PGW",'
                       '"description": "PGW VNFD description",'
                       '"isShared":true,"vnfExtendType":"driver"}}')

    def tearDown(self):
        NSInstModel().clean()
        NfInstModel().clean()

    '''
    def test_get_and_check_params(self):
        aspect, numberOfSteps, scale_type = check_and_set_params(
            self.scaleNsData, "1")
        self.assertEqual(aspect, self.ns_scale_aspect)
        self.assertEqual(numberOfSteps, self.ns_scale_steps)
        self.assertEqual(scale_type, self.ns_scale_direction)

    def test_get_scale_vnf_data_from_json(self):
        vnf_data_package = get_scale_vnf_data_from_json(
            self.scaling_map_json, "23", "TIC_EDGE_IMS", "1")
        self.assertIsNotNone(vnf_data_package)
        self.assertEqual(2, vnf_data_package.__len__())
        self.assertIsNotNone(vnf_data_package)
        self.assertEqual(2, vnf_data_package.__len__())
        self.assertEqual("nf_zte_cscf", vnf_data_package[0]["vnfd_id"])
        self.assertEqual("1", vnf_data_package[0]["numberOfSteps"])
        self.assertEqual("gsu", vnf_data_package[0]["vnf_scaleAspectId"])
        self.assertEqual("nf_zte_hss", vnf_data_package[1]["vnfd_id"])
        self.assertEqual("3", vnf_data_package[1]["numberOfSteps"])
        self.assertEqual("gpu", vnf_data_package[1]["vnf_scaleAspectId"])

    def test_get_scale_vnf_data_from_json_2(self):
        vnf_data_package = get_scale_vnf_data_from_json(
            self.scaling_map_json, "23", "TIC_EDGE_IMS", "2")
        self.assertIsNotNone(vnf_data_package)
        self.assertEqual(2, vnf_data_package.__len__())
        self.assertEqual("nf_zte_cscf", vnf_data_package[0]["vnfd_id"])
        self.assertEqual("2", vnf_data_package[0]["numberOfSteps"])
        self.assertEqual("mpu", vnf_data_package[0]["vnf_scaleAspectId"])
        self.assertEqual("nf_zte_hss", vnf_data_package[1]["vnfd_id"])
        self.assertEqual("4", vnf_data_package[1]["numberOfSteps"])
        self.assertEqual("mpu", vnf_data_package[1]["vnf_scaleAspectId"])

    def test_set_scacle_vnf_instance_id(self):
        result = set_scacle_vnf_instance_id(self.vnf_scale_info_list)
        self.assertEqual(2, result.__len__())
        self.assertEqual(result[0]["numberOfSteps"],
                         self.vnf_scale_info_list[0]["numberOfSteps"])
        self.assertEqual(
            result[0]["vnf_scaleAspectId"],
            self.vnf_scale_info_list[0]["vnf_scaleAspectId"])
        self.assertEqual(result[1]["numberOfSteps"],
                         self.vnf_scale_info_list[1]["numberOfSteps"])
        self.assertEqual(
            result[1]["vnf_scaleAspectId"],
            self.vnf_scale_info_list[1]["vnf_scaleAspectId"])
        self.assertEqual("231", result[0]["vnfInstanceId"])
        self.assertEqual("232", result[1]["vnfInstanceId"])
        self.assertNotIn("vnfd_id", result[0])
        self.assertNotIn("vnfd_id", result[1])

    def test_set_scacle_vnf_instance_id_2(self):
        vnf_scale_info_list = [
            {
                "vnfd_id": "error1",
                "vnf_scaleAspectId": "mpu",
                "numberOfSteps": "1"
            },
            {
                "vnfd_id": "nf_zte_hss",
                "vnf_scaleAspectId": "mpu",
                "numberOfSteps": "1"
            }
        ]
        result = set_scacle_vnf_instance_id(vnf_scale_info_list)
        self.assertEqual(1, result.__len__())
        self.assertEqual(
            result[0]["numberOfSteps"],
            vnf_scale_info_list[0]["numberOfSteps"])
        self.assertEqual(
            result[0]["vnf_scaleAspectId"],
            vnf_scale_info_list[0]["vnf_scaleAspectId"])
        self.assertEqual("232", result[0]["vnfInstanceId"])
        self.assertNotIn("vnfd_id", result[0])

    def test_set_scacle_vnf_instance_id_3(self):
        vnf_scale_info_list = [
            {
                "vnfd_id": "error1",
                "vnf_scaleAspectId": "mpu",
                "numberOfSteps": "1"
            },
            {
                "vnfd_id": "error2",
                "vnf_scaleAspectId": "gsu",
                "numberOfSteps": "1"
            }
        ]
        result = set_scacle_vnf_instance_id(vnf_scale_info_list)
        self.assertEqual(0, result.__len__())

    def test_set_scacle_vnf_instance_id_4(self):
        self.add_another_nf_instance()
        result = set_scacle_vnf_instance_id(self.vnf_scale_info_list)
        self.assertEqual(3, result.__len__())
        self.assertEqual("231", result[0]["vnfInstanceId"])
        self.assertEqual("232", result[1]["vnfInstanceId"])
        self.assertEqual("233", result[2]["vnfInstanceId"])

    def test_set_scaleVnfData_type(self):
        vnf_scale_list = set_scacle_vnf_instance_id(self.vnf_scale_info_list)
        result = set_scaleVnfData_type(vnf_scale_list, self.ns_scale_direction)
        self.assertEqual(2, result.__len__())
        self.assertNotIn("scaleByStepData", result)
        self.assertEqual(
            self.ns_scale_direction,
            result[0]["scaleByStepData"]["type"])
        self.assertEqual("mpu", result[0]["scaleByStepData"]["aspectId"])
        self.assertNotIn("vnf_scaleAspectId", result[0]["scaleByStepData"])
        self.assertEqual("1", result[0]["scaleByStepData"]["numberOfSteps"])
        self.assertEqual(
            self.ns_scale_direction,
            result[1]["scaleByStepData"]["type"])
        self.assertEqual("gsu", result[1]["scaleByStepData"]["aspectId"])
        self.assertNotIn("vnf_scaleAspectId", result[1]["scaleByStepData"])
        self.assertEqual("2", result[1]["scaleByStepData"]["numberOfSteps"])

    def test_get_nsdId(self):
        nsd_id = get_nsdId("1")
        self.assertEqual("23", nsd_id)

    @mock.patch.object(catalog, 'get_scalingmap_json_package')
    def test_get_scale_vnf_data_info_list(
            self, mock_get_scalingmap_json_package):
        mock_get_scalingmap_json_package.return_value = self.scaling_map_json

        scale_vnf_data = get_scale_vnf_data_info_list(self.scaleNsData, "1")
        self.assertIsNotNone(scale_vnf_data)
        self.assertEqual(2, scale_vnf_data.__len__())

    @mock.patch.object(catalog, 'get_scalingmap_json_package')
    def test_get_scale_vnf_data_info_list_2(
            self, mock_get_scalingmap_json_package):
        mock_get_scalingmap_json_package.return_value = self.scaling_map_json

        scale_vnf_data = None
        is_exception_caught = False
        try:
            scale_vnf_data = get_scale_vnf_data_info_list(
                self.scaleNsData2, "1")
        except Exception:
            is_exception_caught = True
        self.assertTrue(is_exception_caught)
        self.assertIsNone(scale_vnf_data)

    @mock.patch.object(catalog, 'get_scalingmap_json_package')
    def test_get_scale_vnf_data_info_list_3(
            self, mock_get_scalingmap_json_package):
        mock_get_scalingmap_json_package.return_value = self.scaling_map_json
        self.add_new_vnf_instance()

        scale_vnf_data = None
        is_exception_caught = False
        try:
            scale_vnf_data = get_scale_vnf_data_info_list(
                self.scaleNsData2, "1")
        except Exception:
            is_exception_caught = True
        self.assertFalse(is_exception_caught)
        self.assertEqual(2, scale_vnf_data.__len__())
        
    '''