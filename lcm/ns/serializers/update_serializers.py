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


class VnfInstanceDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Identifier of the existing VNF instance to be used in the NS.",
                                          required=True)
    vnfProfileId = serializers.CharField(
        help_text="Identifier of (Reference to) a vnfProfile defined in the NSD which the existing VNF instance "
                  "shall be matched with", required=False, allow_null=True)


class InstantiateVnfDataSerializer(serializers.Serializer):
    vnfdId = serializers.CharField(help_text="Information sufficient to identify the VNFD", required=True)
    vnfFlavourId = serializers.CharField(
        help_text="Identifier of the VNF deployment flavour to be instantiated.", required=True)
    vnfInstantiationLevelId = serializers.CharField(
        help_text="Identifier of the instantiation level of the deployment flavour to be instantiated.", required=False,
        allow_null=True)
    vnfInstanceName = serializers.CharField(help_text="Human-readable name of the VNF instance to be created.",
                                            required=False, allow_null=True)


class IpOverEthernetAddressDataSerializer(serializers.Serializer):
    macAddress = serializers.CharField(help_text="Mac address", required=False, allow_null=True)
    ipAddresses = serializers.ListField(help_text="IP address", required=False, allow_null=True)


class CpProtocolDataSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(help_text="Identifier of layer(s) and protocol(s).",
                                            choices=["IP_OVER_ETHERNET"], required=True)
    ipOverEthernet = IpOverEthernetAddressDataSerializer(
        help_text="Network address data for IP over Ethernet to assign to the extCP instance.",
        required=False, allow_null=True)


class VnfExtCpConfigSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="Identifier of the external CP instance to which this set of"
                                                   "configuration parameters is requested to be applied. ",
                                         required=False, allow_null=True)
    linkPortId = serializers.CharField(help_text="Identifier of a pre-conFigured link port to which the"
                                                 "external CP will be associated.", required=False, allow_null=True)
    cpProtocolData = serializers.ListField(help_text="Parameters for configuring the network protocols on the"
                                                     "link port that connects the CP to a VL",
                                           child=(CpProtocolDataSerializer(help_text="Data of cp proto col",
                                                                           required=True)),
                                           required=False, allow_null=True)


class VnfExtCpData(serializers.Serializer):
    cpdId = serializers.CharField(help_text="The identifier of the CPD in the VNFD", required=True)
    cpConfig = serializers.ListField(help_text="List of instance data that need to be conFigured on the CP instances"
                                               "created from the respective CPD.",
                                     child=(VnfExtCpConfigSerializer(help_text="This type represents an externally "
                                                                               "provided link port or network address "
                                                                               "information per instance of a VNF "
                                                                               "external connection point.",
                                                                     required=True)), required=False, allow_null=True)


class ResourceHandleSerializer(serializers.Serializer):
    vimId = serializers.CharField(help_text="ID of vim", required=False, allow_null=True)
    resourceProviderId = serializers.CharField(help_text="ID of resource provider", required=False, allow_null=True)
    resourceId = serializers.CharField(help_text="ID of resource", required=True)
    vimLevelResourceType = serializers.CharField(help_text="Type of vim level resource",
                                                 required=False, allow_null=True)


class ExtLinkPortDataSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="Provided by the entity that has created the link port", required=True)
    resourceHandle = ResourceHandleSerializer(help_text="The resource of handle", required=True)


class ExtVirtualLinkDataSerializer(serializers.Serializer):
    extVirtualLinkId = serializers.CharField(help_text="The identifier of the external VL instance, if provided.",
                                             required=False, allow_null=True)
    vimId = serializers.CharField(help_text="Identifier of the VIM that manages this resource.",
                                  required=False, allow_null=True)
    resourceProviderId = serializers.CharField(help_text="Identifies the entity responsible for the management of this"
                                                         "resource.", required=False, allow_null=True)
    resourceId = serializers.CharField(help_text="The identifier of the resource in the scope of the VIM or the"
                                                 "resource provider.", required=True)
    extCps = serializers.ListField(VnfExtCpData(help_text="External CPs of the VNF to be connected to this external VL",
                                                required=True),
                                   required=False, allow_null=True)
    extLinkPorts = serializers.ListField(help_text="Externally provided link ports to be used to connect external "
                                                   "connection points to this external VL.",
                                         child=(ExtLinkPortDataSerializer(help_text="Data of ext link port",
                                                                          required=True)),
                                         required=False, allow_null=True)


