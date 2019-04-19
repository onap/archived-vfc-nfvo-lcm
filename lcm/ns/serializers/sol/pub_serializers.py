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
from lcm.ns.enum import AFFINITY_OR_ANTIAFFIINTY, AFFINITY_OR_ANTIAFFIINTY_SCOPE
from lcm.pub.utils.enumutil import enum_to_list


class ProblemDetailsSerializer(serializers.Serializer):
    type = serializers.CharField(
        help_text="A URI reference according to IETF RFC 3986 [5] that identifies the problem type.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    title = serializers.CharField(
        help_text="A short, human-readable summary of the problem type.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    status = serializers.IntegerField(
        help_text="The HTTP status code for this occurrence of the problem.",
        required=True
    )
    detail = serializers.CharField(
        help_text="A human-readable explanation specific to this occurrence of the problem.",
        required=True
    )
    instance = serializers.CharField(
        help_text="A URI reference that identifies the specific occurrence of the problem.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    additional_details = serializers.ListField(
        help_text="Any number of additional attributes, as defined in a specification or by an"
                  " implementation.",
        required=False,
        allow_null=True
    )


class LinkSerializer(serializers.Serializer):
    href = serializers.CharField(
        help_text="URI of the referenced resource.",
        required=True,
        allow_null=False,
        allow_blank=False)


class AffinityOrAntiAffinityRuleSerializer(serializers.Serializer):
    vnfdId = serializers.ListField(
        child=serializers.CharField(),
        help_text="Identifier of the VNFD on which the VNF instance is based.",
        required=False,
        allow_null=True)
    vnfProfileId = serializers.ListField(
        child=serializers.CharField(),
        help_text="Identifier of (Reference to) a vnfProfile defined in the NSD which the existing VNF instance shall be matched with.",
        required=False,
        allow_null=True)
    vnfInstanceId = serializers.ListField(
        child=serializers.CharField(),
        help_text="Identifier of the existing VNF instance to be used in the NS.",
        required=True,
        allow_null=False)
    affinityOrAntiAffiinty = serializers.ChoiceField(
        help_text="The type of the constraint.",
        choices=enum_to_list(AFFINITY_OR_ANTIAFFIINTY),
        required=True,
        allow_null=False,
        allow_blank=False)
    scope = serializers.ChoiceField(
        help_text="Specifies the scope of the rule where the placement constraint applies.",
        choices=enum_to_list(AFFINITY_OR_ANTIAFFIINTY_SCOPE),
        required=True,
        allow_null=False,
        allow_blank=False)
