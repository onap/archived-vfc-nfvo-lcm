# Copyright (c) 2018, CMCC Technologies Co., Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework import serializers


class VnfInstanceDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Specify the target NS instance where the VNF instances are "
                                                    "moved to", required=True)
    vnfProfileId = serializers.CharField(help_text="Specify the VNF instance that is moved.",
                                         required=False, allow_null=True)


class InstantiateVnfDataSerializer(serializers.Serializer):
    vnfdId = serializers.CharField(help_text="Information sufficient to identify the VNFD which defines the VNF to be"
                                             " instantiated. ", required=True)
    vnfFlavourId = serializers.CharField(help_text="Identifier of the VNF deployment flavour to be instantiated.",
                                         required=True)
    vnfInstantiationLevelId = serializers.CharField(help_text="Identifier of the instantiation level of the deployment "
                                                              "flavour to be instantiated. ", required=False,
                                                    allow_null=True)
    vnfInstanceName = serializers.CharField(help_text="Human-readable name of the VNF instance to be created.",
                                            required=False, allow_null=True)


class IpOverEthernetAddressDataSerializer(serializers.Serializer):
    macAddress = serializers.CharField(help_text="Mac address", required=False, allow_null=True)
    ipAddresses = serializers.ListField(help_text="List of IP addresses to assign to the extCP instance.",
                                        required=False, allow_null=True)


class CpProtocolDataSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(help_text="Identifier of layer(s) and protocol(s).",
                                            choices=["IP_OVER_ETHERNET"], required=True)
    ipOverEthernet = IpOverEthernetAddressDataSerializer(
        help_text="Network address data for IP over Ethernet to assign to the extCP instance.",
        required=False, allow_null=True)


class VnfExtCpConfigSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="Identifier of the external CP instance to which this set of "
                                                   "configuration parameters is requested to be applied.",
                                         required=False, allow_null=True)
    linkPortId = serializers.CharField(help_text="Identifier of a pre-conFigured link port to which the external CP "
                                                 "will be associated.", required=False, allow_null=True)
    cpProtocolData = serializers.ListField(help_text="Parameters for configuring the network protocols on the link "
                                                     "port that connects the CP to a VL",
                                           child=(CpProtocolDataSerializer(help_text="This type represents network "
                                                                                     "protocol data.", required=True)),
                                           required=False, allow_null=True)


class VnfExtCpData(serializers.Serializer):
    cpdId = serializers.CharField(help_text="The identifier of the CPD in the VNFD.", required=True)
    cpConfig = serializers.ListField(help_text="List of instance data that need to be conFigured on the CP instances "
                                               "created from the respective CPD.",
                                     child=(VnfExtCpConfigSerializer(help_text="Config of vnf ext cp", required=True)),
                                     required=False, allow_null=True)


class ResourceHandleSerializer(serializers.Serializer):
    vimId = serializers.CharField(help_text="Identifier of the VIM under whose control this resource is placed.",
                                  required=False, allow_null=True)
    resourceProviderId = serializers.CharField(help_text="Identifier of the entity responsible for the management of "
                                                         "the resource.", required=False, allow_null=True)
    resourceId = serializers.CharField(help_text="Identifier of the resource in the scope of the VIM or the "
                                                 "resource provider.", required=True)
    vimLevelResourceType = serializers.CharField(help_text="Type of the resource in the scope of the VIM or the "
                                                           "resource provider.", required=False, allow_null=True)


class ExtLinkPortDataSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Provided by the entity that has created the link port", required=True)
    resourceHandle = ResourceHandleSerializer(help_text="Identifier(s) of the virtualised network resource(s) "
                                                        "realizing the VL instance", required=True)


class ExtVirtualLinkDataSerializer(serializers.Serializer):
    extVirtualLinkId = serializers.CharField(help_text="The identifier of the external VL instance, if provided. ",
                                             required=False, allow_null=True)
    vimId = serializers.CharField(help_text="Identifier of the VIM that manages this resource.",
                                  required=False, allow_null=True)
    resourceProviderId = serializers.CharField(help_text="Identifies the entity responsible for the management of "
                                                         "this resource.", required=False, allow_null=True)
    resourceId = serializers.CharField(help_text="The identifier of the resource in the scope of the VIM or the"
                                                 " resource provider.", required=True)
    extCps = serializers.ListField(VnfExtCpData(help_text="External CPs of the VNF to be connected to this external "
                                                          "VL.", required=True), required=False, allow_null=True)
    extLinkPorts = serializers.ListField(help_text="Externally provided link ports to be used to connect external "
                                                   "connection points to this external VL. ",
                                         child=(ExtLinkPortDataSerializer(help_text="This type represents an externally"
                                                                                    "provided link port to be used to "
                                                                                    "connect a VNF external connection "
                                                                                    "point to an external VL",
                                                                          required=True)),
                                         required=False, allow_null=True)


