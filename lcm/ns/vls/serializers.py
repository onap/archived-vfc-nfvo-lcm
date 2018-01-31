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


class CreateVlReqSerializer(serializers.Serializer):
    vlIndex = serializers.CharField(help_text="Index of VL instance", required=True)
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=False, allow_null=True)
    context = serializers.CharField(help_text="Context of VL instance", required=False, allow_null=True)
    additionalParamForNs = serializers.CharField(help_text="Additional param for NS", required=False, allow_null=True)


class CreateVlRespSerializer(serializers.Serializer):
    result = serializers.IntegerField(help_text="VL create result(0: success, 1: failed)", required=True)
    detail = serializers.CharField(help_text="Detail of result", required=False, allow_null=True)
    vlId = serializers.CharField(help_text="ID of VL instance", required=True)


class GetVlRespSerializer(serializers.Serializer):
    vlId = serializers.CharField(help_text="ID of VL instance", required=False, allow_null=True)
    vlName = serializers.CharField(help_text="Name of VL instance", required=False, allow_null=True)
    vlStatus = serializers.CharField(help_text="Status of VL instance", required=False, allow_null=True)


class DeleteVlRespSerializer(serializers.Serializer):
    result = serializers.IntegerField(help_text="VL delete result(0: success)", required=True)
    detail = serializers.CharField(help_text="Detail of result", required=False, allow_null=True)
