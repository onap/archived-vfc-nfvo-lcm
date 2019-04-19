# Copyright (c) 2019, CMCC Technologies Co., Ltd.
# Copyright (c) 2019, ZTE Corporation.

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

from lcm.ns.serializers.sol.inst_ns_serializers import VnfLocationConstraintSerializer, ParamsForVnfSerializer
from lcm.ns.serializers.sol.update_serializers import VnfInstanceDataSerializer
from lcm.ns.serializers.sol.ns_instance import NsScaleInfoSerializer, VnfScaleInfoSerializer
from lcm.ns.enum import SCALING_DIRECTION, SCALE_VNF_TYPE, SCALE_TYPE
from lcm.pub.utils.enumutil import enum_to_list


class ScaleNsByStepsDataSerializer(serializers.Serializer):
    scalingDirection = serializers.ChoiceField(
        help_text="The scaling direction",
        choices=enum_to_list(SCALING_DIRECTION),
        required=True)
    aspectId = serializers.CharField(
        help_text="The aspect of the NS that is requested to be scaled, as declared in the NSD. ",
        required=True)
    numberOfSteps = serializers.CharField(
        help_text="The number of scaling steps to be performed. Defaults to 1. ",
        required=False,
        allow_null=True)


class ScaleNsToLevelDataSerializer(serializers.Serializer):
    nsInstantiationLevel = serializers.CharField(
        help_text="Identifier of the target NS instantiation level "
                  "of the current DF to which the NS instance is requested to be scaled.",
        required=False,
        allow_null=True)
    nsScaleInfo = serializers.ListField(
        help_text="For each NS scaling aspect of the current DF",
        child=NsScaleInfoSerializer(
            help_text="This type represents the target NS Scale level for "
                      "each NS scaling aspect of the current deployment flavour.",
            required=True),
        required=False,
        allow_null=True)


class ScaleNsDataSerializer(serializers.Serializer):
    vnfInstanceToBeAdded = serializers.ListField(
        help_text="An existing VNF instance to be added to the NS instance as part of the scaling operation.",
        child=VnfInstanceDataSerializer(
            help_text="This type specifies an existing VNF instance to be used in the NS instance and if needed",
            required=True),
        required=False,
        allow_null=True)
    vnfInstanceToBeRemoved = serializers.ListField(
        help_text="The VNF instance to be removed from the NS instance as part of the scaling operation",
        required=False,
        allow_null=True)
    scaleNsByStepsData = ScaleNsByStepsDataSerializer(
        help_text="The information used to scale an NS instance by one or more scaling steps",
        required=False,
        allow_null=True)
    scaleNsToLevelData = ScaleNsToLevelDataSerializer(
        help_text="The information used to scale an NS instance to a target size. ",
        required=False,
        allow_null=True)
    additionalParamsForNs = serializers.DictField(
        help_text="Allows the OSS/BSS to provide additional parameter(s) at the NS level necessary for the NS scaling ",
        child=serializers.CharField(help_text="KeyValue Pairs",
                                    allow_blank=True),
        required=False,
        allow_null=True)
    additionalParamsForVnf = serializers.ListField(
        help_text="Allows the OSS/BSS to provide additional parameter(s) per VNF instance",
        child=ParamsForVnfSerializer(
            help_text="This type defines the additional parameters for the VNF instance to be created associated with an NS instance.",
            required=True),
        required=False,
        allow_null=True)
    locationConstraints = serializers.ListField(
        help_text="The location constraints for the VNF to be instantiated as part of the NS scaling.",
        child=VnfLocationConstraintSerializer(
            help_text="This type represents the association of location constraints to a VNF instance to"
                      "be created according to a specific VNF profile",
            required=True),
        required=False,
        allow_null=True)


class ScaleToLevelDataSerializer(serializers.Serializer):
    vnfInstantiationLevelId = serializers.CharField(
        help_text="Identifier of the target instantiation level of the current deployment flavour to which the VNF is requested to be scaled.",
        required=False,
        allow_null=True)
    vnfScaleInfo = serializers.ListField(
        help_text="For each scaling aspect of the current deployment flavour",
        child=VnfScaleInfoSerializer(
            help_text="This type describes the provides information about the scale level of a VNF instance with respect to one scaling aspect",
            required=True),
        required=False,
        allow_null=True)
    additionalParams = serializers.DictField(
        help_text="Additional parameters passed by the NFVO as input to the scaling process",
        required=False,
        allow_null=True)


class ScaleByStepDataSerializer(serializers.Serializer):
    aspectId = serializers.CharField(
        help_text="Identifier of (reference to) the aspect of the VNF that is requested to be scaled.",
        required=True)
    numberOfSteps = serializers.CharField(
        help_text="Number of scaling steps.",
        required=False,
        allow_null=True)
    additionalParams = serializers.DictField(
        help_text="Additional parameters passed by the NFVO as input to the scaling process.",
        required=False,
        allow_null=True)


class ScaleVnfDataSerializers(serializers.Serializer):
    vnfInstanceid = serializers.CharField(
        help_text="Identifier of the VNF instance being scaled.",
        required=True)

    scaleVnfType = serializers.ChoiceField(
        help_text="Type of the scale VNF operation requested.",
        choices=enum_to_list(SCALE_VNF_TYPE),
        required=True)

    scaleToLevelData = ScaleToLevelDataSerializer(
        help_text="The information used for scaling to a given level.",
        required=False)

    scaleByStepData = ScaleByStepDataSerializer(
        help_text="The information used for scaling by steps.",
        required=False)


class ScaleNsRequestSerializer(serializers.Serializer):
    scaleType = serializers.ChoiceField(
        help_text="Indicates the type of scaling to be performed",
        choices=enum_to_list(SCALE_TYPE),
        required=True)
    scaleNsData = ScaleNsDataSerializer(
        help_text="The necessary information to scale the referenced NS instance.",
        required=False,
        allow_null=True)
    scaleVnfData = serializers.ListField(
        help_text="Timestamp indicating the scale time of the NS",
        child=ScaleVnfDataSerializers(
            help_text="This type represents defines the information to scale a VNF instance to a given level",
            required=True),
        required=False,
        allow_null=True)
    scaleTime = serializers.CharField(
        help_text="Timestamp indicating the scale time of the NS",
        required=False,
        allow_null=True)
