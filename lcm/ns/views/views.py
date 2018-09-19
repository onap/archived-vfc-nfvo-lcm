# Copyright 2016-2017 ZTE Corporation.
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

from drf_yasg.utils import swagger_auto_schema
from lcm.ns.biz.ns_manual_scale import NSManualScaleService
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns.serializers.ns_serializers import ManualScaleNsReqSerializer
from lcm.ns.serializers.ns_serializers import NsOperateJobSerializer
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE

logger = logging.getLogger(__name__)


class NSManualScaleView(APIView):
    @swagger_auto_schema(
        request_body=ManualScaleNsReqSerializer(help_text="NS manual scale"),
        responses={
            status.HTTP_202_ACCEPTED: NsOperateJobSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request, ns_instance_id):
        logger.debug("Enter NSManualScaleView::post %s, %s", request.data, ns_instance_id)
        job_id = JobUtil.create_job("NS", JOB_TYPE.MANUAL_SCALE_VNF, ns_instance_id)
        try:
            req_serializer = ManualScaleNsReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NSLCMException(req_serializer.errors)

            NSManualScaleService(ns_instance_id, request.data, job_id).start()

            resp_serializer = NsOperateJobSerializer(data={'jobId': job_id})
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)

            return Response(data=resp_serializer.data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(job_id, 255, 'NS scale failed: %s' % e.message)
            return Response(data={'error': 'NS scale failed: %s' % ns_instance_id},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
