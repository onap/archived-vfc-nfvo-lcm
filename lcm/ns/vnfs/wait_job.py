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
import time
import datetime
import logging

import math

from lcm.pub.utils.jobutil import JobUtil, JOB_MODEL_STATUS
from lcm.pub.msapi.vnfmdriver import query_vnfm_job
from lcm.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


def calc_progress(vnfm_progress, target_range=None):
    target_range = [0, 100] if not target_range else target_range
    progress = int(vnfm_progress) if vnfm_progress else 0
    if progress > 100:
        return progress
    floor_progress = int(math.floor(float(target_range[1] - target_range[0]) / 100 * progress))
    target_range = floor_progress + target_range[0]
    return target_range


def default_callback(vnfo_job_id, vnfm_job_id, job_status, jobs, progress_range, **kwargs):
    for job in jobs:
        progress = calc_progress(
            ignore_case_get(job, 'progress'), 
            progress_range)
        JobUtil.add_job_status(vnfo_job_id, progress, 
            ignore_case_get(job, 'statusdescription'), 
            ignore_case_get(job, 'errorcode'))
    latest_progress = calc_progress(
        ignore_case_get(job_status, 'progress'), 
        progress_range)
    JobUtil.add_job_status(vnfo_job_id, latest_progress, 
        ignore_case_get(job_status, 'statusdescription'),
        ignore_case_get(job_status, 'errorcode'))
    jobstatus = ignore_case_get(job_status, 'status')
    if jobstatus in (JOB_MODEL_STATUS.ERROR, JOB_MODEL_STATUS.FINISHED):
        return True, jobstatus
    return False, JOB_MODEL_STATUS.PROCESSING


def wait_job_finish(vnfm_id, vnfo_job_id, vnfm_job_id, progress_range=None, timeout=600, 
    job_callback=default_callback, **kwargs):
    progress_range = [0, 100] if not progress_range else progress_range
    response_id = 0
    query_interval = 2
    start_time = end_time = datetime.datetime.now()
    while (end_time - start_time).seconds < timeout:
        query_status, result = query_vnfm_job(vnfm_id, vnfm_job_id, response_id)
        time.sleep(query_interval)
        end_time = datetime.datetime.now()
        if not query_status:
            continue
        job_status = ignore_case_get(result, 'responsedescriptor')
        response_id_new = ignore_case_get(job_status, 'responseid')
        if response_id_new == response_id:
            continue
        response_id = response_id_new
        jobs = ignore_case_get(job_status, 'responsehistorylist', [])
        if jobs:
            jobs.reverse()
        is_end, status = job_callback(vnfo_job_id, vnfm_job_id, job_status, 
            jobs, progress_range, **kwargs)
        if is_end:
            return status
    return JOB_MODEL_STATUS.TIMEOUT
