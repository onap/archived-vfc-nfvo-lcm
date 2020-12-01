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
from lcm.pub.utils.enumutil import enum_to_list
from lcm.ns.enum import LCM_NOTIFICATION_STATUS
from lcm.ns_vnfs.enum import RESOURCE_CHANGE_TYPE, LIFE_CYCLE_OPERATION, VNFC_CHANGE_TYPE, NETWORK_RESOURCE_TYPE, SCALE_VNF_TYPE, CANDIDATE_IDENTIFIER_TYPE, PLACE_VNF_REQUEST_STATUS


class InstVnfReqSerializer(serializers.Serializer):
    vnfIndex = serializers.CharField(
        help_text="Index of VNF",
        required=True)
    nsInstanceId = serializers.CharField(
        help_text="ID of NS instance",
        required=True)
    additionalParamForVnf = serializers.ListField(
        child=(serializers.DictField(help_text="Additional param for VNF")),
        required=False,
        allow_null=True)


class InstVnfRespSerializer(serializers.Serializer):
    vnfInstId = serializers.CharField(
        help_text="ID of VNF instance",
        required=True)
    jobId = serializers.CharField(
        help_text="ID of Job",
        required=True)


class VnfVmsSerializer(serializers.Serializer):
    vmId = serializers.CharField(
        help_text="ID of VM",
        required=True)
    vmName = serializers.CharField(
        help_text="Name of VM",
        required=False,
        allow_null=True,
        allow_blank=True)


class GetVnfRespSerializer(serializers.Serializer):
    vnfInstId = serializers.CharField(
        help_text="ID of VNF instance",
        required=True)
    vnfName = serializers.CharField(
        help_text="Name of VNF instance",
        required=True)
    vnfStatus = serializers.CharField(
        help_text="Status of VNF instance",
        required=True)
    vnfVms = VnfVmsSerializer(
        help_text="VMs of VNF",
        many=True)


class TerminateVnfReqSerializer(serializers.Serializer):
    terminationType = serializers.CharField(
        help_text="Termination Type",
        required=False,
        allow_null=True)
    gracefulTerminationTimeout = serializers.CharField(
        help_text="Graceful Termination Timeout",
        required=False,
        allow_null=True,
        allow_blank=True)


class TerminateVnfRespSerializer(serializers.Serializer):
    jobId = serializers.CharField(
        help_text="ID of Job",
        required=True)


class ResourceChangeSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        help_text="Change Type",
        choices=enum_to_list(RESOURCE_CHANGE_TYPE),
        required=True)
    resourceDefinitionId = serializers.CharField(
        help_text="Identifier of resource",
        required=False,
        allow_null=True,
        allow_blank=True)
    vdu = serializers.CharField(
        help_text="Identifier identifier of VDU",
        required=False,
        allow_null=True,
        allow_blank=True)


class AccessinfoSerializer(serializers.Serializer):
    tenant = serializers.CharField(
        help_text="Name of tenant",
        required=True)


class VimSerializer(serializers.Serializer):
    vimid = serializers.CharField(
        help_text="ID of VIM",
        required=True)
    accessinfo = AccessinfoSerializer(
        help_text="Access Info",
        required=False)
    accessInfo = AccessinfoSerializer(
        help_text="Access Info",
        required=False)


class AffectedVnfcLcmSerializer(serializers.Serializer):
    vnfcInstanceId = serializers.CharField(
        help_text="ID of VNFC instance",
        required=False,
        allow_null=True,
        allow_blank=True)
    vduId = serializers.CharField(
        help_text="ID of VDU in VNFD",
        required=False,
        allow_null=True,
        allow_blank=True)
    changeType = serializers.ChoiceField(
        help_text="Type of Change",
        choices=enum_to_list(VNFC_CHANGE_TYPE),  # ["added", "removed", "modified"],
        required=True)
    vimId = serializers.CharField(
        help_text="ID of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    vmId = serializers.CharField(
        help_text="ID of virtual machine",
        required=False,
        allow_null=True,
        allow_blank=True)
    vmName = serializers.CharField(
        help_text="Name of virtual machine",
        required=False,
        allow_null=True,
        allow_blank=True)


