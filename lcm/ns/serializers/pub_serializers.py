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
from link import linkSerializer
from lcm.ns_pnfs.serializers.pnf_serializer import PnfInstanceSerializer


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
    self = linkSerializer(help_text="URI of this resource.", required=True)
    nestedNsInstances = linkSerializer(help_text="Links to the nested NS instances of the present NS"
                                                 "instance.", required=False, allow_null=True)
    instantiate = linkSerializer(help_text="Link to the 'instantiate' task resource", required=False,
                                 allow_null=True)
    terminate = linkSerializer(help_text="Link to the 'terminate' task resource", required=False, allow_null=True)
    update = linkSerializer(help_text="Link to the 'update' task resource", required=False, allow_null=True)
    scale = linkSerializer(help_text="Link to the 'scale' task resource", required=False, allow_null=True)
    heal = linkSerializer(help_text="Link to the 'heal' task resource", required=False, allow_null=True)


class IpOverEthernetAddressDataSerializer(serializers.Serializer):
    macAddress = serializers.CharField(help_text="Mac address", required=False, allow_null=True)
    ipAddresses = IpAddressSerialzier(help_text="List of IP addresses to assign to the extCP instance.",
                                      required=False, allow_null=True, many=True)


class NsOperateJobSerializer(serializers.Serializer):
    jobId = serializers.CharField(help_text="ID of NS operate job", required=True)


class VnfInstSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of VNF instance", required=True)
    vnfInstanceName = serializers.CharField(help_text="Name of VNF instance", required=False, allow_null=True, allow_blank=True)
    vnfdId = serializers.CharField(help_text="ID of VNFD", required=False, allow_null=True, allow_blank=True)


class CpInstInfoSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="ID of CP instance", required=True)
    cpInstanceName = serializers.CharField(help_text="Name of CP instance", required=False, allow_null=True, allow_blank=True)
    cpdId = serializers.CharField(help_text="ID of CPD", required=False, allow_null=True, allow_blank=True)


class VlInstSerializer(serializers.Serializer):
    vlInstanceId = serializers.CharField(help_text="ID of VL instance", required=True)
    vlInstanceName = serializers.CharField(help_text="Name of VL instance", required=False, allow_null=True, allow_blank=True)
    vldId = serializers.CharField(help_text="ID of VLD", required=False, allow_null=True, allow_blank=True)
    relatedCpInstanceId = CpInstInfoSerializer(help_text="Related CP instances", many=True)


class VnffgInstSerializer(serializers.Serializer):
    vnffgInstanceId = serializers.CharField(help_text="ID of VNFFG instance", required=True)
    vnfdId = serializers.CharField(help_text="ID of VNFD", required=False, allow_null=True, allow_blank=True)
    pnfId = serializers.CharField(help_text="ID of PNF", required=False, allow_null=True, allow_blank=True)
    virtualLinkId = serializers.CharField(help_text="ID of virtual link", required=False, allow_null=True, allow_blank=True)
    cpdId = serializers.CharField(help_text="ID of CPD", required=False, allow_null=True, allow_blank=True)
    nfp = serializers.CharField(help_text="nfp", required=False, allow_null=True, allow_blank=True)


class QueryNsRespSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=True)
    nsName = serializers.CharField(help_text="Name of NS instance", required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(help_text="Description of NS instance", required=False, allow_null=True, allow_blank=True)
    nsdId = serializers.CharField(help_text="ID of NSD", required=True)
    vnfInfo = VnfInstSerializer(help_text="VNF instances", many=True, required=False, allow_null=True)
    pnfInfo = PnfInstanceSerializer(help_text="PNF instances", many=True, required=False, allow_null=True)
    vlInfo = VlInstSerializer(help_text="VL instances", many=True, required=False, allow_null=True)
    vnffgInfo = VnffgInstSerializer(help_text="VNFFG instances", many=True, required=False, allow_null=True)
    nsState = serializers.CharField(help_text="State of NS instance", required=False, allow_null=True, allow_blank=True)


class CpProtocolDataSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(help_text="Identifier of layer(s) and protocol(s)",
                                            choices=["IP_OVER_ETHERNET"], required=True)
    ipOverEthernet = IpOverEthernetAddressDataSerializer(help_text="Network address data for IP over Ethernet"
                                                                   "to assign to the extCP instance.",
                                                         required=False, allow_null=True)
