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

logger = logging.getLogger(__name__)


class GetJobInfoService(object):
    def __init__(self, job_id, response_id=0):
        self.job_id = job_id
        self.response_id = response_id if response_id else 0

    def do_biz(self):
        #logger.info("get job info, job_id=:%s, response_id=:%s" % (self.job_id, self.response_id))
        jobs = JobUtil.query_job_status(self.job_id, self.response_id)
        if not jobs:
            return {"jobId": self.job_id}
        ret = {
            "jobId": self.job_id,
            "responseDescriptor": {
                "status": jobs[0].status,
                "progress": jobs[0].progress,
                "statusDescription": jobs[0].descp,
                "errorCode": jobs[0].errcode,
                "responseId": jobs[0].indexid,
                "responseHistoryList": [
                    {
                        "status": job.status,
                        "progress": job.progress,
                        "statusDescription": job.descp,
                        "errorCode": job.errcode,
                        "responseId": job.indexid} for job in jobs[1:]]}}
        return ret
