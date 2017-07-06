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

from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.restcall import req_by_msb


def tosca_plan(uri, inputs):
    """
    https://wiki.open-o.org/view/Common_TOSCA_API_Documentation
    """
    content = {"uri": uri, "inputs": inputs}
    content_str = json.JSONEncoder().encode(content)
    ret = req_by_msb("/openoapi/tosca/v1/indirect/instance", "POST", content_str)
    if ret[0] != 0:
        raise NSLCMException("status code is %s, detail is %s.", ret[2], ret[1])
    if ret[2] != '200':
        raise NSLCMException("tosca error occur when call parser api failed: %s" % content_str)
    return ret[1]