class ExtManagedVirtualLinkDataSerializer(serializers.Serializer):
    extManagedVirtualLinkId = serializers.CharField(help_text="The identifier of the externally-managed internal VL "
                                                              "instance,if provided.", required=False, allow_null=True)
    virtualLinkDescId = serializers.CharField(help_text="The identifier of the VLD in the VNFD for this VL.",
                                              required=True)

    vimId = serializers.CharField(help_text="Identifier of the VIMthat manage this resource.",
                                  required=False, allow_null=True)

    resourceProviderId = serializers.CharField(help_text="Identifies the entity responsible for the management of"
                                                         "this resource.", required=False, allow_null=True)
    resourceId = serializers.CharField(help_text="The identifier of the resource in the scope of the VIM or"
                                                 "the resource provider.", required=True)


class ChangeVnfFlavourDataSerizlizer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Identifier of the VNF instance to be modified.", required=True)
    newFlavourId = serializers.CharField(help_text="Identifier of the VNF deployment flavour to be instantiated.",
                                         required=True)
    instantiationLevelId = serializers.CharField(help_text="Identifier of the instantiation level of the deployment "
                                                           "flavour to be instantiated.",
                                                 required=False, allow_null=True)
    extVirtualLinks = serializers.ListField(help_text="Information about external VLs to connect the VNF to.",
                                            child=(ExtVirtualLinkDataSerializer(help_text="This type represents "
                                                                                          "an external VL",
                                                                                required=True)),
                                            required=False, allow_null=True)
    extManagedVirtualLinks = serializers.ListField(help_text="Information about internal VLs that are managed by NFVO",
                                                   child=ExtManagedVirtualLinkDataSerializer(
                                                       help_text="This type represents an externally-managed internal"
                                                                 "VL.", required=True), required=False, allow_null=True)
    additionalParams = serializers.CharField(help_text="Additional input parameters for the flavour change process",
                                             required=False, allow_null=True)


class OperationalStatesSerializer(serializers.Serializer):
    OperationalStates = serializers.ChoiceField(help_text="State of operation",
                                                choices=["STARTED", "STOPPED"])


class OperateVnfDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Identifier of the VNF instance.", required=True)
    changeStateTo = OperationalStatesSerializer(help_text="The desired operational state to change the VNF to.",
                                                required=True)
    stopType = serializers.ChoiceField(help_text="It signals whether forceful or graceful stop is requested.",
                                       choices=["FORCEFUL ", "GRACEFUL"], required=False, allow_null=True)
    gracefulStopTimeout = serializers.CharField(help_text="The time interval to wait for the VNF to be taken out of"
                                                          "service during graceful stop.",
                                                required=False, allow_null=True)


class ModifyVnfInfoDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Identifier of the VNF instance", required=True)
    vnfInstanceName = serializers.CharField(help_text="New value of the vnfInstanceName attribute in VnfInstance",
                                            required=False, allow_null=True)
    vnfInstanceDescription = serializers.CharField(help_text="New value of the vnfInstanceDescription attribute in"
                                                             "VnfInstance", required=False, allow_null=True)


class ChangeExtVnfConnectivityDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Identifier of the VNF instance.", required=True, allow_null=True)
    extVirtualLinks = serializers.ListField(help_text="Information about external VLs to change",
                                            child=(ExtVirtualLinkDataSerializer(
                                                help_text="Data of ext virtual link", required=True)),
                                            required=False, allow_null=True)
    additionalParams = serializers.CharField(help_text="Additional parameters passed by the OSS as input to the "
                                                       "external connectivity change process",
                                             required=False, allow_null=True)


class SapDataSerializer(serializers.Serializer):
    sapdId = serializers.CharField(help_text="Reference to the SAPD for this SAP.", required=True)
    sapName = serializers.CharField(help_text="Human readable name for the SAP.", required=True)
    description = serializers.CharField(help_text="Human readable description for the SAP. ", required=True)
    sapProtocolData = serializers.ListField(help_text="Parameters for configuring the network protocols on the SAP.",
                                            child=(CpProtocolDataSerializer(
                                                help_text="This type represents network protocol data.", required=True)),
                                            required=False, allow_null=True)


class AssocNewNsdVersionDataSerializer(serializers.Serializer):
    newNsdId = serializers.CharField(help_text="Identifier of the new NSD version that is to be associated to the NS "
                                               "instance. ", required=True)


