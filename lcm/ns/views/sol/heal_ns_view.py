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

from .common import view_safe_call_with_log
from drf_yasg.utils import swagger_auto_schema
from lcm.ns.biz.ns_heal import NSHealService
from lcm.ns.const import NS_OCC_BASE_URI
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION
from lcm.pub.exceptions import BadRequestException
from lcm.ns.serializers.sol.heal_serializers import HealNsReqSerializer
from lcm.ns.serializers.sol.pub_serializers import ProblemDetailsSerializer
from lcm.pub.utils.jobutil import JobUtil
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealNSView(APIView):
    @swagger_auto_schema(
        request_body=HealNsReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: "HTTP_202_ACCEPTED",
            status.HTTP_500_INTERNAL_SERVER_ERROR: ProblemDetailsSerializer()
        }
    )
    @view_safe_call_with_log(logger=logger)
    def post(self, request, ns_instance_id):
        logger.debug("Enter HealNSView::post nsInstanceId:%s, request.data:%s" % (ns_instance_id, request.data))
        req_serializer = HealNsReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.error("request.data is not valid,error: %s" % req_serializer.errors)
            raise BadRequestException(req_serializer.errors)

        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.HEAL, ns_instance_id)
        ns_heal_service = NSHealService(ns_instance_id, request.data, job_id)
        ns_heal_service.start()
        response = Response(data={}, status=status.HTTP_202_ACCEPTED)
        logger.debug("Location: %s" % ns_heal_service.occ_id)
        response["Location"] = NS_OCC_BASE_URI % ns_heal_service.occ_id
        logger.debug("Leave NSHealView")
        return response
