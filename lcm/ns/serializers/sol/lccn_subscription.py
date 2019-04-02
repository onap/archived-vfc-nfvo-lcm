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

from lcm.ns.serializers.sol.lccn_filter_data import LifeCycleChangeNotificationsFilter
from lcm.ns.serializers.sol.pub_serializers import LinkSerializer


class LccnSubscriptionLinkSerializer(serializers.Serializer):
    self = LinkSerializer(
        help_text="URI of this resource.",
        required=True,
        allow_null=False)


class LccnSubscriptionSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this subscription resource.",
        required=True,
        allow_null=False)
    filter = LifeCycleChangeNotificationsFilter(
        help_text="Filter settings for this subscription, to define the of all notifications this subscription relates to.",
        required=False)
    callbackUri = serializers.CharField(
        help_text="The URI of the endpoint to send the notification to.",
        required=True,
        allow_null=False)
    _links = LccnSubscriptionLinkSerializer(
        help_text="Links to resources related to this resource.",
        required=True)


class LccnSubscriptionsSerializer(serializers.ListSerializer):
    child = LccnSubscriptionSerializer()
