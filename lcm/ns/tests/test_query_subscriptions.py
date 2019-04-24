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

import json
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from lcm.pub.database.models import SubscriptionModel
from lcm.ns.tests import SUBSCRIPTION_DICT


class TestQuerySubscriptions(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_single_subscription = SUBSCRIPTION_DICT.copy()
        self.subscription_id = "99442b18-a5c7-11e8-998c-bf1755941f16"
        self.ns_instance_id = "cd552c9c-ab6f-11e8-b354-236c32aa91a1"
        SubscriptionModel.objects.all().delete()

    def tearDown(self):
        pass

    def test_get_subscriptions(self):
        ns_instance_filter = {
            "nsdIds": [],
            "nsInstanceIds": [self.ns_instance_id],
            "nsInstanceNames": []
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(
            subscription_id=self.subscription_id,
            callback_uri="http://aurl.com",
            auth_info="{}",
            notification_types="['NsLcmOperationOccurrenceNotification']",
            operation_types="['INSTANTIATE']",
            operation_states="['STARTING']",
            links=json.dumps(links),
            ns_instance_filter=json.dumps(ns_instance_filter)).save()
        response = self.client.get("/api/nslcm/v1/subscriptions", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([self.test_single_subscription], response.data)

    def test_get_subscriptions_with_ns_instance_id(self):
        ns_instance_filter = {
            "nsdIds": [],
            "nsInstanceIds": [self.ns_instance_id],
            "nsInstanceNames": []
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(
            subscription_id=self.subscription_id,
            callback_uri="http://aurl.com",
            auth_info="{}",
            notification_types="['NsLcmOperationOccurrenceNotification']",
            operation_types="['INSTANTIATE']",
            operation_states="['STARTING']",
            links=json.dumps(links),
            ns_instance_filter=json.dumps(ns_instance_filter)).save()
        dummy_ns_id = "584b35e2-b2a2-11e8-8e11-645106374fd3"
        dummy_subscription_id = "947dcd2c-b2a2-11e8-b365-645106374fd4"
        ns_instance_filter["nsInstanceIds"].append(dummy_ns_id)
        SubscriptionModel(
            subscription_id=dummy_subscription_id,
            callback_uri="http://aurl.com",
            auth_info="{}",
            notification_types="['NsLcmOperationOccurrenceNotification']",
            operation_types="['INSTANTIATE']",
            operation_states="['STARTING']",
            links=json.dumps(links),
            ns_instance_filter=json.dumps(ns_instance_filter)).save()
        response = self.client.get("/api/nslcm/v1/subscriptions?nsInstanceId=" + dummy_ns_id, format='json')
        expected_response = self.test_single_subscription.copy()
        expected_response["id"] = dummy_subscription_id
        expected_response["filter"]["nsInstanceSubscriptionFilter"]["nsInstanceIds"] = ns_instance_filter["nsInstanceIds"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([expected_response], response.data)

    def test_get_subscriptions_with_unknown_ns_instance_id(self):
        ns_instance_filter = {
            "nsdIds": [],
            "nsInstanceIds": [self.ns_instance_id],
            "nsInstanceNames": []
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(
            subscription_id=self.subscription_id,
            callback_uri="http://aurl.com",
            auth_info="{}",
            notification_types="['NsLcmOperationOccurrenceNotification']",
            operation_types="['INSTANTIATE']",
            operation_states="['STARTING']",
            links=json.dumps(links),
            ns_instance_filter=json.dumps(ns_instance_filter)).save()
        response = self.client.get("/api/nslcm/v1/subscriptions?nsInstanceId=dummy", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([], response.data)

    def test_get_subscriptions_with_invalid_filter(self):
        ns_instance_filter = {
            "nsdIds": [],
            "nsInstanceIds": [self.ns_instance_id],
            "nsInstanceNames": []
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(
            subscription_id=self.subscription_id,
            callback_uri="http://aurl.com",
            auth_info="{}",
            notification_types="['NsLcmOperationOccurrenceNotification']",
            operation_types="['INSTANTIATE']",
            operation_states="['STARTING']",
            links=json.dumps(links),
            ns_instance_filter=json.dumps(ns_instance_filter)).save()
        response = self.client.get("/api/nslcm/v1/subscriptions?dummy=dummy", format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_subscriptions_with_operation_type_filter(self):
        ns_instance_filter = {
            "nsdIds": [],
            "nsInstanceIds": [self.ns_instance_id],
            "nsInstanceNames": []
        }
        links = {
            "self": {
                "href": "/api/v1/subscriptions/99442b18-a5c7-11e8-998c-bf1755941f16"
            }
        }
        SubscriptionModel(
            subscription_id=self.subscription_id,
            callback_uri="http://aurl.com",
            auth_info="{}",
            notification_types="['NsLcmOperationOccurrenceNotification']",
            operation_types="['INSTANTIATE']",
            operation_states="['STARTING']",
            links=json.dumps(links),
            ns_instance_filter=json.dumps(ns_instance_filter)).save()
        dummy_ns_id = "584b35e2-b2a2-11e8-8e11-645106374fd3"
        dummy_subscription_id = "947dcd2c-b2a2-11e8-b365-645106374fd4"
        ns_instance_filter["nsInstanceIds"].append(dummy_ns_id)
        SubscriptionModel(
            subscription_id=dummy_subscription_id,
            callback_uri="http://aurl.com",
            auth_info="{}",
            notification_types="['NsLcmOperationOccurrenceNotification']",
            operation_types="['SCALE']",
            operation_states="['STARTING']",
            links=json.dumps(links),
            ns_instance_filter=json.dumps(ns_instance_filter)).save()
        response = self.client.get("/api/nslcm/v1/subscriptions?operationTypes=SCALE", format='json')
        expected_response = self.test_single_subscription.copy()
        expected_response["id"] = dummy_subscription_id
        expected_response["filter"]["nsInstanceSubscriptionFilter"]["nsInstanceIds"] = ns_instance_filter["nsInstanceIds"]
        expected_response["filter"]["operationTypes"] = ["SCALE"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([expected_response], response.data)
