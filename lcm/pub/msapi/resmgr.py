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

import json
import logging

from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.restcall import req_by_msb

logger = logging.getLogger(__name__)


def grant_vnf(req_param):
    grant_data = json.JSONEncoder().encode(req_param)
    ret = req_by_msb("/api/resmgr/v1/resource/grant", "PUT", grant_data)
    if ret[0] != 0:
        logger.error("Failed to grant vnf to resmgr. detail is %s.", ret[1])
        # raise NSLCMException('Failed to grant vnf to resmgr.')
        vim_id = ""
        if "vimId" in req_param:
            vim_id = req_param["vimId"]
        elif "additionalparam" in req_param and "vimid" in req_param["additionalparam"]:
            vim_id = req_param["additionalparam"]["vimid"]
        elif "additionalParams" in req_param and "vimid" in req_param["additionalParams"]:
            vim_id = req_param["additionalParams"]["vimid"]
        try:
            from lcm.pub.msapi import extsys
            vim = extsys.get_vim_by_id(vim_id)
            if isinstance(vim, list):
                vim = vim[0]
                vim_id = vim["vimId"]
            if "vimId" in vim:
                vim_id = vim["vimId"]
            grant_rsp = {
                "vim": {
                    "vimId": vim_id,
                    "accessInfo": {
                        "tenant": vim["tenant"]
                    }
                }
            }
            logger.debug("grant_rsp=%s" % grant_rsp)
            return grant_rsp
        except:
            raise NSLCMException('Failed to grant vnf to resmgr.')
    return json.JSONDecoder().decode(ret[1])
