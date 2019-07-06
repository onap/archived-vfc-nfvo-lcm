# Copyright 2016 ZTE Corporation.
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

from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.values import remove_none_key
from lcm.jobs.api_model import JobQueryResp, JobDescriptor, JobHistory


logger = logging.getLogger(__name__)


class GetJobInfoService(object):
    def __init__(self, job_id, response_id=0):
        self.job_id = job_id
        self.response_id = response_id if response_id else 0

    def do_biz(self):
        logger.debug("GetJobInfoService, job_id=%s, response_id=%s", self.job_id, self.response_id)
        jobs = JobUtil.query_job_status(self.job_id, self.response_id)
        if not jobs:
            job_query_resp = JobQueryResp(self.job_id)
            return remove_none_key(job_query_resp.to_dict())
        job_query_resp = JobQueryResp(
            self.job_id,
            JobDescriptor(
                jobs[0].status,
                jobs[0].progress,
                jobs[0].descp,
                jobs[0].errcode,
                jobs[0].indexid,
                [
                    JobHistory(
                        job.status,
                        job.progress,
                        job.descp,
                        job.errcode,
                        job.indexid
                    ) for job in jobs[1:]
                ]
            )
        )
        return remove_none_key(job_query_resp.to_dict())
