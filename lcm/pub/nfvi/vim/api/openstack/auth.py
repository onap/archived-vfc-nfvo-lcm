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

import logging

from keystoneclient.v2_0 import client

from lcm.pub.nfvi.vim.lib.syscomm import fun_name

logger = logging.getLogger(__name__)

OPENSTACK_CA_CERT = '/etc/httpd/conf.d/cert/vim/ca.cert'
OPENSTACK_CLIENT_CERT = '/etc/httpd/conf.d/cert/vim/client.cert'
OPENSTACK_CLIENT_KEY = '/etc/httpd/conf.d/cert/vim/client.key'


def login(connect_info):
    url, user = connect_info["url"], connect_info["user"]
    passwd, tenant = connect_info["passwd"], connect_info["tenant"]
    cacert, clientcert, clientkey = None, None, None
    insecure = url.startswith('https')
    logger.info(
        "[%s]client.Client(auth_url='%s',"
        "username='%s',password='%s',"
        "tenant_name='%s',insecure=%s,cert='%s',key='%s',cacert='%s')" %
        (fun_name(), url, user, passwd, tenant, insecure, clientcert, clientkey, cacert))
    connect_info["cacert"] = cacert
    connect_info["clientcert"] = clientcert
    connect_info["clientkey"] = clientkey
    connect_info["insecure"] = insecure
    connect_info["keystone"] = client.Client(auth_url=url, username=user, password=passwd, interface='public',
                                             tenant_name=tenant, insecure=insecure, cert=clientcert, key=clientkey,
                                             cacert=cacert, debug=True)
    ret = [0, connect_info]
    return ret
