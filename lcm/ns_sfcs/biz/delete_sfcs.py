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
import traceback

from lcm.pub.database.models import FPInstModel, VNFFGInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi import extsys, resmgr, sdncdriver

logger = logging.getLogger(__name__)


class DeleteSfcs(object):
    def __init__(self, sfc_inst_id):
        self.sfc_inst_id = sfc_inst_id
        self.ns_inst_id = ""

    def do(self):
        try:
            sfc_inst_info = FPInstModel.objects.filter(fpinstid=self.sfc_inst_id)
            if not sfc_inst_info:
                logger.warn("sfc inst id(%s) is not exist or has been already deleted" % self.sfc_inst_id)
                return {"result": 0, "detail": "sfc is not exist or has been already deleted"}
            self.ns_inst_id = sfc_inst_info[0].nsinstid
            self.delete_sfc_from_driver(sfc_inst_info[0])
            self.delete_sfc_from_resmgr()
            self.delete_sfc_from_db(sfc_inst_info)
            return {"result": 0, "detail": "delete sfc success"}
        except NSLCMException as e:
            return self.exception_handle(e)
        except Exception as e:
            logger.error(traceback.format_exc())
            return self.exception_handle(e)

    def exception_handle(self, e):
        detail = 'sfc delete failed, detail message: %s' % e.args[0]
        logger.error(detail)
        return {"result": 1, "detail": detail}

    def delete_sfc_from_driver(self, sfc_inst_info):
        sdn_controller_id = sfc_inst_info.sdncontrollerid
        sdn_controller_url = extsys.get_sdn_controller_by_id(sdn_controller_id)["url"]
        sfc_id = sfc_inst_info.sfcid
        flow_classifiers = sfc_inst_info.flowclassifiers
        port_pair_groups = sfc_inst_info.portpairgroups
        if sfc_id:
            req_param = {"sdnControllerId": sdn_controller_id, "url": sdn_controller_url, "id": sfc_id}
            sdncdriver.delete_port_chain(req_param)
        if flow_classifiers:
            for flow_id in flow_classifiers.split(","):
                req_param = {"sdnControllerId": sdn_controller_id, "url": sdn_controller_url, "id": flow_id}
                sdncdriver.delete_flow_classifier(req_param)
        if port_pair_groups:
            for group in json.JSONDecoder().decode(port_pair_groups):
                group_id = group["groupid"]
                req_param = {"sdnControllerId": sdn_controller_id, "url": sdn_controller_url, "id": group_id}
                sdncdriver.delete_port_pair_group(req_param)
                port_pair = group["portpair"]
                for port_pair_id in port_pair:
                    req_param = {"sdnControllerId": sdn_controller_id, "url": sdn_controller_url, "id": port_pair_id}
                    sdncdriver.delete_port_pair(req_param)

    def delete_sfc_from_db(self, sfc_inst_info):
        # do_biz_with_share_lock("delete-sfclist-in-vnffg-%s" % self.ns_inst_id, self.delete_sfc_inst_id_in_vnffg)
        self.delete_sfc_inst_id_in_vnffg()
        sfc_inst_info.delete()

    def delete_sfc_from_resmgr(self):
        resmgr.delete_sfc(self.sfc_inst_id)

    def delete_sfc_inst_id_in_vnffg(self):
        for vnffg_info in VNFFGInstModel.objects.filter(nsinstid=self.ns_inst_id):
            new_sfc_id_list = ""
            for old_sfc_id in vnffg_info.fplist.split(","):
                if old_sfc_id != self.sfc_inst_id:
                    new_sfc_id_list += old_sfc_id + ","
            new_sfc_id_list = new_sfc_id_list[:-1]
            VNFFGInstModel.objects.filter(vnffginstid=vnffg_info.vnffginstid).update(fplist=new_sfc_id_list)
