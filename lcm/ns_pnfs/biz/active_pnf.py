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
from lcm.pub.msapi.emsdriver import send_active_pnf_request


class ActivePnf(object):
    def __init__(self, ems_id, pnf_id, active_data):
        self.ems_id = ems_id
        self.pnf_id = pnf_id
        self.data = active_data

    def do_biz(self):
        self.active_pnf()

    def active_pnf(self):
        return send_active_pnf_request(self.ems_id, self.pnf_id, self.data)
