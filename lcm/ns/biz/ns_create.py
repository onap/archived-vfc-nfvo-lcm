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
import uuid

from lcm.pub.config.config import REPORT_TO_AAI
from lcm.pub.database.models import NSInstModel
from lcm.pub.exceptions import NSLCMException
from lcm.pub.msapi.aai import create_ns_aai
from lcm.pub.msapi.sdc_run_catalog import query_nspackage_by_id
from lcm.pub.utils.timeutil import now_time
from lcm.pub.utils.values import ignore_case_get
from lcm.ns.const import SERVICE_ROLE, SERVICE_TYPE

logger = logging.getLogger(__name__)


class CreateNSService(object):
    def __init__(self, csar_id, ns_name, description, context):
        self.csar_id = csar_id
        self.ns_name = ns_name
        self.description = description
        self.global_customer_id = ignore_case_get(context, 'globalCustomerId')
        self.service_type = ignore_case_get(context, 'serviceType')
        self.ns_inst_id = ''
        self.ns_package_id = ''

    def do_biz(self):
        self.check_nsd_valid()
        self.check_ns_inst_name_exist()
        self.create_ns_inst()
        if REPORT_TO_AAI:
            self.create_ns_in_aai()
        logger.debug("CreateNSService::do_biz::ns_inst_id=%s" % self.ns_inst_id)
        return self.ns_inst_id

    def check_nsd_valid(self):
        logger.debug("CreateNSService::check_nsd_valid::csar_id=%s" % self.csar_id)
        ns_package_info = query_nspackage_by_id(self.csar_id)
        if not ns_package_info:
            raise NSLCMException("nsd(%s) not exists." % self.csar_id)
        packageInfo = ns_package_info["packageInfo"]
        self.ns_package_id = ignore_case_get(packageInfo, "nsPackageId")
        self.nsd_id = ignore_case_get(packageInfo, "nsdId")
        self.nsd_invariant_id = ignore_case_get(packageInfo, "nsdInvariantId")
        logger.debug("CreateNSService::check_nsd_valid::ns_package_id=%s,nsd_id=%s", self.ns_package_id, self.nsd_id)

    def check_ns_inst_name_exist(self):
        is_exist = NSInstModel.objects.filter(name=self.ns_name).exists()
        logger.debug("CreateNSService::check_ns_inst_name_exist::is_exist=%s" % is_exist)
        if is_exist:
            raise NSLCMException("ns(%s) already existed." % self.ns_name)

    def create_ns_inst(self):
        self.ns_inst_id = str(uuid.uuid4())
        logger.debug("CreateNSService::create_ns_inst::ns_inst_id=%s" % self.ns_inst_id)
        NSInstModel(id=self.ns_inst_id,
                    name=self.ns_name,
                    nspackage_id=self.ns_package_id,
                    nsd_id=self.nsd_id,
                    nsd_invariant_id=self.nsd_invariant_id,
                    description=self.description,
                    status='NOT_INSTANTIATED',  # 'empty',
                    lastuptime=now_time(),
                    global_customer_id=self.global_customer_id,
                    service_type=self.service_type).save()

    def create_ns_in_aai(self):
        logger.debug("CreateNSService::create_ns_in_aai::report ns instance[%s] to aai." % self.ns_inst_id)
        try:
            data = {
                "service-instance-id": self.ns_inst_id,
                "service-instance-name": self.ns_name,
                "service-type": SERVICE_TYPE,
                "service-role": SERVICE_ROLE
            }
            resp_data, resp_status = create_ns_aai(self.global_customer_id, self.service_type, self.ns_inst_id, data)
            logger.debug("Success to create ns[%s] to aai:[%s],[%s].", self.ns_inst_id, resp_data, resp_status)
        except NSLCMException as e:
            logger.debug("Fail to createns[%s] to aai, detail message: %s" % (self.ns_inst_id, e.args[0]))
        except:
            logger.error(traceback.format_exc())
