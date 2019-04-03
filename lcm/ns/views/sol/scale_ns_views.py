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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from lcm.ns.biz.ns_manual_scale import NSManualScaleService
from lcm.ns.serializers.sol.scale_ns_serializers import ScaleNsRequestSerializer
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE
from lcm.ns.const import NS_OCC_BASE_URI
from lcm.pub.exceptions import BadRequestException
from lcm.ns.serializers.sol.pub_serializers import ProblemDetailsSerializer

logger = logging.getLogger(__name__)


class ScaleNSView(APIView):
    @swagger_auto_schema(
        request_body=ScaleNsRequestSerializer(help_text="NS Scale"),
        responses={
            status.HTTP_202_ACCEPTED: "HTTP_202_ACCEPTED",
            status.HTTP_500_INTERNAL_SERVER_ERROR: ProblemDetailsSerializer()
        }
    )
    def post(self, request, ns_instance_id):
        logger.debug("Enter ScaleNSView::post %s, %s", request.data, ns_instance_id)
        job_id = JobUtil.create_job("NS", JOB_TYPE.MANUAL_SCALE_VNF, ns_instance_id)
        try:
            req_serializer = ScaleNsRequestSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NSLCMException(req_serializer.errors)
            nsManualScaleService = NSManualScaleService(ns_instance_id, request.data, job_id)
            nsManualScaleService.start()
            response = Response(data={}, status=status.HTTP_202_ACCEPTED)
            logger.debug("Location: %s" % nsManualScaleService.occ_id)
            response["Location"] = NS_OCC_BASE_URI % nsManualScaleService.occ_id
            logger.debug("Leave ScaleNSView")
            return response
        except BadRequestException as e:
            logger.error("Exception in ScaleNSView: %s", e.message)
            JobUtil.add_job_status(job_id, 255, 'NS scale failed: %s' % e.message)
            data = {'status': status.HTTP_400_BAD_REQUEST, 'detail': e.message}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception in ScaleNSView: %s", e.message)
            JobUtil.add_job_status(job_id, 255, 'NS scale failed: %s' % e.message)
            data = {'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'detail': e.message}
            return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