class NetworkResourceSerializer(serializers.Serializer):
    resourceType = serializers.ChoiceField(
        help_text="Type of Resource",
        choices=enum_to_list(NETWORK_RESOURCE_TYPE),
        required=True)
    resourceId = serializers.CharField(
        help_text="ID of network resource",
        required=False,
        allow_null=True,
        allow_blank=True)
    resourceName = serializers.CharField(
        help_text="Name of network resource",
        required=False,
        allow_null=True,
        allow_blank=True)


class AffectedVirtualLinkLcmSerializer(serializers.Serializer):
    vlInstanceId = serializers.CharField(
        help_text="ID of VL instance",
        required=False,
        allow_null=True,
        allow_blank=True)
    vldId = serializers.CharField(
        help_text="ID of VLD in VNFD",
        required=False,
        allow_null=True,
        allow_blank=True)
    changeType = serializers.ChoiceField(
        help_text="Type of Change",
        choices=enum_to_list(VNFC_CHANGE_TYPE),  # ["added", "removed", "modified"],
        required=True)
    networkResource = NetworkResourceSerializer(
        help_text="Network Resource",
        required=False,
        allow_null=True)


class PortResourceSerializer(serializers.Serializer):
    vimId = serializers.CharField(
        help_text="ID of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    resourceId = serializers.CharField(
        help_text="ID of Resource",
        required=False,
        allow_null=True,
        allow_blank=True)
    resourceName = serializers.CharField(
        help_text="Name of Resource",
        required=False,
        allow_null=True,
        allow_blank=True)
    tenant = serializers.CharField(
        help_text="ID of Tenant",
        required=False,
        allow_null=True,
        allow_blank=True)
    ipAddress = serializers.CharField(
        help_text="IP address of port",
        required=False,
        allow_null=True,
        allow_blank=True)
    macAddress = serializers.CharField(
        help_text="MAC address of port",
        required=False,
        allow_null=True,
        allow_blank=True)
    instId = serializers.CharField(
        help_text="Instance id of server to which the port is attached to",
        required=False,
        allow_null=True,
        allow_blank=True)


class AffectedCpSerializer(serializers.Serializer):
    changeType = serializers.ChoiceField(
        help_text="Type of Change",
        choices=enum_to_list(VNFC_CHANGE_TYPE),  # ["added", "removed", "modified"],
        required=True)
    virtualLinkInstanceId = serializers.CharField(
        help_text="ID of VL instance",
        required=False,
        allow_null=True,
        allow_blank=True)
    cpInstanceId = serializers.CharField(
        help_text="ID of CP instance",
        required=False,
        allow_null=True,
        allow_blank=True)
    cpdId = serializers.CharField(
        help_text="ID of CPD in VNFD",
        required=False,
        allow_null=True,
        allow_blank=True)
    ownerType = serializers.CharField(
        help_text="Type of Owner",
        required=False,
        allow_null=True,
        allow_blank=True)
    ownerId = serializers.CharField(
        help_text="ID of Owner",
        required=False,
        allow_null=True,
        allow_blank=True)
    portResource = PortResourceSerializer(
        help_text="Port Resource",
        required=False,
        allow_null=True)


class AffectedVirtualStorageLcm(serializers.Serializer):
    pass


class NotifyLcmReqSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        help_text="Status of operation",
        choices=enum_to_list(LCM_NOTIFICATION_STATUS),
        required=True
    )
    operation = serializers.ChoiceField(
        help_text="Lifecycle Operation",
        choices=enum_to_list(LIFE_CYCLE_OPERATION),
        required=True
    )
    jobId = serializers.CharField(
        help_text="ID of Job",
        required=False,
        allow_null=True,
        allow_blank=True)
    vnfdmodule = serializers.CharField(
        help_text="VNFD Module",
        required=False,
        allow_null=True,
        allow_blank=True)
    affectedVnfc = AffectedVnfcLcmSerializer(
        help_text="Affected VNFC",
        many=True)
    affectedVl = AffectedVirtualLinkLcmSerializer(
        help_text="Affected VL",
        many=True)
    affectedCp = AffectedCpSerializer(
        help_text="Affected CP",
        many=True)
    affectedVirtualStorage = AffectedVirtualStorageLcm(
        help_text="Affected Virtual Storage(Not supported)",
        many=True)


class ScaleVnfDataSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        help_text="Direction of the scaling",
        choices=enum_to_list(SCALE_VNF_TYPE),
        required=True)
    aspectId = serializers.CharField(
        help_text="Aspect ID of the VNF that is requested to be scaled",
        required=False,
        allow_null=True,
        allow_blank=True)
    numberOfSteps = serializers.CharField(
        help_text="Number of scaling steps to be executed as part of this ScaleVnf operation",
        required=False,
        allow_null=True,
        allow_blank=True)
    additionalParam = serializers.DictField(
        help_text="Additional parameters passed by the NFVO as input to the scaling process, specific to the VNF being scaled",
        child=serializers.CharField(
            help_text="Additional parameters",
            allow_blank=True),
        required=False,
        allow_null=True
    )


class ScaleVnfReqSerializer(serializers.Serializer):
    scaleVnfData = ScaleVnfDataSerializer(
        help_text="Scale data",
        many=False)


class ScaleVnfRespSerializer(serializers.Serializer):
    jobId = serializers.CharField(
        help_text="ID of Job",
        required=True)


class VerifyVnfReqSerializer(serializers.Serializer):
    PackageID = serializers.CharField(
        help_text="ID of Package",
        required=True)


class VerifyVnfRespSerializer(serializers.Serializer):
    jobId = serializers.CharField(
        help_text="ID of Job",
        required=True)


class VnfmInfoRespSerializer(serializers.Serializer):
    vnfmId = serializers.CharField(
        help_text="ID of VNFM",
        required=True)
    name = serializers.CharField(
        help_text="Name of VNFM",
        required=True)
    type = serializers.CharField(
        help_text="Type of VNFM",
        required=True)
    vimId = serializers.CharField(
        help_text="ID of VIM",
        required=True)
    vendor = serializers.CharField(
        help_text="Vendor of VNFM",
        required=False,
        allow_null=True,
        allow_blank=True)
    version = serializers.CharField(
        help_text="Version of VNFM",
        required=False,
        allow_null=True,
        allow_blank=True)
    description = serializers.CharField(
        help_text="Description of VNFM",
        required=False,
        allow_null=True,
        allow_blank=True)
    certificateUrl = serializers.CharField(
        help_text="Certificate PEM of VNFM",
        required=False,
        allow_null=True,
        allow_blank=True)
    url = serializers.CharField(
        help_text="url of VNFM",
        required=False,
        allow_null=True,
        allow_blank=True)
    userName = serializers.CharField(
        help_text="User Name of VNFM",
        required=False,
        allow_null=True,
        allow_blank=True)
    password = serializers.CharField(
        help_text="Password of VNFM",
        required=False,
        allow_null=True,
        allow_blank=True)
    createTime = serializers.CharField(
        help_text="Create Time of VNFM",
        required=False,
        allow_null=True,
        allow_blank=True)


