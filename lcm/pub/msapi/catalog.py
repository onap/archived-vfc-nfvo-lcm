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

from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.exceptions import NSLCMException

logger = logging.getLogger(__name__)

STATUS_ONBOARDED, STATUS_NON_ONBOARDED = "onBoarded", "non-onBoarded"
P_STATUS_ENABLED, P_STATUS_DISABLED = "Enabled", "Disabled"
P_STATUS_NORMAL, P_STATUS_ONBOARDING, P_STATUS_ONBOARDFAILED = "normal", "onBoarding", "onBoardFailed"
P_STATUS_DELETING, P_STATUS_DELETEFAILED = "deleting", "deleteFailed"


def query_csar_from_catalog(csar_id, key=''):
    ret = req_by_msb("/openoapi/catalog/v1/csars/%s" % csar_id, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        if ret[2] == '404':
            raise NSLCMException("CSAR(%s) does not exist." % csar_id)
        raise NSLCMException("Failed to query CSAR(%s) from catalog." % csar_id)
    csar_info = json.JSONDecoder().decode(ret[1])
    return ignore_case_get(csar_info, key) if key else csar_info


def query_rawdata_from_catalog(csar_id, input_parameters=[]):
    req_param = json.JSONEncoder().encode({"csarId": csar_id, "inputParameters": input_parameters})
    ret = req_by_msb("/openoapi/catalog/v1/servicetemplates/queryingrawdata", "POST", req_param)
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query rawdata of CSAR(%s) from catalog." % csar_id)
    return json.JSONDecoder().decode(ret[1])


def set_csar_state(csar_id, prop, val):
    ret = req_by_msb("/openoapi/catalog/v1/csars/%s?%s=%s" % (csar_id, prop, val), "PUT")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        return [1, "Failed to set %s to %s of CSAR(%s)." % (prop, val, csar_id)]
    return [0, "Set %s to %s of CSAR(%s) successfully." % (prop, val, csar_id)]


def delete_csar_from_catalog(csar_id):
    ret = req_by_msb("/openoapi/catalog/v1/csars/%s" % csar_id, "DELETE")
    if ret[0] != 0 and ret[2] != '404':
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        set_csar_state(csar_id, "processState", P_STATUS_DELETEFAILED)
        return [1, "Failed to delete CSAR(%s) from catalog." % csar_id]
    return [0, "Delete CSAR(%s) successfully." % csar_id]


def get_download_url_from_catalog(csar_id, relative_path):
    ret = req_by_msb("/openoapi/catalog/v1/csars/%s/files?relativePath=%s" % (csar_id, relative_path), "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to get download url of CSAR(%s)." % csar_id)
    csar_file_info = json.JSONDecoder().decode(ret[1])
    return ignore_case_get(csar_file_info, "downloadUri"), ignore_case_get(csar_file_info, "localPath")


def get_process_id(name, srv_template_id):
    ret = req_by_msb('/openoapi/catalog/v1/servicetemplates/%s/operations' % srv_template_id, 'GET')
    if ret[0] != 0:
        raise NSLCMException('Failed to get service[%s,%s] process id' % (name, srv_template_id))
    items = json.JSONDecoder().decode(ret[1])
    for item in items:
        if name in item['name']:
            return item['processId']
    raise NSLCMException('service[%s,%s] process id not exist' % (name, srv_template_id))

def get_servicetemplate_id(nsd_id):
    ret = req_by_msb('/openoapi/catalog/v1/servicetemplates', 'GET')
    if ret[0] != 0:
        raise NSLCMException('Failed to get servicetemplates info')
    stpls = json.JSONDecoder().decode(ret[1])
    for stpl in stpls:
        if stpl.get("id", "") == nsd_id:
            return stpl["serviceTemplateId"]
    raise NSLCMException('servicetemplate(%s) does not exist.' % nsd_id)
    
def get_servicetemplate(nsd_id):
    ret = req_by_msb('/openoapi/catalog/v1/servicetemplates', 'GET')
    if ret[0] != 0:
        raise NSLCMException('Failed to get servicetemplates info')
    stpls = json.JSONDecoder().decode(ret[1])
    for stpl in stpls:
        if stpl.get("id", "") == nsd_id:
            return stpl
    return NSLCMException('servicetemplate(%s) does not exist.' % nsd_id)
