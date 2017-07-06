# Copyright 2016 ZTE Corporation.
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

VNF_STATUS = enum(NULL='null', INSTANTIATING="instantiating", INACTIVE='inactive', ACTIVE="active", FAILED="failed",
                  TERMINATING="terminating", SCALING="scaling")
INST_TYPE = enum(VNF=0, VNFM=1)
INST_TYPE_NAME = enum(VNF='VNF', VNFM='VNFM')
PACKAGE_TYPE = enum(VNFD='VNFD', NSD='NSD')

NFVO_VNF_INST_TIMEOUT_SECOND = 1800

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