class MoveVnfInstanceDataSerializer(serializers.Serializer):
    targetNsInstanceId = serializers.CharField(help_text="Specify the target NS instance where the VNF instances "
                                                         "are moved to.", required=True)
    vnfInstanceId = serializers.CharField(help_text="Specify the VNF instance that is moved.",
                                          required=False, allow_null=True)


class NsCpHandleSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Identifier of the VNF instance associated to the CP instance.",
                                          required=False, allow_null=True)
    vnfExtCpInstanceId = serializers.CharField(help_text="Identifier of the VNF external CP instance in the scope "
                                                         "of the VNF instance. ", required=False, allow_null=True)
    pnfInfoId = serializers.CharField(help_text="Identifier of the PNF instance associated to the CP instance.",
                                      required=False, allow_null=True)
    pnfExtCpInstanceId = serializers.CharField(help_text="Identifier of the PNF external CP instance in the scope "
                                                         "of the PNF.", required=False, allow_null=True)
    nsInstanceId = serializers.CharField(help_text="Identifier of the NS instance associated to the SAP instance.",
                                         required=False, allow_null=True)
    nsSapInstanceId = serializers.CharField(help_text="Identifier of the SAP instance in the scope of the NS instance",
                                            required=False, allow_null=True)


class PortRangeSerializer(serializers.Serializer):
    lowerPort = serializers.CharField(help_text="Identifies the lower bound of the port range. ", required=True)
    upperPort = serializers.CharField(help_text="Identifies the upper bound of the port range ", required=True)


class MaskSerializer(serializers.Serializer):
    startingPoint = serializers.CharField(help_text="Indicates the offset between the last bit of the source mac "
                                                    "address and the first bit of the sequence of bits to "
                                                    "be matched.", required=True)
    length = serializers.CharField(help_text="Indicates the number of bits to be matched. ", required=True)
    value = serializers.CharField(help_text="Provide the sequence of bit values to be matched. ", required=True)


class NfpRuleSerializer(serializers.Serializer):
    etherDestinationAddress = serializers.CharField(help_text="Indicates a destination Mac address ",
                                                    required=False, allow_null=True)
    etherSourceAddress = serializers.CharField(help_text="Indicates a source Mac address",
                                               required=False, allow_null=True)
    etherType = serializers.ChoiceField(help_text="Indicates the protocol carried over the Ethernet layer.",
                                        choices=["IPV4", "IPV6"], required=False, allow_null=True)
    vlanTag = serializers.CharField(help_text="Indicates a VLAN identifier in an IEEE 802.1Q-2014 tag [6] ",
                                    required=False, allow_null=True)
    protocol = serializers.ChoiceField(help_text="Indicates the L4 protocol",
                                       choices=["TCP", "UDP", "ICMP"], required=False, allow_null=True)
    dscp = serializers.CharField(help_text="For IPv4 [7] a string of 0 and 1 digits that corresponds to the 6-bit "
                                           "Differentiated Services Code Point (DSCP) field of the IP header",
                                 required=False, allow_null=True)
    sourcePortRange = PortRangeSerializer(help_text="Indicates a range of source ports. ",
                                          required=False, allow_null=True)
    destinationPortRange = PortRangeSerializer(help_text="Indicates a range of destination ports.",
                                               required=False, allow_null=True)
    sourceIpAddressPrefix = serializers.CharField(
        help_text="Prefix of source ip address", required=False, allow_null=True)
    destinationIpAddressPrefix = serializers.CharField(
        help_text="Prefix of destination ip address", required=False, allow_null=True)
    extendedCriteria = serializers.ListField(help_text="Indicates values of specific bits in a frame.",
                                             child=(MaskSerializer(help_text="Mask serializer", required=True)),
                                             required=False, allow_null=True)


class NfpDataSerializer(serializers.Serializer):
    nfpInfoId = serializers.CharField(help_text="Identifier of the NFP to be modified.",
                                      required=False, allow_null=True)
    nfpName = serializers.CharField(help_text="Human readable name for the NFP.", required=False, allow_null=True)
    description = serializers.CharField(help_text="Human readable description for the NFP",
                                        required=False, allow_null=True)
    nsCpHandle = serializers.ListField(help_text="HanIdentifier(s) of the CPs and SAPs which the NFP passes by.",
                                       child=(NsCpHandleSerializer(
                                           help_text="This type represents an identifier of the CP or SAP instance.",
                                           required=True)), required=False, allow_null=True)
    nfpRule = NfpRuleSerializer(help_text="NFP classification and selection rule.", required=False, allow_null=True)


