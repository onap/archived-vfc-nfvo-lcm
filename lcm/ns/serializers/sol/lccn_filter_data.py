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

from ns_instance_subscription_filter import NsInstanceSubscriptionFilter
from lcm.ns.const import NOTIFICATION_TYPES, NS_LCM_OP_TYPES, LCM_OPERATION_STATE_TYPES, NS_COMPOMENT_TYPE,\
    LCM_OPName_For_Change_Notification_Type, LCM_OpOcc_Status_For_ChangeNotification_Type


class LifeCycleChangeNotificationsFilter(serializers.Serializer):
    nsInstanceSubscriptionFilter = NsInstanceSubscriptionFilter(
        help_text="Filter criteria to select NS instances about which to notify.",
        required=False,
        allow_null=False)
    notificationTypes = serializers.ListField(
        help_text="Match particular notification types.",
        child=serializers.ChoiceField(required=True, choices=NOTIFICATION_TYPES),
        required=False,
        allow_null=False)
    operationTypes = serializers.ListField(
        help_text="Match particular NS lifecycle operation types for the notification of type NsLcmOperationOccurrenceNotification.",
        child=serializers.ChoiceField(required=True, choices=NS_LCM_OP_TYPES),
        required=False,
        allow_null=False)
    operationStates = serializers.ListField(
        help_text="Match particular LCM operation state values as reported in notifications of type NsLcmOperationOccurrenceNotification.",
        child=serializers.ChoiceField(required=True, choices=LCM_OPERATION_STATE_TYPES),
        required=False,
        allow_null=False)
    nsComponentTypes = serializers.ListField(
        help_text="Match particular NS component types for the notification of type NsChangeNotification. ",
        child=serializers.ChoiceField(required=True, choices=NS_COMPOMENT_TYPE),
        required=False,
        allow_null=False)
    lcmOpNameImpactingNsComponent = serializers.ListField(
        help_text="Match particular LCM operation names for the notification of type NsChangeNotification.",
        child=serializers.ChoiceField(required=True, choices=LCM_OPName_For_Change_Notification_Type),
        required=False,
        allow_null=False)
    lcmOpOccStatusImpactingNsComponent = serializers.ListField(
        help_text="Match particular LCM operation status values as reported in notifications of type NsChangeNotification.",
        child=serializers.ChoiceField(required=True, choices=LCM_OpOcc_Status_For_ChangeNotification_Type),
        required=False,
        allow_null=False)
