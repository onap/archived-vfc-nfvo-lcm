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


class ResourceHandleSerializer(serializers.Serializer):
    vimConnectionId = serializers.CharField(
        help_text="Identifier of the VIM connection to manage the resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceProviderId = serializers.CharField(
        help_text="Identifier of the entity responsible for the management of the resource.",
        required=False,
        allow_null=True,
        allow_blank=True
    )
    resourceId = serializers.CharField(
        help_text="Identifier of the resource in the scope of the VIM or the resource provider.",
        required=True
    )
    vimLevelResourceType = serializers.CharField(
        help_text="Type of the resource in the scope of the VIM or the resource provider.",
        required=False,
        allow_null=True,
        allow_blank=True
    )


class ResourceDefinitionSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this ResourceDefinition, unique at least within the scope of the GrantRequest.",
        required=True
    )
    type = serializers.ChoiceField(
        help_text="Type of the resource definition referenced.",
        choices=["COMPUTE", "VL", "STORAGE", "LINKPORT"],
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
        choices=["RES_MGMT", "GRANT"],
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
        choices=["AFFINITY", "ANTI_AFFINITY"],
        required=True
    )
    scope = serializers.ChoiceField(
        help_text="The scope of the placement constraint indicating the category of the place where the constraint applies.",
        choices=["NFVI_POP", "ZONE", "ZONE_GROUP", "NFVI_NODE"],
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


class LinkSerializer(serializers.Serializer):
    href = serializers.CharField(
        help_text="URI of the referenced resource.",
        required=True
    )


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
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )
    _links = GrantRequestLinksSerializer(
        help_text="Links to resources related to this request.",
        required=False
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


class AddressRangeSerializer(serializers.Serializer):
    minAddress = serializers.CharField(
        help_text="Lowest IP address belonging to the range.",
        required=True
    )
    maxAddress = serializers.CharField(
        help_text="Highest IP address belonging to the range.",
        required=True
    )


class IpAddresseSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        help_text="The type of the IP addresses.",
        choices=["IPV4", "IPV6"],
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


class IpOverEthernetAddressDataSerializer(serializers.Serializer):
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


class CpProtocolDataSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(
        help_text="Identifier of layer(s) and protocol(s).",
        choices=["IP_OVER_ETHERNET"],
        required=True
    )
    ipOverEthernet = IpOverEthernetAddressDataSerializer(
        help_text="Network address data for IP over Ethernet to assign to the extCP instance.",
        required=False,
        allow_null=True,
    )


class VnfExtCpConfigSerializer(serializers.Serializer):
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
    cpProtocolData = CpProtocolDataSerializer(
        help_text="Parameters for configuring the network protocols on the link port that connects the CP to a VL.",
        many=True,
        required=False
    )


class VnfExtCpDataSerializer(serializers.Serializer):
    cpdId = serializers.CharField(
        help_text="The identifier of the CPD in the VNFD.",
        required=True
    )
    cpConfig = VnfExtCpConfigSerializer(
        help_text="List of instance data that need to be configured on the CP instances created from the respective CPD.",
        many=True,
        required=False
    )


class ExtLinkPortDataSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this link port as provided by the entity that has created the link port.",
        required=True
    )
    resourceHandle = serializers.CharField(
        help_text="Reference to the virtualised resource realizing this link port.",
        required=True
    )


class ExtVirtualLinkDataSerializer(serializers.Serializer):
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
    extCps = VnfExtCpDataSerializer(
        help_text="External CPs of the VNF to be connected to this external VL.",
        many=True,
        required=False
    )
    extLinkPorts = ExtLinkPortDataSerializer(
        help_text="Externally provided link ports to be used to connect external connection points to this external VL.",
        many=True,
        required=False
    )


class ExtManagedVirtualLinkDataSerializer(serializers.Serializer):
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
        required=False,
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
    extVirtualLinks = ExtVirtualLinkDataSerializer(
        help_text="Information about external VLs to connect the VNF to.",
        many=True,
        required=False
    )
    extManagedVirtualLinks = ExtManagedVirtualLinkDataSerializer(
        help_text="Information about internal VLs that are managed by other entities than the VNFM.",
        many=True,
        required=False
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
        choices=["ADDED", "REMOVED", "MODIFIED", "TEMPORARY"],
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


class VnfLcmOperationOccurrenceNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this notification.",
        required=True
    )
    notificationType = serializers.CharField(
        help_text="Discriminator for the different notification types.",
        required=True
    )
    subscriptionId = serializers.CharField(
        help_text="Identifier of the subscription that this notification relates to.",
        required=True
    )
    timeStamp = serializers.CharField(
        help_text="Date-time of the generation of the notification.",
        required=True
    )
    notificationStatus = serializers.ChoiceField(
        help_text="Indicates whether this notification reports about the start of a lifecycle operation or the result of a lifecycle operation.",
        choices=["START", "RESULT"],
        required=True
    )
    operationState = serializers.ChoiceField(
        help_text="The state of the VNF LCM operation occurrence.",
        choices=["STARTING", "PROCESSING", "COMPLETED", "FAILED_TEMP", "FAILED", "ROLLING_BACK", "ROLLED_BACK"],
        required=True
    )
    vnfInstanceId = serializers.CharField(
        help_text="The identifier of the VNF instance affected.",
        required=True
    )
    operation = serializers.ChoiceField(
        help_text="The lifecycle management operation.",
        choices=["INSTANTIATE", "SCALE", "SCALE_TO_LEVEL", "CHANGE_FLAVOUR", "TERMINATE", "HEAL", "OPERATE", "CHANGE_EXT_CONN", "MODIFY_INFO"],
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
