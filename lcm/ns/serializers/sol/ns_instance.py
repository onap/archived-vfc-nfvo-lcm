# Copyright 2019 ZTE Corporation.
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

from lcm.ns.serializers.sol.pub_serializers import LinkSerializer
from lcm.ns.serializers.sol.cp_serializers import CpProtocolDataSerializer, CpProtocolInfoSerializer, VnfExtCpInfoSerializer
from lcm.ns.serializers.sol.resource_handle import ResourceHandleSerializer
from lcm.ns.serializers.sol.ext_virtual_link_info import ExtVirtualLinkInfoSerializer
from lcm.ns.serializers.sol.ext_managed_virtual_link_info import ExtManagedVirtualLinkInfo, VnfLinkPortInfo
from lcm.ns.serializers.sol.pub_serializers import AffinityOrAntiAffinityRuleSerializer
from lcm.ns.enum import IPADDRESSES_TYPE, INSTANTIATION_STATE, VNF_STATE, NFP_STATE, PROTOCOL
from lcm.pub.utils.enumutil import enum_to_list


class VnfScaleInfoSerializer(serializers.Serializer):
    aspectlId = serializers.Serializer(
        help_text="Identifier of the scaling aspect",
        required=True)
    scaleLevel = serializers.Serializer(
        help_text="The scale level for that aspect.",
        required=True)


class NsScaleInfoSerializer(serializers.Serializer):
    nsScalingAspectId = serializers.CharField(
        help_text="Identifier of the NS scaling aspect.",
        required=True)
    nsScaleLevelId = serializers.CharField(
        help_text="Identifier of the NS scale level.",
        required=True)


class VnfcCpInfo(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the external CP instance and the related information instance.",
        required=True)
    cpdId = serializers.CharField(
        help_text="Identifier of the external CPD, VnfExtCpd, in the VNFD.",
        required=True)
    vnfExtCpId = serializers.CharField(
        help_text="When the VNFC CP is exposed as external CP of the VNF, the identifier of this external VNF CP.",
        required=False)
    cpProtocolInfo = CpProtocolInfoSerializer(
        help_text="Network protocol information for this CP.",
        many=True,
        required=False)
    vnfLinkPortId = serializers.CharField(
        help_text="Identifier of the vnfLinkPorts structure in the vnfVirtualLinkResourceInfo structure.",
        required=True)


class VnfcResourceInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this VnfcResourceInfo instance.",
        max_length=255,
        required=False,
        allow_null=False)
    vduId = serializers.CharField(
        help_text="Reference to the applicable VDU in the VNFD.",
        max_length=255,
        required=False,
        allow_null=False)
    computeResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualCompute resource.",
        required=True,
        allow_null=False)
    storageResourceIds = serializers.ListSerializer(
        help_text="References to the VirtualStorage resources. The value refers to a VirtualStorageResourceInfo item in the VnfInstance.",
        child=serializers.CharField(help_text="Identifier In Vnf", allow_blank=True),
        required=False,
        allow_null=True)
    reservationId = serializers.CharField(
        help_text="The reservation identifier applicable to the resource.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfcCpInfo = VnfcCpInfo(
        help_text="CPs of the VNFC instance. Shall be present when that particular CP of the VNFC instance is associated to an external CP of the VNF instance.",
        many=True,
        required=False,
        allow_null=True)
    metadata = serializers.DictField(
        help_text="Metadata about this resource.",
        required=False)


# class VnfLinkPortInfo(serializers.Serializer):
#     id = serializers.CharField(
#         help_text="Identifier of this link port as provided by the entity that has created the link port.",
#         max_length=255,
#         required=True,
#         allow_null=False,
#         allow_blank=False)
#     resourceHandle = ResourceHandleSerializer(
#         help_text="Reference to the virtualised network resource realizing this link port.",
#         required=True,
#         allow_null=False)
#     cpInstanceId = serializers.CharField(
#         help_text="When the link port is used for external connectivity by the VNF, \
#         this attribute represents the identifier of the external CP of the VNF to be connected to this link port.",
#         max_length=255,
#         required=False,
#         allow_null=True,
#         allow_blank=True)


class VnfVirtualLinkResourceInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this VnfVirtualLinkResourceInfo instance.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    virtualLinkDescId = serializers.CharField(
        help_text="Identifier of the VNF Virtual Link Descriptor (VLD) in the VNFD.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    networkResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualNetwork resource.",
        required=True,
        allow_null=False)
    reservationId = serializers.CharField(
        help_text="The reservation identifier applicable to the resource.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfLinkPorts = VnfLinkPortInfo(
        help_text="Links ports of this VL. \
        Shall be present when the linkPort is used for external connectivity by the VNF",
        many=True,
        required=False,
        allow_null=True)
    metadata = serializers.DictField(
        help_text="Metadata about this resource.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)


class VirtualStorageResourceInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this VirtualStorageResourceInfo instance.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    virtualStorageDescId = serializers.CharField(
        help_text="Identifier of the VirtualStorageDesc in the VNFD.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    storageResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualStorage resource.",
        required=True,
        allow_null=False)
    reservationId = serializers.CharField(
        help_text="The reservation identifier applicable to the resource.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    metadata = serializers.DictField(
        help_text="Metadata about this resource.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)


class InstantiatedVnfInfo(serializers.Serializer):
    flavourId = serializers.CharField(
        help_text="Identifier of the VNF deployment flavour applied to this VNF instance.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    vnfState = serializers.ChoiceField(
        help_text="State of the VNF instance.",
        choices=enum_to_list(VNF_STATE),
        required=True,
        allow_null=True,
        allow_blank=False)
    scaleStatus = VnfScaleInfoSerializer(
        help_text="Scale status of the VNF, one entry per aspect. \
        Represents for every scaling aspect how big the VNF has been scaled w.r.t. that aspect.",
        many=True,
        required=False,
        allow_null=True)
    extCpInfo = VnfExtCpInfoSerializer(
        help_text="Information about the external CPs exposed by the VNF instance.",
        many=True,
        required=True,
        allow_null=False)
    extVirtualLinkInfo = ExtVirtualLinkInfoSerializer(
        help_text="Information about the external VLs the VNF instance is connected to.",
        many=True,
        required=False,
        allow_null=True)
    extManagedVirtualLinkInfo = ExtManagedVirtualLinkInfo(
        help_text="Information about the externally-managed inner VLs of the VNF instance.",
        many=True,
        required=False,
        allow_null=True)
    monitoringParameters = serializers.DictField(
        help_text="Active monitoring parameters.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
    localizationLanguage = serializers.CharField(
        help_text="Information about localization language of the VNF.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfcResourceInfo = VnfcResourceInfoSerializer(
        help_text="Information about the virtualised compute and storage resources used by the VNFCs of the VNF instance.",
        many=True,
        required=False,
        allow_null=True)
    vnfVirtualLinkResourceInfo = VnfVirtualLinkResourceInfoSerializer(
        help_text="Information about the virtualised network resources used by the VLs of the VNF instance.",
        many=True,
        required=False,
        allow_null=True)
    virtualStorageResourceInfo = VirtualStorageResourceInfoSerializer(
        help_text="Information about the virtualised storage resources used as storage for the VNF instance.",
        many=True,
        required=False,
        allow_null=True)


class VnfInstanceLinks(serializers.Serializer):
    href = LinkSerializer(
        help_text="URI of this resource.",
        required=True,
        allow_null=False)
    indicators = LinkSerializer(
        help_text="Indicators related to this VNF instance.",
        required=False,
        allow_null=True)
    instantiate = LinkSerializer(
        help_text="Link to the instantiate task resource.",
        required=False,
        allow_null=True)
    termiante = LinkSerializer(
        help_text="Link to the terminate task resource.",
        required=False,
        allow_null=True)
    scale = LinkSerializer(
        help_text="Link to the scale task resource.",
        required=False,
        allow_null=True)
    scaleToLevel = LinkSerializer(
        help_text="Link to the scale_to_level task resource.",
        required=False,
        allow_null=True)
    changeFlavour = LinkSerializer(
        help_text="Link to the change_flavour task resource.",
        required=False,
        allow_null=True)
    heal = LinkSerializer(
        help_text="Link to the heal task resource.",
        required=False,
        allow_null=True)
    operate = LinkSerializer(
        help_text="Link to the operate task resource.",
        required=False,
        allow_null=True)
    changeExtConn = LinkSerializer(
        help_text="Link to the change_ext_conn task resource.",
        required=False,
        allow_null=True)


class VnfInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the VNF instance.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    vnfInstanceName = serializers.CharField(
        help_text="Name of the VNF instance.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfInstanceDescription = serializers.CharField(
        help_text="Human-readable description of the VNF instance.",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfdId = serializers.CharField(
        help_text="Identifier of the VNFD on which the VNF instance is based.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfProvider = serializers.CharField(
        help_text="Provider of the VNF and the VNFD.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    vnfProductName = serializers.CharField(
        help_text="Name to identify the VNF Product.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfSoftwareVersion = serializers.CharField(
        help_text="Software version of the VNF.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfdVersion = serializers.CharField(
        help_text="Identifies the version of the VNFD.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    vnfPkgId = serializers.CharField(
        help_text="Identifier of information held by the NFVO about the specific VNF package on which the VNF is based. \
        This attribute can be modified with the PATCH method.",
        max_length=255,
        required=True,
        allow_null=True,
        allow_blank=False)
    vnfConfigurableProperties = serializers.DictField(
        help_text="Current values of the configurable properties of the VNF instance. \
        Configurable properties referred in this attribute are declared in the VNFD",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True,)
    vimId = serializers.ListField(
        help_text="Identifier set of a VIM that manages resources for the VNF instance.",
        child=serializers.CharField(help_text="Identifier of a VIM that manages resources for the VNF instance.", allow_null=False),
        required=False)
    instantiationState = serializers.ChoiceField(
        help_text="The instantiation state of the VNF.",
        choices=enum_to_list(INSTANTIATION_STATE),
        required=True,
        allow_null=False,
        allow_blank=False)
    instantiatedVnfInfo = InstantiatedVnfInfo(
        help_text="Information specific to an instantiated VNF instance. \
        This attribute shall be present if the instantiateState attribute value is INSTANTIATED",
        required=False,
        allow_null=True)
    metadata = serializers.DictField(
        help_text="Additional VNF-specific metadata describing the VNF instance.\
        This attribute can be modified with the PATCH method.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
    extensions = serializers.DictField(
        help_text="VNF-specific attributes that affect the lifecycle management of this VNF instance by the VNFM, or the lifecycle management scripts. \
        This attribute can be modified with the PATCH method.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True)
    _links = VnfInstanceLinks(
        help_text="Links to resources related to this resource.",
        required=False,
        allow_null=False)


class PnfExtCpInfoSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(
        help_text="Identifier of the CP in the scope of the PNF.",
        required=True)

    cpdId = serializers.CharField(
        help_text="Identifier of (reference to) the Connection Point Descriptor (CPD) for this CP.",
        required=True)

    cpProtocolData = CpProtocolDataSerializer(
        help_text="Parameters for configuring the network protocols on the CP.",
        required=True,
        many=True)


class PnfInfoSerializer(serializers.Serializer):
    pnfId = serializers.CharField(
        help_text="Identifier of the PNF.",
        required=True)
    pnfName = serializers.CharField(
        help_text="Name of the PNF.",
        required=True)
    pnfdId = serializers.CharField(
        help_text="Identifier of the PNFD on which the PNF is based.",
        required=True)
    pnfdInfoId = serializers.CharField(
        help_text="Identifier of the PNFD information onject related to this PNF.",
        required=True)
    pnfProfileId = serializers.CharField(
        help_text="Identifier of the related PnfProfile in the NSD on which the PNF is based.",
        required=True)
    cpInfo = PnfExtCpInfoSerializer(
        help_text="Information on the external CP of the PNF",
        required=True,
        many=True)


class NsLinkPortInfo(serializers.Serializer):
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
        help_text="Identifier of the external CP of the VNF connected to this link port. \
        There shall be at most one link port associated with any external connection point instance.",
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True)


class NsVirtualLinkInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the VL instance.",
        required=True)
    nsVirtualLinkDescId = serializers.CharField(
        help_text="Identifier of the VLD in the NSD.",
        required=True)
    nsVirtualLinkProfileId = serializers.CharField(
        help_text="Identifier of the VL profile in the NSD.",
        required=True)
    resourceHandle = ResourceHandleSerializer(
        help_text="Identifier(s) of the virtualised network resource(s) realizing the VL instance",
        required=True,
        many=True)
    linkPort = NsLinkPortInfo(
        help_text="Link ports of this VL.",
        many=True,
        required=False,
        allow_null=True)


class NsCpHandleSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(
        help_text="Identifier of the VNF instance associated to the CP instance.",
        required=False,
        allow_null=True)
    vnfExtCpInstanceId = serializers.CharField(
        help_text="Identifier of the VNF external CP instance in the scope of the VNF instance.",
        required=False,
        allow_null=True)
    pnfInfoId = serializers.CharField(
        help_text="Identifier of the PNF instance associated to the CP instance.",
        required=False,
        allow_null=True)
    pnfExtCpInstanceId = serializers.CharField(
        help_text="Identifier of the PNF external CP instance in the scope of the PNF.",
        required=False,
        allow_null=True)
    nsInstanceId = serializers.CharField(
        help_text="Identifier of the NS instance associated to the SAP instance",
        required=False,
        allow_null=True)
    nsSapInstanceId = serializers.CharField(
        help_text="Identifier of the SAP instance in the scope of the NS instance.",
        required=False,
        allow_null=True)


class MaskSerializer(serializers.Serializer):
    startingPoint = serializers.CharField(
        help_text="Indicates the offset between the last bit of the source mac address and the first bit of the sequence of bits to be matched.",
        required=True)
    length = serializers.CharField(
        help_text="Indicates the number of bits to be matched.",
        required=True)
    value = serializers.CharField(
        help_text="Provide the sequence of bit values to be matched.",
        required=True)


class NfpRuleSerializer(serializers.Serializer):
    etherDestinationAddress = serializers.CharField(
        help_text="Indicates a destination Mac address",
        required=False,
        allow_null=True)
    etherSourceAddress = serializers.CharField(
        help_text="Indicates a source Mac address",
        required=False,
        allow_null=True)
    etherType = serializers.ChoiceField(
        help_text="Indicates the protocol carried over the Ethernet layer",
        choices=enum_to_list(IPADDRESSES_TYPE),
        required=False,
        allow_null=True)
    vlanTag = serializers.ListField(
        help_text="ndicates a VLAN identifier in an IEEE 802.1Q-2014 tag",
        required=False,
        allow_null=True)
    protocol = serializers.ChoiceField(
        help_text="Indicates the L4 protocol, For IPv4 [7] this corresponds to"
                  "the field called Protocol to identifythe next level protocol",
        choices=enum_to_list(PROTOCOL),
        required=False,
        allow_null=True)
    dscp = serializers.CharField(
        help_text="For IPv4 [7] a string of 0 and 1 digits that corresponds to the"
                  "6-bit Differentiated Services Code Point (DSCP) field of the IP header.",
        required=False,
        allow_null=True)
    sourcePortRange = serializers.CharField(
        help_text="Indicates a range of source ports",
        required=False,
        allow_null=True)
    destinationPortRange = serializers.CharField(
        help_text="Indicates a range of destination ports",
        required=False,
        allow_null=True)
    sourceIpAddressPrefix = serializers.CharField(
        help_text="Indicates the source IP address range in CIDR format.",
        required=False,
        allow_null=True)
    destinationIpAddressPrefix = serializers.CharField(
        help_text="Indicates the destination IP address range in CIDR format.",
        required=False,
        allow_null=True)
    extendedCriteria = MaskSerializer(
        help_text="Indicates values of specific bits in a frame",
        required=False,
        allow_null=True,
        many=True)


class NfpInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this NFP instance.",
        required=True)
    nfpdId = serializers.CharField(
        help_text="Identifier of the NFPD used to instantiate this NFP instance.",
        required=False,
        allow_null=True)
    nfpName = serializers.CharField(
        help_text="Human readable name for the NFP instance.",
        required=False,
        allow_null=True)
    description = serializers.CharField(
        help_text="Human readable description for the NFP instance.",
        required=True)
    nscpHandle = NsCpHandleSerializer(
        help_text="Identifier(s) of the CPs and/or SAPs which the NFP passes by",
        required=True,
        many=True)
    totalCp = serializers.CharField(
        help_text="Total number of CP and SAP instances in this NFP instance.",
        required=False,
        allow_null=True)
    nfpRule = NfpRuleSerializer(
        help_text="The NfpRule data type is an expression of the conditions that shall be met in order for the NFP to be applicable to the packet",
        required=True)
    nfpState = serializers.ChoiceField(
        help_text="The state of the NFP instance.",
        choices=enum_to_list(NFP_STATE),
        required=True)


class VnffgInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this VNFFG instance.",
        required=True)
    vnffgdId = serializers.CharField(
        help_text="Identifier of the VNFFGD in the NSD.",
        required=True)
    vnfInstanceId = serializers.ListField(
        help_text="Identifier(s) of the constituent VNF instance(s) of this VNFFG instance.",
        child=serializers.CharField(
            help_text="ID of vnf instance"),
        required=True)
    pnfInfoId = serializers.ListField(
        help_text="Identifier(s) of the constituent PNF instance(s) of this VNFFG instance",
        child=serializers.CharField(help_text="ID of pnf info"),
        required=False,
        allow_null=True)
    nsVirtualLinkInfoId = serializers.ListField(
        help_text="Identifier(s) of the constituent VL instance(s) of thisVNFFG instance.",
        child=serializers.CharField(help_text="ID of ns virtual link info"),
        required=True)
    nsCpHandle = NsCpHandleSerializer(
        help_text="Identifiers of the CP instances attached to the "
                  "constituent VNFs and PNFs or the SAP instances of the VNFFG.",
        required=True,
        allow_null=False,
        many=True)
    nfpInfo = NfpInfoSerializer(
        help_text="Information on the NFP instances.",
        required=True,
        allow_null=False,
        many=True)


class SapInfo(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the SAP instance.",
        required=True)
    sapdId = serializers.CharField(
        help_text="Reference to the SAPD for this SAP.",
        required=True)
    sapName = serializers.CharField(
        help_text="Human readable name for the SAP.",
        required=True)
    description = serializers.CharField(
        help_text="Human readable description for the SAP. ",
        required=True)
    sapProtocolInfo = CpProtocolInfoSerializer(
        help_text="Parameters for configuring the network protocols on the SAP.",
        many=True,
        required=False,
        allow_null=True)


class NsLinkSerializer(serializers.Serializer):
    self = LinkSerializer(
        help_text="URI of this resource.",
        required=True)
    nestedNsInstances = LinkSerializer(
        help_text="Links to the nested NS instances of the present NS instance.",
        required=False,
        many=True)
    instantiate = LinkSerializer(
        help_text="Link to the instantiate task resource.",
        required=False,
        allow_null=False)
    terminate = LinkSerializer(
        help_text="Link to the terminate task resource.",
        required=False,
        allow_null=False)
    update = LinkSerializer(
        help_text="Link to the update task resource.",
        required=False,
        allow_null=False)
    scale = LinkSerializer(
        help_text="Link to the scale task resource.",
        required=False,
        allow_null=False)
    heal = LinkSerializer(
        help_text="Link to the heal task resource.",
        required=False,
        allow_null=False)


class NsInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the NS instance.",
        required=True)
    nsInstanceName = serializers.CharField(
        help_text="Human readable name of the NS instance.",
        required=True)
    nsInstanceDescription = serializers.CharField(
        help_text="Human readable description of the NS instance.",
        required=True)
    nsdId = serializers.CharField(
        help_text="Identifier of the NSD on which the NS instance is based.",
        required=True)
    nsdInvariantId = serializers.CharField(
        help_text="Identifier of the NSD in a version independent manner.",
        required=False)
    nsdInfoId = serializers.CharField(
        help_text="Identifier of the NSD information object on which the NS instance is based.",
        required=True)
    flavourId = serializers.CharField(
        help_text="Identifier of the NS deployment flavour applied to the NS instance.",
        required=False)
    vnfInstance = VnfInstanceSerializer(
        help_text="Information on constituent VNF(s) of the NS instance.",
        required=False,
        many=True)
    pnfInfo = PnfInfoSerializer(
        help_text="Information on constituent PNF(s) of the NS instance.",
        required=False,
        many=True)
    virtualLinkInfo = NsVirtualLinkInfoSerializer(
        help_text="Information on the VL(s) of the NS instance.",
        required=False,
        many=True)
    vnffgInfo = VnffgInfoSerializer(
        many=True,
        required=False,
        help_text="VNF Forward Graph Information.")
    sapInfo = SapInfo(
        many=True,
        required=False,
        help_text="Create data concerning the SAPs.")
    nestedNsInstanceId = serializers.ListField(
        help_text="Identifier of the nested NS(s) of the NS instance.",
        child=serializers.CharField(),
        required=False,
        allow_null=True)
    nsState = serializers.ChoiceField(
        help_text="The state of the NS instance.",
        choices=enum_to_list(INSTANTIATION_STATE),
        required=True,
        allow_null=True)
    nsScaleStatus = NsScaleInfoSerializer(
        help_text="Status of each NS scaling aspect declared in the applicable DF.",
        required=False,
        allow_null=True,
        many=True)
    additionalAffinityOrAntiAffinityRule = AffinityOrAntiAffinityRuleSerializer(
        help_text="Specifies additional affinity or anti-affinity constraint for the VNF instances to be instantiated as part of the NS instantiation.",
        many=True,
        required=False,
        allow_null=True)
    _links = NsLinkSerializer(
        help_text="The links of the NS instance.",
        required=True)
