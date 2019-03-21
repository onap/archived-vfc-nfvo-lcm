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
from lcm.ns_pnfs.serializers.pnf_serializer import PnfInstanceSerializer


class _ContextSerializer(serializers.Serializer):
    globalCustomerId = serializers.CharField(help_text="Global customer ID", required=False, allow_null=True, allow_blank=True)
    serviceType = serializers.CharField(help_text="Service type", required=False, allow_null=True, allow_blank=True)


class _CreateNsReqSerializer(serializers.Serializer):
    csarId = serializers.CharField(help_text="Package ID of NS", required=False, allow_null=True, allow_blank=True)
    nsName = serializers.CharField(help_text="Name of NS", required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(help_text="Description of NS", required=False, allow_null=True, allow_blank=True)
    context = _ContextSerializer(help_text="Context of NS", required=False)


class _CreateNsRespSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=True)


class _VnfInstSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of VNF instance", required=True)
    vnfInstanceName = serializers.CharField(help_text="Name of VNF instance", required=False, allow_null=True, allow_blank=True)
    vnfdId = serializers.CharField(help_text="ID of VNFD", required=False, allow_null=True, allow_blank=True)


class _CpInstInfoSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="ID of CP instance", required=True)
    cpInstanceName = serializers.CharField(help_text="Name of CP instance", required=False, allow_null=True, allow_blank=True)
    cpdId = serializers.CharField(help_text="ID of CPD", required=False, allow_null=True, allow_blank=True)


class _VlInstSerializer(serializers.Serializer):
    vlInstanceId = serializers.CharField(help_text="ID of VL instance", required=True)
    vlInstanceName = serializers.CharField(help_text="Name of VL instance", required=False, allow_null=True, allow_blank=True)
    vldId = serializers.CharField(help_text="ID of VLD", required=False, allow_null=True, allow_blank=True)
    relatedCpInstanceId = _CpInstInfoSerializer(help_text="Related CP instances", many=True)


class _VnffgInstSerializer(serializers.Serializer):
    vnffgInstanceId = serializers.CharField(help_text="ID of VNFFG instance", required=True)
    vnfdId = serializers.CharField(help_text="ID of VNFD", required=False, allow_null=True, allow_blank=True)
    pnfId = serializers.CharField(help_text="ID of PNF", required=False, allow_null=True, allow_blank=True)
    virtualLinkId = serializers.CharField(help_text="ID of virtual link", required=False, allow_null=True, allow_blank=True)
    cpdId = serializers.CharField(help_text="ID of CPD", required=False, allow_null=True, allow_blank=True)
    nfp = serializers.CharField(help_text="nfp", required=False, allow_null=True, allow_blank=True)


