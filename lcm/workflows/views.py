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
import sys

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from lcm.pub.database.models import WFPlanModel
from lcm.pub.utils.syscomm import fun_name
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.msapi import activiti


logger = logging.getLogger(__name__)


@api_view(http_method_names=['POST'])
def deploy_workflow(request, *args, **kwargs):
    logger.debug("Enter %s", fun_name())
    try:
        file_path = ignore_case_get(request.data, "filePath")
        force_deploy = ignore_case_get(request.data, "forceDeploy")
        logger.debug("file_path is %s, force_deploy is %s", file_path, force_deploy)
        if force_deploy.upper() == "TRUE":
            WFPlanModel.objects.filter().delete()
        else:
            if WFPlanModel.objects.filter():
                logger.warn("Already deployed.")
                return Response(data={'msg': 'Already deployed.'}, status=status.HTTP_202_ACCEPTED)
        deploy_info = activiti.deploy_workflow(file_path)
        WFPlanModel(
            deployed_id=deploy_info["deployedId"], 
            process_id=deploy_info["processId"], 
            status=deploy_info["status"],
            message=deploy_info["message"],
            plan_name="ns_instantiate").save()
    except:
        logger.error(traceback.format_exc())
        return Response(data={'error': str(sys.exc_info())}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    logger.debug("Leave %s", fun_name())
    return Response(data={'msg': 'OK'}, status=status.HTTP_202_ACCEPTED)





