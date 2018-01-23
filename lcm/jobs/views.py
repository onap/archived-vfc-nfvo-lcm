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

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from lcm.jobs.job_get import GetJobInfoService
from lcm.pub.utils.jobutil import JobUtil
from lcm.pub.utils.values import ignore_case_get
from lcm.jobs.serializers import JobUpdReqSerializer, JobUpdRespSerializer
from lcm.jobs.serializers import 
from lcm.pub.exceptions import NSLCMException

logger = logging.getLogger(__name__)


class JobView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: JobQueryRespSerializer()
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request, job_id):
        try:
            response_id = ignore_case_get(request.META, 'responseId')
            ret = GetJobInfoService(job_id, response_id).do_biz()
            resp_serializer = JobQueryRespSerializer(data=ret)
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)
            return Response(data=resp_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(data={'error': e.message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=JobUpdReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: JobUpdRespSerializer()
        }
    )
    def post(self, request, job_id):
        try:
            logger.debug("Enter JobView:post, %s, %s ", job_id, request.data)

            req_serializer = JobUpdReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NSLCMException(req_serializer.errors)

            jobs = JobUtil.query_job_status(job_id)
            if not jobs:
                raise NSLCMException("Job(%s) does not exist.")

            if jobs[-1].errcode != '255':
                progress = request.data.get('progress')
                desc = request.data.get('desc', '%s' % progress)
                errcode = '0' if request.data.get('errcode') in ('true', 'active') else '255'
                logger.debug("errcode=%s", errcode)
                JobUtil.add_job_status(job_id, progress, desc, error_code=errcode)

            resp_serializer = JobUpdRespSerializer(data={'result': 'ok'})
            if not resp_serializer.is_valid():
                raise NSLCMException(req_serializer.errors)

            return Response(data=resp_serializer.data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            resp_serializer = JobUpdRespSerializer(data={
                'result': 'error',
                'msg': e.message})
            if not resp_serializer.is_valid():
                logger.error(resp_serializer.errors)
                return Response(data={
                    'result': 'error',
                    'msg': resp_serializer.errors}, status=status.HTTP_202_ACCEPTED)
            return Response(data=resp_serializer.data, status=status.HTTP_202_ACCEPTED)
