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


class ContextSerializer(serializers.Serializer):
    globalCustomerId = serializers.CharField(help_text="Global customer ID", required=False, allow_null=True)
    serviceType = serializers.CharField(help_text="Service type", required=False, allow_null=True)


class CreateNsReqSerializer(serializers.Serializer):
    csarId = serializers.CharField(help_text="Package ID of NS", required=False, allow_null=True)
    nsName = serializers.CharField(help_text="Name of NS", required=False, allow_null=True)
    description = serializers.CharField(help_text="Description of NS", required=False, allow_null=True)
    context = ContextSerializer(help_text="Context of NS", required=False)


class CreateNsRespSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=True)


class VnfInstSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of VNF instance", required=True)
    vnfInstanceName = serializers.CharField(help_text="Name of VNF instance", required=False, allow_null=True)
    vnfdId = serializers.CharField(help_text="ID of VNFD", required=False, allow_null=True)


class CpInstInfoSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="ID of CP instance", required=True)
    cpInstanceName = serializers.CharField(help_text="Name of CP instance", required=False, allow_null=True)
    cpdId = serializers.CharField(help_text="ID of CPD", required=False, allow_null=True)


class VlInstSerializer(serializers.Serializer):
    vlInstanceId = serializers.CharField(help_text="ID of VL instance", required=True)
    vlInstanceName = serializers.CharField(help_text="Name of VL instance", required=False, allow_null=True)
    vldId = serializers.CharField(help_text="ID of VLD", required=False, allow_null=True)
    relatedCpInstanceId = CpInstInfoSerializer(help_text="Related CP instances", many=True)


class VnffgInstSerializer(serializers.Serializer):
    vnffgInstanceId = serializers.CharField(help_text="ID of VNFFG instance", required=True)
    vnfdId = serializers.CharField(help_text="ID of VNFD", required=False, allow_null=True)
    pnfId = serializers.CharField(help_text="ID of PNF", required=False, allow_null=True)
    virtualLinkId = serializers.CharField(help_text="ID of virtual link", required=False, allow_null=True)
    cpdId = serializers.CharField(help_text="ID of CPD", required=False, allow_null=True)
    nfp = serializers.CharField(help_text="nfp", required=False, allow_null=True)


class QueryNsRespSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=True)
    nsName = serializers.CharField(help_text="Name of NS instance", required=False, allow_null=True)
    description = serializers.CharField(help_text="Description of NS instance", required=False, allow_null=True)
    nsdId = serializers.CharField(help_text="ID of NSD", required=True)
    vnfInfo = VnfInstSerializer(help_text="VNF instances", many=True)
    vlInfo = VlInstSerializer(help_text="VL instances", many=True)
    vnffgInfo = VnffgInstSerializer(help_text="VNFFG instances", many=True)
    nsState = serializers.CharField(help_text="State of NS instance", required=False, allow_null=True)
