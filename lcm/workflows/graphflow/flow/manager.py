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
from lcm.workflows.graphflow import STARTED, PROCESSING, FINISHED, ERROR
import logging
import time

logger = logging.getLogger(__name__)


class TaskManager(object):

    def __init__(self):
        self.task_set = {}

    def add_task(self, key, task, timeout=None):
        self.task_set[key] = task
        logger.debug("task_set %s" % self.task_set)

    def update_task_status(self, key, status):
        if key in self.task_set:
            task = self.task_set[key]
            task.update_task(status)

    def update_task(self, key, task):
        if key in self.task_set:
            self.task_set[key] = task

    def get_task(self, key):
        if key in self.task_set:
            return self.task_set[key]
        else:
            return None

    def get_all_task(self):
        return self.task_set

    def is_all_task_finished(self, task_key_set=None):
        states = []
        if not task_key_set:
            task_key_set = list(self.task_set.keys())
        total = len(task_key_set)
        for key in task_key_set:
            if key in self.task_set:
                states.append(self.task_set[key].status)
        if len([state for state in states if state == FINISHED]) == total:
            return True
        else:
            for key in task_key_set:
                logger.debug("task key %s, status %s" % (key, self.task_set[key].status))
            return False

    def wait_tasks_done(self, task_key_set=None):
        if task_key_set:
            for key in task_key_set:
                if key in list(self.task_set.keys()):
                    task = self.task_set[key]
                    logger.debug("current wait task %s, endtime %s, status %s" % (task.key, task.endtime, task.status))
                    while task.endtime >= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') and task.status in [STARTED, PROCESSING]:
                        time.sleep(1)
                    if task.status in [STARTED, PROCESSING]:
                        task.status = ERROR
                    logger.debug("wait task final status %s" % task.status)
        else:
            for task in list(self.task_set.values()):
                while task.endtime >= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') and task.status in [STARTED, PROCESSING]:
                    time.sleep(1)
                if task.status in [STARTED, PROCESSING]:
                    task.status = ERROR
