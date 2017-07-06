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

from lcm.pub.nfvi.vim.lib.vimexception import VimException


logger = logging.getLogger(__name__)


def get_tenant_id(funname, auth_info, tenant):
    logger.debug("[%s]call get_tenant_id(%s)", funname, tenant)
    keystone = auth_info["keystone"]
    tids = [t.id for t in keystone.tenants.list() if t.name == tenant]
    if not tids:
        raise VimException("Tenant(%s) does not exist." % tenant)
    logger.debug("[%s]tenant_id=%s", funname, tids[0])
    return tids[0]
