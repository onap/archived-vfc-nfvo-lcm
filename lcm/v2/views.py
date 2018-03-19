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
import traceback

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from lcm.v2.serializers import GrantRequestSerializer
from lcm.v2.serializers import GrantSerializer
from lcm.v2.serializers import VnfLcmOperationOccurrenceNotificationSerializer
from lcm.v2.grant_vnf import GrantVnf

logger = logging.getLogger(__name__)


class VnfGrantView(APIView):
    @swagger_auto_schema(
        request_body=GrantRequestSerializer(),
        responses={
            status.HTTP_201_CREATED: GrantSerializer(
                help_text="The grant was created successfully (synchronous mode)."
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request):
        logger.debug("VnfGrantView Post: %s" % request.data)
        try:
            req_serializer = GrantRequestSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise Exception(req_serializer.errors)

            grant_resp = GrantVnf(request.data).exec_grant()

            resp_serializer = GrantSerializer(data=grant_resp)
            if not resp_serializer.is_valid():
                raise Exception(resp_serializer.errors)

            return Response(data=resp_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Exception in VnfGrant: %s", e.message)
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VnfNotifyView(APIView):
    @swagger_auto_schema(
        request_body=VnfLcmOperationOccurrenceNotificationSerializer(
            help_text="A notification about lifecycle changes triggered by a VNF LCM operation occurrence."
        ),
        responses={
            status.HTTP_204_NO_CONTENT: "The notification was delivered successfully.",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request, vnfmId, vnfInstanceId):
        logger.debug("VnfNotifyView post: %s" % request.data)
        logger.debug("vnfmId: %s vnfInstanceId: %s", vnfmId, vnfInstanceId)
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_204_NO_CONTENT: "The notification endpoint was tested successfully.",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request, vnfmId, vnfInstanceId):
        logger.debug("VnfNotifyView get")
        logger.debug("vnfmId: %s vnfInstanceId: %s", vnfmId, vnfInstanceId)
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)
