# Copyright 2017 ZTE Corporation.
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
import os

from lcm.pub.database.models import WFPlanModel
from lcm.pub.msapi import activiti

logger = logging.getLogger(__name__)


def deploy_workflow_on_startup():
    try:
        if WFPlanModel.objects.filter():
            logger.warn("Workflow is already deployed.")
            return
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_path, "ns/data/nsinit.bpmn20.xml")
        deploy_info = activiti.deploy_workflow(file_path)
        WFPlanModel(
            deployed_id=deploy_info["deployedId"],
            process_id=deploy_info["processId"],
            status=deploy_info["status"],
            message=deploy_info["message"],
            plan_name="ns_instantiate").save()
        logger.info("Deploy workflow successfully.")
    except:
        logger.error(traceback.format_exc())
