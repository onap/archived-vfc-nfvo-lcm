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
from lcm.pub.config.config import MSB_BASE_URL


SERVICE_TYPE = 'NetworkService'
SERVICE_ROLE = 'NetworkService'
NS_INSTANCE_BASE_URI = MSB_BASE_URL + '/api/nslcm/v1/ns_instances/%s'
NS_OCC_BASE_URI = MSB_BASE_URL + '/api/nslcm/v1/ns_lcm_op_occs/%s'
SUBSCRIPTION_ROOT_URI = MSB_BASE_URL + "/api/nslcm/v1/subscriptions/%s"
