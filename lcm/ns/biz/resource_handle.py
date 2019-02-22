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


class ResourceHandleSerializer(serializers.Serializer):
    vimConnectionId = serializers.CharField(
        help_text="Identifier of the VIM connection to manage the resource.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    resourceProviderId = serializers.CharField(
        help_text="Identifier of the entity responsible for the management of the resource.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    resourceId = serializers.CharField(
        help_text="Identifier of the resource in the scope of the VIM or the resource provider.",
        required=True,
        max_length=255,
        allow_null=False,
        allow_blank=False)
    vimLevelResourceType = serializers.CharField(
        help_text="String, type of the resource in the scope of the VIM or the resource provider.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
