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
from lcm.ns_vls.biz.delete_vls import DeleteVls
from lcm.ns_vls.biz.get_vls import GetVls
from lcm.ns_vls.serializers.serializers import CreateVlReqSerializer, CreateVlRespSerializer
from lcm.ns_vls.serializers.serializers import DeleteVlRespSerializer
from lcm.ns_vls.serializers.serializers import GetVlRespSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns_vls.biz.create_vls import CreateVls

logger = logging.getLogger(__name__)


class VlView(APIView):
    @swagger_auto_schema(
        request_body=CreateVlReqSerializer(),
        responses={
            status.HTTP_201_CREATED: CreateVlRespSerializer()
        }
    )
    def post(self, request):
        logger.debug("VlsCreateView--post::> %s" % request.data)

        req_serializer = CreateVlReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.error(req_serializer.errors)
            resp = {"result": 1, "detail": req_serializer.errors, "vlId": ""}
            return Response(data=resp, status=status.HTTP_201_CREATED)

        resp = CreateVls(request.data).do()

        resp_serializer = CreateVlRespSerializer(data=resp)
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)
            resp = {"result": 1, "detail": resp_serializer.errors, "vlId": ""}
            return Response(data=resp, status=status.HTTP_201_CREATED)

        return Response(data=resp, status=status.HTTP_201_CREATED)


class VlDetailView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: GetVlRespSerializer(),
            status.HTTP_404_NOT_FOUND: "VL instance is not found",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request, vl_inst_id):
        logger.debug("VlDetailView--get::> %s" % vl_inst_id)
        vl_inst_info = GetVls(vl_inst_id).do()
        if not vl_inst_info:
            return Response(status=status.HTTP_404_NOT_FOUND)

        resp_serializer = GetVlRespSerializer(data={
            'vlId': vl_inst_id,
            'vlName': vl_inst_info[0].vlinstancename,
            'vlStatus': "active"})
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)
            return Response(data={'error': resp_serializer.errors},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK, data=resp_serializer.data)

    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_202_ACCEPTED: DeleteVlRespSerializer()
        }
    )
    def delete(self, request_paras, vl_inst_id):
        logger.debug("VlDetailView--delete::> %s" % vl_inst_id)
        resp = DeleteVls(vl_inst_id).do()

        resp_serializer = DeleteVlRespSerializer(data=resp)
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)
            resp = {"result": 0, "detail": resp_serializer.errors}
            return Response(data=resp, status=status.HTTP_202_ACCEPTED)

        return Response(data=resp, status=status.HTTP_202_ACCEPTED)
