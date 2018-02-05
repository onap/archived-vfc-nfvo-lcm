# Copyright 2018 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework import serializers


class InstVnfReqSerializer(serializers.Serializer):
    vnfIndex = serializers.CharField(help_text="Index of VNF", required=True)
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=True)
    additionalParamForVnf = serializers.CharField(help_text="Additional param for VNF", required=False, allow_null=True)


class InstVnfRespSerializer(serializers.Serializer):
    vnfInstId = serializers.CharField(help_text="ID of VNF instance", required=True)
    jobId = serializers.CharField(help_text="ID of Job", required=True)


class GetVnfRespSerializer(serializers.Serializer):
    vnfInstId = serializers.CharField(help_text="ID of VNF instance", required=True)
    vnfName = serializers.CharField(help_text="Name of VNF instance", required=True)
    vnfStatus = serializers.CharField(help_text="Status of VNF instance", required=True)


class TerminateVnfReqSerializer(serializers.Serializer):
    terminationType = serializers.CharField(help_text="Termination Type", required=False, allow_null=True)
    gracefulTerminationTimeout = serializers.CharField(help_text="Graceful Termination Timeout", required=False, allow_null=True)


class TerminateVnfRespSerializer(serializers.Serializer):
    jobId = serializers.CharField(help_text="ID of Job", required=True)


class ResourceChangeSerializer(serializers.Serializer):
    type = serializers.ChoiceField(help_text="Change Type", choices=["VDU"], required=True)
    resourceDefinitionId = serializers.CharField(help_text="Identifier of resource", required=False, allow_null=True)
    vdu = serializers.CharField(help_text="Identifier identifier of VDU", required=False, allow_null=True)


class GrantVnfReqSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of VNF instance", required=True)
    vnfDescriptorId = serializers.CharField(help_text="ID of VNF Descriptor", required=False, allow_null=True)
    lifecycleOperation = serializers.ChoiceField(
        help_text="Lifecycle Operation",
        choices=["Terminal", "Instantiate", "Scalein", "Scaleout", "Scaledown", "Scaleup", "Heal"],
        required=True
    )
    jobId = serializers.CharField(help_text="ID of Job", required=False, allow_null=True)
    addResource = ResourceChangeSerializer(help_text="Add resources", many=True)
    removeResource = ResourceChangeSerializer(help_text="Remove resources", many=True)
    additionalParam = serializers.DictField(
        help_text="Additional parameters passed to the NFVO, specific to the VNF and the LCM operation. The currently interpreted keys are the following: vimId",
        child=serializers.CharField(help_text="Additional parameters", allow_blank=True),
        required=False,
        allow_null=True
    )
