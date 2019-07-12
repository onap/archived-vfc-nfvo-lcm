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

from lcm.ns.biz.ns_delete import DeleteNsService
from lcm.ns.biz.ns_get import GetNSInfoService
from lcm.pub.exceptions import NSLCMException
from lcm.ns.serializers.deprecated.ns_serializers import _QueryNsRespSerializer
from .common import view_safe_call_with_log

logger = logging.getLogger(__name__)


class NSDetailView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: _QueryNsRespSerializer(help_text="NS instance", many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error",
            status.HTTP_404_NOT_FOUND: "Ns instance does not exist"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def get(self, request, ns_instance_id):
        logger.debug("Enter NSDetailView::get ns(%s)", ns_instance_id)
        ns_filter = {"ns_inst_id": ns_instance_id}
        ret = GetNSInfoService(ns_filter).get_ns_info()
        if not ret:
            return Response(status=status.HTTP_404_NOT_FOUND)
        logger.debug("Leave NSDetailView::get::ret=%s", ret)
        resp_serializer = _QueryNsRespSerializer(data=ret[0])
        if not resp_serializer.is_valid():
            raise NSLCMException(resp_serializer.errors)
        return Response(data=resp_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_204_NO_CONTENT: 'successful',
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def delete(self, request, ns_instance_id):
        logger.debug("Enter NSDetailView::delete ns(%s)", ns_instance_id)
        DeleteNsService(ns_instance_id).do_biz()
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)
