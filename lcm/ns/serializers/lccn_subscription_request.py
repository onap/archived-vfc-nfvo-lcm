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

from lccn_filter_data import LifeCycleChangeNotificationsFilter
from subscription_auth_data import SubscriptionAuthenticationSerializer


class LccnSubscriptionRequestSerializer(serializers.Serializer):
    callbackUri = serializers.CharField(
        help_text="The URI of the endpoint to send the notification to.",
        required=True,
        allow_null=False)
    filter = LifeCycleChangeNotificationsFilter(
        help_text="Filter settings for this subscription, to define the subset of all notifications this "
                  "subscription relates to A particular notification is sent to the subscriber if the filter "
                  "matches, or if there is no filter.", required=False, allow_null=True)
    authentication = SubscriptionAuthenticationSerializer(
        help_text="Authentication parameters to conFigure the use of Authorization when sending "
                  "notifications corresponding to this subscription, as defined in clause 4.5.3 This "
                  "attribute shall only be present if the subscriber requires authorization of "
                  "notifications.", required=False, allow_null=True)
