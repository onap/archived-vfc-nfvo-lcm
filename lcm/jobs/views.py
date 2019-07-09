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

from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from lcm.jobs.enum import JOB_ERROR_CODE
from lcm.jobs.job_get import GetJobInfoService
from lcm.pub.utils.jobutil import JobUtil
from lcm.jobs.api_model import JobUpdReq, JobUpdResp
from lcm.jobs.serializers import JobUpdReqSerializer, JobUpdRespSerializer
from lcm.jobs.serializers import JobQueryRespSerializer
from lcm.pub.exceptions import BadRequestException, NSLCMException

logger = logging.getLogger(__name__)


class JobView(APIView):

    input_job_id = openapi.Parameter(
        'job_id',
        openapi.IN_QUERY,
        description="job id",
        type=openapi.TYPE_STRING)
    input_response_id = openapi.Parameter(
        'responseId',
        openapi.IN_QUERY,
        description="job response id",
        type=openapi.TYPE_STRING)

    @swagger_auto_schema(
        operation_description="Query job",
        manual_parameters=[input_job_id, input_response_id],
        responses={
            status.HTTP_200_OK: JobQueryRespSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "HTTP_500_INTERNAL_SERVER_ERROR"
        }
    )
    def get(self, request, job_id):
        try:
            logger.debug("Enter JobView::get, job_id: %s, request= %s ", job_id, request.data)
            response_id = int(request.GET.get('responseId', 0))
            ret = GetJobInfoService(job_id, response_id).do_biz()
            resp_serializer = JobQueryRespSerializer(data=ret)
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)
            logger.debug("Leave JobView::get, response=%s", resp_serializer.data)
            return Response(data=resp_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update job",
        manual_parameters=[input_job_id],
        request_body=JobUpdReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: JobUpdRespSerializer()
        }
    )
    def post(self, request, job_id):
        try:
            logger.debug("Enter JobView:post, job_id=%s, request=%s", job_id, request.data)
            req_serializer = JobUpdReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise BadRequestException(req_serializer.errors)

            jobs = JobUtil.query_job_status(job_id)
            if not jobs:
                raise BadRequestException("Job(%s) does not exist." % job_id)

            if jobs[-1].errcode != JOB_ERROR_CODE.ERROR:
                job_up_req = JobUpdReq(**request.data)
                desc = job_up_req.desc
                no_err_list = ('true', 'active', '0')
                err_code = JOB_ERROR_CODE.NO_ERROR if job_up_req.errcode in no_err_list else JOB_ERROR_CODE.ERROR
                logger.debug("errcode=%s", err_code)
                JobUtil.add_job_status(job_id, job_up_req.progress, desc, error_code=err_code)
            job_update_resp = JobUpdResp('ok')
            resp_serializer = JobUpdRespSerializer(job_update_resp)
            logger.debug("Leave JobView::post, response=%s", resp_serializer.data)
            return Response(data=resp_serializer.data, status=status.HTTP_202_ACCEPTED)
        except BadRequestException as e:
            job_update_resp = JobUpdResp('error', e.args[0])
            resp_serializer = JobUpdRespSerializer(job_update_resp)
            return Response(data=resp_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            job_update_resp = JobUpdResp('error', e.args[0])
            resp_serializer = JobUpdRespSerializer(job_update_resp)
            return Response(data=resp_serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
