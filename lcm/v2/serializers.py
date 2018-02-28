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


class VimConnectionInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="The identifier of the VIM Connection. This identifier is managed by the NFVO.",
        required=True
    )
    vimId = serializers.CharField(
        help_text="The identifier of the VIM instance. This identifier is managed by the NFVO.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vimType = serializers.CharField(
        help_text="Discriminator for the different types of the VIM information.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    interfaceInfo = serializers.DictField(
        help_text="Information about the interface or interfaces to the VIM.",
        child=serializers.CharField(help_text="Interface Info", allow_blank=True),
        required=False,
        allow_null=True
    )
    accessInfo = serializers.DictField(
        help_text="Authentication credentials for accessing the VIM.",
        child=serializers.CharField(help_text="Access Info", allow_blank=True),
        required=False,
        allow_null=True
    )
    extra = serializers.DictField(
        help_text="VIM type specific additional information.",
        child=serializers.CharField(help_text="Extra", allow_blank=True),
        required=False,
        allow_null=True
    )


class ZoneInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="The identifier of this ZoneInfo instance, for the purpose of referencing it from other structures in the Grant structure.",
        required=True
    )
    zoneId = serializers.CharField(
        help_text="The identifier of the resource zone, as managed by the resource management layer(typically, the VIM).",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vimConnectionId = serializers.CharField(
        help_text="Identifier of the connection to the VIM that manages the resource zone.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceProviderId = serializers.CharField(
        help_text="Identifies the entity responsible for the management the resource zone.",
        required=False,
        allow_null=True,
        allow_blank=True
    )


class ZoneGroupInfoSerializer(serializers.Serializer):
    zoneId = serializers.ListSerializer(
        help_text="References of identifiers of ZoneInfo structures.",
        child=serializers.CharField(help_text="IdentifierLocal", allow_blank=True)
        required=False,
        allow_null=True
    )


class GrantSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the grant.",
        required=True
    )
    vnfInstanceId = serializers.CharField(
        help_text="Identifier of the related VNF instance.",
        required=True
    )
    vnfLcmOpOccId = serializers.CharField(
        help_text="Identifier of the related VNF lifecycle management operation occurrence.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vimConnections = VimConnectionInfoSerializer(
        help_text="Provides information regarding VIM connections that are approved to be used by the VNFM to allocate resources.",
        many=True
    )
    zones = ZoneInfoSerializer(
        help_text="Identifies resource zones where the resources are approved to be allocated by the VNFM.",
        many=True
    )
    zoneGroups = ZoneGroupInfoSerializer(
        help_text="Information about groups of resource zones",
        many=True
    )
