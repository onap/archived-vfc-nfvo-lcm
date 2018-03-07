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

import json
import logging
import uuid

logger = logging.getLogger(__name__)


class GrantVnf(object):
    def __init__(self, grant_data):
        self.data = grant_data

    def exec_grant(self):
        if isinstance(self.data, (unicode, str)):
            self.data = json.JSONDecoder().decode(self.data)
        grant_resp = {
            "id": str(uuid.uuid4()),
            "vnfInstanceId": self.data.get("vnfInstanceId"),
            "vnfLcmOpOccId": self.data.get("vnfLcmOpOccId")
        }
        logger.debug("grant_resp=%s", grant_resp)
        return grant_resp
