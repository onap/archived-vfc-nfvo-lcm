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

from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils import restcall

"""
Input:
file:formdata
filename:formdata
=================================
Output:
{
    "status": "int",
    "message": "string",
    "deployedId": "string",
    "processId": "string"
}
"""


def deploy_workflow(file_path):
    file_name = file_path.split("/")[-1]
    file_data = {
        'file': open(file_path, 'rb'),
        'filename': file_name}
    file_data = json.JSONEncoder().encode(file_data)
    ret = restcall.upload_by_msb("api/workflow/v1/package", "POST", file_data)
    if ret[0] != 0:
        raise NSLCMException("Status code is %s, detail is %s.", ret[2], ret[1])
    return json.JSONDecoder().decode(ret[1])


"""
Input:
None
=================================
Output:
{
    "status": "int",
    "message": "string",
}
"""


def undeploy_workflow(deploy_id):
    uri = "api/workflow/v1/package/{deployId}".format(deployId=deploy_id)
    ret = restcall.req_by_msb(uri, "DELETE")
    if ret[0] != 0:
        raise NSLCMException("Status code is %s, detail is %s.", ret[2], ret[1])
    return json.JSONDecoder().decode(ret[1])


"""
Input:
{
    "processId": "string",
    "params": "Map<String, String>"
}
=================================
Output:
{
    "status": "int",
    "message": "string",
}
"""


def exec_workflow(content):
    content_str = json.JSONEncoder().encode(content)
    ret = restcall.req_by_msb("api/workflow/v1/process/instance", "POST", content_str)
    if ret[0] != 0:
        raise NSLCMException("Status code is %s, detail is %s.", ret[2], ret[1])
    return json.JSONDecoder().decode(ret[1])
