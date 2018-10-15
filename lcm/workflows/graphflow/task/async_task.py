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
import time
import datetime
from threading import Thread
from lcm.workflows.graphflow.task.task import Task

logger = logging.getLogger(__name__)


class AsyncTask(Task):

    def __init__(self, *args):
        super(AsyncTask, self).__init__(*args)

    def execute(self):
        logger.debug("start task: %s", self.key)
        status, output = self.run()
        self.update_task(status, output)
        if status == self.PROCESSING:
            WatchTask(self).start()

    def run(self):
        pass

    def get_task_status(self):
        status = self.get_ext_status()
        return status if status else self.status

    def update_task_status(self, status):
        self.status = status

    def get_ext_status(self):
        return None


class WatchTask(Thread):

    def __init__(self, task):
        Thread.__init__(self)
        self.task = task
        self.timeout = task.timeout
        self.endtime = (datetime.datetime.now() + datetime.timedelta(seconds=self.timeout)).strftime(self.task.TIME_FORMAT)

    def run(self):
        status = ""
        while status not in [self.task.FINISHED, self.task.ERROR] and self.endtime >= datetime.datetime.now().strftime(self.task.TIME_FORMAT):
            status = self.task.get_task_status()
            logger.debug("task %s, status %s", self.task.key, status)
            time.sleep(1)
        status = self.task.ERROR if status != self.task.FINISHED else self.task.FINISHED
        self.task.update_task_status(status)
