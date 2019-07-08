# Copyright (c) 2018, CMCC Technologies Co., Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns.biz.ns_update import NSUpdateService
from lcm.ns.serializers.sol.update_serializers import UpdateNsReqSerializer
from lcm.pub.exceptions import BadRequestException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION
from lcm.ns.const import NS_OCC_BASE_URI
from lcm.ns.serializers.sol.pub_serializers import ProblemDetailsSerializer
from .common import view_safe_call_with_log

logger = logging.getLogger(__name__)


class UpdateNSView(APIView):
    @swagger_auto_schema(
        request_body=UpdateNsReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: "HTTP_202_ACCEPTED",
            status.HTTP_500_INTERNAL_SERVER_ERROR: ProblemDetailsSerializer()
        }
    )
    @view_safe_call_with_log(logger=logger)
    def post(self, request, ns_instance_id):
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.UPDATE, ns_instance_id)

        logger.debug("Enter UpdateNSView::post %s, %s", request.data, ns_instance_id)
        req_serializer = UpdateNsReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.debug("request.data is not valid,error: %s" % req_serializer.errors)
            raise BadRequestException(req_serializer.errors)
        ns_update_service = NSUpdateService(ns_instance_id, request.data, job_id)
        ns_update_service.start()
        response = Response(data={}, status=status.HTTP_202_ACCEPTED)
        logger.debug("Location: %s" % ns_update_service.occ_id)
        response["Location"] = NS_OCC_BASE_URI % ns_update_service.occ_id
        logger.debug("Leave UpdateNSView")
        return response
