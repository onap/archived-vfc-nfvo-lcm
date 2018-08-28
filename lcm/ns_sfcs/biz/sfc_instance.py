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

from lcm.pub.database.models import VNFFGInstModel, FPInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.share_lock import do_biz_with_share_lock

logger = logging.getLogger(__name__)


class SfcInstance(object):
    def __init__(self, data):
        self.ns_inst_id = data["nsinstid"]
        self.ns_model_data = data["ns_model_data"]
        self.fp_id = data["fpindex"]
        self.fp_inst_id = data["fpinstid"]
        self.sdnControllerId = data["sdncontrollerid"]

    def do_biz(self):
        self.init_data()
        return self.save()

    def init_data(self):
        self.fp_model = self.get_fp_model_by_fp_id()
        logger.info("fp_model.properties:%s, fp_id:%s" % (self.fp_model["properties"], self.fp_id))
        if not self.fp_model:
            return
        logger.info("sfc_inst_symmetric %s" % self.fp_model["properties"].get("symmetric"))
        self.symmetric = self.fp_model["properties"].get("symmetric")
        logger.info("sfc_inst_symmetric %s" % self.symmetric)
        self.policyinfo = self.fp_model["properties"].get("policy")
        self.status = "processing"
        vnffg_database_info = VNFFGInstModel.objects.filter(vnffgdid=self.get_vnffgdid_by_fp_id(),
                                                            nsinstid=self.ns_inst_id).get()
        self.vnffg_inst_id = vnffg_database_info.vnffginstid

    def get_fp_model_by_fp_id(self):
        fps_model = self.ns_model_data["fps"]
        for fp_model in fps_model:
            if fp_model["fp_id"] == self.fp_id:
                return fp_model
        return None

    def get_vnffgdid_by_fp_id(self):
        vnffgs_model = self.ns_model_data["vnffgs"]
        for vnffg_model in vnffgs_model:
            fp_ids = vnffg_model["members"]
            for fp_id in fp_ids:
                if fp_id == self.fp_id:
                    return vnffg_model["vnffg_id"]

    def save(self):
        try:
            logger.info("Sfc Instanciate save2db start : ")
            FPInstModel(fpid=self.fp_id,
                        fpinstid=self.fp_inst_id,
                        nsinstid=self.ns_inst_id,
                        vnffginstid=self.vnffg_inst_id,
                        symmetric=1 if self.symmetric else 0,
                        policyinfo=self.policyinfo,
                        status=self.status,
                        sdncontrollerid=self.sdnControllerId
                        ).save()

            do_biz_with_share_lock("update-sfclist-in-vnffg-%s" % self.ns_inst_id, self.update_vnfffg_info)
            logger.info("Sfc Instanciate save2db end : ")

        except:
            logger.error('SFC instantiation failed')
            raise NSLCMException('SFC instantiation failed.')
        return {
            "fpinstid": self.fp_inst_id
        }

    def update_vnfffg_info(self):
        vnffg_database_info = VNFFGInstModel.objects.filter(vnffginstid=self.vnffg_inst_id).get()
        fp_inst_list = vnffg_database_info.fplist
        fp_inst_list = fp_inst_list + ',' + self.fp_inst_id if fp_inst_list else self.fp_inst_id
        VNFFGInstModel.objects.filter(vnffginstid=self.vnffg_inst_id).update(fplist=fp_inst_list)
