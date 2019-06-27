# Copyright (c) 2019, ZTE Corporation.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast
import json
import logging
import requests
import uuid
from collections import Counter

from rest_framework import status

from lcm.ns.enum import NOTIFICATION_TYPE, AUTH_TYPE
from lcm.pub.database.models import SubscriptionModel
from lcm.pub.exceptions import NSLCMException, SeeOtherException
from lcm.pub.utils.values import ignore_case_get
from lcm.ns import const

logger = logging.getLogger(__name__)


def is_filter_type_equal(new_filter, existing_filter):
    return Counter(new_filter) == Counter(existing_filter)


FILTER_TYPE = [
    "operation_types",
    "ns_component_types",
    "lcm_opname_impacting_nscomponent",
    "lcm_opoccstatus_impacting_nscomponent",
    "notification_types",
    "operation_states"
]

NS_FILTER_TYPE = [
    "nsdIds",
    "nsInstanceIds",
    "vnfdIds",
    "pnfdIds",
    "nsInstanceNames"
]


class CreateSubscription:

    def __init__(self, data):
        self.data = data
        self.filter = ignore_case_get(self.data, "filter", {})
        self.callback_uri = ignore_case_get(self.data, "callbackUri")
        self.authentication = ignore_case_get(self.data, "authentication", {})
        self.notification_types = ignore_case_get(self.filter, "notificationTypes", [])
        self.operation_types = ignore_case_get(self.filter, "operationTypes", [])
        self.operation_states = ignore_case_get(self.filter, "notificationStates", [])
        self.ns_component_types = ignore_case_get(self.filter, "nsComponentTypes", [])
        self.lcm_opname_impacting_nscomponent = ignore_case_get(
            self.filter,
            "lcmOpNameImpactingNsComponent",
            []
        )
        self.lcm_opoccstatus_impacting_nscomponent = ignore_case_get(
            self.filter,
            "lcmOpOccStatusImpactingNsComponent",
            []
        )
        self.ns_filter = ignore_case_get(
            self.filter,
            "nsInstanceSubscriptionFilter",
            {}
        )

    def check_callback_uri(self):
        logger.debug("SubscribeNotification-post::> Sending GET request to %s" % self.callback_uri)
        try:
            response = requests.get(self.callback_uri, timeout=2)
            if response.status_code != status.HTTP_204_NO_CONTENT:
                raise NSLCMException("callbackUri %s returns %s status code." % (
                    self.callback_uri,
                    response.status_code
                ))
        except Exception:
            raise NSLCMException("callbackUri %s didn't return 204 status code." % self.callback_uri)

    def do_biz(self):
        self.subscription_id = str(uuid.uuid4())
        # self.check_callback_uri()
        self.check_valid_auth_info()
        self.check_filter_types()
        self.check_valid()
        self.save_db()
        subscription = SubscriptionModel.objects.get(subscription_id=self.subscription_id)
        return subscription

    def check_filter_types(self):
        logger.debug("SubscribeNotification--post::> Validating operationTypes and operationStates if exists")
        occ_notification = NOTIFICATION_TYPE.NSLCM_OPERATION_OCCURRENCE_NOTIFICATION
        if self.operation_types and occ_notification not in self.notification_types:
            except_message = "If you are setting operationTypes, notificationTypes must be %s"
            raise NSLCMException(except_message % occ_notification)
        if self.operation_states and occ_notification not in self.notification_types:
            except_message = "If you are setting operationStates, notificationTypes must be %s"
            raise NSLCMException(except_message % occ_notification)

    def check_valid_auth_info(self):
        logger.debug("SubscribeNotification--post::> Validating Auth details if provided")
        auth_type = self.authentication.get("authType")
        params_basic = self.authentication.get("paramsBasic")
        params_oauth2 = self.authentication.get("paramsOauth2ClientCredentials")
        if params_basic and AUTH_TYPE.BASIC not in auth_type:
            raise NSLCMException('Auth type should be ' + AUTH_TYPE.BASIC)
        if params_oauth2 and AUTH_TYPE.OAUTH2_CLIENT_CREDENTIALS not in auth_type:
            raise NSLCMException('Auth type should be ' + AUTH_TYPE.OAUTH2_CLIENT_CREDENTIALS)

    def check_filter_exists(self, sub):
        # Check the notificationTypes, operationTypes, operationStates
        for filter_type in FILTER_TYPE:
            if not is_filter_type_equal(
                getattr(self, filter_type),
                ast.literal_eval(getattr(sub, filter_type))
            ):
                return False
        # If all the above types are same then check ns instance filters
        ns_filter = json.loads(sub.ns_instance_filter)
        for ns_filter_type in NS_FILTER_TYPE:
            if not is_filter_type_equal(
                self.ns_filter.get(ns_filter_type, []),
                ns_filter.get(ns_filter_type, [])
            ):
                return False
        return True

    def check_valid(self):
        logger.debug("SubscribeNotification--post::> Checking DB if callbackUri already exists")
        subscriptions = SubscriptionModel.objects.filter(callback_uri=self.callback_uri)
        if not subscriptions.exists():
            return True
        for subscription in subscriptions:
            if self.check_filter_exists(subscription):
                raise SeeOtherException("Already Subscription exists with the same callbackUri and filter")
        return False

    def save_db(self):
        logger.debug("SubscribeNotification--post::> Saving the subscription(%s) to the database" % self.subscription_id)
        links = {
            "self": {
                "href": const.SUBSCRIPTION_ROOT_URI % self.subscription_id
            }
        }
        SubscriptionModel.objects.create(
            subscription_id=self.subscription_id,
            callback_uri=self.callback_uri,
            auth_info=self.authentication,
            notification_types=json.dumps(self.notification_types),
            operation_types=json.dumps(self.operation_types),
            operation_states=json.dumps(self.operation_states),
            ns_instance_filter=json.dumps(self.ns_filter),
            ns_component_types=json.dumps(self.ns_component_types),
            lcm_opname_impacting_nscomponent=json.dumps(self.lcm_opname_impacting_nscomponent),
            lcm_opoccstatus_impacting_nscomponent=json.dumps(self.lcm_opoccstatus_impacting_nscomponent),
            links=json.dumps(links))
        logger.debug('Create Subscription[%s] success', self.subscription_id)
