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

from lcm.pub.database.models import FPInstModel
from lcm.pub.msapi import extsys
from lcm.pub.msapi import sdncdriver
from lcm.ns_sfcs.biz.utils import get_fp_model_by_fp_inst_id

logger = logging.getLogger(__name__)


class CreateFlowClassifier(object):
    def __init__(self, data):
        self.ns_model_data = data["ns_model_data"]
        self.fp_inst_id = data["fpinstid"]
        self.flow_classifiers_model = get_fp_model_by_fp_inst_id(data["ns_model_data"], self.fp_inst_id)["properties"][
            "policy"]
        self.sdnControllerId = ""
        self.url = ""
        self.dscp = ""
        self.ip_proto = ""
        self.source_port_range = ""
        self.dest_port_range = ""
        self.source_ip_range = ""
        self.dest_ip_range = ""
        self.flow_classfier_id = ""

    def do_biz(self):
        logger.info("CreateFlowClassifier start:")
        self.init_data(self.flow_classifiers_model)
        self.create_flow_classfier()
        self.update_fp_inst()
        logger.info("CreateFlowClassifier end:")

    def init_data(self, flow_classifiers_model):
        fp_database_info = FPInstModel.objects.filter(fpinstid=self.fp_inst_id).get()
        self.sdnControllerId = fp_database_info.sdncontrollerid
        self.url = extsys.get_sdn_controller_by_id(self.sdnControllerId)["url"]
        self.dscp = flow_classifiers_model["criteria"]["dscp"]
        self.ip_proto = flow_classifiers_model["criteria"]["ip_protocol"]
        self.source_port_range = flow_classifiers_model["criteria"]["source_port_range"]
        self.dest_port_range = flow_classifiers_model["criteria"]["dest_port_range"]
        self.dest_ip_range = flow_classifiers_model["criteria"]["dest_ip_range"]
        self.source_ip_range = flow_classifiers_model["criteria"]["source_ip_range"]

    def update_fp_inst(self):
        fp_inst_info = FPInstModel.objects.filter(fpinstid=self.fp_inst_id).get()
        fp_inst_info.flowclassifiers = self.flow_classfier_id
        FPInstModel.objects.filter(fpinstid=self.fp_inst_id).update(flowclassifiers=fp_inst_info.flowclassifiers)

    def create_flow_classfier(self):
        data = {
            "sdnControllerId": self.sdnControllerId,
            "url": self.url,
            "name": "",
            "description": "",
            "dscp": self.dscp,
            "ip_proto": self.ip_proto,
            "source_port_range": self.source_port_range,
            "dest_port_range": self.dest_port_range,
            "source_ip_range": self.concat_str(self.source_ip_range),
            "dest_ip_range": self.concat_str(self.dest_ip_range)
        }
        # req_param = json.JSONEncoder().encoding(data)
        # url = "/api/sdncdriver/v1.0/createflowclassfier"
        # ret = req_by_msb(url,"POST", data)
        # if ret[0] > 0:
        #     logger.error('Send Flow Classifier request to Driver failed.')
        #     utils.sfc_inst_failed_handle(self.fp_inst_id, "Send Flow Classifier request to Driver failed.")
        #     raise NSLCMException('Send Flow Classifier request to Driver failed.')
        # resp_body = json.loads(ret[1])
        self.flow_classfier_id = sdncdriver.create_flow_classfier(data)

    def concat_str(self, str_list):
        final_str = ""
        for str in str_list:
            final_str += str + ","
        return final_str[:-1]
