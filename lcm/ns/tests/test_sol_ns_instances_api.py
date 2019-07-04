# Copyright 2019 ZTE Corporation.
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
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from lcm.pub.database.models import NSInstModel
from lcm.pub.utils import restcall
from lcm.ns.biz.ns_create import CreateNSService
from lcm.pub.exceptions import NSLCMException
from lcm.ns.tests import SOL_CREATE_NS_DICT, SOL_REST_HEADER_DICT, NS_PACKAGE_INFO_DICT, NS_INFO_AAI_DICT


class TestNsInstanceApi(TestCase):

    def setUp(self):
        self.apiClient = APIClient()
        self.format = 'json'
        self.ns_instances_url = '/api/nslcm/v1/ns_instances'
        self.nsd_id = "c9f0a95e-dea0-4698-96e5-5a79bc5a233d"
        self.ns_package_id = "c9f0a95e-dea0-4698-96e5-5a79bc5a233d"

    def tearDown(self):
        NSInstModel.objects.all().delete()

    @mock.patch.object(restcall, 'call_req')
    def test_create_ns(self, mock_call_req):
        r1_query_nspackage_from_catalog = [0, json.JSONEncoder().encode(NS_PACKAGE_INFO_DICT), '201']
        r2_create_ns_to_aai = [0, json.JSONEncoder().encode({}), '201']
        mock_call_req.side_effect = [r1_query_nspackage_from_catalog, r2_create_ns_to_aai]
        response = self.apiClient.post(self.ns_instances_url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        return response.data['id']

    @mock.patch.object(restcall, 'call_req')
    def test_create_ns_cpe(self, mock_call_req):
        r1_query_nspackage_from_catalog = [0, json.JSONEncoder().encode(NS_PACKAGE_INFO_DICT), '201']
        r2_create_ns_to_aai = [0, json.JSONEncoder().encode({}), '201']
        mock_call_req.side_effect = [r1_query_nspackage_from_catalog, r2_create_ns_to_aai]
        response = self.apiClient.post(self.ns_instances_url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    @mock.patch.object(restcall, 'call_req')
    def test_create_ns_when_ns_name_exist(self, mock_call_req):
        NSInstModel.objects.all().delete()
        NSInstModel(id="1", name="ns").save()
        nspackage_info = json.JSONEncoder().encode(NS_PACKAGE_INFO_DICT)
        mock_call_req.return_value = [0, nspackage_info, '200']
        response = self.apiClient.post(self.ns_instances_url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @mock.patch.object(CreateNSService, "do_biz")
    def test_create_ns_empty_data(self, mock_do_biz):
        mock_do_biz.side_effect = Exception("Exception in CreateNS.")
        response = self.apiClient.post(self.ns_instances_url, data={}, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch.object(CreateNSService, "do_biz")
    def test_create_ns_no_header(self, mock_do_biz):
        mock_do_biz.side_effect = Exception("Exception in CreateNS.")
        response = self.apiClient.post(self.ns_instances_url, data=SOL_CREATE_NS_DICT, format=self.format)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch.object(CreateNSService, "do_biz")
    def test_create_ns_non_existing_nsd(self, mock_do_biz):
        mock_do_biz.side_effect = NSLCMException("nsd not exists.")
        response = self.apiClient.post(self.ns_instances_url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @mock.patch.object(restcall, 'call_req')
    def test_create_ns_when_fail_to_get_nsd(self, mock_call_req):
        mock_call_req.return_value = [1, "Failed to get nsd.", '500']
        response = self.apiClient.post(self.ns_instances_url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_ns_instances_method_not_allowed(self):
        response = self.apiClient.delete(self.ns_instances_url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.apiClient.put(self.ns_instances_url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.apiClient.patch(self.ns_instances_url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_invidual_ns_instance_method_not_allowed(self):
        url = self.ns_instances_url + '/1'
        response = self.apiClient.post(url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.apiClient.put(url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        response = self.apiClient.patch(url, data=SOL_CREATE_NS_DICT, format=self.format, **SOL_REST_HEADER_DICT)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_query_ns(self):
        NSInstModel.objects.all().delete()
        self.test_create_ns()
        response = self.apiClient.get(self.ns_instances_url)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertIsNotNone(response.data)
        self.assertEqual(1, len(response.data))
        self.assertEqual(self.nsd_id, response.data[0]['nsdId'])
        self.assertEqual('ns', response.data[0]['nsInstanceName'])
        self.assertEqual('NOT_INSTANTIATED', response.data[0]['nsState'])

    def test_query_one_ns(self):
        NSInstModel.objects.all().delete()
        id = self.test_create_ns()
        url = self.ns_instances_url + '/' + id
        response = self.apiClient.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        self.assertIsNotNone(response.data)
        self.assertEqual(self.nsd_id, response.data['nsdId'])
        self.assertEqual('ns', response.data['nsInstanceName'])
        self.assertEqual('NOT_INSTANTIATED', response.data['nsState'])

    @mock.patch.object(restcall, 'call_req')
    def test_delete_ns(self, mock_call_req):
        NSInstModel(id="1", nspackage_id="7", nsd_id="2").save()
        r1_query_ns_to_aai = [0, json.JSONEncoder().encode(NS_INFO_AAI_DICT), '200']
        r2_delete_ns_to_aai = [0, json.JSONEncoder().encode({}), '200']
        mock_call_req.side_effect = [r1_query_ns_to_aai, r2_delete_ns_to_aai]
        url = self.ns_instances_url + '/1'
        response = self.apiClient.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
