# Copyright 2018 ZTE Corporation.
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
from lcm.pub.database.models import PNFInstModel

logger = logging.getLogger(__name__)


class DeletePnf(object):
    def __init__(self, pnf_id):
        self.pnfId = pnf_id

    def do_biz(self):
        self.check_pnf_used()
        self.delete_pnf()

    def check_pnf_used(self):
        pass  # todo check whether the PNF is used in NS Instances

    def delete_pnf(self):
        logger.debug("delele PnfInstModel(%s)", self.pnfId)
        PNFInstModel.objects.filter(pnfId=self.pnfId).delete()