class UpdateVnffgDataSerializer(serializers.Serializer):
    vnffgInfoId = serializers.CharField(help_text="Identifier of an existing VNFFG to be updated for the NS Instance.",
                                        required=True)
    nfp = serializers.ListField(help_text="nfp", child=(NfpDataSerializer(help_text="This type contains information "
                                                                                    "used to create or modify NFP "
                                                                                    "instance parameters for the update"
                                                                                    "of an existing VNFFG instance. ",
                                                                          required=True)),
                                required=False, allow_null=True)
    nfpInfoId = serializers.ListField(help_text="Identifier(s) of the NFP to be deleted from a given VNFFG.",
                                      required=False, allow_null=True)


class ChangeNsFlavourDataSerializer(serializers.Serializer):
    newNsFlavourId = serializers.CharField(
        help_text="Identifier of the new NS DF to apply to this NS instance.", required=True)
    instantiationLevelId = serializers.CharField(
        help_text="Identifier of the instantiation level of the deployment flavour to be instantiated.",
        required=False, allow_null=True)


class IdentifierInPnfSerializer(serializers.Serializer):
    IdentifierInPnf = serializers.Serializer(help_text="An Identifier that is unique within respect to a PNF.")


class IdentifierInNsdSerializer(serializers.Serializer):
    IdentifierInNsd = serializers.Serializer(help_text="An identifier that is unique within a NS descriptor")


class PnfExtCpDataSerializer(serializers.Serializer):
    cpInstanceI16 = IdentifierInPnfSerializer(help_text="Identifier of the CP. Shall be present for existing CP.",
                                              required=False, allow_null=True)
    cpdId = IdentifierInNsdSerializer(help_text="Identifier of the Connection Point Descriptor (CPD) for this CP",
                                      required=False, allow_null=True)
    cpProtocolData = serializers.ListField(help_text="Address assigned for this CP.",
                                           child=(CpProtocolDataSerializer(
                                               help_text="This type represents network protocol data.", required=True)),
                                           required=False, allow_null=True)


class AddPnfDataSerializer(serializers.Serializer):
    pnfId = serializers.CharField(help_text="Identifier of the PNF.", required=True)
    pnfName = serializers.CharField(help_text="Name of the PNF.", required=True)
    pnfdId = serializers.CharField(help_text="Identifier of the PNFD on which the PNF is based.", required=True)
    pnfProfileId = serializers.CharField(
        help_text="Identifier of related PnfProfile in the NSD on which the PNF is based.", required=True)
    cpData = serializers.ListField(help_text="Address assigned for the PNF external CP(s). ",
                                   child=(PnfExtCpDataSerializer(
                                       help_text="Serializer data of pnf ext cp", required=True)),
                                   required=False, allow_null=True)


class ModifyPnfDataSerializer(serializers.Serializer):
    pnfId = serializers.CharField(help_text="Identifier of the PNF.", required=True)
    pnfName = serializers.CharField(help_text="Name of the PNF", required=False, allow_null=True)
    cpData = serializers.ListField(
        help_text="Address assigned for the PNF external CP(s).",
        child=(PnfExtCpDataSerializer(
            help_text="This type represents the configuration data on the external CP of the PNF.")),
        required=False, allow_null=True)


class DateTimeSerializer(serializers.Serializer):
    DateTime = serializers.Serializer(help_text="Date-time stamp.")


