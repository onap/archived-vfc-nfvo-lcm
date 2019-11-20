# Copyright 2019 ZTE Corporation.
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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns.biz.ns_terminate import TerminateNsService
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION
from lcm.pub.utils.values import ignore_case_get
from lcm.ns.serializers.sol.terminate_ns_serializers import TerminateNsReqSerializer
from lcm.pub.exceptions import BadRequestException
from lcm.ns.const import NS_OCC_BASE_URI
from lcm.ns.serializers.sol.pub_serializers import ProblemDetailsSerializer
from .common import view_safe_call_with_log

logger = logging.getLogger(__name__)


class TerminateNsView(APIView):

    @swagger_auto_schema(
        request_body=TerminateNsReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: "HTTP_202_ACCEPTED",
            status.HTTP_500_INTERNAL_SERVER_ERROR: ProblemDetailsSerializer()
        }
    )
    @view_safe_call_with_log(logger=logger)
    def post(self, request, ns_instance_id):
        job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.TERMINATE, ns_instance_id)

        logger.debug("Enter TerminateNSView::post %s", request.data)
        req_serializer = TerminateNsReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.debug("request.data is not valid,error: %s" % req_serializer.errors)
            raise BadRequestException(req_serializer.errors)
        termination_time = ignore_case_get(request.data, 'terminationTime')
        logger.debug("terminationTime is %s" % termination_time)
        # todo terminationTime
        terminate_ns_service = TerminateNsService(ns_instance_id, job_id, request.data)
        terminate_ns_service.start()
        logger.debug("Location: %s" % terminate_ns_service.occ_id)
        response = Response(data={'jobId': job_id}, status=status.HTTP_202_ACCEPTED)
        response["Location"] = NS_OCC_BASE_URI % terminate_ns_service.occ_id
        logger.debug("Leave TerminateNSView")
        return response
