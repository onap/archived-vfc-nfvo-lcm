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


class NsInstanceSubscriptionFilterSerializer(serializers.Serializer):
    nsdIds = serializers.CharField(help_text="If present, match NS instances that were created based on a"
                                             " NSD identified by one of the nsdId values listed in this"
                                             " attribute.", required=False, allow_null=True, many=True)
    vnfdIds = serializers.CharField(help_text="If present, match NS instances that contain VNF instances that"
                                              " were created based on a VNFD identified by one of the vnfdId "
                                              "values listed in this attribute.", required=False,
                                    allow_null=True, many=True)
    pnfdIds = serializers.CharField(help_text="If present, match NS instances that contain PNFs that are "
                                              "represented by a PNFD identified by one of the pnfdId values "
                                              "listed in this attribute", required=False,
                                    allow_null=True, many=True)
    nsInstanceIds = serializers.CharField(help_text="If present, match NS instances with an instance "
                                                    "identifier listed in this attribute.",
                                          required=False, allow_null=True, many=True)
    nsInstanceNames = serializers.CharField(help_text="If present, match NS instances with a NS Instance Name"
                                                      " listed in this attribute",
                                            required=False, allow_null=True, many=True)


class PmNotificationsFilterSerializer(serializers.Serializer):
    nsInstanceSubscriptionFilter = NsInstanceSubscriptionFilterSerializer(help_text="Filter criteria to"
                                                                                    " select NS instances "
                                                                                    "about which to notify",
                                                                          required=False, allow_null=True,
                                                                          allow_blank=True)
    notificationTypes = serializers.ChoiceField(help_text="Match particular notification types.",
                                                choices=["ThresholdCrossedNotification",
                                                         "PerformanceInformationAvailableNotification"],
                                                required=False, allow_null=True, many=True)


class SubscriptionAuthenticationSerializer(serializers.Serializer):
    authType = serializers.ChoiceField(help_text="Defines the types of Authentication Authorization the API"
                                                 " consumer is willing to accept when receiving a"
                                                 " notification.", choices=["BASIC",
                                                                            "OAUTH2_CLIENT_CREDENTIALS",
                                                                            "TLS_CERT"], required=True,
                                       allow_null=False, many=True)
    paramsBasic = serializers.CharField(help_text="Parameters for authentication authorization using BASIC",
                                        required=False, allow_null=True, allow_blank=True)
    paramsOauth2ClientCredentials = serializers.CharField(help_text="Parameters for authentication "
                                                                    "authorization using OAUTH2"
                                                                    "_CLIENT_CREDENTIALS.",
                                                          required=False, allow_null=True, allow_blank=True)


class PmSubscriptionRequestSerializer(serializers.Serializer):
    filter = PmNotificationsFilterSerializer(help_text="Filter settings for this subscription, to define the "
                                                       "subset of all notifications this subscription"
                                                       " relates to", required=False, allow_null=True,
                                             allow_blank=True)
    callbackUri = serializers.CharField(help_text="The URI of the endpoint to send the notification to",
                                        required=True, allow_null=False, allow_blank=False)
    authentication = SubscriptionAuthenticationSerializer(help_text="Authentication parameters to conFigure"
                                                                    " the use of Authorization when sending"
                                                                    " notifications corresponding to "
                                                                    "this subscription",
                                                          required=False, allow_null=True, allow_blank=True)
