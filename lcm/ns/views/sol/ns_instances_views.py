# Copyright 2019 ZTE Corporation.
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

from lcm.ns.serializers.sol.create_ns_serializers import CreateNsRequestSerializer, CreateNsRespSerializer
from lcm.ns.serializers.sol.pub_serializers import QueryNsRespSerializer

logger = logging.getLogger(__name__)


class NSInstancesView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: QueryNsRespSerializer(help_text="NS instances", many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request):
        logger.debug(request.query_params)
        # todo

    @swagger_auto_schema(
        request_body=CreateNsRequestSerializer(),
        responses={
            status.HTTP_201_CREATED: CreateNsRespSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request):
        logger.debug("Enter NSInstancesView::POST ns_instances %s", request.data)
        # todo
        return Response(data={}, status=status.HTTP_201_CREATED)


class IndividualNsInstanceView(APIView):
    def get(self, request, id):
        logger.debug("Enter IndividualNsInstanceView::get ns(%s)", id)
        # todo
        return Response(data={}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_204_NO_CONTENT: None
        }
    )
    def delete(self, request, id):
        logger.debug("Enter IndividualNsInstanceView::DELETE ns_instance(%s)", id)
        # todo
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)
