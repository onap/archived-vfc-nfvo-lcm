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
from lcm.ns.serializers.sol.resource_handle import ResourceHandleSerializer


class ExtlinkPortInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this link port as provided by the entity that has created the link port.",
        max_length=255,
        required=True,
        allow_blank=False,
        allow_null=False)
    resourceHandle = ResourceHandleSerializer(
        help_text="Reference to the virtualised resource realizing this link port.",
        required=True,
        allow_null=False)
    cpInstanceId = serializers.CharField(
        help_text="Identifier of the external CP of the VNFconnected to this link port.",
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True)


class ExtVirtualLinkInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the external VL and the related external VL information instance.",
        required=True,
        max_length=255,
        allow_null=False,
        allow_blank=False)
    resourceHandle = ResourceHandleSerializer(
        help_text="Reference to the resource realizing this VL.",
        required=True,
        allow_null=False)
    extlinkPorts = ExtlinkPortInfoSerializer(
        help_text="Link ports of this VL.",
        many=True,
        required=False,
        allow_null=True)
