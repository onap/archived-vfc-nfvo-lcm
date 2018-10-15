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

import logging
import json
from lcm.workflows.graphflow.task.sync_rest_task import SyncRestTask
from lcm.pub.utils import restcall

logger = logging.getLogger(__name__)


class LcmSyncRestTask(SyncRestTask):
    def call_rest(self, url, method, content):
        ret = restcall.req_by_msb(url, method, content)
        logger.debug("call_rest result %s" % ret)
        return ret[2], json.JSONDecoder().decode(ret[1])
