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


class ContextSerializer(serializers.Serializer):
    globalCustomerId = serializers.CharField(help_text="Global customer ID", required=False, allow_null=True)
    serviceType = serializers.CharField(help_text="Service type", required=False, allow_null=True)


class CreateNsReqSerializer(serializers.Serializer):
    csarId = serializers.CharField(help_text="Package ID of NS", required=False, allow_null=True)
    nsName = serializers.CharField(help_text="Name of NS", required=False, allow_null=True)
    description = serializers.CharField(help_text="Description of NS", required=False, allow_null=True)
    context = ContextSerializer(help_text="Context of NS", required=False)


class CreateNsRespSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=True)


class VnfInstSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of VNF instance", required=True)
    vnfInstanceName = serializers.CharField(help_text="Name of VNF instance", required=False, allow_null=True)
    vnfdId = serializers.CharField(help_text="ID of VNFD", required=False, allow_null=True)


class CpInstInfoSerializer(serializers.Serializer):
    cpInstanceId = serializers.CharField(help_text="ID of CP instance", required=True)
    cpInstanceName = serializers.CharField(help_text="Name of CP instance", required=False, allow_null=True)
    cpdId = serializers.CharField(help_text="ID of CPD", required=False, allow_null=True)


class VlInstSerializer(serializers.Serializer):
    vlInstanceId = serializers.CharField(help_text="ID of VL instance", required=True)
    vlInstanceName = serializers.CharField(help_text="Name of VL instance", required=False, allow_null=True)
    vldId = serializers.CharField(help_text="ID of VLD", required=False, allow_null=True)
    relatedCpInstanceId = CpInstInfoSerializer(help_text="Related CP instances", many=True)


class VnffgInstSerializer(serializers.Serializer):
    vnffgInstanceId = serializers.CharField(help_text="ID of VNFFG instance", required=True)
    vnfdId = serializers.CharField(help_text="ID of VNFD", required=False, allow_null=True)
    pnfId = serializers.CharField(help_text="ID of PNF", required=False, allow_null=True)
    virtualLinkId = serializers.CharField(help_text="ID of virtual link", required=False, allow_null=True)
    cpdId = serializers.CharField(help_text="ID of CPD", required=False, allow_null=True)
    nfp = serializers.CharField(help_text="nfp", required=False, allow_null=True)


class QueryNsRespSerializer(serializers.Serializer):
    nsInstanceId = serializers.CharField(help_text="ID of NS instance", required=True)
    nsName = serializers.CharField(help_text="Name of NS instance", required=False, allow_null=True)
    description = serializers.CharField(help_text="Description of NS instance", required=False, allow_null=True)
    nsdId = serializers.CharField(help_text="ID of NSD", required=True)
    vnfInfo = VnfInstSerializer(help_text="VNF instances", many=True, required=False, allow_null=True)
    vlInfo = VlInstSerializer(help_text="VL instances", many=True, required=False, allow_null=True)
    vnffgInfo = VnffgInstSerializer(help_text="VNFFG instances", many=True, required=False, allow_null=True)
    nsState = serializers.CharField(help_text="State of NS instance", required=False, allow_null=True)


class VimSerializer(serializers.Serializer):
    vimid = serializers.CharField(help_text="ID of VIM", required=False, allow_null=True)


class LocationConstraintSerializer(serializers.Serializer):
    vnfProfileId = serializers.CharField(help_text="ID of VNF profile", required=False, allow_null=True)
    locationConstraints = VimSerializer(help_text="Location constraints", required=False, allow_null=True)


class InstantNsReqSerializer(serializers.Serializer):
    locationConstraints = LocationConstraintSerializer(required=False, allow_null=True)
    additionalParamForNs = serializers.CharField(help_text="Additional param for NS", required=False, allow_null=True)


class NsOperateJobSerializer(serializers.Serializer):
    jobId = serializers.CharField(help_text="ID of NS operate job", required=True)


class TerminateNsReqSerializer(serializers.Serializer):
    terminationType = serializers.CharField(help_text="Type of NS termination", required=False, allow_null=True)
    gracefulTerminationTimeout = serializers.CharField(help_text="Timeout of NS graceful termination", required=False, allow_null=True)


class ActionVmSerializer(serializers.Serializer):
    vmid = serializers.CharField(help_text="ID of VM", required=False, allow_null=True)
    vmname = serializers.CharField(help_text="Name of VM", required=False, allow_null=True)


class HealNsAdditionalParamsSerializer(serializers.Serializer):
    action = serializers.CharField(help_text="Action of NS heal", required=False, allow_null=True)
    actionvminfo = ActionVmSerializer(help_text="VM info of action", required=False, allow_null=True)


class HealVnfDataSerializer(serializers.Serializer):
    vnfInstanceId = serializers.CharField(help_text="ID of VNF Instance", required=True)
    cause = serializers.CharField(help_text="Cause of NS heal", required=False, allow_null=True)
    additionalParams = HealNsAdditionalParamsSerializer(help_text="Additional params of NS heal", required=False, allow_null=True)


class HealNsReqSerializer(serializers.Serializer):
    healVnfData = HealVnfDataSerializer(help_text="Data of heal VNF", required=False, allow_null=True)


class InstNsPostDealReqSerializer(serializers.Serializer):
    status = serializers.CharField(help_text="Status of NS Inst", required=True)


class ScaleNsByStepsSerializer(serializers.Serializer):
    aspectId = serializers.CharField(help_text="ID of aspect", required=True)
    numberOfSteps = serializers.CharField(help_text="Number of steps", required=True)
    scalingDirection = serializers.CharField(help_text="Scaling direction", required=True)


class ScaleNsDataSerializer(serializers.Serializer):
    scaleNsByStepsData = ScaleNsByStepsSerializer(help_text="Scale NS by steps data", many=True)


class ManualScaleNsReqSerializer(serializers.Serializer):
    scaleType = serializers.CharField(help_text="Type of NS Scale", required=True)
    scaleNsData = ScaleNsDataSerializer(help_text="Scale NS data", many=True)
