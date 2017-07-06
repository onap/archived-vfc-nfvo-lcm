# Copyright 2016 ZTE Corporation.
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

import logging

import neutronclient.v2_0.client as neutronclient

logger = logging.getLogger(__name__)


def get_neutron(funname, auth_info, tenant_name):
    username = auth_info["user"]
    passwd = auth_info["passwd"]
    url = auth_info["url"]
    cacert = auth_info["cacert"]
    insecure = auth_info["insecure"]
    logger.info("[%s]call neutronclient.Client(auth_url='%s',"
                "username='%s',password='%s',tenant_name='%s',insecure=%s,ca_cert='%s')"
                % (funname, url, username, passwd, tenant_name, insecure, cacert))
    return neutronclient.Client(username=username, password=passwd, tenant_name=tenant_name,
                                insecure=insecure, auth_url=url, ca_cert=cacert)


def get_neutron_by_tenant_id(funname, auth_info, tenant_id):
    username = auth_info["user"]
    passwd = auth_info["passwd"]
    url = auth_info["url"]
    cacert = auth_info["cacert"]
    logger.info("[%s]call neutronclient.Client(auth_url='%s',"
                "username='%s',password='%s',tenant_id='%s',ca_cert='%s')"
                % (funname, url, username, passwd, tenant_id, cacert))
    return neutronclient.Client(username=username, password=passwd, tenant_id=tenant_id, auth_url=url, ca_cert=cacert)


def get_neutron_default(funname, auth_info):
    return get_neutron(funname, auth_info, auth_info["tenant"])
