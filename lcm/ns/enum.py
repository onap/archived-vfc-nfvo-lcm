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

ACTION_TYPE = enum(
    START=1,
    STOP=2,
    REBOOT=3
)
AUTH_TYPE = enum(
    BASIC="BASIC",
    OAUTH2_CLIENT_CREDENTIALS="OAUTH2_CLIENT_CREDENTIALS",
    TLS_CERT="TLS_CERT"
)
CHANGE_RESULT = enum(
    COMPLETED='COMPLETED',
    ROLLED_BACK='ROLLED_BACK',
    FAILED='FAILED',
    PARTIALLY_COMPLETED='PARTIALLY_COMPLETED'
)
CHANGE_TYPE = enum(
    ADD='ADD',
    DELETE='DELETE',
    REMOVE='REMOVE',
    INSTANTIATE='INSTANTIATE',
    TERMINATE='TERMINATE',
    SCALE='SCALE',
    UPDATE='UPDATE',
    CHANGE_FLAVOUR='CHANGE_FLAVOUR',
    HEAL='HEAL',
    OPERATE='OPERATE',
    MODIFY='MODIFY',
    MODIFY_INFORMATION='MODIFY_INFORMATION',
    CHANGE_EXTERNAL_VNF_CONNECTIVITY='CHANGE_EXTERNAL_VNF_CONNECTIVITY',
    ADD_LINK_PORT='ADD_LINK_PORT',
    REMOVE_LINK_PORT='REMOVE_LINK_PORT'
)
GRANT_TYPE = enum(
    INSTANTIATE="INSTANTIATE",
    TERMINATE="TERMINATE",
    HEAL_CREATE="Heal Create",
    HEAL_RESTART="Heal Restart",
    OPERATE="OPERATE"
)
HEAL_ACTION_TYPE = enum(
    START="vmCreate",
    RESTART="vmReset"
)
IPADDRESSES_TYPE = enum(
    IPV4='IPV4',
    IPV6='IPV6'
)
LCM_NOTIFICATION_STATUS = enum(
    START="START",
    RESULT="RESULT"
)
LAYER_PROTOCOL = enum(
    IP_OVER_ETHERNET="IP_OVER_ETHERNET"
)
NS_COMPOMENT_TYPE = enum(
    VNF="VNF",
    PNF="PNF",
    NS="NS"
)
NS_INST_STATUS = enum(
    EMPTY='empty',
    INSTANTIATING='instantiating',
    TERMINATING='terminating',
    ACTIVE='active',
    FAILED='failed',
    INACTIVE='inactive',
    UPDATING='updating',
    SCALING='scaling',
    HEALING='healing'
)
OPERATION_STATE_TYPE = enum(
    STARTING="STARTING",
    PROCESSING="PROCESSING",
    COMPLETED="COMPLETED",
    FAILED_TEMP="FAILED_TEMP",
    FAILED="FAILED",
    ROLLING_BACK="ROLLING_BACK",
    ROLLED_BACK="ROLLED_BACK"
)
OPERATION_TYPE = enum(
    INSTANTIATE="INSTANTIATE",
    SCALE="SCALE",
    TERMINATE="TERMINATE",
    UPDATE="UPDATE",
    HEAL="HEAL",
)
OPNAME_FOR_CHANGE_NOTIFICATION_TYPE = enum(
    VNF_INSTANTIATE="VNF_INSTANTIATE",
    VNF_SCALE="VNF_SCALE",
    VNF_SCALE_TO_LEVEL="VNF_SCALE_TO_LEVEL",
    VNF_CHANGE_FLAVOUR="VNF_CHANGE_FLAVOUR",
    VNF_TERMINATE="VNF_TERMINATE",
    VNF_HEAL="VNF_HEAL",
    VNF_OPERATE="VNF_OPERATE",
    VNF_CHANGE_EXT_CONN="VNF_CHANGE_EXT_CONN",
    VNF_MODIFY_INFO="VNF_MODIFY_INFO",
    NS_INSTANTIATE="NS_INSTANTIATE",
    NS_SCALE="NS_SCALE",
    NS_UPDATE="NS_UPDATE",
    NS_TERMINATE="NS_TERMINATE",
    NS_HEAL="NS_HEAL"
)
OPOCC_STATUS_FOR_CHANGENOTIFICATION_TYPE = enum(
    START="START",
    COMPLETED="COMPLETED ",
    PARTIALLY_COMPLETED="PARTIALLY_COMPLETED",
    FAILED="FAILED",
    ROLLED_BACK="ROLLED_BACK",
)
OWNER_TYPE = enum(
    VNF=0,
    VNFM=1,
    NS=2
)
VNF_STATUS = enum(
    NULL='null',
    INSTANTIATING="instantiating",
    INACTIVE='inactive',
    ACTIVE="active",
    FAILED="failed",
    TERMINATING="terminating",
    SCALING="scaling",
    OPERATING="operating",
    UPDATING="updating",
    HEALING="healing"
)
