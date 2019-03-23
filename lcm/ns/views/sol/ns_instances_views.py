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
import traceback

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns.serializers.sol.create_ns_serializers import CreateNsRequestSerializer
from lcm.ns.serializers.sol.ns_instance import NsInstanceSerializer
from lcm.pub.exceptions import BadRequestException, NSLCMException
from lcm.pub.utils.values import ignore_case_get
from lcm.ns.biz.ns_create import CreateNSService
from lcm.ns.biz.ns_get import GetNSInfoService

logger = logging.getLogger(__name__)


class NSInstancesView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: NsInstanceSerializer(help_text="NS instances", many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request):
        logger.debug(request.query_params)
        try:
            logger.debug("CreateNSView::get")
            ret = GetNSInfoService().get_ns_info()  # todo
            logger.debug("CreateNSView::get::ret=%s", ret)
            resp_serializer = NsInstanceSerializer(data=ret, many=True)
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)
            return Response(data=resp_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Exception in GetNS: %s", e.message)
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=CreateNsRequestSerializer(),
        responses={
            status.HTTP_201_CREATED: NsInstanceSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request):
        logger.debug("Enter NSInstancesView::POST ns_instances: Header:%s, Body: %s" % (request.META, request.data))
        try:
            globalCustomerId = request.META.get("HTTP_GLOBALCUSTOMERID ", None)
            if not globalCustomerId:
                raise BadRequestException("Not found globalCustomerId in header")
            req_serializer = CreateNsRequestSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise BadRequestException(req_serializer.errors)

            if ignore_case_get(request.data, 'test') == "test":
                return Response(data={'nsInstanceId': "test"}, status=status.HTTP_201_CREATED)
            csar_id = ignore_case_get(request.data, 'nsdId')
            ns_name = ignore_case_get(request.data, 'nsName')
            description = ignore_case_get(request.data, 'description')
            context = {
                "globalCustomerId": globalCustomerId,
                "serviceType": "NetworkService"
            }
            ns_inst_id = CreateNSService(csar_id, ns_name, description, context).do_biz()
            logger.debug("CreateNSView::post::ret={'nsInstanceId':%s}", ns_inst_id)
            ns_filter = {"ns_inst_id": ns_inst_id}
            nsInstance = GetNSInfoService(ns_filter).get_ns_info()[0]  # todo
            resp_serializer = NsInstanceSerializer(data=nsInstance)
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)
            return Response(data=resp_serializer.data, status=status.HTTP_201_CREATED)
        except BadRequestException as e:
            logger.error("Exception in CreateNS: %s", e.message)
            data = {'status': status.HTTP_400_BAD_REQUEST, 'detail': e.message}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception in CreateNS: %s", e.message)
            data = {'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'detail': e.message}
            return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IndividualNsInstanceView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: NsInstanceSerializer(help_text="NS instances", many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request, ns_instance_id):
        logger.debug("Enter IndividualNsInstanceView::get ns(%s)", ns_instance_id)
        # todo
        return Response(data={}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_204_NO_CONTENT: None
        }
    )
    def delete(self, request, ns_instance_id):
        logger.debug("Enter IndividualNsInstanceView::DELETE ns_instance(%s)", ns_instance_id)
        # todo
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)
