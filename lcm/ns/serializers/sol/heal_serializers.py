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
from lcm.ns.enum import DEGREE_HEALING
from lcm.pub.utils.enumutil import enum_to_list


# class ActionVmSerializer(serializers.Serializer):
#    vmid = serializers.CharField(help_text="ID of VM", required=False, allow_null=True, allow_blank=True)
#    vduid = serializers.CharField(help_text="ID of vdu", required=False, allow_null=True, allow_blank=True)
#    vmname = serializers.CharField(help_text="Name of VM", required=False, allow_null=True, allow_blank=True)


# class HealNsAdditionalParamsSerializer(serializers.Serializer):
#    action = serializers.CharField(help_text="Action of NS heal", required=False, allow_null=True, allow_blank=True)
#    actionvminfo = ActionVmSerializer(help_text="VM info of action", required=False, allow_null=True)


class HealVnfDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(
        help_text="Identifies the VNF instance, part of the NS, requiring a healing action.",
        required=True)
    cause = serializers.CharField(
        help_text="Indicates the reason why a healing procedure is required.",
        required=False,
        allow_null=True,
        allow_blank=True)
    additionalParams = serializers.DictField(
        help_text="Additional parameters passed by the NFVO as input to the healing process, specific to the VNF being healed.",
        required=False,
        allow_null=True)


class HealNsDataSerializer(serializers.Serializer):
    degreeHealing = serializers.ChoiceField(
        help_text="Indicates the degree of healing.",
        choices=enum_to_list(DEGREE_HEALING),
        required=True)
    actionsHealing = serializers.ListField(
        help_text="Used to specify dedicated healing actions in a particular order",
        child=serializers.CharField(
            help_text="one dedicated healing action",
            required=True),
        required=False)
    healScript = serializers.CharField(
        help_text="Reference to a script from the NSD that shall be used to execute dedicated healing actions in a particular order.",
        required=False,
        allow_null=True,
        allow_blank=True)
    additionalParamsforNs = serializers.DictField(
        help_text="Allows the OSS/BSS to provide additional parameter(s) to the healing process at the NS level.",
        required=False)


class HealNsReqSerializer(serializers.Serializer):
    healVnfData = HealVnfDataSerializer(
        help_text="Provides the information needed to heal a VNF.",
        required=False,
        allow_null=True,
        many=True)
    healNsData = HealNsDataSerializer(
        help_text="Provides the information needed to heal an NS.",
        required=False,
        allow_null=True)
