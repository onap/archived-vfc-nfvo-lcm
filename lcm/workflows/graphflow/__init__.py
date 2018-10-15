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

TASK_STAUS = (STARTED, PROCESSING, FINISHED, ERROR) = ("started", "processing", "finished", "error")
TIMEOUT_DEFAULT = 10

from lcm.workflows.graphflow.flow.flow import GraphFlow
from lcm.workflows.graphflow.task.task import Task
from lcm.workflows.graphflow.task.sync_task import SyncTask
from lcm.workflows.graphflow.task.sync_rest_task import SyncRestTask
from lcm.workflows.graphflow.task.async_task import AsyncTask
from lcm.workflows.graphflow.task.async_rest_task import ASyncRestTask
from lcm.workflows.graphflow.task.lcm_async_rest_task import LcmASyncRestTask
from lcm.workflows.graphflow.task.lcm_sync_rest_task import LcmSyncRestTask
