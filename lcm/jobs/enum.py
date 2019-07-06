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

JOB_STATUS = enum(
    FINISH=1,
    PROCESSING=0
)
JOB_MODEL_STATUS = enum(
    ERROR='error',
    FINISHED='finished',
    PROCESSING='processing',
    STARTED='started',
    TIMEOUT='timeout'
)
JOB_TYPE = enum(
    NS="NS",
    VNF="VNF"
)
JOB_ACTION = enum(
    CREATE="CREATE",
    INSTANTIATE="INSTANTIATE",
    UPDATE="UPDATE",
    HEAL="HEAL",
    GRANT="GRANT",
    MANUAL_SCALE="MANUAL SCALE",
    TERMINATE="TERMINATE"
)
JOB_PROGRESS = enum(
    ERROR=255,
    FINISHED=100,
    PARTLY_FINISHED=101,
    STARTED=0
)
JOB_ERROR_CODE = enum(
    NO_ERROR="0",
    ERROR="255"
)