class IdentifierInVimSerializer(serializers.Serializer):
    IdentifierInVim = serializers.CharField(help_text="An identifier maintained by the VIM or other resource provider.")


class ExtManagedVirtualLinkDataSerializer(serializers.Serializer):
    extManagedVirtualLinkId = serializers.CharField(help_text="The identifier of the externally-managed internal VL"
                                                              "instance, if provided.", required=False, allow_null=True)

    virtualLinkDescId = serializers.CharField(help_text="The identifier of the VLD in the VNFD for this VL",
                                              required=True)

    resourceProviderId = serializers.CharField(help_text="Identifies the entity responsible for the management of"
                                                         "this resource.", required=False, allow_null=True)

    resourceId = IdentifierInVimSerializer(help_text="The identifier of the resource in the scope of the VIM or the"
                                                     "resource provider.", required=True)


class KeyValuePairsSerializer(serializers.Serializer):
    KeyValuePairs = serializers.CharField(help_text="This type represents a list of key-value pairs.")


class ChangeVnfFlavourDataSerizlizer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="Identifier of the VNF instance to be modified.", required=True)
    newFlavourId = serializers.CharField(help_text="Identifier of the VNF deployment flavour to be instantiated.",
                                         required=True)
    instantiationLevelId = serializers.CharField(help_text="Identifier of the instantiation level of the deployment "
                                                           "flavour to be instantiated.",
                                                 required=False, allow_null=True)
    extVirtualLinks = serializers.ListField(help_text="Information about external VLs to connect the VNF to.",
                                            child=(ExtVirtualLinkDataSerializer(
                                                help_text="This type represents an external VL", required=True)),
                                            required=False, allow_null=True)
    extManagedVirtualLinks = serializers.ListField(help_text="Information about internal VLs that are managed by NFVO.",
                                                   child=(ExtManagedVirtualLinkDataSerializer(
                                                       help_text="This type represents an externally-managed internal"
                                                                 "VL.", required=True)),
                                                   required=False, allow_null=True)
    additionalParams = KeyValuePairsSerializer(help_text="Additional input parameters for the flavour change process,",
                                               required=False, allow_null=True)


class OperationalStatesSerializer(serializers.Serializer):
    OperationalStates = serializers.ChoiceField(help_text="STARTED The VNF instance is up and running or the VNF"
                                                          "instance has been shut down. ",
                                                choices=["STARTED", "STOPPED"])


class StopTypeSerializer(serializers.Serializer):
    StopType = serializers.ChoiceField(help_text="Type of stop", choices=["FORCEFUL ", "GRACEFUL"])


class OperateVnfDataSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="Identifier of the VNF instance.", required=True)
    changeStateTo = OperationalStatesSerializer(help_text="The desired operational state", required=True)
    stopType = StopTypeSerializer(help_text="It signals whether forceful or graceful stop is requested.",
                                  required=False, allow_null=True)
    gracefulStopTimeout = serializers.CharField(help_text="The time interval (in seconds) to wait for the VNF to be "
                                                          "taken out of service during graceful stop",
                                                required=False, allow_null=True)


class ModifyVnfInfoDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of vnf instance", required=True)
    vnfInstanceName = serializers.CharField(help_text="Name of vnf instance", required=False, allow_null=True)
    vnfInstanceDescription = serializers.CharField(help_text="Description of vnf instance",
                                                   required=False, allow_null=True)


class ChangeExtVnfConnectivityDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of vnf instance", required=True, allow_null=True)
    newFlavourId = serializers.CharField(help_text="ID of new flavour", required=True, allow_null=True)
    instantiationLevelId = serializers.CharField(help_text="ID of instantiation level", required=False, allow_null=True)
    extVirtualLinks = serializers.ListField(help_text="ext virtual links", child=(ExtVirtualLinkDataSerializer(
        help_text="Data of ext virtual link", required=True)), required=False, allow_null=True)


class SapDataSerializer(serializers.Serializer):
    sapdId = serializers.CharField(help_text="ID of sap", required=True)
    sapName = serializers.CharField(help_text="Name of sap", required=True)
    description = serializers.CharField(help_text="Description of sap", required=True)
    sapProtocolData = serializers.ListField(help_text="Data of sap proto col", child=(
        CpProtocolDataSerializer(help_text="Data of cp proto col", required=True)), required=False, allow_null=True)


class AssocNewNsdVersionDataSerializer(serializers.Serializer):
    newNsdId = serializers.CharField(help_text="ID of new nsd", required=True)


class MoveVnfInstanceDataSerializer(serializers.Serializer):
    targetNsInstanceId = serializers.CharField(help_text="ID of target ns instance", required=True)
    vnfInstanceId = serializers.CharField(help_text="ID of vnf instance", required=False, allow_null=True)


class NsCpHandleSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of vnf instance", required=False, allow_null=True)
    vnfExtCpInstanceId = serializers.CharField(help_text="ID of vnf ext cp instance", required=False, allow_null=True)
    pnfInfoId = serializers.CharField(help_text="ID of pnf info", required=False, allow_null=True)
    pnfExtCpInstanceId = serializers.CharField(help_text="ID of pnf ext cp instance", required=False, allow_null=True)
    nsInstanceId = serializers.CharField(help_text="ID of ns instance", required=False, allow_null=True)
    nsSapInstanceId = serializers.CharField(help_text="ID of ns sap instance", required=False, allow_null=True)


class PortRangeSerializer(serializers.Serializer):
    lowerPort = serializers.CharField(help_text="Port of lower", required=True)
    upperPort = serializers.CharField(help_text="Port of upper", required=True)


class MaskSerializer(serializers.Serializer):
    startingPoint = serializers.CharField(help_text="Starting point", required=True)
    length = serializers.CharField(help_text="Length", required=True)
    value = serializers.CharField(help_text="Value", required=True)


class NfpRuleSerializer(serializers.Serializer):
    etherDestinationAddress = serializers.CharField(help_text="Mac address", required=False, allow_null=True)
    etherSourceAddress = serializers.CharField(help_text="Mac address", required=False, allow_null=True)
    etherType = serializers.ChoiceField(help_text="Type of ether",
                                        choices=["IPV4", "IPV6"], required=False, allow_null=True)
    vlanTag = serializers.CharField(help_text="Tag of vlan", required=False, allow_null=True)
    protocol = serializers.ChoiceField(help_text="Col of proto",
                                       choices=["TCP", "UDP", "ICMP"], required=False, allow_null=True)
    dscp = serializers.CharField(help_text="Dscp", required=False, allow_null=True)
    sourcePortRange = PortRangeSerializer(help_text="Range of source port", required=False, allow_null=True)
    destinationPortRange = PortRangeSerializer(help_text="Range of destination port", required=False, allow_null=True)
    sourceIpAddressPrefix = serializers.CharField(
        help_text="Prefix of source ip address", required=False, allow_null=True)
    destinationIpAddressPrefix = serializers.CharField(
        help_text="Perfix of destination ip address", required=False, allow_null=True)
    extendedCriteria = serializers.ListField(help_text="Criteria of extended",
                                             child=(MaskSerializer(help_text="Mask serializer", required=True)),
                                             required=False, allow_null=True)


class NfpDataSerializer(serializers.Serializer):
    nfpInfoId = serializers.CharField(help_text="ID of nfp info", required=False, allow_null=True)
    nfpName = serializers.CharField(help_text="Name of nfp", required=False, allow_null=True)
    description = serializers.CharField(help_text="Description of nfp", required=False, allow_null=True)
    nsCpHandle = serializers.ListField(help_text="Handle of nscp", child=(
        NsCpHandleSerializer(help_text="Handle of nscp", required=True)), required=False, allow_null=True)
    nfpRule = NfpRuleSerializer(help_text="Rule of nfp", required=False, allow_null=True)


