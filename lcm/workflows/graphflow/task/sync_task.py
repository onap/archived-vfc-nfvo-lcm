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

from lcm.workflows.graphflow.task.task import Task
import logging

logger = logging.getLogger(__name__)


class SyncTask(Task):

    def execute(self):
        logger.debug("start task: %s", self.key)
        status, output = self.run()
        logger.debug("SyncTask status %s, output %s" % (status, output))
        self.update_task(status, output)

    def run(self):
        pass
