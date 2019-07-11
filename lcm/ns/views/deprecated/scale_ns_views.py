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

from lcm.ns.biz.ns_manual_scale import NSManualScaleService
from lcm.ns.serializers.deprecated.ns_serializers import _NsOperateJobSerializer
from lcm.ns.serializers.deprecated.ns_serializers import _ManualScaleNsReqSerializer
from lcm.pub.exceptions import NSLCMException
from lcm.pub.exceptions import BadRequestException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION
from .common import view_safe_call_with_log

logger = logging.getLogger(__name__)


class NSManualScaleView(APIView):
    @swagger_auto_schema(
        request_body=_ManualScaleNsReqSerializer(help_text="NS manual scale"),
        responses={
            status.HTTP_202_ACCEPTED: _NsOperateJobSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def post(self, request, ns_instance_id):
        logger.debug("Enter NSManualScaleView::post %s, %s", request.data, ns_instance_id)
        req_serializer = _ManualScaleNsReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            raise BadRequestException(req_serializer.errors)

        req = request.data
        scale_data = {}
        scale_data['scaleType'] = req['scaleType']
        scaleNsData = req['scaleNsData'][0]
        scale_data['scaleNsData'] = {
            "scaleNsByStepsData": scaleNsData['scaleNsByStepsData'][0]
        }
        job_id = JobUtil.create_job(
            JOB_TYPE.NS,
            JOB_ACTION.MANUAL_SCALE,
            ns_instance_id
        )
        NSManualScaleService(ns_instance_id, scale_data, job_id).start()

        resp_serializer = _NsOperateJobSerializer(data={'jobId': job_id})
        if not resp_serializer.is_valid():
            raise NSLCMException(resp_serializer.errors)

        return Response(data=resp_serializer.data, status=status.HTTP_202_ACCEPTED)
