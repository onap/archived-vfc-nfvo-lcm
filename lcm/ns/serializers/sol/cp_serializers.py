# Copyright (c) 2019, CMCC Technologies Co., Ltd.
# Copyright (c) 2019, ZTE Corporation.

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
from lcm.ns.enum import LAYER_PROTOCOL, IPADDRESSES_TYPE
from lcm.pub.utils.enumutil import enum_to_list


class AddressRangeSerializer(serializers.Serializer):
    minAddress = serializers.IPAddressField(
        help_text="Lowest IP address belonging to the range.",
        required=True)
    maxAddress = serializers.IPAddressField(
        help_text="Highest IP address belonging to the range.",
        required=True)


class IpAddressesDataSerialzier(serializers.Serializer):
    type = serializers.ChoiceField(
        help_text="The type of the IP addresses.",
        required=True,
        choices=enum_to_list(IPADDRESSES_TYPE))
    fixedAddresses = serializers.ListField(
        child=serializers.CharField(
            help_text="Fixed addresses to assign.",
            required=False,
            allow_null=True))
    numDynamicAddresses = serializers.IntegerField(
        help_text="Number of dynamic addresses to assign.",
        required=False)
    addressRange = AddressRangeSerializer(
        help_text="An IP address range to be used.",
        required=False)
    subnetId = serializers.CharField(
        help_text="Subnet defined by the identifier of the subnet resource in the VIM.",
        required=False,
        allow_null=True,
        allow_blank=True)


class IpAddressesInfoSerialzier(serializers.Serializer):
    type = serializers.ChoiceField(
        help_text="The type of the IP addresses.",
        required=True,
        choices=enum_to_list(IPADDRESSES_TYPE))
    addresses = serializers.ListField(
        help_text="An IPV4 or IPV6 address",
        required=False,
        allow_null=True)
    isDynamic = serializers.BooleanField(
        help_text="Indicates whether this set of addresses was assigned"
                  " dynamically (true) or based on address information"
                  " provided as input from the API consumer (false).",
        required=False)
    addressRange = AddressRangeSerializer(
        help_text="An IP address range used,",
        required=False,
        allow_null=True)
    subnetId = serializers.CharField(
        help_text="Subnet defined by the identifier of the subnet resource in the VIM.",
        required=False,
        allow_null=True)


class IpOverEthernetAddressDataSerializer(serializers.Serializer):
    macAddress = serializers.CharField(
        help_text="Mac address",
        required=False,
        allow_null=True)
    ipAddresses = IpAddressesDataSerialzier(
        help_text="List of IP addresses to assign to the extCP instance.",
        required=False,
        allow_null=True,
        many=True)


class IpOverEthernetAddressInfoSerializer(serializers.Serializer):
    macAddress = serializers.CharField(
        help_text="Mac address",
        required=False,
        allow_null=True)
    ipAddresses = IpAddressesInfoSerialzier(
        help_text="List of IP addresses to assign to the extCP instance.",
        required=False,
        allow_null=True,
        many=True)


class CpProtocolDataSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(
        help_text="Identifier of layer(s) and protocol(s)",
        choices=enum_to_list(LAYER_PROTOCOL),
        required=True)
    ipOverEthernet = IpOverEthernetAddressDataSerializer(
        help_text="Network address data for IP over Ethernet to assign to the extCP instance.",
        required=False,
        allow_null=True)


class CpProtocolInfoSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(
        help_text="Identifier of layer(s) and protocol(s)",
        choices=enum_to_list(LAYER_PROTOCOL),
        required=True)
    ipOverEthernet = IpOverEthernetAddressInfoSerializer(
        help_text="Network address data for IP over Ethernet to assign to the extCP instance.",
        required=False,
        allow_null=True)


class VnfExtCpInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the external CP instance and the related information instance.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    cpdId = serializers.CharField(
        help_text="Identifier of the external CPD, VnfExtCpd, in the VNFD.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    cpProtocolInfo = CpProtocolInfoSerializer(
        help_text="Network protocol information for this CP.",
        many=True,
        required=False,
        allow_null=True)
    extLinkPortId = serializers.CharField(
        help_text="Identifier of the extLinkPortInfo structure inside the extVirtualLinkInfo structure.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
