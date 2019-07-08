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
from threading import Thread

from lcm.ns_sfcs.biz.create_flowcla import CreateFlowClassifier
from lcm.ns_sfcs.biz.create_port_chain import CreatePortChain
from lcm.ns_sfcs.biz.create_portpairgp import CreatePortPairGroup

from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.ns_sfcs.biz.utils import update_fp_status

logger = logging.getLogger(__name__)


class CreateSfcWorker(Thread):
    def __init__(self, data):
        super(CreateSfcWorker, self).__init__()
        self.ns_inst_id = data["nsinstid"]
        self.ns_model_data = data["ns_model_data"]
        self.fp_id = data["fpindex"]
        self.sdnControllerId = data["sdncontrollerid"]
        self.fp_inst_id = data["fpinstid"]
        self.data = data
        self.job_id = ""

    def init_data(self):
        self.job_id = JobUtil.create_job("SFC", "sfc_init", self.ns_inst_id + "_" + self.fp_id)
        return self.job_id

    def run(self):
        try:
            logger.info("Service Function Chain Worker  start : ")

            CreateFlowClassifier(self.data).do_biz()
            JobUtil.add_job_status(self.job_id, 50, "create flow classifer successfully!", "")
            CreatePortPairGroup(self.data).do_biz()
            JobUtil.add_job_status(self.job_id, 75, "create port pair group successfully!", "")
            CreatePortChain(self.data).do_biz()
            update_fp_status(self.fp_inst_id, "active")
            JobUtil.add_job_status(self.job_id, 100, "create port chain successful!", "")
            logger.info("Service Function Chain Worker end : ")
        except NSLCMException as e:
            self.handle_exception(e)
        except Exception as e:
            self.handle_exception(e)

    def handle_exception(self, e):
        detail = "sfc instantiation failed, detail message: %s" % e.args[0]
        JobUtil.add_job_status(self.job_id, 255, "create sfc failed!", "")
        logger.error(traceback.format_exc())
        logger.error(detail)
        update_fp_status(self.fp_inst_id, "failed")
