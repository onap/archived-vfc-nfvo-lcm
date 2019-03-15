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

from rest_framework import serializers

from link import LinkSerializer
from lccn_filter_data import LifeCycleChangeNotificationsFilter


class Link_Serializer(serializers.Serializer):
    self = LinkSerializer(
        help_text="URI of this resource.",
        required=True,
        allow_null=False)


class LccnSubscriptionSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this subscription resource.",
        max_length=255,
        required=True,
        allow_null=False)
    callbackUri = serializers.CharField(
        help_text="The URI of the endpoint to send the notification to.",
        max_length=255,
        required=True,
        allow_null=False)
    filter = LifeCycleChangeNotificationsFilter(
        help_text="Filter settings for this subscription, to define the of all notifications this "
                  "subscription relates to A particular notification is sent to the subscriber if the filter"
                  " matches, or if there is no filter.", required=False)
    _links = LinkSerializer(
        help_text="Links to resources related to this resource.", required=True)
