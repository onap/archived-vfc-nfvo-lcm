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


class ActionVmSerializer(serializers.Serializer):
    vmid = serializers.CharField(help_text="ID of VM", required=False, allow_null=True, allow_blank=True)
    vduid = serializers.CharField(help_text="ID of vdu", required=False, allow_null=True, allow_blank=True)
    vmname = serializers.CharField(help_text="Name of VM", required=False, allow_null=True, allow_blank=True)


class HealNsAdditionalParamsSerializer(serializers.Serializer):
    action = serializers.CharField(help_text="Action of NS heal", required=False, allow_null=True, allow_blank=True)
    actionvminfo = ActionVmSerializer(help_text="VM info of action", required=False, allow_null=True)


class HealVnfDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Identifies the VNF instance,", required=True)
    cause = serializers.CharField(help_text="Indicates the reason why a healing procedure is required",
                                  required=False, allow_null=True, allow_blank=True)
    additionalParams = serializers.DictField(help_text="Additional parameters passed by the NFVO as input to "
                                                       "the healing process",
                                             child=HealNsAdditionalParamsSerializer(
                                                 help_text="KeyValue Pairs"), required=False, allow_null=True)


class HealNsDataSerializer(serializers.Serializer):
    degreeHealing = serializers.ChoiceField(help_text="degree of healing", choices=["HEAL_RESTORE", "HEAL_QOS", "HEAL_RESET", "PARTIAL_HEALING"], required=True)
    actionsHealing = serializers.ListField(
        help_text="A list of actions",
        child=serializers.CharField(help_text="One action", required=True),
        required=False)
    healScript = serializers.CharField(help_text="script of NS heal", required=False, allow_null=True, allow_blank=True)
    additionalParamsforNs = serializers.CharField(help_text="Addition params of NS heal", required=False, allow_null=True, allow_blank=True)


class HealNsReqSerializer(serializers.Serializer):
    healVnfData = HealVnfDataSerializer(help_text="Data of heal VNF", required=False, allow_null=True,
                                        many=True)
    healNsData = HealNsDataSerializer(help_text="Provides the information needed to heal an NS",
                                      required=False, allow_null=True)
