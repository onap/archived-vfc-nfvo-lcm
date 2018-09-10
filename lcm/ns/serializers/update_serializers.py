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
    linkPortId = serializers.CharField(help_text="ID of link prot", required=False, allow_null=True)
    cpProtocolData = serializers.ListField(help_text="Data of cp proto col",
                                           child=(CpProtocolDataSerializer(help_text="Data of cp proto col",
                                                                           required=True)),
                                           required=False, allow_null=True)


class VnfExtCpData(serializers.Serializer):
    cpdId = serializers.CharField(help_text="ID of cpd", required=True)
    cpConfig = serializers.ListField(help_text="Config of cp",
                                     child=(VnfExtCpConfigSerializer(help_text="Config of vnf ext cp", required=True)),
                                     required=False, allow_null=True)


class ExtVirtualLinkDataSerializer(serializers.Serializer):
    extVirtualLinkId = serializers.CharField(help_text="ID of ext virtual link", required=False, allow_null=True)
    vimId = serializers.CharField(help_text="ID of vim", required=False, allow_null=True)
    resourceProviderId = serializers.CharField(help_text="ID of resource provider", required=False, allow_null=True)
    resourceId = serializers.CharField(help_text="ID of resource", required=True)
    extCps = serializers.ListField(VnfExtCpData(help_text="Data of vnf ext cp", required=True),
                                   required=False, allow_null=True)


class ChangeVnfFlavourDataSerizlizer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of vnf instance", required=True)
    newFlavourId = serializers.CharField(help_text="ID of new flavour", required=True)
    instantiationLevelId = serializers.CharField(help_text="ID of instantiation level", required=False, allow_null=True)
    extVirtualLinks = serializers.ListField(help_text="Ext of virtual links",
                                            child=(ExtVirtualLinkDataSerializer(help_text="Data of ext virtual link",
                                                                                required=True)),
                                            required=False, allow_null=True)


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