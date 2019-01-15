# Copyright (c) 2018, CMCC Technologies Co., Ltd.

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

from lcm.ns.serializers.pub_serializers import Links, IpAddressSerialzier, ipAddressesSerializer


class ContextSerializer(serializers.Serializer):
    globalCustomerId = serializers.CharField(help_text="Global customer ID", required=False, allow_null=True)
    serviceType = serializers.CharField(help_text="Service type", required=False, allow_null=True)


class CreateNsReqSerializer(serializers.Serializer):
    csarId = serializers.CharField(help_text="Package ID of NS", required=False, allow_null=True)
    nsdId = serializers.CharField(help_text="Identifier of the NSD that defines the NS instance to be"
                                            "created.", required=True, allow_null=False)
    nsName = serializers.CharField(help_text="Name of NS", required=False, allow_null=True)
    nsDescription = serializers.CharField(help_text="Description of NS", required=False, allow_null=True)
    context = ContextSerializer(help_text="Context of NS", required=False)


class VnfInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of the VNF instance.", required=True)
    vnfInstanceName = serializers.CharField(help_text="Name of the VNF instance.", required=False,
                                            allow_null=True)


class IpOverEthernetAddressDataSerializer(serializers.Serializer):
    macAddress = serializers.CharField(help_text="Mac address", required=False, allow_null=True)
    ipAddresses = IpAddressSerialzier(help_text="List of IP addresses to assign to the extCP instance.",
                                      required=False, allow_null=True, many=True)


class cpProtocolDataSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(help_text="Identifier of layer(s) and protocol(s).",
                                            choices=["IP_OVER_ETHERNET"], required=True, allow_null=False)
    ipOverEthernet = IpOverEthernetAddressDataSerializer(help_text="Network address data for IP over Ethernet"
                                                                   " to assign to the extCP instance.",
                                                         required=False, allow_null=True)


class PnfExtCpInfoSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="Identifier of the CP in the scope of the PNF.",
                                         required=True)

    cpdId = serializers.CharField(help_text="Identifier of (reference to) the Connection Point Descriptor"
                                            "(CPD) for this CP.", required=True)

    cpProtocolData = cpProtocolDataSerializer(help_text="Parameters for configuring the network protocols on"
                                                        "the CP.", required=True, many=True)


class PnfInfoSerializer(serializers.Serializer):
    pnfId = serializers.CharField(help_text="Identifier of the PNF.", required=True)
    pnfName = serializers.CharField(help_text="Name of the PNF.", required=True)
    pnfdId = serializers.CharField(help_text="Identifier of the PNFD on which the PNF is based.",
                                   required=True)

    pnfdInfoId = serializers.CharField(help_text="Identifier of the PNFD information onject related to this "
                                                 "PNF.", required=True)
    pnfProfileId = serializers.CharField(help_text="Identifier of the related PnfProfile in the NSD on which "
                                                   "the PNF is based.", required=True)

    cpInfo = PnfExtCpInfoSerializer(help_text="Information on the external CP of the PNF",
                                    required=True, many=True)


class ResourceHandleSerializer(serializers.Serializer):
    vimId = serializers.CharField(help_text="Identifier of the VIM under whose control this resource is"
                                            "placed.", required=False, allow_null=True)
    resourceProviderId = serializers.CharField(help_text="Identifier of the entity responsible for the"
                                                         "management of the resource", required=False,
                                               allow_null=True)
    resourceId = serializers.CharField(help_text="Identifier of the resource in the scope of the VIM or the "
                                                 "resource provider.", required=True)
    vimLevelResourceType = serializers.CharField(help_text="Type of the resource in the scope of the VIM or"
                                                           "the resource provider",
                                                 required=False, allow_null=True)


class NsVirtualLinkInfoSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of the VL instance.", required=True)
    nsVirtualLinkDescId = serializers.CharField(help_text="Identifier of the VLD in the NSD.", required=True)
    resourceHandle = ResourceHandleSerializer(help_text="Identifier(s) of the virtualised network resource(s)"
                                                        " realizing the VL instance",
                                              required=True, many=True)


class NsCpHandleSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Identifier of the VNF instance associated to the CP"
                                                    "instance.", required=False, allow_null=True)
    vnfExtCpInstanceId = serializers.CharField(help_text="Identifier of the VNF external CP instance in the"
                                                         "scope of the VNF instance.",
                                               required=False, allow_null=True)
    pnfInfoId = serializers.CharField(help_text="Identifier of the PNF instance associated to the CP"
                                                "instance.", required=False, allow_null=True)
    pnfExtCpInstanceId = serializers.CharField(help_text="Identifier of the PNF external CP instance in the"
                                                         "scope of the PNF.", required=False, allow_null=True)
    nsInstanceId = serializers.CharField(help_text="Identifier of the NS instance associated to the SAP"
                                                   "instance", required=False, allow_null=True)
    nsSapInstanceId = serializers.CharField(help_text="Identifier of the SAP instance in the scope of the NS"
                                                      "instance.", required=False, allow_null=True)


