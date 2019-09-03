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

from lcm.ns.serializers.sol.ext_virtual_link_info import ExtVirtualLinkInfoSerializer
from lcm.ns.serializers.sol.cp_serializers import AddressRangeSerializer
from lcm.ns.serializers.sol.resource_handle import ResourceHandleSerializer
from lcm.ns.serializers.sol.pub_serializers import ProblemDetailsSerializer, LinkSerializer
from lcm.ns.enum import LAYER_PROTOCOL, IPADDRESSES_TYPE, AFFINITY_OR_ANTIAFFIINTY_SCOPE, AFFINITY_OR_ANTIAFFIINTY, LCM_NOTIFICATION_STATUS, OPERATION_STATE_TYPE
from lcm.ns_vnfs.enum import STORAGE_CHANGE_TYPE, VNFC_CHANGE_TYPE, VL_CHANGE_TYPE, RESOURE_TYPE, RESOURCE_ID_TYPE, GRANT_OPERATION, VNF_NOTIFICATION_TYPE
from lcm.pub.utils.enumutil import enum_to_list


class ResourceDefinitionSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this ResourceDefinition, unique at least within the scope of the GrantRequest.",
        required=True
    )
    type = serializers.ChoiceField(
        help_text="Type of the resource definition referenced.",
        choices=enum_to_list(RESOURE_TYPE),
        required=True
    )
    vduId = serializers.CharField(
        help_text="Reference to the related VDU in the VNFD applicable to this resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceTemplateId = serializers.CharField(
        help_text="Reference to a resource template(such as VnfVirtualLinkDesc) in the VNFD.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resource = ResourceHandleSerializer(
        help_text="Resource information for an existing resource.",
        required=False,
        allow_null=True
    )


