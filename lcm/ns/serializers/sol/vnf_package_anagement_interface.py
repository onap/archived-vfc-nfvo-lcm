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

from lcm.ns.enum import PACKAGE_USAGE_STATE_TYPE, PACKAGE_ONBOARDING_STATE_TYPE, \
    PACKAGE_OPERATIONAL_STATE_TYPE, CONTAINER_FORMAT, DISK_FORMAT, NOTIFICATION_TYPES, AUTH_TYPE, \
    PACKAGE_CHANGE_TYPE
from lcm.pub.utils.enumutil import enum_to_list


class CreateVnfPkgInfoRequestSerializer(serializers.Serializer):
    userDefinedData = serializers.DictField(help_text="User defined data for the VNF package.",
                                            required=False, allow_null=True)


class VnfPkgInfoModifications(serializers.Serializer):
    operationalState = serializers.ListField(help_text="New value of the operational state of the on-boarded "
                                                       "instance of the VNF package",
                                             child=serializers.ChoiceField(
                                                 choices=enum_to_list(PACKAGE_OPERATIONAL_STATE_TYPE)),
                                             required=False, allow_null=True, many=True,)
    userDefinedData = serializers.DictField(help_text="User defined data to be updated.",
                                            required=False, allow_null=True)


# UploadVnfPackageFromUriRequest
class UploadVnfPackageFromUriRequestSerializer(serializers.Serializer):
    addressInformation = serializers.CharField(help_text="Address information of the VNF package content. The"
                                                         " NFVO can use this address to obtain the VNF"
                                                         " package.", required=True, allow_null=False)
    userName = serializers.CharField(help_text="User name to be used for authentication.",
                                     required=False, allow_null=True)
    password = serializers.CharField(help_text="Password to be used for authentication.",
                                     required=False, allow_null=True)


# VnfPkgInfo
class VnfPackageSoftwareImageInfoSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of the software image.", required=True, allow_null=False)
    name = serializers.CharField(help_text="Name of the software image.", required=True, allow_null=False)
    provider = serializers.CharField(help_text="Provider of the software image.",
                                     required=True, allow_null=False)
    version = serializers.CharField(help_text="Version of the software image.",
                                    required=True, allow_null=False)
    checksum = serializers.CharField(help_text="Checksum of the software image file.",
                                     required=True, allow_null=False)
    containerFormat = serializers.ListField(help_text="Container format indicates whether the software image"
                                                      " is in a file format that also contains metadata"
                                                      " about the actual software.",
                                            child=serializers.ChoiceField(
                                                choices=enum_to_list(CONTAINER_FORMAT)),
                                            required=True, allow_null=False)
    diskFormat = serializers.ListField(help_text="Disk format of a software image is the format of the "
                                                 "underlying disk image",
                                       child=serializers.ChoiceField(
                                                 choices=enum_to_list(DISK_FORMAT)),
                                       required=True, allow_null=False)
    createdAt = serializers.DateField(help_text="Time when this software image was created.",
                                      required=True, allow_null=False)
    minDisk = serializers.CharField(help_text="The minimal disk for this software image in bytes.",
                                    required=True, allow_null=False)
    minRam = serializers.CharField(help_text="The minimal RAM for this software image in bytes.",
                                   required=True, allow_null=False)
    size = serializers.CharField(help_text="Size of this software image in bytes.",
                                 required=True, allow_null=False)
    userMetadata = serializers.DictField(help_text="User-defined data.", required=False, allow_null=True)
    imagePath = serializers.CharField(help_text="Path in the VNF package, which identifies the image "
                                                "artifact and also allows to access a copy of the image "
                                                "artifact.", required=True, allow_null=False)


