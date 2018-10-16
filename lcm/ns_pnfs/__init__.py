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

from lcm.workflows.graphflow.task.lcm_sync_rest_task import LcmSyncRestTask


class CreatePnf(LcmSyncRestTask):
    def __init__(self, *args):
        super(CreatePnf, self).__init__(*args)
        self.url = "/api/nslcm/v1/pnfs"
        self.method = self.POST
        self.timeout = 10


class DeletePnf(LcmSyncRestTask):
    def __init__(self, *args):
        super(DeletePnf, self).__init__(*args)
        self.url = "/api/nslcm/v1/pnfs/%s"
        self.method = self.DELETE
        self.timeout = 10
