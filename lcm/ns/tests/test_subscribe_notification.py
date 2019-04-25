# Copyright (c) 2019, CMCC Technologies Co., Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import mock
from django.test import TestCase
from rest_framework.test import APIClient
import uuid
from lcm.ns.tests import SUBSCRIPTION_NS_DELETION_DICT, SUBSCRIPTION_NS_OPERATION_DICT


class TestSubscription(TestCase):
    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        pass

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_subscribe_notification_simple(self, mock_uuid4, mock_requests):
        temp_uuid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        dummy_subscription = {
            "callbackUri": "http://test.com"
        }
        mock_requests.return_value.status_code = 204
        mock_requests.get.status_code = 204
        mock_uuid4.return_value = temp_uuid
        response = self.client.post("/api/nslcm/v1/subscriptions", data=dummy_subscription, format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(dummy_subscription["callbackUri"], response.data["callbackUri"])
        self.assertEqual(temp_uuid, response.data["id"])

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_subscribe_notification(self, mock_uuid4, mock_requests):
        temp_uuid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        mock_uuid4.return_value = temp_uuid
        response = self.client.post("/api/nslcm/v1/subscriptions", data=SUBSCRIPTION_NS_OPERATION_DICT, format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(SUBSCRIPTION_NS_OPERATION_DICT["callbackUri"], response.data["callbackUri"])
        self.assertEqual(temp_uuid, response.data["id"])

    @mock.patch("requests.get")
    def test_subscription_notification_invalide_auth(self, mock_requests):
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        expected_data = {
            'status': 500,
            'detail': 'Auth type should be BASIC'
        }
        subscription = copy.deepcopy(SUBSCRIPTION_NS_OPERATION_DICT)
        subscription["authentication"]["authType"] = ["OAUTH2_CLIENT_CREDENTIALS"]
        response = self.client.post("/api/nslcm/v1/subscriptions", data=subscription, format='json')
        self.assertEqual(500, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch("requests.get")
    def test_invalid_notification_type(self, mock_requests):
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        expected_data = {
            'status': 500,
            'detail': 'If you are setting operationTypes, notificationTypes must be '
            'NsLcmOperationOccurrenceNotification'
        }
        response = self.client.post("/api/nslcm/v1/subscriptions", data=SUBSCRIPTION_NS_DELETION_DICT, format='json')
        self.assertEqual(500, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_duplicate_subscription(self, mock_uuid4, mock_requests):
        temp_uuid = str(uuid.uuid4())
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        mock_uuid4.return_value = temp_uuid
        response = self.client.post("/api/nslcm/v1/subscriptions", data=SUBSCRIPTION_NS_OPERATION_DICT, format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(SUBSCRIPTION_NS_OPERATION_DICT["callbackUri"], response.data["callbackUri"])
        self.assertEqual(temp_uuid, response.data["id"])
        response = self.client.post("/api/nslcm/v1/subscriptions", data=SUBSCRIPTION_NS_OPERATION_DICT, format='json')
        self.assertEqual(303, response.status_code)
        expected_data = {
            'status': 303,
            'detail': 'Already Subscription exists with the same callbackUri and filter'
        }
        self.assertEqual(expected_data, response.data)