class VnfPackageArtifactInfoSerializer(serializers.Serializer):
    artifactPath = serializers.CharField(help_text="Path in the VNF package, which identifies the artifact "
                                                   "and also allows to access a copy of the artifact.",
                                         required=True, allow_null=False)
    checksum = serializers.CharField(help_text="Checksum of the artifact file",
                                     required=True, allow_null=False)

    metadata = serializers.DictField(help_text="The metadata of the artifact that are available in the VNF "
                                               "package, such as Content type, size, creation date, etc.",
                                     required=False, allow_null=True)


class VnfPkgInfoSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of the VNF package.", required=True, allow_null=False)
    vnfdId = serializers.CharField(help_text="This identifier, which is managed by the VNF provider",
                                   required=False, allow_null=True)
    vnfProvider = serializers.CharField(help_text="Provider of the VNF package and the VNFD.",
                                        required=False, allow_null=True)
    vnfProductName = serializers.CharField(help_text="Name to identify the VNF product.",
                                           required=False, allow_null=True)
    vnfSoftwareVersion = serializers.CharField(help_text="Software version of the VNF.",
                                               required=False, allow_null=True)
    vnfdVersion = serializers.CharField(help_text="The version of the VNFD.", required=False, allow_null=True)
    checksum = serializers.CharField(help_text="Checksum of the on-boarded VNF package.",
                                     required=False, allow_null=True)
    softwareImages = VnfPackageSoftwareImageInfoSerializer(help_text="Information about VNF package artifacts"
                                                                     " that are software images",
                                                           required=False, allow_null=True, many=True)
    additionalArtifacts = VnfPackageArtifactInfoSerializer(help_text="Information about VNF package artifacts"
                                                                     " contained in the VNF package that are"
                                                                     " not software images.",
                                                           required=False, allow_null=True, many=True)
    onboardingState = serializers.ListField(help_text="On-boarding state of the VNF package",
                                            child=serializers.ChoiceField(
                                                choices=enum_to_list(PACKAGE_ONBOARDING_STATE_TYPE)),
                                            required=True, allow_null=False)
    operationalState = serializers.ListField(help_text="Operational state of the VNF package",
                                             child=serializers.ChoiceField(
                                                 choices=enum_to_list(PACKAGE_OPERATIONAL_STATE_TYPE)),
                                             required=True, allow_null=False)
    usageState = serializers.ListField(help_text="Usage state of the VNF package.",
                                       child=serializers.ChoiceField(
                                                 choices=enum_to_list(PACKAGE_USAGE_STATE_TYPE)),
                                       required=True, allow_null=False)
    _links = serializers.CharField(help_text="Links to resources related to this resource.",
                                   required=True, allow_null=False)


#  PkgmSubscriptionRequest
class PkgmNotificationsFilterSerializer(serializers.Serializer):
    notificationTypes = serializers.ListField(help_text="Match particular notification types",
                                              child=serializers.ChoiceField(
                                                  choices=enum_to_list(NOTIFICATION_TYPES)),
                                              required=True, allow_null=False)
    vnfProductsFromProviders = serializers.ListField(help_text="If present, match VNF packages that contain"
                                                               " VNF products from certain providers.",
                                                     required=False, allow_null=True, many=True)
    vnfdId = serializers.ListField(help_text="Match VNF packages with a VNFD identifier listed in the"
                                             " attribute", required=False, allow_null=True, many=True)
    vnfPkgId = serializers.ListField(help_text="Match VNF packages with a package identifier listed in "
                                               "the attribute.", required=False, allow_null=True, many=True)
    operationalState = serializers.ListField(help_text="Match particular operational state of the on"
                                                       "boarded VNF package.",
                                             child=serializers.ChoiceField(
                                                 choices=enum_to_list(PACKAGE_OPERATIONAL_STATE_TYPE)),
                                             required=True, allow_null=False)
    usageState = serializers.ListField(help_text="Match particular usage state of the on-boarded "
                                                 "VNF package.",
                                       child=serializers.ChoiceField(
                                                 choices=enum_to_list(PACKAGE_USAGE_STATE_TYPE)),
                                       required=True, allow_null=False)


