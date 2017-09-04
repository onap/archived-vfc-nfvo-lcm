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

from lcm.pub.database.models import FPInstModel
from lcm.pub.msapi import extsys
from lcm.pub.msapi import sdncdriver

logger = logging.getLogger(__name__)


class CreatePortChain(object):
    def __init__(self, data):
        self.fp_inst_id = data["fpinstid"]
        self.ns_model_info = data["ns_model_data"]
        self.sdnControllerId = ""
        self.symmetric = ""
        self.port_pair_groups_ids = []
        self.flow_classifier_ids = []

    def do_biz(self):
        logger.info("CreatePortChain start:")
        self.init_data()
        self.create_sfc()
        logger.info("CreatePortChain end:")

    def init_data(self):
        fp_inst_info = FPInstModel.objects.filter(fpinstid=self.fp_inst_id).get()
        self.sdnControllerId = fp_inst_info.sdncontrollerid
        self.symmetric = "true" if fp_inst_info.symmetric == 1 else "false"
        flow_classfier_str = fp_inst_info.flowclassifiers
        self.flow_classifier_ids = [flow_classfier_str]
        portpairgroup_ids = []
        for portpairgroup in json.loads(fp_inst_info.portpairgroups):
            portpairgroup_ids.append(portpairgroup["groupid"])
        self.port_pair_groups_ids = portpairgroup_ids

    def create_sfc(self):
        data = {
            "sdnControllerId": self.sdnControllerId,
            "url": extsys.get_sdn_controller_by_id(self.sdnControllerId)["url"],
            "flowClassifiers": self.flow_classifier_ids,
            "portPairGroups": self.port_pair_groups_ids,
            "symmetric": self.symmetric
        }

        # url = "/api/sdncdriver/v1.0/createchain"
        # req_param = json.JSONEncoder.encoding(data)
        # ret = req_by_msb(url, "POST", req_param)
        # ret = req_by_msb("OPENAPI_CREATE_SERVICE_PORT_CHAIN",data)
        # if ret[0] > 0:
        #     logger.error('Send SFC Create request to Driver failed.')
        #     sfc_inst_failed_handle( "Send SFC Create request to Driver failed.")
        #     raise NSLCMException('Send SFC Create request to Driver failed.')
        # resp_body = json.loads(ret[1])
        # sfc_id = resp_body["id"]
        sfc_id = sdncdriver.create_port_chain(data)
        FPInstModel.objects.filter(fpinstid=self.fp_inst_id).update(sfcid=sfc_id)

        # def get_url_by_sdncontrollerid(self):
        #     try:
        #         logger.warn("query sdncontroller by id begins:")
        #
        #         url = "/api/aai-esr-server/v1/sdncontrollers/%s" % (self.sdnControllerId)
        #         ret = req_by_msb(url, "GET")
        #         if ret[0] > 0:
        #             logger.error('query sdncontroller failed.')
        #             raise VnfoException('query sdncontroller failed.')
        #         resp_body = json.JSONDecoder().decode(ret[1])
        #         logger.warn("query sdncontroller by id ends:")
        #     except:
        #         if ret[0] > 0:
        #             logger.error('Send Flow Classifier request to Driver failed.')
        #             self.sfc_inst_failed_handle(self.fp_inst_id, "Send Flow Classifier request to Driver failed.")
        #             raise VnfoException('Send Flow Classifier request to Driver failed.')
        #
        #     return resp_body('url')

        # def sfc_inst_failed_handle(fp_inst_id, error_msg):
        #     logger.error('create sfc  failed, detail message: %s' % error_msg)
        #     FPInstModel.objects.filter(fpid=fp_inst_id).update(status="disabled").get()
