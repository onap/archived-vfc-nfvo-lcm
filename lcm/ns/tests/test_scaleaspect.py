# Copyright 2016-2018 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import mock
import os

from django.test import TestCase
from lcm.pub.database.models import NSInstModel, NfInstModel
from lcm.ns_vnfs.enum import VNF_STATUS
from lcm.ns.biz.scale_aspect import mapping_conv, get_vnf_instance_id_list, check_scale_list, get_scale_vnf_data, \
    get_nsdId, check_and_set_params, get_scale_vnf_data_info_list, get_vnf_scale_info, get_scale_vnf_data_from_json


class TestScaleAspect(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        NSInstModel.objects.all().delete()
        NfInstModel.objects.all().delete()

    def test_mapping_conv(self):
        keyword_map = {'a': 1, 'b': 2, 'c': 3, 'd': {'d.1': 'd.1'}}
        rest_return = {'b': 2, 'C': 3}
        resp_data = mapping_conv(keyword_map, rest_return)
        self.assertEqual(resp_data, {'a': '', 'b': 2, 'c': 3, 'd': {'d.1': ''}})

    def test_get_vnf_instance_id_list_when_no_model(self):
        self.assertEqual(get_vnf_instance_id_list('package_1'), [])

    def test_check_scale_list_when_empty_vnf_scale_list(self):
        try:
            check_scale_list([], 'ns_instanceId_01', '', '')
        except Exception as e:
            self.assertEqual(e.args, ('The scaling option[ns=ns_instanceId_01, aspect=, step=] does not exist. '
                                      'Pls check the config file.',))

    @mock.patch.object(os.path, 'abspath')
    def test_get_scale_vnf_data(self, mock_abspath):
        mock_abspath.return_value = 'lcm/1/2/3.py'
        scale_ns_data = {'scaleNsByStepsData': {'aspectId': 'TIC_EDGE_IMS', 'numberOfSteps': 1,
                                                'scalingDirection': 'r'}}
        ns_instance_id = 'ns_instanceId_01'
        scale_vnf_data_list = get_scale_vnf_data(scale_ns_data, ns_instance_id)
        success_list = [
            {
                'vnfInstanceId': 'nf_zte_cscf',
                'scaleByStepData': {
                    'type': 'r',
                    'aspectId': 'gsu',
                    'numberOfSteps': '1'
                }
            },
            {
                'vnfInstanceId': 'nf_zte_hss',
                'scaleByStepData': {
                    'type': 'r',
                    'aspectId': 'gpu',
                    'numberOfSteps': '3'
                }
            }
        ]
        self.assertEqual(scale_vnf_data_list, success_list)

    def test_get_nsd_id_when_none(self):
        self.assertEqual(get_nsdId('ns_instance_id_01'), None)

    def test_check_and_set_params_when_scale_ns_data_is_none(self):
        try:
            check_and_set_params(None, '')
        except Exception as e:
            self.assertEqual(e.args, ('Error! scaleNsData in the request is Empty!',))

    def test_check_and_set_params_when_scale_ns_by_steps_data_is_none(self):
        scale_ns_data = {'scaleNsByStepsData': None}
        try:
            check_and_set_params(scale_ns_data, '')
        except Exception as e:
            self.assertEqual(e.args, ('Error! scaleNsByStepsData in the request is Empty!',))

    @mock.patch.object(os.path, 'abspath')
    def test_get_scale_vnf_data_info_list(self, mock_abspath):
        NSInstModel(id='ns_instanceId_02', nsd_id='02').save()
        NfInstModel(package_id='nf_hw_cscf', status=VNF_STATUS.ACTIVE, nfinstid='nfinst_01').save()
        mock_abspath.return_value = 'lcm/1/2/3.py'
        scale_ns_data = {
            'scaleNsByStepsData': {'aspectId': 'TIC_EDGE_HW', 'numberOfSteps': 4, 'scalingDirection': 'r'}}
        ns_instance_id = 'ns_instanceId_02'
        scale_vnf_data_info_list = get_scale_vnf_data_info_list(scale_ns_data, ns_instance_id)
        success_list = [
            {
                'vnfInstanceId': 'nfinst_01',
                'scaleByStepData': {
                    'type': 'r',
                    'aspectId': 'gsu',
                    'numberOfSteps': '1'
                }
            }
        ]
        self.assertEqual(scale_vnf_data_info_list, success_list)

    def test_get_vnf_scale_info_when_return_none(self):
        filename = 'lcm/ns/tests/data/scalemapping.json'
        ns_instance_id = 'ns_instanceId_03'
        self.assertEqual(get_vnf_scale_info(filename, ns_instance_id, '', ''), None)

    def test_get_scale_vnf_data_from_json_when_return_none(self):
        self.assertEqual(get_scale_vnf_data_from_json({}, '', '', ''), None)