class SubscriptionAuthenticationSerializer(serializers.Serializer):
    authType = serializers.ListField(help_text="Defines the types of Authentication "
                                               "Authorization the API consumer is willing to "
                                               "accept when receiving a notification.",
                                     child=serializers.ChoiceField(
                                         choices=enum_to_list(AUTH_TYPE)),
                                     required=True, allow_null=False)
    paramsBasic = serializers.CharField(help_text="Parameters for authentication/authorization using BASIC",
                                        required=False, allow_null=True)
    paramsOauth2ClientCredentials = serializers.CharField(help_text="Parameters for authentication/"
                                                                    "authorization using "
                                                                    "OAUTH2_CLIENT_CREDENTIALS",
                                                          required=False, allow_null=True)


class PkgmSubscriptionRequestSerializer(serializers.Serializer):
    filter = PkgmNotificationsFilterSerializer(help_text="Filter settings for this subscription, to define"
                                                         " the subset of all notifications this subscription"
                                                         " relates to", required=False, allow_null=True)
    callbackUri = serializers.CharField(help_text="The URI of the endpoint to send the notification to.",
                                        required=True, allow_null=False)
    authentication = SubscriptionAuthenticationSerializer(
        help_text="Authentication parameters to conFigure the use of authorization when sending"
                  " notifications corresponding to this subscription", required=False, allow_null=True)


# PkgmSubscription
class PkgmSubscriptionSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this subscription resource.",
                               required=True, allow_null=False)
    filter = PkgmNotificationsFilterSerializer(help_text="Filter settings for this subscription, to define"
                                                         " the subset of all notifications this"
                                                         " subscription relates to.",
                                               required=False, allow_null=True)
    callbackUri = serializers.CharField(help_text="The URI of the endpoint to send the notification to.",
                                        required=True, allow_null=False)
    _links = serializers.CharField(help_text="Links to resources related to this resource.",
                                   required=True, allow_null=False)


# VnfPackageChangeNotification
class VnfPackageChangeNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this notification",
                               required=True, allow_null=False)
    notificationType = serializers.CharField(help_text="Discriminator for the different notification types.",
                                             required=True, allow_null=False)
    subscriptionId = serializers.CharField(help_text="Identifier of the subscription that this notification"
                                                     " relates to.",
                                           required=False, allow_null=True)
    timeStamp = serializers.DateField(help_text="Date-time of the generation of the notification",
                                      required=True, allow_null=False)
    vnfPkgId = serializers.CharField(help_text="Identifier of the VNF package",
                                     required=True, allow_null=False)
    vnfdId = serializers.CharField(help_text="Identifier of the VNFD contained in the VNF package",
                                   required=True, allow_null=False)
    changeType = serializers.ListField(help_text="The type of change of the VNF package.",
                                       child=serializers.ChoiceField(
                                           choices=enum_to_list(PACKAGE_CHANGE_TYPE)),
                                       required=True, allow_null=False)
    operationalState = serializers.ListField(help_text="New operational state of the VNF package.",
                                             child=serializers.ChoiceField(
                                                 choices=enum_to_list(PACKAGE_OPERATIONAL_STATE_TYPE)),
                                             required=False, allow_null=True)
    _links = serializers.CharField(help_text="Links to resources related to this notification.",
                                   required=True, allow_null=False)


# PkgmLinks
class PkgmLinksSerializer(serializers.Serializer):
    vnfPackage = serializers.CharField(help_text="Link to the resource representing the VNF package to "
                                                 "which the notified change applies,",
                                       required=True, allow_null=False)
    subscription = serializers.CharField(help_text="Link to the related subscription.",
                                         required=True, allow_null=False)


# Checksum
class ChecksumSerializer(serializers.Serializer):
    algorithm = serializers.CharField(help_text="Name of the algorithm used to generate the checksum",
                                      required=True, allow_null=False)
    hash = serializers.CharField(help_text="The hexadecimal value of the checksum.",
                                 required=True, allow_null=False)