class MaskSerializer(serializers.Serializer):
    startingPoint = serializers.CharField(help_text="Indicates the offset between the last bit of the source"
                                                    "mac address and the first bit of the sequence of bits"
                                                    "to be matched.", required=True)
    length = serializers.CharField(help_text="Indicates the number of bits to be matched", required=True)
    value = serializers.CharField(help_text="Provide the sequence of bit values to be matched.",
                                  required=True)


class NfpRuleSerializer(serializers.Serializer):
    etherDestinationAddress = serializers.CharField(help_text="Indicates a destination Mac address",
                                                    required=False, allow_null=True)
    etherSourceAddress = serializers.CharField(help_text="Indicates a source Mac address",
                                               required=False, allow_null=True)
    etherType = serializers.ChoiceField(help_text="Indicates the protocol carried over the Ethernet layer",
                                        choices=["IPV4", "IPV6"], required=False, allow_null=True)
    vlanTag = serializers.ListField(help_text="ndicates a VLAN identifier in an IEEE 802.1Q-2014 tag",
                                    required=False, allow_null=True)
    protocol = serializers.ChoiceField(help_text="Indicates the L4 protocol, For IPv4 [7] this corresponds to"
                                                 "the field called Protocol to identifythe next level "
                                                 "protocol", choices=["TCP", "UDP", "ICMP"],
                                       required=False, allow_null=True)
    dscp = serializers.CharField(help_text="For IPv4 [7] a string of 0 and 1 digits that corresponds to the"
                                           "6-bit Differentiated Services Code Point (DSCP) field of the"
                                           "IP header.", required=False, allow_null=True)
    sourcePortRange = serializers.CharField(help_text="Indicates a range of source ports",
                                            required=False, allow_null=True)
    destinationPortRange = serializers.CharField(help_text="Indicates a range of destination ports",
                                                 required=False, allow_null=True)
    sourceIpAddressPrefix = serializers.CharField(help_text="Indicates the source IP address range in CIDR"
                                                            "format.", required=False, allow_null=True)
    destinationIpAddressPrefix = serializers.CharField(help_text="Indicates the destination IP address range"
                                                                 "in CIDRformat.",
                                                       required=False, allow_null=True)
    extendedCriteria = MaskSerializer(help_text="Indicates values of specific bits in a frame",
                                      required=False, allow_null=True, many=True)


class NfpInfoSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this NFP instance.", required=True)
    nfpdId = serializers.CharField(help_text="Identifier of the NFPD used to instantiate this NFP"
                                             "instance.", required=False, allow_null=True)
    nfpName = serializers.CharField(help_text="Human readable name for the NFP instance.",
                                    required=False, allow_null=True)
    description = serializers.CharField(help_text="Human readable description for the NFP instance.",
                                        required=True)
    nscpHandle = NsCpHandleSerializer(help_text="Identifier(s) of the CPs and/or SAPs which the NFP "
                                                "passes by", required=True, many=True)
    totalCp = serializers.CharField(help_text="Total number of CP and SAP instances in this NFP"
                                              "instance.", required=False, allow_null=True)
    nfpRule = NfpRuleSerializer(help_text="The NfpRule data type is an expression of the conditions that "
                                          "shall be met in order for the NFP to be applicable to the packet",
                                required=True)
    nfpState = serializers.ChoiceField(help_text="The state of the NFP instance.",
                                       choices=["ENABLED", "DISABLED"], required=True)


class VnffgInfoSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of this VNFFG instance.", required=True)
    vnffgdId = serializers.CharField(help_text="Identifier of the VNFFGD in the NSD.", required=True)
    vnfInstanceId = serializers.ListField(help_text="Identifier(s) of the constituent VNF instance(s) of this"
                                                    "VNFFG instance.",
                                          child=serializers.CharField(help_text="ID of vnf instance"),
                                          required=True)
    pnfInfoId = serializers.ListField(help_text="Identifier(s) of the constituent PNF instance(s) of this"
                                                "VNFFG instance",
                                      child=serializers.CharField(help_text="ID of pnf info"),
                                      required=False, allow_null=True)
    nsVirtualLinkInfoId = serializers.ListField(help_text="Identifier(s) of the constituent VL instance(s) of"
                                                          "thisVNFFG instance.",
                                                child=serializers.CharField(
                                                    help_text="ID of ns virtual link info"), required=True)
    nsCpHandle = NsCpHandleSerializer(help_text="Identifiers of the CP instances attached to the "
                                                "constituent VNFs and PNFs or the SAP instances of "
                                                "the VNFFG.", required=True, allow_null=False, many=True)
    nfpInfo = NfpInfoSerializer(help_text="Information on the NFP instances.",
                                required=True, allow_null=False, many=True)


class IpOverEthernetAddressInfoSerializer(serializers.Serializer):
    macAddress = serializers.CharField(help_text="Assigned MAC address", required=True)
    ipAddresses = ipAddressesSerializer(help_text="Addresses assigned to the CP or SAP instance.",
                                        required=False, allow_null=True, many=True)


class CpProtocolInfoSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(help_text="The identifier of layer(s) and protocol(s) associated"
                                                      "to the network address information.",
                                            choices=["IP_OVER_ETHERNET"], required=True)
    ipOverEthernet = IpOverEthernetAddressInfoSerializer(help_text="IP addresses over Ethernet to assign to"
                                                                   "the CPor SAP instance.",
                                                         required=False, allow_null=True)


class SapInfoSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Identifier of the SAP instance.", required=True)
    sapdId = serializers.CharField(help_text="Identifier of the SAPD in the NSD.", required=True)
    sapName = serializers.CharField(help_text="Human readable name for the SAP instance.", required=True)
    description = serializers.CharField(help_text="Human readable description for the SAP instance.",
                                        required=True)
    sapProtocolInfo = CpProtocolInfoSerializer(help_text="Network protocol information for this SAP.",
                                               required=True, many=True)


class NsScaleInfoSerializer(serializers.Serializer):
    nsScalingAspectId = serializers.CharField(help_text="Identifier of the NS scaling aspect.", required=True)
    nsScaleLevelId = serializers.CharField(help_text="Identifier of the NS scale level.", required=True)


class AffinityOrAntiAffinityRuleSerializer(serializers.Serializer):
    vnfdId = serializers.ListField(help_text="Reference to a VNFD.",
                                   child=serializers.CharField(help_text="Identifier of the vnfd"),
                                   required=False, allow_null=True)
    vnfProfileId = serializers.ListField(help_text="Reference to a vnfProfile defined in the NSD.",
                                         child=serializers.CharField(
                                             help_text="Identifier of the vnfProfile"), required=True)
    vnfInstanceId = serializers.ListField(help_text="Reference to the existing VNF instance as the subject of"
                                                    "the affinity or anti-affinity rule",
                                          child=serializers.CharField(help_text="identifier of the"
                                                                                "vnfInstanceId"),
                                          required=False, allow_null=True)
    affinityOrAntiAffiinty = serializers.ChoiceField(help_text="The type of the constraint.",
                                                     choices=["AFFINITY", "ANTI_AFFINITY"], required=True)
    scope = serializers.ChoiceField(help_text="Specifies the scope of the rule where the placement"
                                              "constraint applies.",
                                    choices=["NFVI_POP", "ZONE", "ZONE_GROUP", "NFVI_NODE"], required=True)


class CreateNsRespSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=True)
    nsInstanceName = serializers.CharField(help_text="Human readable name of the NS instance.", required=True)
    nsInstanceDescription = serializers.CharField(help_text="Human readable description of the NS instance.",
                                                  required=True)
    nsdId = serializers.CharField(help_text="Identifier of the NSD on which the NS instance is based.",
                                  required=True)
    nsdInfoId = serializers.CharField(help_text="Identifier of the NSD information object on which the "
                                                "NS instance is based.", required=True)
    flavourId = serializers.CharField(help_text="Identifier of the NS deployment flavour applied to "
                                                "the NS instance.", required=False, allow_null=True)
    vnfInstance = VnfInstanceSerializer(help_text="Information on constituent VNF(s) of the NS instance.",
                                        required=False, allow_null=True, many=True)

    pnfInfo = PnfInfoSerializer(help_text="Information on the PNF(s) that are part of the NS instance.",
                                required=False, allow_null=True, many=True)
    virtualLinkInfo = NsVirtualLinkInfoSerializer(help_text="Information on the VL(s) of the NS instance.",
                                                  required=False, allow_null=True, many=True)
    vnffgInfo = VnffgInfoSerializer(help_text="Information on the VNFFG(s) of the NS instance",
                                    required=False, allow_null=True, many=True)
    sapInfo = SapInfoSerializer(help_text="Information on the SAP(s) of the NS instance",
                                required=False, allow_null=True, many=True)
    nestedNsInstanceId = serializers.ListField(help_text="Identifier of the nested NS(s) of the NS instance.",
                                               child=serializers.CharField(help_text="nested of the NS"
                                                                                     "instance",),
                                               required=False, allow_null=True)
    nsState = serializers.ChoiceField(help_text="The state of the NS instance.", required=True,
                                      choices=["NOT_INSTANTIATED", "INSTANTIATED"])
    nsScaleStatus = NsScaleInfoSerializer(help_text="Status of each NS scaling aspect declared in the"
                                                    "applicable DF, how 'big' the NS instance has been"
                                                    "scaled w.r.t. that aspect.",
                                          required=False, allow_null=True, many=True)
    additionalAffinityOrAntiAffinityRule = AffinityOrAntiAffinityRuleSerializer(
        help_text="Information on the additional affinity or anti-affinity rule from NS instantiation "
                  "operation.", required=False, allow_null=True, many=True)
    _links = Links(help_text="Links to resources related to this resource.", required=True)
