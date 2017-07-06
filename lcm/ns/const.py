# Copyright 2016-2017 ZTE Corporation.
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

OWNER_TYPE = enum(VNF=0, VNFM=1, NS=2)

NS_INST_STATUS = enum(EMPTY='empty', INSTANTIATING='instantiating', TERMINATING='terminating',
                      ACTIVE='active', FAILED='failed', INACTIVE='inactive', UPDATING='updating', SCALING='scaling')