class UpdateVnffgDataSerializer(serializers.Serializer):
    vnffgInfoId = serializers.CharField(help_text="ID of vnf fg info", required=True)
    nfp = serializers.ListField(help_text="nfp", child=(NfpDataSerializer(help_text="Data of nfp", required=True)),
                                required=False, allow_null=True)
    nfpInfoId = serializers.ListField(help_text="ID of nfp info", required=False, allow_null=True)


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
    addVnfInstance = serializers.ListField(
        help_text="Identifies an existing VNF instance to be added to the NS instance.",
        child=(VnfInstanceDataSerializer(
            help_text="This type specifies an existing VNF instance to be used in the NS instance and if needed",
            required=True)), required=False, allow_null=True)
    removeVnfInstanceId = serializers.ListField(
        help_text="Identifies an existing VNF instance to be removed from the NS instance. ",
        required=False, allow_null=True)
    instantiateVnfData = serializers.ListField(help_text="Identifies the new VNF to be instantiated.",
                                               child=(InstantiateVnfDataSerializer(
                                                   help_text="This type represents the information related to a SAP "
                                                             "of a NS.", required=True)),
                                               required=False, allow_null=True)
    changeVnfFlavourData = serializers.ListField(help_text="Identifies the new DF of the VNF instance to be changed to",
                                                 child=(ChangeVnfFlavourDataSerizlizer(
                                                     help_text="The type represents the information that is requested "
                                                               "to be changed deployment flavour for an existing VNF"
                                                               " instance.", required=True)),
                                                 required=False, allow_null=True)
    operateVnfData = serializers.ListField(help_text="Identifies the state of the VNF instance to be changed.",
                                           child=(OperateVnfDataSerializer(help_text="This type represents a VNF "
                                                                                     "instance for which the "
                                                                                     "operational state needs to be"
                                                                                     " changed and the requested new "
                                                                                     "state.", required=True)),
                                           required=False, allow_null=True)
    modifyVnfInfoData = serializers.ListField(help_text="Data of modify vnf",
                                              child=(ModifyVnfInfoDataSerializer(help_text="Data of modify vnf info",
                                                                                 required=True)),
                                              required=False, allow_null=True)
    changeExtVnfConnectivityData = serializers.ListField(help_text="Data of ext changed  in vnf connectivity",
                                                         child=(ChangeExtVnfConnectivityDataSerializer(
                                                             help_text="Data of change ext vnf connectivity",
                                                             required=True)),
                                                         required=False, allow_null=True)
    addSap = serializers.ListField(help_text="Add Sap",
                                   child=(SapDataSerializer(help_text="Data of sap", required=True)),
                                   required=False, allow_null=True)
    removeSapId = serializers.ListField(help_text="Id of sap removed", required=False, allow_null=True)
    addNestedNsId = serializers.ListField(help_text="Id of ns add nested", required=False, allow_null=True)
    removeNestedNsId = serializers.ListField(help_text="Id of ns remove nested", required=False, allow_null=True)
    assocNewNsdVersionData = AssocNewNsdVersionDataSerializer(help_text="Data of assoc new nsd version",
                                                              required=False, allow_null=True)
    moveVnfInstanceData = serializers.ListField(help_text="Data of move vnf instance",
                                                child=(MoveVnfInstanceDataSerializer()),
                                                required=False, allow_null=True)
    addVnffg = serializers.ListField(help_text="Add vnf fg", required=False, allow_null=True)
    removeVnffgId = serializers.ListField(help_text="Id of remove vnf fg", required=False, allow_null=True)
    updateVnffg = serializers.ListField(help_text="Update vnf fg",
                                        child=(UpdateVnffgDataSerializer(
                                            help_text="Data of update vnf fg", required=True)),
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
