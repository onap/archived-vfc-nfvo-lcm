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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from lcm.ns_pnfs.serializers.pnf_serializer import PnfInstanceSerializer, PnfInstancesSerializer
from lcm.ns_pnfs.biz.create_pnf import CreatePnf
from lcm.ns_pnfs.biz.delete_pnf import DeletePnf
from lcm.ns_pnfs.biz.get_pnf import GetPnf
from lcm.pub.exceptions import NSLCMException

logger = logging.getLogger(__name__)


class PnfView(APIView):
    @swagger_auto_schema(
        request_body=PnfInstanceSerializer(),
        responses={
            status.HTTP_201_CREATED: PnfInstanceSerializer()
        }
    )
    def post(self, request):
        logger.debug("PnfView--post::> %s" % request.data)

        req_serializer = PnfInstanceSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.error(req_serializer.errors)
            resp = {"result": 1, "detail": req_serializer.errors, "pnfId": ""}
            return Response(data=resp, status=status.HTTP_201_CREATED)

        pnfInstData = CreatePnf(request.data).do_biz()
        resp_serializer = PnfInstanceSerializer(data=pnfInstData.__dict__)
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)
            resp = {"result": 1, "detail": resp_serializer.errors, "pnfId": ""}
            return Response(data=resp, status=status.HTTP_201_CREATED)

        return Response(data=resp_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: PnfInstancesSerializer(help_text="Pnf instances", many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request):
        try:
            logger.debug("PnfView::get")
            nsInstanceId = request.query_params.get('nsInstanceId', None)
            if nsInstanceId is not None:
                filter = {"nsInstanceId": nsInstanceId}
                pnfInstDataSet = GetPnf(filter).do_biz()
            else:
                pnfInstDataSet = GetPnf().do_biz()
            logger.debug("PnfView::get::ret=%s", pnfInstDataSet)
            resp_serializer = PnfInstancesSerializer(data=[pnfInstData.__dict__ for pnfInstData in pnfInstDataSet])
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)
            return Response(data=resp_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Exception in GetPnf: %s", e.args[0])
            return Response(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IndividualPnfView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_204_NO_CONTENT: 'successful',
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def delete(self, request, pnf_id):
        try:
            logger.debug("Enter IndividualPnfView::delete pnf(%s)", pnf_id)
            DeletePnf(pnf_id).do_biz()
            return Response(data={}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Exception in delete pnf: %s", e.args[0])
            return Response(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: PnfInstanceSerializer(help_text="Pnf instance", many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error",
            status.HTTP_404_NOT_FOUND: "Pnf instance does not exist"
        }
    )
    def get(self, request, pnf_id):
        try:
            logger.debug("Enter IndividualPnfView::get pnf(%s)", pnf_id)
            pnf_filter = {"pnfId": pnf_id}
            pnfInstData = GetPnf(pnf_filter, True).do_biz()
            if not pnfInstData:
                return Response(status=status.HTTP_404_NOT_FOUND)
            logger.debug("Leave IndividualPnfView::get::ret=%s", pnfInstData)
            resp_serializer = PnfInstanceSerializer(data=pnfInstData.__dict__)
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)
            return Response(data=resp_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Exception in IndividualPnfView: %s", e.args[0])
            return Response(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
