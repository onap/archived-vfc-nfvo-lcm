# Copyright 2017 ZTE Corporation.
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
import json
import logging
import os
import threading
import traceback
import time
from lcm.jobs.const import JOB_INSTANCE_RESPONSE_ID_URI
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_PROGRESS, JOB_ACTION
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils.restcall import req_by_msb


logger = logging.getLogger(__name__)


class VerifyVnfs(threading.Thread):
    def __init__(self, data, job_id):
        super(VerifyVnfs, self).__init__()
        self.data = data
        self.job_id = job_id
        self.vnf_inst_id = ''
        self.verify_ok = False
        self.verify_config = ''

    def run(self):
        try:
            self.verify_config = self.load_config()
            JobUtil.create_job(JOB_TYPE.VNF, JOB_ACTION.CREATE, self.job_id, 'vnfsdk', self.job_id)
            self.do_on_boarding()
            self.do_inst_vnf()
            self.do_func_test()
            self.verify_ok = True
        except NSLCMException as e:
            self.update_job(JOB_PROGRESS.ERROR, e.args[0])
        except:
            logger.error(traceback.format_exc())
            self.update_job(JOB_PROGRESS.ERROR, 'Unknown error in vnf verify.')
        finally:
            logger.warn("Ignore terminate vnf operation")
            if self.verify_ok:
                self.update_job(100, "Ignore terminate vnf operation.")

    def do_on_boarding(self):
        self.update_job(10, "Start vnf on boarding.")
        onboarding_data = {
            "csarId": self.data["PackageID"],
            "labVimId": ignore_case_get(self.verify_config, "labVimId")
        }
        ret = req_by_msb("/api/nslcm/v1/vnfpackage", "POST", json.JSONEncoder().encode(onboarding_data))
        if ret[0] != 0:
            raise NSLCMException("Failed to call vnf onboarding: %s" % ret[1])
        rsp_data = json.JSONDecoder().decode(ret[1])
        if not self.wait_until_job_done(rsp_data["jobId"], 15):
            raise NSLCMException("Vnf onboarding failed")
        self.update_job(20, "Vnf on boarding success.")

    def do_inst_vnf(self):
        self.update_job(30, "Start inst vnf.")
        vnf_param = ignore_case_get(self.verify_config, "additionalParamForVnf")
        if vnf_param and "additionalParam" in vnf_param[0]:
            vnf_param[0]["additionalParam"]["vimId"] = ignore_case_get(self.verify_config, "lab_vim_id")
        inst_data = {
            "nsInstanceId": "",
            "additionalParamForVnf": vnf_param,
            "vnfIndex": "1"
        }
        ret = req_by_msb("/api/nslcm/v1/ns/ns_vnfs", "POST", json.JSONEncoder().encode(inst_data))
        if ret[0] != 0:
            raise NSLCMException("Failed to call inst vnf: %s" % ret[1])
        rsp_data = json.JSONDecoder().decode(ret[1])
        self.vnf_inst_id = rsp_data["vnfInstId"]
        if not self.wait_until_job_done(rsp_data["jobId"], 40):
            raise NSLCMException("Vnf(%s) inst failed" % self.vnf_inst_id)
        self.update_job(50, "Inst vnf success.")

    def do_func_test(self):
        self.update_job(60, "Start vnf function test.")
        func_data = {"PackageID": self.data["PackageID"]}
        ret = req_by_msb("/openapi/vnfsdk/v1/functest/taskmanager/testtasks", "POST", json.JSONEncoder().encode(func_data))
        if ret[0] != 0:
            raise NSLCMException("Failed to call func test: %s" % ret[1])
        rsp_data = json.JSONDecoder().decode(ret[1])

        if not self.wait_func_test_job_done(rsp_data["TaskID"], 40):
            raise NSLCMException("Func test failed")
        logger.info("Query(%s) job success.", rsp_data["TaskID"])

        ret = req_by_msb("/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s/result" % rsp_data["TaskID"], "GET")
        if ret[0] != 0:
            raise NSLCMException("Failed to get func test result: %s" % ret[1])
        rsp_result_data = json.JSONDecoder().decode(ret[1])
        logger.info("Func test(%s) result: %s", rsp_result_data)
        self.update_job(80, "Vnf function test success.")

    def do_term_vnf(self):
        if not self.vnf_inst_id:
            return
        self.update_job(90, "Start term vnf.")
        term_data = {
            "terminationType": "forceful",
            "gracefulTerminationTimeout": "600"
        }
        ret = req_by_msb("/api/nslcm/v1/ns/ns_vnfs/%s" % self.vnf_inst_id, "POST", json.JSONEncoder().encode(term_data))
        if ret[0] != 0:
            raise NSLCMException("Failed to call term vnf: %s" % ret[1])
        rsp_data = json.JSONDecoder().decode(ret[1])
        end_progress = 100 if self.verify_ok else JOB_PROGRESS.ERROR
        term_progress = 95 if self.verify_ok else JOB_PROGRESS.ERROR
        if not self.wait_until_job_done(rsp_data["jobId"], term_progress):
            logger.error("Vnf(%s) term failed", self.vnf_inst_id)
            end_progress = JOB_PROGRESS.ERROR
        self.update_job(end_progress, "Term vnf end.")

    def update_job(self, progress, desc=''):
        JobUtil.add_job_status(self.job_id, progress, desc)

    def wait_until_job_done(self, job_id, global_progress, retry_count=60, interval_second=3):
        count = 0
        response_id, new_response_id = 0, 0
        job_end_normal, job_timeout = False, True
        while count < retry_count:
            count = count + 1
            time.sleep(interval_second)
            ret = req_by_msb(JOB_INSTANCE_RESPONSE_ID_URI % (job_id, response_id), "GET")
            if ret[0] != 0:
                logger.error("Failed to query job: %s:%s", ret[2], ret[1])
                continue
            job_result = json.JSONDecoder().decode(ret[1])
            if "responseDescriptor" not in job_result:
                logger.error("Job(%s) does not exist.", job_id)
                continue
            progress = job_result["responseDescriptor"]["progress"]
            new_response_id = job_result["responseDescriptor"]["responseId"]
            job_desc = job_result["responseDescriptor"]["statusDescription"]
            if new_response_id != response_id:
                self.update_job(global_progress, job_desc)
                logger.debug("%s:%s:%s", progress, new_response_id, job_desc)
                response_id = new_response_id
                count = 0
            if progress == JOB_PROGRESS.ERROR:
                if 'already onBoarded' in job_desc:
                    logger.warn("%s:%s", job_id, job_desc)
                    job_end_normal, job_timeout = True, False
                    logger.info("Job(%s) ended", job_id)
                    break
                job_timeout = False
                logger.error("Job(%s) failed: %s", job_id, job_desc)
                break
            elif progress == 100:
                job_end_normal, job_timeout = True, False
                logger.info("Job(%s) ended normally", job_id)
                break
        if job_timeout:
            logger.error("Job(%s) timeout", job_id)
        return job_end_normal

    def wait_func_test_job_done(self, job_id, global_progress, retry_count=60, interval_second=3):
        count = 0
        response_id, new_response_id = 0, 0
        job_end_normal, job_timeout = False, True
        while count < retry_count:
            count = count + 1
            time.sleep(interval_second)
            ret = req_by_msb("/openapi/vnfsdk/v1/functest/taskmanager/testtasks/%s?responseId=%s"
                             % (job_id, response_id), "GET")
            if ret[0] != 0:
                logger.error("Failed to query job: %s:%s", ret[2], ret[1])
                continue
            job_result = json.JSONDecoder().decode(ret[1])
            if "responseDescriptor" not in job_result:
                logger.error("Job(%s) does not exist.", job_id)
                continue
            progress = job_result["responseDescriptor"]["progress"]
            new_response_id = job_result["responseDescriptor"]["responseId"]
            job_desc = job_result["responseDescriptor"]["statusDescription"]
            if new_response_id != response_id:
                self.update_job(global_progress, job_desc)
                logger.debug("%s:%s:%s", progress, new_response_id, job_desc)
                response_id = new_response_id
                count = 0
            if progress == JOB_PROGRESS.ERROR:
                if 'already onBoarded' in job_desc:
                    logger.warn("%s:%s", job_id, job_desc)
                    job_end_normal, job_timeout = True, False
                    logger.info("Job(%s) ended", job_id)
                    break
                job_timeout = False
                logger.error("Job(%s) failed: %s", job_id, job_desc)
                break
            elif progress == 100:
                job_end_normal, job_timeout = True, False
                logger.info("Job(%s) ended normally", job_id)
                break
        if job_timeout:
            logger.error("Job(%s) timeout", job_id)
        return job_end_normal

    def load_config(self):
        json_file = os.path.join(os.path.dirname(__file__), '../biz/verify_vnfs_config.json')
        f = open(json_file)
        json_data = json.JSONDecoder().decode(f.read())
        f.close()
        return json_data
