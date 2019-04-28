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


class JobHistory(object):
    def __init__(self, status="", progress="", statusDescription="", errorCode="", responseId=""):
        self.status = status
        self.progress = progress
        self.statusDescription = statusDescription
        self.errorCode = errorCode
        self.responseId = responseId


class JobDescriptor(object):
    def __init__(self, status="", progress=0, statusDescription="", errorCode="", responseId="", responseHistoryList=None):
        self.status = status
        self.progress = progress
        self.statusDescription = statusDescription
        self.errorCode = errorCode
        self.responseId = responseId
        self.responseHistoryList = responseHistoryList


class JobQueryResp(object):
    def __init__(self, jobId="", responseDescriptor=None):
        self.jobId = jobId
        self.responseDescriptor = responseDescriptor


class JobUpdReq(object):
    def __init__(self, progress="", desc="", errcode=""):
        self.progress = progress
        self.desc = desc
        self.errcode = errcode

    def load(self, data):
        self.progress = data["progress"]
        self.desc = data["desc"]
        self.errcode = data["errcode"]


class JobUpdResp(object):
    def __init__(self, result="", msg=""):
        self.result = result
        self.msg = msg

    def load(self, data):
        self.result = data["result"]
        self.msg = data["msg"]
