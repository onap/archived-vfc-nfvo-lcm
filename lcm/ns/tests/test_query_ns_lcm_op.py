# Copyright (c) 2019, CMCC Technologies Co., Ltd.
# Copyright (c) 2019 ZTE Corporation.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework import status
from lcm.pub.database.models import NSLcmOpOccModel
from lcm.ns.tests import OCCURRENCE_DICT, NSLCMOP_WITH_EXCLUDE_DEFAULT_DICT


class TestNSLcmOpOccs(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.multiple_ns_lcm_op = OCCURRENCE_DICT
        self.single_ns_lcm_op = self.multiple_ns_lcm_op[0]
        self.nslcmop_with_exclude_default = NSLCMOP_WITH_EXCLUDE_DEFAULT_DICT
        NSLcmOpOccModel.objects.all().delete()

    def tearDown(self):
        pass

    def test_get_nslcmopoccs(self):
        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        ns_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        NSLcmOpOccModel(
            id=lcm_op_id,
            operation_state="STARTING",
            state_entered_time="2019-01-01",
            start_time="2019-01-01",
            ns_instance_id=ns_instance_id,
            operation="SCALE",
            is_automatic_invocation=False,
            operation_params='{}',
            is_cancel_pending=False,
            cancel_mode=None,
            error=None,
            resource_changes=None,
            links=json.dumps({"self": {"href": "demo"}, "nsInstance": "demo"})).save()
        response = self.client.get("/api/nslcm/v1/ns_lcm_op_occs", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_nslcmopoccs_with_id_not_exist(self):
        response = self.client.get("/api/nslcm/v1/ns_lcm_op_occs?id=dummy", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_nslcmopoccs_with_filters(self):
        lcm_op_id = "a6b9415c-ab99-11e8-9d37-dbb5e0378955"
        ns_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        NSLcmOpOccModel(
            id=lcm_op_id,
            operation_state="STARTING",
            state_entered_time="2019-01-01",
            start_time="2019-01-01",
            ns_instance_id=ns_instance_id,
            operation="INSTANTIATE",
            is_automatic_invocation=False,
            operation_params='{}',
            is_cancel_pending=False,
            cancel_mode=None,
            error=None,
            resource_changes=None,
            links=json.dumps({"self": {"href": "demo"}, "nsInstance": "demo"})).save()
        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        NSLcmOpOccModel(
            id=lcm_op_id,
            operation_state="STARTING",
            state_entered_time="2019-01-01",
            start_time="2019-01-01",
            ns_instance_id=ns_instance_id,
            operation="SCALE",
            is_automatic_invocation=False,
            operation_params='{}',
            is_cancel_pending=False,
            cancel_mode=None,
            error=None,
            resource_changes=None,
            links=json.dumps({"self": {"href": "demo"}, "nsInstance": "demo"})).save()
        response = self.client.get("/api/nslcm/v1/ns_lcm_op_occs", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/nslcm/v1/ns_lcm_op_occs?operation=SCALE", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/nslcm/v1/ns_lcm_op_occs?nsInstanceId=%s" % ns_instance_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_nslcmopoccs_with_extra_flags(self):
        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        ns_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        NSLcmOpOccModel(
            id=lcm_op_id,
            operation_state="STARTING",
            state_entered_time="2019-01-01",
            start_time="2019-01-01",
            ns_instance_id=ns_instance_id,
            operation="SCALE",
            is_automatic_invocation=False,
            operation_params='{}',
            is_cancel_pending=False,
            cancel_mode=None,
            error=None,
            resource_changes=None,
            links=json.dumps({"self": {"href": "demo"}, "nsInstance": "demo"})).save()
        response = self.client.get("/api/nslcm/v1/ns_lcm_op_occs?exclude_default", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_nslcmopocc_with_id(self):
        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        ns_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        NSLcmOpOccModel(
            id=lcm_op_id,
            operation_state="STARTING",
            state_entered_time="2019-01-01",
            start_time="2019-01-01",
            ns_instance_id=ns_instance_id,
            operation="SCALE",
            is_automatic_invocation=False,
            operation_params='{}',
            is_cancel_pending=False,
            cancel_mode=None,
            error=None,
            resource_changes=None,
            links=json.dumps({"self": {"href": "demo"}, "nsInstance": "demo"})).save()
        response = self.client.get("/api/nslcm/v1/ns_lcm_op_occs/" + lcm_op_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.single_ns_lcm_op['id'], response.data['id'])

    def test_single_nslcmopocc_with_unknown_id(self):
        lcm_op_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        response = self.client.get("/api/nslcm/v1/ns_lcm_op_occs/" + lcm_op_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        expected_data = {
            "status": 500,
            "detail": "LCM Operation Occurance does not exist"
        }
        self.assertEqual(expected_data, response.data)