class VimInfoRespSerializer(serializers.Serializer):
    vimId = serializers.CharField(
        help_text="ID of VIM",
        required=True)
    name = serializers.CharField(
        help_text="Name of VIM",
        required=True)
    url = serializers.CharField(
        help_text="Url of VIM",
        required=True)
    userName = serializers.CharField(
        help_text="User Name of VIM",
        required=True)
    password = serializers.CharField(
        help_text="Password of VIM",
        required=True)
    tenantId = serializers.CharField(
        help_text="Tenant ID of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    tenant = serializers.CharField(
        help_text="Default Tenant of VIM",
        required=False,
        allow_null=True, allow_blank=True)
    vendor = serializers.CharField(
        help_text="Vendor of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    version = serializers.CharField(
        help_text="Version of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    description = serializers.CharField(
        help_text="Description of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    domain = serializers.CharField(
        help_text="Domain of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    type = serializers.CharField(
        help_text="Type of VIM",
        required=True)
    createTime = serializers.CharField(
        help_text="Create Time of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    sslCacert = serializers.CharField(
        help_text="SSL Cacert of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    sslInsecure = serializers.CharField(
        help_text="SSL Insecure of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)
    status = serializers.CharField(
        help_text="Status of VIM",
        required=False,
        allow_null=True,
        allow_blank=True)


class CandidateSerializer(serializers.Serializer):
    identifierType = serializers.ChoiceField(
        help_text="The type of a candidate",
        choices=enum_to_list(CANDIDATE_IDENTIFIER_TYPE),
        required=True)
    identifiers = serializers.ListField(
        help_text="A list of identifiers",
        child=serializers.CharField(
            help_text="One identifier",
            required=True),
        required=True)
    cloudOwner = serializers.CharField(
        help_text="The name of a cloud owner. Only required if identifier Type is cloudRegionId",
        required=False,
        allow_null=True,
        allow_blank=True)


class LicenseSolutionSerializer(serializers.Serializer):
    resourceModuleName = serializers.CharField(
        help_text="Name of Resource as defined in the Service Model",
        required=True)
    serviceResourceId = serializers.CharField(
        help_text="Resource Id defined in the Service Model",
        required=True)
    entitlementPoolUUID = serializers.ListField(
        help_text="A list of entitlementPoolUUIDs",
        child=serializers.CharField(
            help_text="entitlementPoolUUID",
            required=True),
        required=True)
    licenseKeyGroupUUID = serializers.ListField(
        help_text="A list of licenseKeyGroupUUID",
        child=serializers.CharField(
            help_text="licenseKeyGroupUUID",
            required=True),
        required=True)
    entitlementPoolInvariantUUID = serializers.ListField(
        help_text="A list of entitlementPoolInvariantUUIDs",
        child=serializers.CharField(
            help_text="entitlementPoolInvariantUUID",
            required=True),
        required=True)
    licenseKeyGroupInvariantUUID = serializers.ListField(
        help_text="A list of licenseKeyGroupInvariantUUID",
        child=serializers.CharField(
            help_text="licenseKeyGroupInvariantUUID",
            required=True),
        required=True)


class AssignmentInfoSerializer(serializers.Serializer):
    key = serializers.CharField(
        help_text="Any attribute Key needed",
        required=True)
    value = serializers.JSONField(
        help_text="Attribute value for that key",
        required=True)


class PlacementSolutionSerializer(serializers.Serializer):
    resourceModuleName = serializers.CharField(
        help_text="Name of Resource as defined in the Service Model",
        required=True)
    serviceResourceId = serializers.CharField(
        help_text="Resource Id defined in the Service Model",
        required=True)
    solution = CandidateSerializer(
        help_text="The Placement Solution",
        required=True)
    assignmentInfo = AssignmentInfoSerializer(
        help_text="Additonal information related to a candidate",
        required=False,
        many=True)


class ComprehensiveSolutionSerializer(serializers.ListSerializer):
    child = PlacementSolutionSerializer(
        help_text="A list of placement solutions",
        allow_null=True,
        required=True)


class SolutionSerializer(serializers.Serializer):
    placementSolutions = ComprehensiveSolutionSerializer(
        help_text="A list of Placement Solutions",
        required=True,
        allow_empty=True,
        many=True)
    licenseSolutions = LicenseSolutionSerializer(
        help_text="A list of License Solutions",
        required=False,
        many=True)


class PlaceVnfReqSerializer(serializers.Serializer):
    requestId = serializers.CharField(
        help_text="ID of Homing Request",
        required=True)
    transactionId = serializers.CharField(
        help_text="ID of Homing Transaction",
        required=True,
        allow_null=False,
        allow_blank=True)
    statusMessage = serializers.CharField(
        help_text="Status Message of Request",
        required=False,
        allow_null=True,
        allow_blank=True)
    requestStatus = serializers.ChoiceField(
        help_text="The Status of a Request",
        choices=enum_to_list(PLACE_VNF_REQUEST_STATUS),
        required=True,
        allow_null=False)
    solutions = SolutionSerializer(
        help_text="Request Solutions",
        required=True,
        allow_null=False)
