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

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from lcm.ns.biz.ns_instant import InstantNSService
from lcm.ns.serializers.inst_ns_serializers import InstantNsReqSerializer
from lcm.ns.serializers.pub_serializers import NsOperateJobSerializer

logger = logging.getLogger(__name__)


class NSInstView(APIView):
    @swagger_auto_schema(
        request_body=InstantNsReqSerializer(),
        responses={
            status.HTTP_200_OK: NsOperateJobSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request, ns_instance_id):
        logger.debug("Enter NSInstView::post::ns_instance_id=%s", ns_instance_id)
        logger.debug("request.data=%s", request.data)
        req_serializer = InstantNsReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.debug("request.data is not valid,error: %s" % req_serializer.errors)
            return Response({'error': req_serializer.errors},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        ack = InstantNSService(ns_instance_id, request.data).do_biz()
        logger.debug("Leave NSInstView::post::ack=%s", ack)
        return Response(data=ack['data'], status=ack['status'])
