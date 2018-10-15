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

from lcm.workflows.graphflow.task.async_task import AsyncTask
from lcm.workflows.graphflow.task.sync_task import SyncTask
from lcm.workflows.graphflow.task.lcm_async_rest_task import LcmASyncRestTask
import logging

logger = logging.getLogger(__name__)


class CreateSynVNF(SyncTask):
    def __init__(self, *args):
        super(CreateSynVNF, self).__init__(*args)

    def run(self):
        logger.debug("test CreateSynVNF %s" % self.key)
        return self.FINISHED, {}


class CreateAsynVNF(AsyncTask):
    def __init__(self, *args):
        super(CreateAsynVNF, self).__init__(*args)

    def run(self):
        logger.debug("test CreateAsynVNF %s" % self.key)
        return self.PROCESSING, None

    def get_ext_status(self):
        return self.FINISHED


class CreateASynRestVNF(LcmASyncRestTask):

    def __init__(self, *args):
        super(CreateASynRestVNF, self).__init__(*args)
        self.url = "/api/nslcm/v1/vnfs"
        self.method = self.POST
