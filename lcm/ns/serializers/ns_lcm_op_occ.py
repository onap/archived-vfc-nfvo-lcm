# Copyright (c) 2019, CMCC Technologies Co., Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from rest_framework import serializers

from affected_vnfs import AffectedVnfsSerializer
from affected_pnfs import AffectedPnfsSerializer
from affected_vls import AffectedVLsSerializer
from affected_vnffgs import AffectedVnffgsSerializer
from affected_nss import AffectedNssSerializer
from affected_saps import AffectedSapsSerializer

from link import linkSerializer
from response import ProblemDetailsSerializer
from lcm.ns import const


class ResourceChangesSerializer(serializers.Serializer):
    affectedVnfs = AffectedVnfsSerializer(
        help_text="Information about VNFC instances that were affected during the lifecycle operation.",
        required=False,
        many=True
    )
    affectedPnfs = AffectedPnfsSerializer(
        help_text="Information about the PNF instances that were affected during the lifecycle operation.",
        required=False,
        many=True
    )
    affectedVls = AffectedVLsSerializer(
        help_text="Information about the VL instances that were affected during the lifecycle operation",
        required=False,
        many=True
    )
    affectedVnffgs = AffectedVnffgsSerializer(
        help_text="Information about the VNFFG instances that were affected during the lifecycle operation.",
        required=False,
        many=True
    )
    affectedNss = AffectedNssSerializer(
        help_text="Information about the nested NS instances that were affected during the lifecycle operation.",
        required=False,
        many=True
    )
    affectedSaps = AffectedSapsSerializer(
        help_text="Information about the SAP instances that were affected during the lifecycle operation.",
        required=False,
        many=True
    )


class LcmOpLinkSerializer(serializers.Serializer):
    self = linkSerializer(
        help_text="URI of this resource.",
        required=True,
        allow_null=False)
    nsInstance = serializers.CharField(
        help_text="Link to the NS instance that the operation applies to.",
        required=True)
    cancel = serializers.CharField(
        help_text="Link to the task resource that represents the 'cancel' operation for this LCM operation occurrence.",
        required=False)
    retry = serializers.CharField(
        help_text="Link to the task resource that represents the 'retry' operation for this LCM operation occurrence, "
                  "if retrying is currently allowed",
        required=False)
    rollback = serializers.CharField(
        help_text="Link to the task resource that represents the 'cancel' operation for this LCM operation occurrence.",
        required=False)
    fail = serializers.CharField(
        help_text="Link to the task resource that represents the 'fail' operation for this LCM operation occurrence.",
        required=False)


class NSLCMOpOccSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this NS lifecycle management operation occurrence,",
        max_length=255,
        required=True,
        allow_null=False
    )
    operationState = serializers.ChoiceField(
        help_text="The state of the VNF LCM operation occurrence. ",
        required=True,
        choices=const.LCM_OPERATION_STATE_TYPES
    )
    stateEnteredTime = serializers.CharField(
        help_text="Date-time when the current state was entered.",
        max_length=50
    )
    startTime = serializers.CharField(
        help_text="Date-time of the start of the operation.",
        max_length=50
    )
    nsInstanceId = serializers.UUIDField(
        help_text="Identifier of the ns instance to which the operation applies"
    )
    operation = serializers.ChoiceField(
        help_text="The lifecycle management operation",
        required=True,
        choices=const.NS_LCM_OP_TYPES
    )
    isAutomaticInvocation = serializers.BooleanField(
        help_text="Set to true if this NS LCM operation occurrence has been automatically triggered by the NFVO.",
        default=False
    )
    operationParams = serializers.DictField(
        help_text="Input parameters of the LCM operation. This attribute shall be formatted according to the request "
                  "data type of the related LCM operation. The following mapping between operationType and the data "
                  "type of this attribute shall apply: "
                  "1. INSTANTIATE: InstantiateVnfRequest "
                  "2. SCALE: ScaleVnfRequest "
                  "3. CHANGE_FLAVOUR: ChangeVnfFlavourRequest"
                  "4. HEAL: HealVnfRequest "
                  "5. TERMINATE: TerminateVnfRequest ",
        required=True,
        allow_null=False
    )
    isCancelPending = serializers.BooleanField(
        help_text="If the NS LCM operation occurrence is in 'STARTING' or 'PROCESSING' or 'ROLLING_BACK' state and "
                  "the operation is being cancelled, this attribute shall be set to True. Otherwise, it shall be set "
                  "to False.",
        required=True
    )
    cancelMode = serializers.CharField(
        help_text="The mode of an ongoing cancellation. Shall be present when isCancelPending=true, and shall be None "
                  "otherwise.",
        allow_null=True,
        required=False
    )
    error = ProblemDetailsSerializer(
        help_text="If 'operationState' is 'FAILED_TEMP' or 'FAILED' or PROCESSING' or 'ROLLING_BACK' and previous "
                  "value of 'operationState' was 'FAILED_TEMP'  this attribute shall be present ",
        allow_null=True,
        required=False
    )
    resourceChanges = ResourceChangesSerializer(
        help_text="It contains information about the cumulative changes to virtualised resources that were performed "
                  "so far by the LCM operation since its start, if applicable.",
        required=False,
        allow_null=True)
    _links = LcmOpLinkSerializer(
        help_text="Links to resources related to this resource.",
        required=True)
