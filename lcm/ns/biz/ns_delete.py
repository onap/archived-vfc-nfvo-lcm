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
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.aai import query_ns_aai, delete_ns_aai

logger = logging.getLogger(__name__)


class DeleteNsService(object):
    def __init__(self, ns_inst_id):
        self.ns_inst_id = ns_inst_id

    def do_biz(self):
        try:
            if REPORT_TO_AAI:
                self.delete_ns_in_aai()
            self.delete_ns()
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
        try:
            ns_insts = NSInstModel.objects.filter(id=self.ns_inst_id)
            if ns_insts:
                self.global_customer_id = ns_insts[0].global_customer_id
                self.service_type = ns_insts[0].service_type
                # query ns instance in aai, get resource_version
                logger.debug("self.global_customer_id=[%s], self.service_type=[%s], self.ns_inst_id=[%s]"
                             % (self.global_customer_id, self.service_type, self.ns_inst_id))
                ns_info = query_ns_aai(self.global_customer_id, self.service_type, self.ns_inst_id)
                resource_version = ns_info["resource-version"]

                # delete ns instance from aai
                logger.debug("ns instance resource_version=[%s]" % resource_version)
                resp_data, resp_status = delete_ns_aai(self.global_customer_id, self.service_type,
                                                       self.ns_inst_id, resource_version)
                logger.debug("Success to delete ns[%s] from aai, resp_status: [%s]." % (self.ns_inst_id, resp_status))
        except NSLCMException as e:
            logger.debug("Fail to delete ns[%s] from aai, detail message: %s" % (self.ns_inst_id, e.args[0]))
        except:
            logger.error(traceback.format_exc())
