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


class GrantRequestSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(
        help_text="Identifier of the VNF instance which this grant request is related to.",
        required=True
    )
    vnfLcmOpOccId = serializers.CharField(
        help_text="The identifier of the VNF lifecycle management operation occurrence associated to the GrantRequest.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfdId = serializers.CharField(
        help_text="Identifier of the VNFD that defines the VNF for which the LCM operation is to be granted.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    flavourId = serializers.CharField(
        help_text="Identifier of the VNF deployment flavour of the VNFD that defines the VNF for which the LCM operation is to be granted.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    operation = serializers.ChoiceField(
        help_text="The lifecycle management operation for which granting is requested.",
        choices=["INSTANTIATE", "SCALE", "SCALE_TO_LEVEL", "CHANGE_FLAVOUR", "TERMINATE", "HEAL", "OPERATE", "OPERATE", "CHANGE_EXT_CONN", "MODIFY_INFO"],
        required=True
    )
