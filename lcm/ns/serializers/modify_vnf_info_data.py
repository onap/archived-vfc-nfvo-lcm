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


class ModifyVnfInfoDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.UUIDField(
        help_text="Identifier of the VNF instance."
    )
    vnfInstanceName = serializers.CharField(
        help_text="New value of the 'vnfInstanceName' attribute in 'VnfInstance', or 'null' to remove the attribute.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfInstanceDescription = serializers.CharField(
        help_text="If present, this attribute signals modifications of the 'vnfInstanceDescription' attribute in "
                  "'VnfInstance'",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfPkgId = serializers.UUIDField(
        help_text="New value of the 'vnfPkgId' attribute in 'VnfInstance' The value 'null' is not permitted.."
    )
    vnfConfigurableProperties = serializers.DictField(
        help_text="Modifications to entries in the 'vnfConfigurableProperties' list, as defined below this Table.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
    metaData = serializers.DictField(
        help_text="If present, this attribute signals modifications of certain 'metadata' attribute in 'vnfInstance'.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
    extensions = serializers.DictField(
        help_text="If present,this attribute signals modifications of certain 'extensions' attribute in 'vnfInstance'.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
