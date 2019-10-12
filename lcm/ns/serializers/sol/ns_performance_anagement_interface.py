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


# PmSubscriptionRequest
from lcm.ns.enum import CROSSINGDIRECTION_Type, threshold_Type
from lcm.pub.utils.enumutil import enum_to_list


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


# PmSubscription
class PmSubscriptionSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier that identifies the subscription.",
                               required=True, allow_null=False)
    filter = PmNotificationsFilterSerializer(help_text="Filter settings for this subscription, to define the"
                                                       " subset of all notifications this subscription "
                                                       "relates to", required=False, allow_null=True)
    callbackUri = serializers.CharField(help_text="The URI of the endpoint to send the notification to.",
                                        required=True, allow_null=False)
    _links = serializers.CharField(help_text="Links to resources related to this resource.",
                                   required=True, allow_null=False)


#  ThresholdCrossedNotification
class CrossingDirectionTypeSerializer(serializers.Serializer):
    pass


class ThresholdCrossedNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this notification. If a notification is sent multiple"
                                         " times due to multiple subscriptions",
                               required=True, allow_null=False)
    notificationType = serializers.CharField(help_text="Discriminator for the different notification types.",
                                             required=True, allow_null=False)
    subscriptionId = serializers.CharField(help_text="Identifier of the subscription that this notification "
                                                     "relates to.", required=True, allow_null=False)
    timeStamp = serializers.CharField(help_text="Date and time of the generation of the notification.",
                                      required=True, allow_null=False)
    thresholdId = serializers.CharField(help_text="Identifier of the threshold which has been crossed.",
                                        required=True, allow_null=False)
    crossingDirection = serializers.ListField(help_text="An indication of whether the threshold was crossed "
                                                        "in upward or downward direction.",
                                              child=serializers.ChoiceField(
                                                  required=True,
                                                  choices=enum_to_list(CROSSINGDIRECTION_Type)),
                                              required=True, allow_null=False)
    objectInstanceId = serializers.CharField(help_text="Identifier that identifies a NS instance.",
                                             required=True, allow_null=False)
    performanceMetric = serializers.CharField(help_text="Performance metric associated with the "
                                                        "threshold", required=True, allow_null=False)
    performanceValue = serializers.CharField(help_text="Value of the metric that resulted in threshold "
                                                       "crossing.", required=True, allow_null=False)
    _links = serializers.CharField(help_text="Links to resources related to this notification",
                                   required=True, allow_null=False)


#  PerformanceInformationAvailableNotification
class PerformanceInformationAvailableNotification(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this notification.", required=True, allow_null=False)
    notificationType = serializers.CharField(help_text="Discriminator for the different notification types",
                                             required=True, allow_null=False)
    subscriptionId = serializers.CharField(help_text="Identifier of the subscription that this notification "
                                                     "relates to.", required=True, allow_null=False)
    timeStamp = serializers.DateField(help_text="Date and time of the generation of the notification.",
                                      required=True, allow_null=False)
    objectInstanceId = serializers.CharField(help_text="Identifier that identifies a NS instance.",
                                             required=True, allow_null=False)
    _links = serializers.CharField(help_text="Links to resources related to this notification",
                                   required=True, allow_null=False)


# CreatePmJobRequest
class PmJobCriteriaSerializer(serializers.Serializer):
    performanceMetric = serializers.CharField(help_text="This defines the types of performance metrics for"
                                                        " the specified object instances",
                                              required=False, allow_null=True, many=True)
    performanceMetricGroup = serializers.CharField(help_text="Group of performance metrics.",
                                                   required=False, allow_null=True, many=True)
    collectionPeriod = serializers.CharField(help_text="Specifies the periodicity at which the producer "
                                                       "will collect performance information",
                                             required=True, allow_null=False)
    reportingPeriod = serializers.CharField(help_text="Specifies the periodicity at which the producer "
                                                      "will report to the consumer",
                                            required=True, allow_null=False)
    reportingBoundary = serializers.DateField(help_text="Identifies a time boundary after which the "
                                                        "reporting will stop",
                                              required=False, allow_null=True)


class CreatePmJobRequestSerializer(serializers.Serializer):
    objectInstanceIds = serializers.CharField(help_text="Identifiers of the NS instances for which"
                                                        " performance information is requested to be"
                                                        " collected.",
                                              required=True, allow_null=False, many=True)
    criteria = PmJobCriteriaSerializer(help_text="Criteria of the collection of performance information.",
                                       required=True, allow_null=False)


# PmJob
class PmJobSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this PM job.", required=True, allow_null=False)
    objectInstanceIds = serializers.CharField(help_text="Identifiers of the NS instances for which "
                                                        "performance information is collected.",
                                              required=True, allow_null=False, many=True)
    criteria = PmJobCriteriaSerializer(help_text="Criteria of the collection of performance "
                                                 "information.", required=True)
    reports = serializers.CharField(help_text="Information about available reports collected by this PM job",
                                    required=False, allow_null=True, many=True)
    _links = serializers.CharField(help_text="Links for this resource.", required=False, allow_null=True)


# CreateThresholdRequest
class ThresholdCriteriaSerializer(serializers.Serializer):
    performanceMetric = serializers.CharField(help_text="Defines the performance metric associated with the "
                                                        "threshold", required=True, allow_null=False)
    thresholdType = serializers.ListField(help_text="Type of threshold.",
                                          child=serializers.ChoiceField(
                                              required=True, choices=enum_to_list(threshold_Type)),
                                          required=True, allow_null=False)


class CreateThresholdRequestSerializer(serializers.Serializer):
    objectInstanceId = serializers.CharField(help_text="Identifier of the NS instance associated with this "
                                                       "threshold", required=True, allow_null=False)
    criteria = ThresholdCriteriaSerializer(help_text="Criteria that define this threshold.",
                                           required=True, allow_null=False)


# Threshold
class ThresholdSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this threshold resource.",
                               required=True, allow_null=False)
    objectInstanceId = serializers.CharField(help_text="Identifier of the NS instance associated with the "
                                                       "threshold.", required=True, allow_null=False)
    criteria = serializers.CharField(help_text="Criteria that define this threshold.",
                                     required=True, allow_null=False)
    _links = serializers.CharField(help_text="Links for this resource.", required=True, allow_null=False)


# PerformanceReport
class PerformanceReportSerializer(serializers.Serializer):
    entries = serializers.CharField(help_text="List of performance information entries.",
                                    required=True, allow_null=False, many=True)
