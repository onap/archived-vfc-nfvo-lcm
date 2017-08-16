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

from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils import restcall
from lcm.pub.config.config import SDC_BASE_URL, SDC_USER, SDC_PASSWD

logger = logging.getLogger(__name__)

ASSETTYPE_RESOURCES = "resources" 
ASSETTYPE_SERVICES = "services"

def call_sdc(resource, method, content=''):
    return restcall.call_req(base_url=SDC_BASE_URL, 
        user=SDC_USER, 
        passwd=SDC_PASSWD, 
        auth_type=restcall.rest_no_auth, 
        resource=resource, 
        method=method, 
        content=content)

def get_artifacts(asset_type):
    resource = "/sdc/v1/catalog/{assetType}"
    resource = resource.format(assetType=asset_type)
    ret = call_sdc(resource, "GET")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to query artifacts(%s) from sdc." % asset_type)
    return json.JSONDecoder().decode(ret[1])

def get_artifact(asset_type, csar_id):
    artifacts = get_artifacts(asset_type)
    for artifact in artifacts:
        if artifact["uuid"] == csar_id:
            return artifact
    raise NSLCMException("Failed to query artifact(%s,%s) from sdc." % (asset_type, csar_id))

def delete_artifact(asset_type, asset_id, artifact_id):
    resource = "/sdc/v1/catalog/{assetType}/{uuid}/artifacts/{artifactUUID}"
    resource = resource.format(assetType=asset_type, uuid=asset_id, artifactUUID=artifact_id)
    ret = call_sdc(resource, "DELETE")
    if ret[0] != 0:
        logger.error("Status code is %s, detail is %s.", ret[2], ret[1])
        raise NSLCMException("Failed to delete artifacts(%s) from sdc." % artifact_id)
    return json.JSONDecoder().decode(ret[1])

def download_artifacts(download_url, local_path):
    ret = restcall.call_req(base_url=download_url, 
        user=SDC_USER, 
        passwd=SDC_PASSWD, 
        auth_type=rest_no_auth, 
        resource="", 
        method="GET")
    # TODO:
    

    


   