class _QueryNsRespSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=True)
    nsName = serializers.CharField(help_text="Name of NS instance", required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(help_text="Description of NS instance", required=False, allow_null=True, allow_blank=True)
    nsdId = serializers.CharField(help_text="ID of NSD", required=True)
    vnfInfo = _VnfInstSerializer(help_text="VNF instances", many=True, required=False, allow_null=True)
    pnfInfo = PnfInstanceSerializer(help_text="PNF instances", many=True, required=False, allow_null=True)
    vlInfo = _VlInstSerializer(help_text="VL instances", many=True, required=False, allow_null=True)
    vnffgInfo = _VnffgInstSerializer(help_text="VNFFG instances", many=True, required=False, allow_null=True)
    nsState = serializers.CharField(help_text="State of NS instance", required=False, allow_null=True, allow_blank=True)


class _VnfLocationSerializer(serializers.Serializer):
    vimId = serializers.CharField(help_text="ID of VIM", required=False, allow_null=True, allow_blank=True)


class _LocationConstraintSerializer(serializers.Serializer):
    vnfProfileId = serializers.CharField(help_text="ID of VNF profile", required=False, allow_null=True, allow_blank=True)
    locationConstraints = _VnfLocationSerializer(help_text="Location constraint", required=False, allow_null=True)


class _AddressRange(serializers.Serializer):
    minAddress = serializers.IPAddressField(help_text="Lowest IP address belonging to the range.", required=True)
    maxAddress = serializers.IPAddressField(help_text="Highest IP address belonging to the range.", required=True)


class _IpAddress(serializers.Serializer):
    type = serializers.ChoiceField(help_text="The type of the IP addresses.", required=True, choices=["IPV4", "IPV6"])
    fixedAddresses = serializers.ListField(child=serializers.CharField(help_text="Fixed addresses to assign."), required=False)
    numDynamicAddresses = serializers.IntegerField(help_text="Number of dynamic addresses to assign.", required=False)
    addressRange = _AddressRange(help_text="An IP address range to be used.", required=False)
    subnetId = serializers.CharField(help_text="Subnet defined by the identifier of the subnet resource in the VIM.", required=False, allow_null=True, allow_blank=True)


class _IpOverEthernetSerializer(serializers.Serializer):
    macAddress = serializers.CharField(help_text="MAC address.", required=False, allow_null=True, allow_blank=True)
    ipAddresses = _IpAddress(help_text="List of IP addresses to assign to the extCP instance.", required=False, many=True)


class _CpProtocolInfoSerializer(serializers.Serializer):
    layerProtocol = serializers.ChoiceField(
        help_text="The identifier of layer(s) and protocol(s) associated to the network address information.",
        choices=["IP_OVER_ETHERNET"],
        required=True,
        allow_null=False)
    ipOverEthernet = _IpOverEthernetSerializer(
        help_text="IP addresses over Ethernet to assign to the extCP instance.",
        required=False,
        allow_null=True)


class _PnfExtCpData(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="Identifier of the CP", required=False, allow_null=True, allow_blank=True)
    cpdId = serializers.CharField(help_text="Identifier of the Connection Point Descriptor", required=False, allow_null=True, allow_blank=True)
    cpProtocolData = _CpProtocolInfoSerializer(help_text="Address assigned for this CP", required=True, allow_null=False, many=True)


class _AddPnfData(serializers.Serializer):
    pnfId = serializers.CharField(help_text="Identifier of the PNF", required=True, allow_null=False, allow_blank=True)
    pnfName = serializers.CharField(help_text="Name of the PNF", required=True, allow_null=True, allow_blank=True)
    pnfdId = serializers.CharField(help_text="Identifier of the PNFD", required=True, allow_null=False, allow_blank=True)
    pnfProfileId = serializers.CharField(help_text="Identifier of related PnfProfile in the NSD", required=True, allow_null=False, allow_blank=True)
    cpData = _PnfExtCpData(help_text="Address assigned for the PNF external CP", required=False, many=True)


class _InstantNsReqSerializer(serializers.Serializer):
    locationConstraints = _LocationConstraintSerializer(help_text="Location constraints", required=False, many=True)
    additionalParamForNs = serializers.DictField(
        help_text="Additional param for NS",
        child=serializers.CharField(help_text="KeyValue Pairs", allow_blank=True),
        required=False,
        allow_null=True
    )
    addpnfData = _AddPnfData(help_text="Information on the PNF", required=False, many=True)


class _NsOperateJobSerializer(serializers.Serializer):
    jobId = serializers.CharField(help_text="ID of NS operate job", required=True)


class _TerminateNsReqSerializer(serializers.Serializer):
    terminationType = serializers.CharField(help_text="Type of NS termination", required=False, allow_null=True, allow_blank=True)
    gracefulTerminationTimeout = serializers.CharField(help_text="Timeout of NS graceful termination", required=False, allow_null=True, allow_blank=True)


class _ActionVmSerializer(serializers.Serializer):
    vmid = serializers.CharField(help_text="ID of VM", required=False, allow_null=True, allow_blank=True)
    vduid = serializers.CharField(help_text="ID of vdu", required=False, allow_null=True, allow_blank=True)
    vmname = serializers.CharField(help_text="Name of VM", required=False, allow_null=True, allow_blank=True)


class _HealNsAdditionalParamsSerializer(serializers.Serializer):
    action = serializers.CharField(help_text="Action of NS heal", required=False, allow_null=True, allow_blank=True)
    actionvminfo = _ActionVmSerializer(help_text="VM info of action", required=False, allow_null=True)


class _HealVnfDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of VNF Instance", required=True)
    cause = serializers.CharField(help_text="Cause of NS heal", required=False, allow_null=True, allow_blank=True)
    additionalParams = _HealNsAdditionalParamsSerializer(help_text="Additional params of NS heal", required=False, allow_null=True)


class _HealNsDataSerializer(serializers.Serializer):
    degreeHealing = serializers.ChoiceField(help_text="degree of healing", choices=["HEAL_RESTORE", "HEAL_QOS", "HEAL_RESET", "PARTIAL_HEALING"], required=True)
    actionsHealing = serializers.ListField(
        help_text="A list of actions",
        child=serializers.CharField(help_text="One action", required=True),
        required=False)
    healScript = serializers.CharField(help_text="script of NS heal", required=False, allow_null=True, allow_blank=True)
    additionalParamsforNs = serializers.CharField(help_text="Addition params of NS heal", required=False, allow_null=True, allow_blank=True)


class _HealNsReqSerializer(serializers.Serializer):
    healVnfData = _HealVnfDataSerializer(help_text="Data of heal VNF", required=False, allow_null=True)
    healNsData = _HealNsDataSerializer(help_text="Data of heal NS", required=False, allow_null=True)


class _InstNsPostDealReqSerializer(serializers.Serializer):
    status = serializers.CharField(help_text="Status of NS Inst", required=True)


class _ScaleNsByStepsSerializer(serializers.Serializer):
    aspectId = serializers.CharField(help_text="ID of aspect", required=True)
    numberOfSteps = serializers.CharField(help_text="Number of steps", required=True)
    scalingDirection = serializers.CharField(help_text="Scaling direction", required=True)


class _ScaleNsDataSerializer(serializers.Serializer):
    scaleNsByStepsData = _ScaleNsByStepsSerializer(help_text="Scale NS by steps data", many=True)


class _ManualScaleNsReqSerializer(serializers.Serializer):
    scaleType = serializers.CharField(help_text="Type of NS Scale", required=True)
    scaleNsData = _ScaleNsDataSerializer(help_text="Scale NS data", many=True)
