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

from lcm.pub.config.config import REPORT_TO_AAI
from lcm.pub.database.models import VLInstModel, VNFFGInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi import resmgr, extsys
from lcm.pub.msapi.aai import query_network_aai, delete_network_aai
from lcm.pub.nfvi.vim import vimadaptor

logger = logging.getLogger(__name__)


class DeleteVls(object):
    def __init__(self, vl_inst_id):
        self.vl_inst_id = vl_inst_id
        self.ns_inst_id = ""

    def do(self):
        try:
            vl_inst_info = VLInstModel.objects.filter(vlinstanceid=self.vl_inst_id)
            if not vl_inst_info:
                logger.info("vl inst id(%s) is not exist or has been already deleted" % self.vl_inst_id)
                return {"result": 0, "detail": "vl is not exist or has been already deleted"}
            self.ns_inst_id = vl_inst_info[0].ownerid
            # vim_id = vl_inst_info[0].vimid
            vim_id = json.JSONDecoder().decode(vl_inst_info[0].vimid) if isinstance(vl_inst_info[0].vimid, str) \
                else vl_inst_info[0].vimid
            subnetwork_id_list = vl_inst_info[0].relatedsubnetworkid.split(",")
            network_id = vl_inst_info[0].relatednetworkid
            self.delete_vl_from_vim(vim_id, subnetwork_id_list, network_id)
            self.delete_vl_from_resmgr()
            if REPORT_TO_AAI:
                self.delete_network_and_subnet_in_aai()
            self.delete_vl_from_db(vl_inst_info)
            return {"result": 0, "detail": "delete vl success"}
        except NSLCMException as e:
            return self.exception_handle(e)
        except Exception as e:
            logger.error(traceback.format_exc())
            return self.exception_handle(e)

    def exception_handle(self, e):
        detail = "vl delete failed, detail message: %s" % e.args[0]
        logger.error(detail)
        return {"result": 0, "detail": detail}

    def delete_vl_from_vim(self, vim_id, subnetwork_id_list, network_id):
        vim_resp_body = extsys.get_vim_by_id(vim_id)
        data = {
            "vimid": vim_id,
            "vimtype": vim_resp_body["type"],
            "url": vim_resp_body["url"],
            "user": vim_resp_body["userName"],
            "passwd": vim_resp_body["password"],
            "tenant": vim_resp_body["tenant"]}
        vim_api = vimadaptor.VimAdaptor(data)
        for subnetwork_id in subnetwork_id_list:
            vim_api.delete_subnet(subnet_id=subnetwork_id)
        vim_api.delete_network(network_id=network_id)

    def delete_vl_from_resmgr(self):
        resmgr.delete_vl(self.vl_inst_id)

    def delete_vl_inst_id_in_vnffg(self):
        for vnffg_info in VNFFGInstModel.objects.filter(nsinstid=self.ns_inst_id):
            new_vl_id_list = ""
            for old_vl_id in vnffg_info.vllist.split(","):
                if old_vl_id != self.vl_inst_id:
                    new_vl_id_list += old_vl_id + ","
            new_vl_id_list = new_vl_id_list[:-1]
            VNFFGInstModel.objects.filter(vnffginstid=vnffg_info.vnffginstid).update(vllist=new_vl_id_list)

    def delete_network_and_subnet_in_aai(self):
        logger.debug("DeleteVls::delete_network_in_aai[%s] in aai.", self.vl_inst_id)
        try:
            # query network in aai, get resource_version
            customer_info = query_network_aai(self.vl_inst_id)
            resource_version = customer_info.get("resource-version")

            # delete network from aai
            resp_data, resp_status = delete_network_aai(self.vl_inst_id, resource_version)
            logger.debug("Delete network[%s] from aai successfully, status: %s", self.vl_inst_id, resp_status)
        except NSLCMException as e:
            logger.debug("Fail to delete network[%s] from aai: %s", self.vl_inst_id, e.args[0])
        except Exception as e:
            logger.error("Exception occurs when delete network[%s] from aai: %s", self.vl_inst_id, e.args[0])
            logger.error(traceback.format_exc())

    def delete_vl_from_db(self, vl_inst_info):
        # do_biz_with_share_lock("delete-vllist-in-vnffg-%s" % self.ns_inst_id, self.delete_vl_inst_id_in_vnffg)
        self.delete_vl_inst_id_in_vnffg()
        vl_inst_info.delete()
