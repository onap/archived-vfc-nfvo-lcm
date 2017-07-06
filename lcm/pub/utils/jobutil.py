# Copyright 2016-2017 ZTE Corporation.
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
import logging
import uuid
import traceback

from lcm.pub.database.models import JobStatusModel, JobModel
from lcm.pub.utils import idutil

logger = logging.getLogger(__name__)


def enum(**enums):
    return type('Enum', (), enums)


JOB_STATUS = enum(PROCESSING=0, FINISH=1)
JOB_MODEL_STATUS = enum(STARTED='started', PROCESSING='processing', FINISHED='finished', ERROR='error',
                        TIMEOUT='timeout')
JOB_TYPE = enum(CREATE_VNF="create vnf", TERMINATE_VNF="terminate vnf", GRANT_VNF="grant vnf", MANUAL_SCALE_VNF="manual scale vnf")


class JobUtil(object):
    def __init__(self):
        pass

    @staticmethod
    def __gen_job_id(job_name):
        return "%s-%s" % (job_name if job_name else "UnknownJob", uuid.uuid1())

    @staticmethod
    def query_job_status(job_id, index_id=-1):
        #logger.info("Query job status, jobid =[%s], responseid [%d]" % (job_id, index_id))
        jobs = []
        if index_id < 0:
            row = JobStatusModel.objects.filter(jobid=job_id).order_by("-indexid").first()
            if row:
                jobs.append(row)
        else:
            [jobs.append(job) for job in JobStatusModel.objects.filter(jobid=job_id).order_by("-indexid")
             if job.indexid > index_id]

        #logger.info("Query job status, rows=%s" % str(jobs))
        return jobs

    @staticmethod
    def is_job_exists(job_id):
        jobs = JobModel.objects.filter(jobid=job_id)
        return len(jobs) > 0

    @staticmethod
    def create_job(inst_type, jobaction, inst_id, user='', job_id=None, res_name=''):
        if job_id is None:
            job_id = JobUtil.__gen_job_id(
                '%s-%s-%s' % (str(inst_type).replace(' ', '_'), str(jobaction).replace(' ', '_'), str(inst_id)))
        job = JobModel()
        job.jobid = job_id
        job.jobtype = inst_type
        job.jobaction = jobaction
        job.resid = str(inst_id)
        job.status = JOB_STATUS.PROCESSING
        job.user = user
        job.starttime = datetime.datetime.now().strftime('%Y-%m-%d %X')
        job.progress = 0
        job.resname = res_name
        logger.debug("create a new job, jobid=%s, jobtype=%s, jobaction=%s, resid=%s, status=%d" %
                     (job.jobid, job.jobtype, job.jobaction, job.resid, job.status))
        job.save()
        return job_id

    @staticmethod
    def clear_job(job_id):
        [job.delete() for job in JobModel.objects.filter(jobid=job_id)]
        logger.debug("Clear job, job_id=%s" % job_id)

    @staticmethod
    def add_job_status(job_id, progress, status_decs, error_code=""):
        jobs = JobModel.objects.filter(jobid=job_id)
        if not jobs:
            logger.error("Job[%s] is not exists, please create job first." % job_id)
            raise Exception("Job[%s] is not exists." % job_id)
        try:
            int_progress = int(progress)
            job_status = JobStatusModel()
            job_status.indexid = int(idutil.get_auto_id(job_id))
            job_status.jobid = job_id
            job_status.status = "processing"
            job_status.progress = int_progress

            if job_status.progress == 0:
                job_status.status = "started"
            elif job_status.progress == 100:
                job_status.status = "finished"
            elif job_status.progress == 101:
                job_status.status = "partly_finished"
            elif job_status.progress > 101:
                job_status.status = "error"

            if error_code == "255":
                job_status.status = "error"

            job_status.descp = status_decs
            job_status.errcode = error_code
            job_status.addtime = datetime.datetime.now().strftime('%Y-%m-%d %X')
            job_status.save()
            logger.debug("Add a new job status, jobid=%s, indexid=%d,"
                         " status=%s, description=%s, progress=%d, errcode=%s, addtime=%r" %
                         (job_status.jobid, job_status.indexid, job_status.status, job_status.descp,
                          job_status.progress, job_status.errcode, job_status.addtime))

            job = jobs[0]
            job.progress = int_progress
            if job_status.progress >= 100:
                job.status = JOB_STATUS.FINISH
                job.endtime = datetime.datetime.now().strftime('%Y-%m-%d %X')
            job.save()
            logger.debug("update job, jobid=%s, progress=%d" % (job_status.jobid, int_progress))
        except:
            logger.error(traceback.format_exc())

    @staticmethod
    def clear_job_status(job_id):
        [job.delete() for job in JobStatusModel.objects.filter(jobid=job_id)]
        logger.debug("Clear job status, job_id=%s" % job_id)

    @staticmethod
    def get_unfinished_jobs(url_prefix, inst_id, inst_type):
        jobs = JobModel.objects.filter(resid=inst_id, jobtype=inst_type, status=JOB_STATUS.PROCESSING)
        progresses = reduce(lambda content, job: content + [url_prefix + "/" + job.jobid], jobs, [])
        return progresses