class UpdateNsReqSerializer(serializers.Serializer):
    updateType = serializers.ChoiceField(help_text="The type of update.",
                                         choices=["ADD_VNF", "REMOVE_VNF", "INSTANTIATE_VNF", "CHANGE_VNF_DF",
                                                  "OPERATE_VNF", "MODIFY_VNF_INFORMATION",
                                                  "CHANGE_EXTERNAL_VNF_CONNECTIVITY", "REMOVE_SAP", "ADD_NESTED_NS",
                                                  "REMOVE_NESTED_NS", "ASSOC_NEW_NSD_VERSION", "MOVE_VNF", "ADD_VNFFG",
                                                  "REMOVE_VNFFG", "UPDATE_VNFFG", "CHANGE_NS_DF", "ADD_PNF",
                                                  "MODIFY_PNF", "REMOVE_PNF"], required=True)
    addVnfInstance = serializers.ListField(help_text="Identifies an existing VNF instance to be added to the NS "
                                                     "instance.",
                                           child=(VnfInstanceDataSerializer(help_text="Data of vnf instance",
                                                                            required=True)),
                                           required=False, allow_null=True)
    removeVnfInstanceId = serializers.ListField(help_text="Identifies an existing VNF instance to be removed from "
                                                          "the NS instance.", required=False, allow_null=True)
    instantiateVnfData = serializers.ListField(help_text="Identifies the new VNF to be instantiated.",
                                               child=(InstantiateVnfDataSerializer(help_text="Data of vnf instance",
                                                                                   required=True)),
                                               required=False, allow_null=True)
    changeVnfFlavourData = serializers.ListField(help_text="Identifies the new DF of the VNF instance to be "
                                                           "changed to.",
                                                 child=(ChangeVnfFlavourDataSerizlizer(
                                                     help_text="The type represents the information that is requested "
                                                               "to be changed deployment flavour for an existing "
                                                               "VNF instance.", required=True)),
                                                 required=False, allow_null=True)
    operateVnfData = serializers.ListField(help_text="This type represents a VNF instance for which the operational "
                                                     "state needs to be changed and the requested new state.",
                                           child=(OperateVnfDataSerializer(
                                               help_text="This type represents a VNF instance for which the operational"
                                                         " state needs to be changed and the requested new state",
                                                         required=True)), required=False, allow_null=True)
    modifyVnfInfoData = serializers.ListField(help_text="This type represents the information that is requested to be"
                                                        " modified for a VNF instance. ",
                                              child=(ModifyVnfInfoDataSerializer(
                                                  help_text="This type represents the information that is requested to "
                                                            "be modified for a VNF instance. ", required=True)),
                                              required=False, allow_null=True)
    changeExtVnfConnectivityData = serializers.ListField(help_text="Specifies the new external connectivity data of the"
                                                                   "VNF instance to be changed",
                                                         child=(ChangeExtVnfConnectivityDataSerializer(
                                                             help_text="This type describes the information invoked by"
                                                                       "the NFVO to change the external VNF "
                                                                       "connectivity information maintained by"
                                                                       " the VNFM.", required=True)),
                                                         required=False, allow_null=True)
    addSap = serializers.ListField(help_text="Identifies a new SAP to be added to the NS instance.",
                                   child=(SapDataSerializer(help_text="This type represents the information related to "
                                                                      "a SAP of a NS", required=True)),
                                   required=False, allow_null=True)
    removeSapId = serializers.ListField(help_text="The identifier an existing SAP to be removed from the "
                                                  "NS instance", required=False, allow_null=True)
    addNestedNsId = serializers.ListField(help_text="The identifier of an existing nested NS instance to be added to "
                                                    "the NS instance", required=False, allow_null=True)
    removeNestedNsId = serializers.ListField(help_text="The identifier of an existing nested NS instance to be "
                                                       "removed from the NS instance.",
                                             required=False, allow_null=True)
    assocNewNsdVersionData = AssocNewNsdVersionDataSerializer(help_text="Specify the new NSD to be used for the NS "
                                                                        "instance.", required=False, allow_null=True)
    moveVnfInstanceData = serializers.ListField(help_text="Specify existing VNF instance to be moved from one NS "
                                                          "instance to another NS instance",
                                                child=(MoveVnfInstanceDataSerializer()),
                                                required=False, allow_null=True)
    addVnffg = serializers.ListField(help_text="The identifier of an existing nested NS instance to be added to the"
                                               " NS instance.", required=False, allow_null=True)
    removeVnffgId = serializers.ListField(help_text="The identifier of an existing nested NS instance to be removed "
                                                    "from the NS instance", required=False, allow_null=True)
    updateVnffg = serializers.ListField(help_text="Specify the new VNFFG Information data to be updated for a VNFFG"
                                                  " of the NS Instance",
                                        child=(UpdateVnffgDataSerializer(help_text="This type specifies the parameters "
                                                                                   "used for the update of an existing "
                                                                                   "VNFFG instance.", required=True)),
                                        required=False, allow_null=True)
    changeNsFlavourData = ChangeNsFlavourDataSerializer(
        help_text="Specifies the new DF to be applied to the NS instance", required=False, allow_null=True)
    addPnfData = serializers.ListField(help_text="Specifies the PNF to be added into the NS instance.",
                                       child=(AddPnfDataSerializer(help_text="Serializer data of add pnf", required=True)),
                                       required=False, allow_null=True)
    modifyPnfData = serializers.ListField(help_text="Specifies the PNF to be modified in the NS instance.",
                                          child=(ModifyPnfDataSerializer(
                                              help_text="This type specifies an PNF to be modified in the NS instance.",
                                              required=True)),
                                          required=False, allow_null=True)
    removePnfId = serializers.ListField(help_text="Identifier of the PNF to be deleted from the NS instance.",
                                        required=False, allow_null=True)
    updateTime = DateTimeSerializer(help_text="Timestamp indicating the update time of the NS",
                                    required=False, allow_null=True)
