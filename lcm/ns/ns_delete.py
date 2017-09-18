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
import traceback

from lcm.pub.config.config import REPORT_TO_AAI
from lcm.pub.database.models import DefPkgMappingModel, InputParamMappingModel, ServiceBaseInfoModel
from lcm.pub.database.models import NSInstModel
from lcm.pub.msapi.aai import get_customer_aai, delete_customer_aai


logger = logging.getLogger(__name__)


class DeleteNsService(object):
    def __init__(self, ns_inst_id):
        self.ns_inst_id = ns_inst_id

    def do_biz(self):
        try:
            self.delete_ns()
            if REPORT_TO_AAI:
                self.delete_ns_in_aai()
        except:
            logger.error(traceback.format_exc())

    def delete_ns(self):
        logger.debug("delele NSInstModel(%s)", self.ns_inst_id)
        NSInstModel.objects.filter(id=self.ns_inst_id).delete()

        logger.debug("delele InputParamMappingModel(%s)", self.ns_inst_id)
        InputParamMappingModel.objects.filter(service_id=self.ns_inst_id).delete()

        logger.debug("delele DefPkgMappingModel(%s)", self.ns_inst_id)
        DefPkgMappingModel.objects.filter(service_id=self.ns_inst_id).delete()

        logger.debug("delele ServiceBaseInfoModel(%s)", self.ns_inst_id)
        ServiceBaseInfoModel.objects.filter(service_id=self.ns_inst_id).delete()

    def delete_ns_in_aai(self):
        logger.debug("DeleteNsService::delete_ns_in_aai::delete ns instance[%s] in aai." % self.ns_inst_id)
        global_customer_id = "global-customer-id-" + self.ns_inst_id

        # query ns instance in aai, get resource_version
        customer_info = get_customer_aai(global_customer_id)
        resource_version = customer_info["resource-version"]

        # delete ns instance from aai
        resp_data, resp_status = delete_customer_aai(global_customer_id, resource_version)
        if resp_data:
            logger.debug("Fail to delete ns instance[%s] from aai, resp_status: [%s]." % (self.ns_inst_id, resp_status))
        else:
            logger.debug(
                "Success to delete ns instance[%s] from aai, resp_status: [%s]." % (self.ns_inst_id, resp_status))
