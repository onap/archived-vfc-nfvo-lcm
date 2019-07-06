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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns.biz.ns_heal import NSHealService
from lcm.ns.serializers.deprecated.ns_serializers import _HealNsReqSerializer
from lcm.ns.serializers.deprecated.ns_serializers import _NsOperateJobSerializer
from lcm.pub.exceptions import NSLCMException
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.enum import JOB_TYPE, JOB_ACTION

logger = logging.getLogger(__name__)


class NSHealView(APIView):
    @swagger_auto_schema(
        request_body=_HealNsReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: _NsOperateJobSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request, ns_instance_id):
        try:
            logger.debug("Enter HealNSView::post %s", request.data)
            logger.debug("Enter HealNSView:: %s", ns_instance_id)
            req_serializer = _HealNsReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NSLCMException(req_serializer.errors)

            job_id = JobUtil.create_job(JOB_TYPE.NS, JOB_ACTION.HEAL, ns_instance_id)
            NSHealService(ns_instance_id, request.data, job_id).start()

            resp_serializer = _NsOperateJobSerializer(data={'jobId': job_id})
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)

            logger.debug("Leave HealNSView::post ret=%s", resp_serializer.data)
            return Response(data=resp_serializer.data, status=status.HTTP_202_ACCEPTED)
        except NSLCMException as e:
            logger.error("Exception in HealNSView: %s", e.args[0])
            return Response(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error("Exception in HealNSView: %s", e.args[0])
            return Response(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
