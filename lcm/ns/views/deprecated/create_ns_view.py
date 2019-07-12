# Copyright 2018 ZTE Corporation.
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

from lcm.ns.biz.ns_create import CreateNSService
from lcm.ns.biz.ns_get import GetNSInfoService
from lcm.ns.serializers.deprecated.ns_serializers import _CreateNsReqSerializer
from lcm.ns.serializers.deprecated.ns_serializers import _CreateNsRespSerializer
from lcm.ns.serializers.deprecated.ns_serializers import _QueryNsRespSerializer
from lcm.pub.exceptions import NSLCMException
from lcm.pub.exceptions import BadRequestException
from lcm.pub.utils.values import ignore_case_get
from .common import view_safe_call_with_log

logger = logging.getLogger(__name__)


class CreateNSView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: _QueryNsRespSerializer(help_text="NS instances", many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def get(self, request):
        logger.debug("CreateNSView::get")
        ret = GetNSInfoService().get_ns_info()
        logger.debug("CreateNSView::get::ret=%s", ret)
        resp_serializer = _QueryNsRespSerializer(data=ret, many=True)
        if not resp_serializer.is_valid():
            raise NSLCMException(resp_serializer.errors)
        return Response(data=resp_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=_CreateNsReqSerializer(),
        responses={
            status.HTTP_201_CREATED: _CreateNsRespSerializer(),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def post(self, request):
        logger.debug("Enter CreateNS: %s", request.data)
        req_serializer = _CreateNsReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            raise BadRequestException(req_serializer.errors)

        if ignore_case_get(request.data, 'test') == "test":
            return Response(
                data={'nsInstanceId': "test"},
                status=status.HTTP_201_CREATED
            )
        csar_id = ignore_case_get(request.data, 'csarId')
        ns_name = ignore_case_get(request.data, 'nsName')
        description = ignore_case_get(request.data, 'description')
        context = ignore_case_get(request.data, 'context')
        ns_inst_id = CreateNSService(
            csar_id,
            ns_name,
            description,
            context
        ).do_biz()

        logger.debug("CreateNSView::post::ret={'nsInstanceId':%s}", ns_inst_id)
        resp_serializer = _CreateNsRespSerializer(
            data={'nsInstanceId': ns_inst_id,
                  'nsInstanceName': 'nsInstanceName',
                  'nsInstanceDescription': 'nsInstanceDescription',
                  'nsdId': 123,
                  'nsdInfoId': 456,
                  'nsState': 'NOT_INSTANTIATED',
                  '_links': {'self': {'href': 'href'}}})
        if not resp_serializer.is_valid():
            raise NSLCMException(resp_serializer.errors)
        return Response(data=resp_serializer.data, status=status.HTTP_201_CREATED)
