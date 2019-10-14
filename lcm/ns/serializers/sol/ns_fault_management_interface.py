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

from lcm.ns.enum import NOTIFICATION_TYPES, EVENT_TYPE, PERCEIVED_SEVERITY_TYPE, FAULTY_RESOURCE_TYPE, \
    ACK_STATE
from lcm.ns.serializers.sol.ns_performance_anagement_interface import NsInstanceSubscriptionFilterSerializer, \
    SubscriptionAuthenticationSerializer
from lcm.pub.utils.enumutil import enum_to_list


# FmSubscriptionRequest
class FmNotificationsFilterSerializer(serializers.Serializer):
    nsInstanceSubscriptionFilter = NsInstanceSubscriptionFilterSerializer(
        help_text="Filter criteria to select NS instances about which to notify.",
        required=False, allow_null=True)
    notificationTypes = serializers.ListField(help_text="Match particular notification types",
                                              child=serializers.ChoiceField(
                                                  required=False,
                                                  choices=enum_to_list(NOTIFICATION_TYPES)),
                                              required=False, allow_null=True, many=True)
    faultyResourceTypes = serializers.ListField(help_text="Match alarms related to NSs with a faulty "
                                                          "resource type listed in this attribute",
                                                child=serializers.ChoiceField(
                                                    choices=enum_to_list(FAULTY_RESOURCE_TYPE)),
                                                required=False, allow_null=True, many=True,)
    perceivedSeverities = serializers.ListField(help_text="Match alarms related to NSs with a perceived "
                                                          "severity listed in this attribute.",
                                                child=serializers.ChoiceField(
                                                    choices=enum_to_list(PERCEIVED_SEVERITY_TYPE)),
                                                required=False, allow_null=True, many=True,)
    eventTypes = serializers.ListField(help_text="Match alarms releted to NSs with an event type listed in"
                                                 "this attribute.",
                                       child=serializers.ChoiceField(choices=enum_to_list(EVENT_TYPE)),
                                       required=False, allow_null=True, many=True,)
    probableCauses = serializers.CharField(help_text="Match alarms related to NSs with a probable cause "
                                                     "listed in this attribute",
                                           required=False, allow_null=True, many=True)


class FmSubscriptionRequestSerializer(serializers.Serializer):
    filter = FmNotificationsFilterSerializer(help_text="Filter settings for this subscription, to define the"
                                                       " subset of all notifications this subscription"
                                                       " relates to", required=False, allow_null=True)
    callbackUri = serializers.CharField(help_text="The URI of the endpoint to send the notification to.",
                                        required=True, allow_null=False)
    authentication = SubscriptionAuthenticationSerializer(
        help_text="Authentication parameters to conFigure the use of Authorization when sendingnotifications"
                  " corresponding to this subscription", required=False, allow_null=True)


# FmSubscription
class FmSubscriptionSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this subscription resource",
                               required=True, allow_null=False)
    filter = FmNotificationsFilterSerializer(help_text="Filter settings for this subscription, to define"
                                                       " the subset of all notifications this subscription"
                                                       " relates to.",
                                             required=False, allow_null=True)
    callbackUri = serializers.CharField(help_text="The URI of the endpoint to send the notification to.",
                                        required=False, allow_null=True)
    _links = serializers.CharField(help_text="Links for this resource.", required=True, allow_null=False)


#  Alarm
class FaultyComponentInfoSerializer(serializers.Serializer):
    faultyNestedNsInstanceId = serializers.CharField(help_text="Identifier of the faulty nested NS instance",
                                                     required=False, allow_null=True)
    faultyNsVirtualLinkInstanceId = serializers.CharField(help_text="Identifier of the faulty NS "
                                                                    "virtual link instance.",
                                                          required=True, allow_null=False)
    faultyVnfInstanceId = serializers.CharField(help_text="Identifier of the faulty VNF instance",
                                                required=True, allow_null=False)


class ResourceHandleSerualizer(serializers.Serializer):
    vimId = serializers.CharField(help_text="Identifier of the VIM under whose control this resource is "
                                            "placed.", required=False, allow_null=True)
    resourceProviderId = serializers.CharField(help_text="Identifier of the entity responsible for the "
                                                         "management of the resource.",
                                               required=False, allow_null=True)
    resourceId = serializers.CharField(help_text="Identifier of the resource in the scope of the VIM or the "
                                                 "resource provider", required=True, allow_null=False)
    vimLevelResourceType = serializers.CharField(help_text="Type of the resource in the scope of the VIM or"
                                                           " the resource provider.",
                                                 required=False, allow_null=True)


class FaultyResourceInfoSerialzier(serializers.Serializer):
    faultyResource = ResourceHandleSerualizer(help_text="Information that identifies the faulty resource "
                                                        "instance and its managing entity",
                                              required=True, allow_null=False)
    faultyResourceType = serializers.ListField(help_text="Type of the faulty resource.",
                                               child=serializers.ChoiceField(
                                                   choices=enum_to_list(FAULTY_RESOURCE_TYPE)),
                                               required=True, allow_null=False,)


class AlarmSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this Alarm information element.",
                               required=True, allow_null=False)
    managedObjectId = serializers.CharField(help_text="Identifier of the affected NS instance.",
                                            required=True, allow_null=False)
    rootCauseFaultyComponent = FaultyComponentInfoSerializer(
        help_text="The NS components that are causing the NS fault.", required=False, allow_null=True)
    rootCauseFaultyResource = FaultyResourceInfoSerialzier(help_text="The virtualised resources that are"
                                                                     " causing the NS fault.",
                                                           required=False, allow_null=True)
    alarmRaisedTime = serializers.DateField(help_text="Time stamp indicating when the alarm is raised by "
                                                      "the managed object", required=True, allow_null=False)
    alarmChangedTime = serializers.DateField(help_text="Time stamp indicating when the alarm was last"
                                                       " changed.", required=False, allow_null=True)
    alarmClearedTime = serializers.DateField(help_text="Time stamp indicating when the alarm was cleared.",
                                             required=False, allow_null=True)
    ackState = serializers.ListField(help_text="Acknowledgement state of the alarm.",
                                     child=serializers.ChoiceField(choices=enum_to_list(ACK_STATE)),
                                     required=True, allow_null=False)
    perceivedSeverity = serializers.ListField(help_text="Perceived severity of the managed object failure.",
                                              child=serializers.ChoiceField(
                                                  choices=enum_to_list(PERCEIVED_SEVERITY_TYPE)),
                                              required=True, allow_null=False)
    eventTime = serializers.DateField(help_text="Time stamp indicating when the fault was observed.",
                                      required=True, allow_null=False)
    eventType = serializers.ListField(help_text="Type of event",
                                                child=serializers.ChoiceField(
                                                    choices=enum_to_list(EVENT_TYPE)),
                                                required=True, allow_null=False)
    faultType = serializers.CharField(help_text="Additional information to clarify the type of the fault.",
                                      required=False, allow_null=True)
    probableCause = serializers.CharField(help_text="Information about the probable cause of the fault.",
                                          required=True, allow_null=False)


#  AlarmNotification
class AlarmNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this notification.", required=True, allow_null=False)
    notificationType = serializers.CharField(help_text="Discriminator for the different notification types.",
                                             required=True, allow_null=False)
    subscriptionId = serializers.CharField(help_text="Identifier of the subscription that this notification"
                                                     " relates to.", required=True, allow_null=False)
    timeStamp = serializers.DateField(help_text="Date-time of the generation of the notification.",
                                      required=True, allow_null=False)
    alarm = AlarmSerializer(help_text="Information about an alarm including AlarmId, affected NS identifier,"
                                      " and FaultDetails.", required=True, allow_null=False)
    _links = serializers.CharField(help_text="Links to resources related to this notification.",
                                   required=True, allow_null=False)


# AlarmClearedNotification
class AlarmClearedNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this notification.",
                               required=True, allow_null=False)
    notificationType = serializers.CharField(help_text="Discriminator for the different notification "
                                                       "types.", required=True, allow_null=False)
    subscriptionId = serializers.CharField(help_text="Identifier of the subscription that this"
                                                     " notification relates to.",
                                           required=True, allow_null=False)
    timeStamp = serializers.DateField(help_text="Date-time of the generation of the notification.",
                                      required=True, allow_null=False)
    alarmId = serializers.CharField(help_text="Alarm identifier.", required=True, allow_null=False)
    alarmClearedTime = serializers.DateField(help_text="The time stamp indicating when the alarm was"
                                                       " cleared.", required=True, allow_null=False)
    _links = serializers.CharField(help_text="Links to resources related to this notification.",
                                   required=True, allow_null=False)


# AlarmListRebuiltNotification
class AlarmListRebuiltNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this notification.",
                               required=True, allow_null=False)
    notificationType = serializers.CharField(help_text="Discriminator for the different notification types.",
                                             required=True, allow_null=False)
    subscriptionId = serializers.CharField(help_text="Identifier of the subscription that this notification"
                                                     " relates to.",
                                           required=True, allow_null=False)
    timeStamp = serializers.DateField(help_text="Date-time of the generation of the notification.",
                                      required=True, allow_null=False)
    _links = serializers.CharField(help_text="Links to resources related to this notification.",
                                   required=True, allow_null=False)


# AlarmModifications
class AlarmModificationsSerializer(serializers.Serializer):
    ackState = serializers.ListField(help_text="New value of the ackState attribute in Alarm",
                                     child=serializers.ChoiceField(choices=enum_to_list(ACK_STATE)),
                                     required=True, allow_null=False)
