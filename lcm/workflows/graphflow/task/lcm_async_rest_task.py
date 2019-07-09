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
from lcm.jobs.const import JOB_INSTANCE_URI
from lcm.workflows.graphflow.task.async_rest_task import ASyncRestTask
from lcm.pub.utils import restcall

logger = logging.getLogger(__name__)


class LcmASyncRestTask(ASyncRestTask):

    METHOD_GET_JOB_STATUS = "status"

    def __init__(self, *args):
        super(LcmASyncRestTask, self).__init__(*args)
        # self.job_url = JOB_INSTANCE_URI

    def call_rest(self, url, method, content=None):
        ret = restcall.req_by_msb(url, method, content)
        return ret[2], json.JSONDecoder().decode(ret[1])

    def get_ext_status(self):
        job_id = self.parse_job_id()
        logger.debug("get_ext_status %s", self.key)
        job_status = None
        if job_id:
            url = JOB_INSTANCE_URI % job_id
            status, job_result = self.call_rest(url, self.GET)
            if status in self.STATUS_OK:
                progress = job_result["responseDescriptor"]["progress"]
                if progress == 100:
                    job_status = self.FINISHED
                elif progress == 255:
                    job_status = self.ERROR
                else:
                    job_status = self.PROCESSING
        return job_status

    def parse_job_id(self):
        if self.output:
            return self.output["jobId"] if "jobId" in self.output else None
        else:
            return None
