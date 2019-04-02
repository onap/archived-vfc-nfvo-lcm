# Copyright (c) 2018, CMCC Technologies Co., Ltd.
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

from lcm.ns.serializers.sol.pub_serializers import AffinityOrAntiAffinityRuleSerializer
from lcm.ns.serializers.sol.update_serializers import AddPnfDataSerializer, VnfInstanceDataSerializer, SapDataSerializer


class civicAddressElementSerializer(serializers.Serializer):
    caType = serializers.CharField(
        help_text="Describe the content type of caValue.",
        required=True)
    caValue = serializers.CharField(
        help_text="Content of civic address element corresponding to the caType.",
        required=True)


class LocationConstraintsSerializer(serializers.Serializer):
    countryCode = serializers.CharField(
        help_text="The two-letter ISO 3166 [29] country code in capital letters.",
        required=True)
    civicAddressElement = civicAddressElementSerializer(
        help_text="Zero or more elements comprising the civic address.",
        required=False,
        many=True)


class VnfLocationConstraintSerializer(serializers.Serializer):
    vnfProfileId = serializers.CharField(
        help_text="Identifier (reference to) of a VnfProfile in the NSD used to manage the lifecycle of the VNF instance.",
        required=True)
    locationConstraints = LocationConstraintsSerializer(
        help_text="Defines the location constraints for the VNF instance to be created based on the VNF profile.",
        required=True)


class ParamsForVnfSerializer(serializers.Serializer):
    vnfProfileId = serializers.CharField(
        help_text="Identifier of (reference to) a vnfProfile to which the additional parameters apply.",
        required=True)
    additionalParams = serializers.DictField(
        help_text="Additional parameters that are applied for the VNF instance to be created.",
        required=False)


class NestedNsInstanceDataSerializer(serializers.Serializer):
    nestedNsInstanceId = serializers.CharField(
        help_text="Identifier of the existing nested NS instance to be used in the NS.",
        required=True)
    nsProfileId = serializers.CharField(
        help_text="Identifier of an NsProfile defined in the NSD which the existing nested NS instance shall be matched with.",
        required=True)


class InstantNsReqSerializer(serializers.Serializer):
    nsFlavourId = serializers.CharField(
        help_text="Identifier of the NS deployment flavour to be instantiated.",
        required=True)
    sapData = SapDataSerializer(
        help_text="Create data concerning the SAPs of this NS",
        required=False,
        many=True)
    addpnfData = AddPnfDataSerializer(
        help_text="Information on the PNF(s) that are part of this NS.",
        required=False,
        many=True)
    vnfInstanceData = VnfInstanceDataSerializer(
        help_text="Specify an existing VNF instance to be used in the NS.",
        required=False,
        many=True)
    nestedNsInstanceData = NestedNsInstanceDataSerializer(
        help_text="Specify an existing NS instance to be used as a nested NS within the NS",
        required=False,
        many=True)
    localizationLanguage = VnfLocationConstraintSerializer(
        help_text="Defines the location constraints for the VNF to be instantiated as part of the NS instantiation.",
        required=False,
        many=True)
    additionalParamForNs = serializers.DictField(
        help_text="Allows the OSS/BSS to provide additional parameters at the NS level ",
        required=False,
        allow_null=True
    )
    additionalParamsForVnf = ParamsForVnfSerializer(
        help_text="Allows the OSS/BSS to provide additional parameter(s)per VNF instance",
        required=False,
        many=True)
    startTime = serializers.DateTimeField(
        help_text="Timestamp indicating the earliest time to instantiate the NS.",
        required=False)
    nsInstantiationLevelId = serializers.CharField(
        help_text="Identifies one of the NS instantiation levels declared in the DF applicable to this NS instance",
        required=False)
    additionalAffinityOrAntiAffiniityRule = AffinityOrAntiAffinityRuleSerializer(
        help_text="Specifies additional affinity or anti-affinity constraint for the VNF instances to be"
                  " instantiated as part of the NS instantiation.",
        required=False,
        many=True)
