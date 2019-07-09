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
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.sdc_run_catalog import query_pnf_descriptor
from lcm.ns_pnfs.biz.get_pnf import GetPnf

logger = logging.getLogger(__name__)


class CreatePnf(object):
    def __init__(self, data):
        self.pnfId = data.get("pnfId")
        self.pnfName = data.get("pnfName")
        self.pnfdId = data.get("pnfdId")
        self.pnfdInfoId = data.get("pnfdInfoId", "")
        self.pnfProfileId = data.get("pnfProfileId", "")
        self.cpInfo = data.get("cpInfo", "")
        self.emsId = data.get("emsId", "")
        self.nsInstances = data.get("nsInstances")

    def do_biz(self):
        self.check_pnfd_valid()
        self.build_cpInfo()
        self.build_emsId()
        self.create_pnf_inst()
        logger.debug("CreatePnf::do_biz::pnfId=%s" % self.pnfId)
        return GetPnf({"pnfId": self.pnfId}, True).do_biz()

    def check_pnfd_valid(self):
        pnf_package_info = query_pnf_descriptor({"pnfdId": self.pnfdId})
        if not pnf_package_info:
            raise NSLCMException("Pnfd(%s) does not exist." % self.pnfdInfoId)

    def build_cpInfo(self):
        # todo
        pass

    def build_emsId(self):
        # todo
        pass

    def create_pnf_inst(self):
        pnfInstances = PNFInstModel.objects.filter(pnfId=self.pnfId)
        if pnfInstances:
            if pnfInstances[0].nsInstances:
                if not pnfInstances.filter(nsInstances__contains=self.nsInstances):
                    for pnfInstance in pnfInstances:
                        new_nsInstances = pnfInstance.nsInstances + "," + self.nsInstances
                        pnfInstance.nsInstances = new_nsInstances
                        pnfInstance.save()
        else:
            PNFInstModel(pnfId=self.pnfId,
                         pnfName=self.pnfName,
                         pnfdId=self.pnfdId,
                         pnfdInfoId=self.pnfdInfoId,
                         pnfProfileId=self.pnfProfileId,
                         cpInfo=self.cpInfo,
                         emsId=self.emsId,
                         nsInstances=self.nsInstances).save()
