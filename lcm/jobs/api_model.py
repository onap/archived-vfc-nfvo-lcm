# Copyright 2019 ZTE Corporation.
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

from lcm.pub.base import ApiModelBase


class JobHistory(ApiModelBase):
    def __init__(self, status="", progress="", statusDescription="", errorCode="", responseId=""):
        self.status = status
        self.progress = progress
        self.statusDescription = statusDescription
        self.errorCode = errorCode
        self.responseId = responseId


class JobDescriptor(ApiModelBase):
    def __init__(self, status="", progress=0, statusDescription="", errorCode="", responseId="", responseHistoryList=None, dict_str=None):
        self.status = dict_str.get("status", "") if dict_str else status
        self.progress = dict_str.get("progress", 0) if dict_str else progress
        self.statusDescription = dict_str.get("statusDescription", "") if dict_str else statusDescription
        self.errorCode = dict_str.get("errorCode", "") if dict_str else errorCode
        self.responseId = dict_str.get("responseId", "") if dict_str else responseId
        self.responseHistoryList = [JobHistory(job_history) for job_history in dict_str.get("responseHistoryList", None)] if dict_str else responseHistoryList


class JobQueryResp(ApiModelBase):
    def __init__(self, jobId="", responseDescriptor=None, dict_str=None):
        self.jobId = dict_str.get("jobId", "") if dict_str else jobId
        self.responseDescriptor = JobDescriptor(dict_str=dict_str.get("responseDescriptor", None)) if dict_str else responseDescriptor


class JobUpdReq(ApiModelBase):
    def __init__(self, progress="", desc="", errcode=""):
        self.progress = progress
        self.desc = desc
        self.errcode = errcode


class JobUpdResp(ApiModelBase):
    def __init__(self, result="", msg=""):
        self.result = result
        self.msg = msg