class ConstraintResourceRefSerializer(serializers.Serializer):
    idType = serializers.ChoiceField(
        help_text="The type of the identifier.",
        choices=enum_to_list(RESOURCE_ID_TYPE),
        required=True
    )
    resourceId = serializers.CharField(
        help_text="An actual resource-management-level identifier(idType=RES_MGMT), or an identifier that references a ResourceDefinition(idType=GRANT).",
        required=True
    )
    vimConnectionId = serializers.CharField(
        help_text="",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceProviderId = serializers.CharField(
        help_text="Identifier of the resource provider. It shall only be present when idType = RES_MGMT.",
        required=False,
        allow_null=True,
        allow_blank=True
    )


class PlacementConstraintSerializer(serializers.Serializer):
    affinityOrAntiAffinity = serializers.ChoiceField(
        help_text="The type of the constraint.",
        choices=enum_to_list(AFFINITY_OR_ANTIAFFIINTY),
        required=True
    )
    scope = serializers.ChoiceField(
        help_text="The scope of the placement constraint indicating the category of the place where the constraint applies.",
        choices=enum_to_list(AFFINITY_OR_ANTIAFFIINTY_SCOPE),
        required=True
    )
    resource = ConstraintResourceRefSerializer(
        help_text="References to resources in the constraint rule.",
        many=True,
        required=False
    )


class VimConstraintSerializer(serializers.Serializer):
    sameResourceGroup = serializers.BooleanField(
        help_text="Set to true when the constraint applies not only to the same VIM connection, but also to the same infrastructure resource group.",
        required=False
    )
    resource = ConstraintResourceRefSerializer(
        help_text="References to resources in the constraint rule.",
        many=True,
        required=False
    )


# class LinkSerializer(serializers.Serializer):
#     href = serializers.CharField(
#         help_text="URI of the referenced resource.",
#         required=True
#     )


class GrantRequestLinksSerializer(serializers.Serializer):
    vnfLcmOpOcc = LinkSerializer(
        help_text="Related VNF lifecycle management operation occurrence.",
        required=True
    )
    vnfInstance = LinkSerializer(
        help_text="Related VNF instance.",
        required=True
    )


class GrantRequestSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(
        help_text="Identifier of the VNF instance which this grant request is related to.",
        required=True
    )
    vnfLcmOpOccId = serializers.CharField(
        help_text="The identifier of the VNF lifecycle management operation occurrence associated to the GrantRequest.",
        required=False,  # TODO required
        allow_null=True,
        allow_blank=True
    )
    vnfdId = serializers.CharField(
        help_text="Identifier of the VNFD that defines the VNF for which the LCM operation is to be granted.",
        required=False,  # TODO required
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
        choices=enum_to_list(GRANT_OPERATION),
        required=True
    )
    isAutomaticInvocation = serializers.BooleanField(
        help_text="Set to true if this VNF LCM operation occurrence has been triggered by an automated procedure inside the VNFM, set to false otherwise.",
        required=True
    )
    instantiationLevelId = serializers.CharField(
        help_text="If operation=INSTANTIATE, the identifier of the instantiation level may be provided as an alternative way to define the resources to be added.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    addResources = ResourceDefinitionSerializer(
        help_text="List of resource definitions in the VNFD for resources to be added by the LCM operation.",
        many=True,
        required=False
    )
    tempResources = ResourceDefinitionSerializer(
        help_text="List of resource definitions in the VNFD for resources to be temporarily instantiated during the runtime of the LCM operation.",
        many=True,
        required=False
    )
    removeResources = ResourceDefinitionSerializer(
        help_text="Provides the definitions of resources to be removed by the LCM operation.",
        many=True,
        required=False
    )
    updateResources = ResourceDefinitionSerializer(
        help_text="Provides the definitions of resources to be modified by the LCM operation.",
        many=True,
        required=False
    )
    placementConstraints = PlacementConstraintSerializer(
        help_text="Placement constraints that the VNFM may send to the NFVO in order to influence the resource placement decision.",
        many=True,
        required=False
    )
    vimConstraints = VimConstraintSerializer(
        help_text="Used by the VNFM to require that multiple resources are managed through the same VIM connection.",
        many=True,
        required=False
    )
    additionalParams = serializers.DictField(
        help_text="Additional parameters passed by the VNFM.",
        # child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )
    _links = GrantRequestLinksSerializer(
        help_text="Links to resources related to this request.",
        required=False  # TODO required
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
        child=serializers.CharField(help_text="IdentifierLocal", allow_blank=True),
        required=False,
        allow_null=True
    )


class GrantInfoSerializer(serializers.Serializer):
    resourceDefinitionId = serializers.CharField(
        help_text="Identifier of the related ResourceDefinition from the related GrantRequest.",
        required=True
    )
    reservationId = serializers.CharField(
        help_text="The reservation identifier applicable to the VNFC/VirtualLink/VirtualStorage.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vimConnectionId = serializers.CharField(
        help_text="Identifier of the VIM connection to be used to manage this resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceProviderId = serializers.CharField(
        help_text="Identifies the entity responsible for the management of the virtualised resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    zoneId = serializers.CharField(
        help_text="Reference to the identifier of the ZoneInfo in the Grant.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceGroupId = serializers.CharField(
        help_text="Identifier of the infrastructure resource group.",
        required=False,
        allow_null=True,
        allow_blank=True
    )


class VimComputeResourceFlavourSerializer(serializers.Serializer):
    vimConnectionId = serializers.CharField(
        help_text="Identifier of the VIM connection to access the flavour referenced in this structure.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceProviderId = serializers.CharField(
        help_text="Identifies the entity responsible for the management of the virtualised resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfdVirtualComputeDescId = serializers.CharField(
        help_text="Identifier which references the virtual compute descriptor in the VNFD that maps to this flavour.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vimFlavourId = serializers.CharField(
        help_text="Identifier of the compute resource flavour in the resource management layer (i.e. VIM).",
        required=False,
        allow_null=True,
        allow_blank=True
    )


class VimSoftwareImageSerializer(serializers.Serializer):
    vimConnectionId = serializers.CharField(
        help_text="Identifier of the VIM connection to access the flavour referenced in this structure.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceProviderId = serializers.CharField(
        help_text="Identifies the entity responsible for the management of the virtualised resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfdSoftwareImageId = serializers.CharField(
        help_text="Identifier which references the software image descriptor in the VNFD.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vimSoftwareImageId = serializers.CharField(
        help_text="Identifier of the software image in the resource management layer (i.e. VIM).",
        required=False,
        allow_null=True,
        allow_blank=True
    )


class VimAssetsSerializer(serializers.Serializer):
    computeResourceFlavours = VimComputeResourceFlavourSerializer(
        help_text="Mappings between virtual compute descriptors defined in the VNFD and compute resource flavours managed in the VIM.",
        many=True,
        required=False
    )
    softwareImages = VimSoftwareImageSerializer(
        help_text="Mappings between software images defined in the VNFD and software images managed in the VIM.",
        many=True,
        required=False
    )


# class AddressRangeSerializer(serializers.Serializer):
#     minAddress = serializers.CharField(
#         help_text="Lowest IP address belonging to the range.",
#         required=True
#     )
#     maxAddress = serializers.CharField(
#         help_text="Highest IP address belonging to the range.",
#         required=True
#     )


class IpAddresseSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        help_text="The type of the IP addresses.",
        choices=enum_to_list(IPADDRESSES_TYPE),
        required=True
    )
    fixedAddresses = serializers.ListSerializer(
        help_text="Fixed addresses to assign.",
        child=serializers.CharField(help_text="IpAddress"),
        required=False,
        allow_null=True
    )
    numDynamicAddresses = serializers.IntegerField(
        help_text="Number of dynamic addresses to assign.",
        required=True
    )
    addressRange = AddressRangeSerializer(
        help_text="An IP address range to be used, e.g. in case of egress connections.",
        required=False,
        allow_null=True
    )
    subnetId = serializers.CharField(
        help_text="Subnet defined by the identifier of the subnet resource in the VIM.",
        required=False,
        allow_null=True,
        allow_blank=True
    )


class IpOverEthernetAddressSerializer(serializers.Serializer):
    macAddress = serializers.CharField(
        help_text="MAC address.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    ipAddresses = IpAddresseSerializer(
        help_text="List of IP addresses to assign to the CP instance.",
        many=True,
        required=False
    )


class CpProtocolDataConfigSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(
        help_text="Identifier of layer(s) and protocol(s).",
        choices=enum_to_list(LAYER_PROTOCOL),
        required=True
    )
    ipOverEthernet = IpOverEthernetAddressSerializer(
        help_text="Network address data for IP over Ethernet to assign to the extCP instance.",
        required=False,
        allow_null=True,
    )


class VnfExtCpConfigDataSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(
        help_text="Identifier of the external CP instance to which this set of configuration parameters is requested to be applied.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    linkPortId = serializers.CharField(
        help_text="Identifier of a pre-configured link port to which the external CP will be associated.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    cpProtocolData = CpProtocolDataConfigSerializer(
        help_text="Parameters for configuring the network protocols on the link port that connects the CP to a VL.",
        many=True,
        required=False
    )


class VnfExtCpSerializer(serializers.Serializer):
    cpdId = serializers.CharField(
        help_text="The identifier of the CPD in the VNFD.",
        required=True
    )
    cpConfig = VnfExtCpConfigDataSerializer(
        help_text="List of instance data that need to be configured on the CP instances created from the respective CPD.",
        many=True,
        required=False
    )


class ExtLinkPortSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this link port as provided by the entity that has created the link port.",
        required=True
    )
    resourceHandle = serializers.CharField(
        help_text="Reference to the virtualised resource realizing this link port.",
        required=True
    )


class ExtVirtualLinkSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="The identifier of the external VL instance.",
        required=True
    )
    vimConnectionId = serializers.CharField(
        help_text="Identifier of the VIM connection to manage this resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceProviderId = serializers.CharField(
        help_text="Identifies the entity responsible for the management of this resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceId = serializers.CharField(
        help_text="The identifier of the resource in the scope of the VIM or the resource provider.",
        required=True
    )
    extCps = VnfExtCpSerializer(
        help_text="External CPs of the VNF to be connected to this external VL.",
        many=True,
        required=False
    )
    extLinkPorts = ExtLinkPortSerializer(
        help_text="Externally provided link ports to be used to connect external connection points to this external VL.",
        many=True,
        required=False
    )


class ExtManagedVirtualLinkSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="The identifier of the externally-managed internal VL instance.",
        required=True
    )
    virtualLinkDescId = serializers.CharField(
        help_text="The identifier of the VLD in the VNFD for this VL.",
        required=True
    )
    vimConnectionId = serializers.CharField(
        help_text="Identifier of the VIM connection to manage this resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceProviderId = serializers.CharField(
        help_text="Identifies the entity responsible for the management of this resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceId = serializers.CharField(
        help_text="The identifier of the resource in the scope of the VIM or the resource provider.",
        required=True
    )


