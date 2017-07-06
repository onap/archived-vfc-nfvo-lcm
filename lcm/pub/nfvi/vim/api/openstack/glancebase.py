# Copyright 2016 ZTE Corporation.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#         http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

logger = logging.getLogger(__name__)


def get_glance(funname, auth_info, ver='v2'):
    import glanceclient.v1.client as glanceclient1
    import glanceclient.v2.client as glanceclient2
    keystone = auth_info["keystone"]
    cacert = auth_info["cacert"]
    clientcert = auth_info["clientcert"]
    clientkey = auth_info["clientkey"]
    insecure = auth_info["insecure"]
    glance_endpoint = keystone.service_catalog.url_for(service_type='image')
    logger.info("[%s]call glanceclient.Client('%s',token='%s',insecure=%s,cert_file='%s',key_file='%s',cacert='%s')"
                % (funname, glance_endpoint, keystone.auth_token, insecure, clientcert, clientkey, cacert))
    if 'v1' == ver:
        logger.info("return glanceclient1")
        return glanceclient1.Client(glance_endpoint,
                                    token=keystone.auth_token,
                                    insecure=insecure,
                                    cert_file=clientcert,
                                    key_file=clientkey,
                                    cacert=cacert)
    else:
        logger.info("return glanceclient2")
        return glanceclient2.Client(glance_endpoint,
                                    token=keystone.auth_token,
                                    insecure=insecure,
                                    cert_file=clientcert,
                                    key_file=clientkey,
                                    cacert=cacert)
