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

from django.conf.urls import include, url
from django.contrib import admin

from lcm.pub.config.config import DEPLOY_WORKFLOW_WHEN_START
from lcm.pub.config.config import REG_TO_MSB_WHEN_START, REG_TO_MSB_REG_URL, REG_TO_MSB_REG_PARAM, MSB_SVC_URL


urlpatterns = [
    url(r'^api/nslcm/v1/admin', admin.site.urls),
    url(r'^', include('lcm.samples.urls')),
    url(r'^', include('lcm.ns_vnfs.urls')),
    url(r'^', include('lcm.ns_pnfs.urls')),
    url(r'^', include('lcm.ns_vls.urls')),
    url(r'^', include('lcm.ns_sfcs.urls')),
    url(r'^', include('lcm.ns.urls')),
    url(r'^', include('lcm.jobs.urls')),
    url(r'^', include('lcm.workflows.urls')),
    url(r'^', include('lcm.swagger.urls')),
]

# regist to MSB when startup
if REG_TO_MSB_WHEN_START == "true":
    import json
    from lcm.pub.utils.restcall import req_by_msb
    req_by_msb(MSB_SVC_URL % "v1", "DELETE")
    req_by_msb(REG_TO_MSB_REG_URL, "POST", json.JSONEncoder().encode(REG_TO_MSB_REG_PARAM))

    req_by_msb(MSB_SVC_URL % "v2", "DELETE")
    v2_param = REG_TO_MSB_REG_PARAM.copy()
    v2_param["version"] = "v2"
    v2_param["url"] = v2_param["url"].replace("v1", "v2")
    req_by_msb(REG_TO_MSB_REG_URL, "POST", json.JSONEncoder().encode(v2_param))

# deploy workflow when startup
if DEPLOY_WORKFLOW_WHEN_START:
    from lcm.workflows import auto_deploy
    auto_deploy.deploy_workflow_on_startup()
