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
from lcm.ns.serializers.common_Link import LinkSerializer


class AddressRangeSerializer(serializers.Serializer):
    minAddress = serializers.IPAddressField(help_text="Lowest IP address belonging to the range.",
                                            required=True)
    maxAddress = serializers.IPAddressField(help_text="Highest IP address belonging to the range.",
                                            required=True)


class IpAddressSerialzier(serializers.Serializer):
    type = serializers.ChoiceField(help_text="The type of the IP addresses.",
                                   required=True, choices=["IPV4", "IPV6"])
    fixedAddresses = serializers.ListField(child=serializers.CharField(help_text="Fixed addresses to assign.",
                                                                       required=False, allow_null=True))
    numDynamicAddresses = serializers.IntegerField(help_text="Number of dynamic addresses to assign.",
                                                   required=False)
    addressRange = AddressRangeSerializer(help_text="An IP address range to be used.", required=False)
    subnetId = serializers.CharField(help_text="Subnet defined by the identifier of the subnet resource"
                                               " in the VIM.", required=False, allow_null=True,
                                     allow_blank=True)


class ipAddressesSerializer(serializers.Serializer):
    type = serializers.ChoiceField(help_text="The type of the IP addresses.",
                                   required=True, choices=["IPV4", "IPV6"])
    addresses = serializers.ListField(help_text="An IPV4 or IPV6 address", required=False, allow_null=True)
    isDynamic = serializers.BooleanField(help_text="Indicates whether this set of addresses was assigned"
                                                   " dynamically (true) or based on address information"
                                                   " provided as input from the API consumer (false). ",
                                         required=False)
    addressRange = AddressRangeSerializer(help_text="An IP address range used,",
                                          required=False, allow_null=True)
    subnetId = serializers.CharField(help_text="Subnet defined by the identifier of the subnet resource in "
                                               "the VIM. ", required=False, allow_null=True)


class Links(serializers.Serializer):
    self = LinkSerializer(help_text="URI of this resource.", required=True)
    nestedNsInstances = LinkSerializer(help_text="Links to the nested NS instances of the present NS"
                                                 "instance.", required=False, allow_null=True)
    instantiate = LinkSerializer(help_text="Link to the 'instantiate' task resource", required=False,
                                 allow_null=True)
    terminate = LinkSerializer(help_text="Link to the 'terminate' task resource", required=False, allow_null=True)
    update = LinkSerializer(help_text="Link to the 'update' task resource", required=False, allow_null=True)
    scale = LinkSerializer(help_text="Link to the 'scale' task resource", required=False, allow_null=True)
    heal = LinkSerializer(help_text="Link to the 'heal' task resource", required=False, allow_null=True)


class IpOverEthernetAddressDataSerializer(serializers.Serializer):
    macAddress = serializers.CharField(help_text="Mac address", required=False, allow_null=True)
    ipAddresses = IpAddressSerialzier(help_text="List of IP addresses to assign to the extCP instance.",
                                      required=False, allow_null=True, many=True)
