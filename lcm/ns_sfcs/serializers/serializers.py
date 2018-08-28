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


class CreateSfcInstReqSerializer(serializers.Serializer):
    fpindex = serializers.CharField(help_text="Index of FP", required=True)
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=False, allow_null=True)
    context = serializers.CharField(help_text="Context of NS instance", required=False, allow_null=True)
    sdnControllerId = serializers.CharField(help_text="ID of SDN controller", required=False, allow_null=True)


class CreateSfcInstRespSerializer(serializers.Serializer):
    fpinstid = serializers.CharField(help_text="ID of FP instance", required=True)


class CreateSfcReqSerializer(serializers.Serializer):
    fpindex = serializers.CharField(help_text="Index of FP", required=True)
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=False, allow_null=True)
    context = serializers.CharField(help_text="Context of NS instance", required=False, allow_null=True)
    sdnControllerId = serializers.CharField(help_text="ID of SDN controller", required=False, allow_null=True)


class CreateSfcRespSerializer(serializers.Serializer):
    jobId = serializers.CharField(help_text="ID of job", required=True)
    sfcInstId = serializers.CharField(help_text="ID of SFC instance", required=True)


class GetSfcRespSerializer(serializers.Serializer):
    sfcInstId = serializers.CharField(help_text="ID of SFC instance", required=True)
    sfcName = serializers.CharField(help_text="Name of SFC instance", required=True)
    sfcStatus = serializers.CharField(help_text="Status of SFC instance", required=True)


class DeleteSfcRespSerializer(serializers.Serializer):
    result = serializers.CharField(help_text="Delete SFC result(0: success, 1: failed)", required=True)
    detail = serializers.CharField(help_text="Result detail", required=False, allow_null=True)


class CreatePortPairGpSerializer(serializers.Serializer):
    fpinstid = serializers.CharField(help_text="ID of FP instance", required=False, allow_null=True)
    context = serializers.CharField(help_text="Context of NS instance", required=False, allow_null=True)
    nsinstanceid = serializers.CharField(help_text="ID of NS instance", required=False, allow_null=True)


class CreateFlowClaSerializer(serializers.Serializer):
    fpinstid = serializers.CharField(help_text="ID of FP instance", required=False, allow_null=True)
    context = serializers.CharField(help_text="Context of NS instance", required=False, allow_null=True)


class CreatePortChainSerializer(serializers.Serializer):
    fpinstid = serializers.CharField(help_text="ID of FP instance", required=False, allow_null=True)
    context = serializers.CharField(help_text="Context of NS instance", required=False, allow_null=True)
