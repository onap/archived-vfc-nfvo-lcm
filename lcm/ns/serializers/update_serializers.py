from rest_framework import serializers


class VnfInstanceDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="The id of vnf instance", required=True)
    vnfProfileId = serializers.CharField(help_text="The id of vnf profile", required=False, allow_null=True)


class InstantiateVnfDataSerializer(serializers.Serializer):
    vnfdId = serializers.CharField(help_text="ID of vnfd", required=True)
    vnfFlavourId = serializers.CharField(help_text="Id of vnf flavour", required=True)
    vnfInstantiationLevelId = serializers.CharField(help_text="Id of vnf instantiation level", required=False,
                                                    allow_null=True)
    vnfInstanceName = serializers.CharField(help_text="Name of vnf instance", required=False, allow_null=True)


class IpOverEthernetAddressDataSerializer(serializers.Serializer):
    macAddress = serializers.CharField(help_text="Mac address", required=False, allow_null=True)
    ipAddresses = serializers.ListField(help_text="IP address", required=False, allow_null=True)


class CpProtocolDataSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(help_text="layer proto col",
                                            choices=["IP_OVER_ETHERNET"], required=True)
    ipOverEthernet = IpOverEthernetAddressDataSerializer(help_text="Data of ip over ethernet address", required=False,
                                                         allow_null=True)


class VnfExtCpConfigSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="ID of cp instance", required=False, allow_null=True)
    linkPortId = serializers.CharField(help_text="ID of link port", required=False, allow_null=True)
    cpProtocolData = serializers.ListField(help_text="Data of cp proto col",
                                           child=(CpProtocolDataSerializer(help_text="Data of cp proto col",
                                                                           required=True)),
                                           required=False, allow_null=True)


class VnfExtCpData(serializers.Serializer):
    cpdId = serializers.CharField(help_text="ID of cpd", required=True)
    cpConfig = serializers.ListField(help_text="Config of cp",
                                     child=(VnfExtCpConfigSerializer(help_text="Config of vnf ext cp", required=True)),
                                     required=False, allow_null=True)


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
    extVirtualLinkId = serializers.CharField(help_text="ID of ext virtual link", required=False, allow_null=True)
    vimId = serializers.CharField(help_text="ID of vim", required=False, allow_null=True)
    resourceProviderId = serializers.CharField(help_text="ID of resource provider", required=False, allow_null=True)
    resourceId = serializers.CharField(help_text="ID of resource", required=True)
    extCps = serializers.ListField(VnfExtCpData(help_text="Data of vnf ext cp", required=True),
                                   required=False, allow_null=True)
    extLinkPorts = serializers.ListField(help_text="Ext link ports", child=(
        ExtLinkPortDataSerializer(help_text="Data of ext link port", required=True)), required=False, allow_null=True)


class ChangeVnfFlavourDataSerizlizer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of vnf instance", required=True)
    newFlavourId = serializers.CharField(help_text="ID of new flavour", required=True)
    instantiationLevelId = serializers.CharField(help_text="ID of instantiation level", required=False, allow_null=True)
    extVirtualLinks = serializers.ListField(help_text="Ext of virtual links",
                                            child=(ExtVirtualLinkDataSerializer(help_text="Data of ext virtual link",
                                                                                required=True)),
                                            required=False, allow_null=True)


class OperationalStatesSerializer(serializers.Serializer):
    OperationalStates = serializers.ChoiceField(help_text="State of operation",
                                                choices=["STARTED", "STOPPED"])


class StopTypeSerializer(serializers.Serializer):
    StopType = serializers.ChoiceField(help_text="Type of stop", choices=["FORCEFUL ", "GRACEFUL"])


class OperateVnfDataSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="ID of NS Instance", required=True)
    changeStateTo = OperationalStatesSerializer(help_text="Change state of start or stop", required=True)
    stopType = StopTypeSerializer(help_text="Stop of VNF after accepting the request", required=False, allow_null=True)
    gracefulStopTimeout = serializers.CharField(help_text="Timeout of NS", required=False, allow_null=True)


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
        NsCpHandleSerializer(help_text="Handle of nscp")), required=False, allow_null=True)
    nfpRule = NfpRuleSerializer(help_text="Rule of nfp", required=False, allow_null=True)


class UpdateVnffgDataSerializer(serializers.Serializer):
    vnffgInfoId = serializers.CharField(help_text="ID of vnf fg info", required=True)
    nfp = serializers.ListField(help_text="nfp", child=(NfpDataSerializer(help_text="Data of nfp", required=True)),
                                required=False, allow_null=True)
    nfpInfoId = serializers.ListField(help_text="ID of nfp info", required=False, allow_null=True)


class UpdateNsReqSerializer(serializers.Serializer):
    updateType = serializers.ChoiceField(help_text="Type of NS Update",
                                         choices=["ADD_VNF", "REMOVE_VNF", "INSTANTIATE_VNF", "CHANGE_VNF_DF",
                                                  "OPERATE_VNF", "MODIFY_VNF_INFORMATION",
                                                  "CHANGE_EXTERNAL_VNF_CONNECTIVITY", "REMOVE_SAP", "ADD_NESTED_NS",
                                                  "REMOVE_NESTED_NS", "ASSOC_NEW_NSD_VERSION", "MOVE_VNF", "ADD_VNFFG",
                                                  "REMOVE_VNFFG", "UPDATE_VNFFG", "CHANGE_NS_DF", "ADD_PNF",
                                                  "MODIFY_PNF", "REMOVE_PNF"], required=True)
    addVnfInstance = serializers.ListField(help_text="Add vnf instance",
                                           child=(VnfInstanceDataSerializer(help_text="Data of vnf instance",
                                                                            required=True)),
                                           required=False, allow_null=True)
    removeVnfInstanceId = serializers.ListField(help_text="ID of remove vnf instance", required=False, allow_null=True)
    instantiateVnfData = serializers.ListField(help_text="Instantiate data of vnf",
                                               child=(InstantiateVnfDataSerializer(help_text="Data of vnf instance",
                                                                                   required=True)),
                                               required=False, allow_null=True)
    changeVnfFlavourData = serializers.ListField(help_text="Change data of vnf flavour",
                                                 child=(ChangeVnfFlavourDataSerizlizer(help_text="Data of vnf flavour"
                                                                                                 "Changed",
                                                                                       required=True)),
                                                 required=False, allow_null=True)
    operateVnfData = serializers.ListField(help_text="Data of operate Vnf",
                                           child=(OperateVnfDataSerializer(help_text="Data of vnf operate",
                                                                           required=True)),
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
