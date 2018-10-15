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

import datetime
from lcm.workflows.graphflow import STARTED, PROCESSING, FINISHED, ERROR, TIMEOUT_DEFAULT
import logging

logger = logging.getLogger(__name__)


class Task(object):
    TASK_STATUS = (STARTED, PROCESSING, FINISHED, ERROR) = (STARTED, PROCESSING, FINISHED, ERROR)
    TASK_ATTRIBUTES = (KEY, MANAGER, INPUT, TIMEOUT, ENDTIME, OUTPUT, STATUS) = ("key", "manager", "input", "timeout", "endtime", "output", "status")
    INPUT_REST = (URL, METHOD, CONTENT) = ("url", "method", "content")
    TIMEOUT_DEFAULT = TIMEOUT_DEFAULT
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, *args):
        task = args[0]
        self.key = task[self.KEY]
        self.taskManager = task[self.MANAGER]
        self.input = task[self.INPUT]
        self.timeout = task[self.TIMEOUT] if self.TIMEOUT in task else self.TIMEOUT_DEFAULT
        self.endtime = (datetime.datetime.now() + datetime.timedelta(seconds=self.timeout)).strftime(self.TIME_FORMAT)
        self.status = STARTED
        self.output = None

    def execute(self):
        pass

    def update_task(self, status, output=None):
        task = self.taskManager.get_task(self.key)
        task.status = status
        if output:
            task.output = output
        logger.debug("Update task %s status %s" % (task.key, task.status))
        self.taskManager.update_task(self.key, task)