class GrantLinksSerializer(serializers.Serializer):
    self = LinkSerializer(
        help_text="URI of this resource.",
        required=True
    )
    vnfLcmOpOcc = LinkSerializer(
        help_text="Related VNF lifecycle management operation occurrence.",
        required=True
    )
    vnfInstance = LinkSerializer(
        help_text="Related VNF instance.",
        required=True
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
        required=False,  # TODO required
        allow_null=True,
        allow_blank=True
    )
    vimConnections = VimConnectionInfoSerializer(
        help_text="Provides information regarding VIM connections that are approved to be used by the VNFM to allocate resources.",
        many=True,
        required=False
    )
    zones = ZoneInfoSerializer(
        help_text="Identifies resource zones where the resources are approved to be allocated by the VNFM.",
        many=True,
        required=False
    )
    zoneGroups = ZoneGroupInfoSerializer(
        help_text="Information about groups of resource zones.",
        many=True,
        required=False
    )
    computeReservationId = serializers.CharField(
        help_text="Information that identifies a reservation applicable to the compute resource requirements.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    networkReservationId = serializers.CharField(
        help_text="Information that identifies a reservation applicable to the network resource requirements.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    storageReservationId = serializers.CharField(
        help_text="Information that identifies a reservation applicable to the storage resource requirements.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    addResources = GrantInfoSerializer(
        help_text="List of resources that are approved to be added.",
        many=True,
        required=False
    )
    tempResources = GrantInfoSerializer(
        help_text="List of resources that are approved to be temporarily instantiated during the runtime of the lifecycle operation.",
        many=True,
        required=False
    )
    removeResources = GrantInfoSerializer(
        help_text="List of resources that are approved to be removed.",
        many=True,
        required=False
    )
    updateResources = GrantInfoSerializer(
        help_text="List of resources that are approved to be modified.",
        many=True,
        required=False
    )
    vimAssets = VimAssetsSerializer(
        help_text="Information about assets for the VNF that are managed by the NFVO in the VIM.",
        required=False,
        allow_null=True
    )
    extVirtualLinks = ExtVirtualLinkSerializer(
        help_text="Information about external VLs to connect the VNF to.",
        many=True,
        required=False
    )
    extManagedVirtualLinks = ExtManagedVirtualLinkSerializer(
        help_text="Information about internal VLs that are managed by other entities than the VNFM.",
        many=True,
        required=False
    )
    additionalParams = serializers.DictField(
        help_text="Additional parameters passed by the NFVO, \
        specific to the VNF and the LCM operation.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )
    _links = GrantLinksSerializer(
        help_text="Links to resources related to this resource.",
        required=False
    )


class AffectedVnfcSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the Vnfc instance.",
        required=True
    )
    vduId = serializers.CharField(
        help_text="Identifier of the related VDU in the VNFD.",
        required=True
    )
    changeType = serializers.ChoiceField(
        help_text="Signals the type of change.",
        choices=enum_to_list(VNFC_CHANGE_TYPE),
        required=True
    )
    computeResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualCompute resource.",
        required=True
    )
    metadata = serializers.DictField(
        help_text="Metadata about this resource.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )
    affectedVnfcCpIds = serializers.ListSerializer(
        help_text="Identifiers of CP(s) of the VNFC instance that were affected by the change.",
        child=serializers.CharField(help_text="Identifier In Vnf", allow_blank=True),
        required=False,
        allow_null=True
    )
    addedStorageResourceIds = serializers.ListSerializer(
        help_text="References to VirtualStorage resources that have been added.",
        child=serializers.CharField(help_text="Identifier In Vnf", allow_blank=True),
        required=False,
        allow_null=True
    )
    removedStorageResourceIds = serializers.ListSerializer(
        help_text="References to VirtualStorage resources that have been removed.",
        child=serializers.CharField(help_text="Identifier In Vnf", allow_blank=True),
        required=False,
        allow_null=True
    )


class AffectedVirtualLinkSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the virtual link instance.",
        required=True
    )
    virtualLinkDescId = serializers.CharField(
        help_text="Identifier of the related VLD in the VNFD.",
        required=True
    )
    changeType = serializers.ChoiceField(
        help_text="Signals the type of change.",
        choices=enum_to_list(VL_CHANGE_TYPE),
        required=True
    )
    networkResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualNetwork resource.",
        required=False,
        allow_null=True
    )
    metadata = serializers.DictField(
        help_text="Metadata about this resource.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )


class AffectedVirtualStorageSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the storage instance.",
        required=True
    )
    virtualStorageDescId = serializers.CharField(
        help_text="Identifier of the related VirtualStorage descriptor in the VNFD.",
        required=True
    )
    changeType = serializers.ChoiceField(
        help_text="Signals the type of change.",
        choices=enum_to_list(STORAGE_CHANGE_TYPE),
        required=True
    )
    storageResource = ResourceHandleSerializer(
        help_text="Reference to the VirtualStorage resource.",
        required=False,
        allow_null=True
    )
    metadata = serializers.DictField(
        help_text="Metadata about this resource.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )


class VnfInfoModificationsSerializer(serializers.Serializer):
    vnfInstanceName = serializers.CharField(
        help_text="If present, this attribute signals modifications of the vnfInstanceName attribute in VnfInstance.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfInstanceDescription = serializers.CharField(
        help_text="If present, this attribute signals modifications of the vnfInstanceDescription attribute in VnfInstance.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfConfigurableProperties = serializers.DictField(
        help_text="If present, this attribute signals modifications of the vnfConfigurableProperties attribute in VnfInstance.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )
    metadata = serializers.DictField(
        help_text="If present, this attribute signals modifications of the metadata attribute in VnfInstance.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )
    extensions = serializers.DictField(
        help_text="If present, this attribute signals modifications of the extensions attribute in VnfInstance.",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )
    vimConnectionInfo = VimConnectionInfoSerializer(
        help_text="If present, this attribute signals modifications of the vimConnectionInfo attribute in VnfInstance.",
        many=True,
        required=False
    )
    vnfPkgId = serializers.CharField(
        help_text="If present, this attribute signals modifications of the vnfPkgId attribute in VnfInstance.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfdId = serializers.CharField(
        help_text="If present, this attribute signals modifications of the vnfdId attribute in VnfInstance.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfProvider = serializers.CharField(
        help_text="If present, this attribute signals modifications of the vnfProvider attribute in VnfInstance.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfProductName = serializers.CharField(
        help_text="If present, this attribute signals modifications of the vnfProductName attribute in VnfInstance.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfSoftwareVersion = serializers.CharField(
        help_text="If present, this attribute signals modifications of the vnfSoftwareVersion attribute in VnfInstance.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    vnfdVersion = serializers.CharField(
        help_text="If present, this attribute signals modifications of the vnfdVersion attribute in VnfInstance.",
        required=False,
        allow_null=True,
        allow_blank=True
    )


class ExtLinkPortInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this link port as provided by the entity that has created the link port.",
        required=True
    )
    resourceHandle = ResourceHandleSerializer(
        help_text="Reference to the virtualised resource realizing this link port.",
        required=True
    )
    cpInstanceId = serializers.CharField(
        help_text="Identifier of the external CP of the VNF connected to this link port.",
        required=False,
        allow_null=True,
        allow_blank=True
    )


# class ExtVirtualLinkInfoSerializer(serializers.Serializer):
#     id = serializers.CharField(
#         help_text="Identifier of the external VL and the related external VL information instance.",
#         required=True
#     )
#     resourceHandle = ResourceHandleSerializer(
#         help_text="Reference to the resource realizing this VL.",
#         required=True
#     )
#     extLinkPorts = ExtLinkPortInfoSerializer(
#         help_text="Link ports of this VL.",
#         many=True,
#         required=False
#     )


# class ProblemDetailsSerializer(serializers.Serializer):
#     type = serializers.CharField(
#         help_text="A URI reference according to IETF RFC 3986 [5] that identifies the problem type.",
#         required=False,
#         allow_null=True,
#         allow_blank=True
#     )
#     title = serializers.CharField(
#         help_text="A short, human-readable summary of the problem type.",
#         required=False,
#         allow_null=True,
#         allow_blank=True
#     )
#     status = serializers.IntegerField(
#         help_text="The HTTP status code for this occurrence of the problem.",
#         required=True
#     )
#     detail = serializers.CharField(
#         help_text="A human-readable explanation specific to this occurrence of the problem.",
#         required=True
#     )
#     instance = serializers.CharField(
#         help_text="A URI reference that identifies the specific occurrence of the problem.",
#         required=False,
#         allow_null=True,
#         allow_blank=True
#     )


class LccnLinksSerializer(serializers.Serializer):
    vnfInstance = LinkSerializer(
        help_text="Link to the resource representing the VNF instance to which the notified change applies.",
        required=True
    )
    subscription = LinkSerializer(
        help_text="Link to the related subscription.",
        required=True
    )
    vnfLcmOpOcc = LinkSerializer(
        help_text="Link to the VNF lifecycle management operation occurrence that this notification is related to.",
        required=False,
        allow_null=True
    )


class VnfLcmOperationOccurrenceNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this notification.",
        required=True
    )
    notificationType = serializers.ChoiceField(
        help_text="Discriminator for the different notification types.",
        choices=enum_to_list(VNF_NOTIFICATION_TYPE),
        required=True
    )
#     subscriptionId = serializers.CharField(
#         help_text="Identifier of the subscription that this notification relates to.",
#         required=True
#     )
    timeStamp = serializers.CharField(
        help_text="Date-time of the generation of the notification.",
        required=True
    )
    notificationStatus = serializers.ChoiceField(
        help_text="Indicates whether this notification reports about the start of a lifecycle operation or the result of a lifecycle operation.",
        choices=enum_to_list(LCM_NOTIFICATION_STATUS),
        required=True
    )
    operationState = serializers.ChoiceField(
        help_text="The state of the VNF LCM operation occurrence.",
        choices=enum_to_list(OPERATION_STATE_TYPE),
        required=True
    )
    vnfInstanceId = serializers.CharField(
        help_text="The identifier of the VNF instance affected.",
        required=True
    )
    operation = serializers.ChoiceField(
        help_text="The lifecycle management operation.",
        choices=enum_to_list(GRANT_OPERATION),
        required=True
    )
    isAutomaticInvocation = serializers.BooleanField(
        help_text="Set to true if this VNF LCM operation occurrence has been triggered by an automated procedure inside the VNFM.",
        required=True
    )
    vnfLcmOpOccId = serializers.CharField(
        help_text="The identifier of the VNF lifecycle management operation occurrence associated to the notification.",
        required=True
    )
    affectedVnfcs = AffectedVnfcSerializer(
        help_text="Information about VNFC instances that were affected during the lifecycle operation.",
        many=True,
        required=False
    )
    affectedVirtualLinks = AffectedVirtualLinkSerializer(
        help_text="Information about VL instances that were affected during the lifecycle operation.",
        many=True,
        required=False
    )
    affectedVirtualStorages = AffectedVirtualStorageSerializer(
        help_text="Information about virtualised storage instances that were affected during the lifecycle operation.",
        many=True,
        required=False
    )
#     changedInfo = VnfInfoModificationsSerializer(
#         help_text="Information about the changed VNF instance information, including changed VNF configurable properties.",
#         required=False,
#         allow_null=True
#     )
    changedExtConnectivity = ExtVirtualLinkInfoSerializer(
        help_text="Information about changed external connectivity.",
        many=True,
        required=False
    )
    error = ProblemDetailsSerializer(
        help_text="Details of the latest error, if one has occurred during executing the LCM operation",
        required=False,
        allow_null=True
    )
#     _links = LccnLinksSerializer(
#         help_text="Links to resources related to this notification.",
#         required=False,
#         allow_null=True
#     )
#
#
# class VnfIdentifierCreationNotificationSerializer(serializers.Serializer):
#     id = serializers.CharField(
#         help_text="Identifier of this notification. \
#         If a notification is sent multiple times due to multiple subscriptions, \
#         the id attribute of all these notifications shall have the same value.",
#         required=True,
#         allow_null=False,
#         allow_blank=False
#     )
#     notificationType = serializers.ChoiceField(
#         help_text="Discriminator for the different notification types.",
#         choices=enum_to_list(VNF_NOTIFICATION_TYPE),
#         required=True
#     )
#     subscriptionId = serializers.CharField(
#         help_text="Identifier of the subscription that this notification relates to.",
#         required=False,
#         allow_null=True,
#         allow_blank=True
#     )
#     timeStamp = serializers.DateTimeField(
#         help_text="Date-time of the generation of the notification.",
#         required=True,
#         allow_null=False,
#     )
#     vnfInstanceId = serializers.CharField(
#         help_text="The created VNF instance identifier.",
#         required=True,
#         allow_null=False,
#         allow_blank=False
#     )
#     _links = LccnLinksSerializer(
#         help_text="Links to resources related to this notification.",
#         required=True,
#         allow_null=False
#     )
#

class VnfIdentifierDeletionNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this notification. \
        If a notification is sent multiple times due to multiple subscriptions, \
        the id attribute of all these notifications shall have the same value.",
        required=True,
        allow_null=False,
        allow_blank=False
    )
    notificationType = serializers.ChoiceField(
        help_text="Discriminator for the different notification types.",
        choices=enum_to_list(VNF_NOTIFICATION_TYPE),
        required=True
    )
    subscriptionId = serializers.CharField(
        help_text="Identifier of the subscription that this notification relates to.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    timeStamp = serializers.DateTimeField(
        help_text="Date-time of the generation of the notification.",
        required=True,
        allow_null=False,
    )
    vnfInstanceId = serializers.CharField(
        help_text="The deleted VNF instance identifier.",
        required=True,
        allow_null=False,
        allow_blank=False
    )
    _links = LccnLinksSerializer(
        help_text="Links to resources related to this notification.",
        required=True,
        allow_null=False
    )
