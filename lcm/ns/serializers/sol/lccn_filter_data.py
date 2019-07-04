# Copyright (c) 2019, CMCC Technologies Co., Ltd.
# Copyright 2019 ZTE Corporation.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework import serializers

from .ns_instance_subscription_filter import NsInstanceSubscriptionFilter
from lcm.ns.enum import NOTIFICATION_TYPE, OPERATION_TYPE, OPERATION_STATE_TYPE, NS_COMPOMENT_TYPE, OPNAME_FOR_CHANGE_NOTIFICATION_TYPE, OPOCC_STATUS_FOR_CHANGENOTIFICATION_TYPE
from lcm.pub.utils.enumutil import enum_to_list


class LifeCycleChangeNotificationsFilter(serializers.Serializer):
    nsInstanceSubscriptionFilter = NsInstanceSubscriptionFilter(
        help_text="Filter criteria to select NS instances about which to notify.",
        required=False,
        allow_null=False)
    notificationTypes = serializers.ListField(
        help_text="Match particular notification types.",
        child=serializers.ChoiceField(required=True, choices=enum_to_list(NOTIFICATION_TYPE)),
        required=False,
        allow_null=False)
    operationTypes = serializers.ListField(
        help_text="Match particular NS lifecycle operation types for the notification of type NsLcmOperationOccurrenceNotification.",
        child=serializers.ChoiceField(required=True, choices=enum_to_list(OPERATION_TYPE)),
        required=False,
        allow_null=False)
    operationStates = serializers.ListField(
        help_text="Match particular LCM operation state values as reported in notifications of type NsLcmOperationOccurrenceNotification.",
        child=serializers.ChoiceField(required=True, choices=enum_to_list(OPERATION_STATE_TYPE)),
        required=False,
        allow_null=False)
    nsComponentTypes = serializers.ListField(
        help_text="Match particular NS component types for the notification of type NsChangeNotification. ",
        child=serializers.ChoiceField(required=True, choices=enum_to_list(NS_COMPOMENT_TYPE)),
        required=False,
        allow_null=False)
    lcmOpNameImpactingNsComponent = serializers.ListField(
        help_text="Match particular LCM operation names for the notification of type NsChangeNotification.",
        child=serializers.ChoiceField(required=True, choices=enum_to_list(OPNAME_FOR_CHANGE_NOTIFICATION_TYPE)),
        required=False,
        allow_null=False)
    lcmOpOccStatusImpactingNsComponent = serializers.ListField(
        help_text="Match particular LCM operation status values as reported in notifications of type NsChangeNotification.",
        child=serializers.ChoiceField(required=True, choices=enum_to_list(OPOCC_STATUS_FOR_CHANGENOTIFICATION_TYPE)),
        required=False,
        allow_null=False)
