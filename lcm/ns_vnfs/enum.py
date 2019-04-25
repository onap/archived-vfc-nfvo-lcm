# Copyright 2019 ZTE Corporation.
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
from lcm.pub.utils.enumutil import enum

CANDIDATE_IDENTIFIER_TYPE = enum(
    SERVICE_INSTANCE_ID="serviceInstanceId",
    VNF_NAME="vnfName",
    CLOUD_REGION_ID="cloudRegionId",
    VIM_ID="vimId"
)
GRANT_OPERATION = enum(
    INSTANTIATE="INSTANTIATE",
    SCALE="SCALE",
    SCALE_TO_LEVEL="SCALE_TO_LEVEL",
    CHANGE_FLAVOUR="CHANGE_FLAVOUR",
    TERMINATE="TERMINATE",
    HEAL="HEAL",
    OPERATE="OPERATE",
    CHANGE_EXT_CONN="CHANGE_EXT_CONN",
    MODIFY_INFO="MODIFY_INFO"
)
INST_TYPE = enum(
    VNF=0,
    VNFM=1)
INST_TYPE_NAME = enum(
    VNF="VNF",
    VNFM="VNFM")
LIFE_CYCLE_OPERATION = enum(
    TERMINATE="Terminate",
    INSTANTIATE="Instantiate",
    SCALEIN="Scalein",
    SCALEOUT="Scaleout",
    SCALEDOWN="Scaledown",
    SCALEUP="Scaleup",
    HEAL="Heal"
)
NETWORK_RESOURCE_TYPE = enum(
    NETWORK="network",
    PORT="port"
)
PLACE_VNF_REQUEST_STATUS = enum(
    COMPLETED="completed",
    FAILED="failed",
    PENDING="pending"
)
RESOURCE_CHANGE_TYPE = enum(
    VDU="VDU"
)
RESOURE_TYPE = enum(
    COMPUTE="COMPUTE",
    VL="VL",
    STORAGE="STORAGE",
    LINKPORT="LINKPORT"
)
RESOURCE_ID_TYPE = enum(
    RES_MGMT="RES_MGMT",
    GRANT="GRANT"
)
SCALE_VNF_TYPE = enum(
    SCALE_IN="SCALE_IN",
    SCALE_OUT="SCALE_OUT"
)
STORAGE_CHANGE_TYPE = enum(
    ADDED="ADDED",
    MODIFIED="MODIFIED",
    REMOVED="REMOVED",
    TEMPORARY="TEMPORARY"
)
VL_CHANGE_TYPE = enum(
    ADDED="ADDED",
    REMOVED="REMOVED",
    MODIFIED="MODIFIED",
    TEMPORARY="TEMPORARY",
    LINK_PORT_ADDED="LINK_PORT_ADDED",
    LINK_PORT_REMOVED="LINK_PORT_REMOVED"
)
VNF_NOTIFICATION_TYPE = enum(
    VNFLCMOPERATIONOCCURRENCENOTIFICATION="VnfLcmOperationOccurrenceNotification",
    VnfIdentifierCreationNotification="VnfIdentifierCreationNotification",
    VnfIdentifierDeletionNotification="VnfIdentifierDeletionNotification"
)
VNF_STATUS = enum(
    NULL="null",
    INSTANTIATING="instantiating",
    INACTIVE="inactive",
    ACTIVE="active",
    FAILED="failed",
    TERMINATING="terminating",
    SCALING="scaling",
    HEALING="healing",
    UPDATING="updating"
)
VNFC_CHANGE_TYPE = enum(
    ADDED="ADDED",
    MODIFIED="MODIFIED",
    REMOVED="REMOVED",
    TEMPORARY="TEMPORARY"
)
