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
from lcm.ns_sfcs.biz.get_sfcs import GetSfcs
from lcm.ns_sfcs.serializers.serializers import DeleteSfcRespSerializer
from lcm.ns_sfcs.serializers.serializers import GetSfcRespSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns_sfcs.biz.delete_sfcs import DeleteSfcs

logger = logging.getLogger(__name__)


class SfcDetailView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: GetSfcRespSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error",
            status.HTTP_404_NOT_FOUND: "SFC not found"
        }
    )
    def get(self, request, sfc_inst_id):
        logger.debug("SfcCreateView--get::> %s", sfc_inst_id)
        sfc_inst_info = GetSfcs(sfc_inst_id).do()
        if not sfc_inst_info:
            return Response(status=status.HTTP_404_NOT_FOUND)

        resp_data = {'sfcInstId': sfc_inst_id,
                     'sfcName': "xxx",
                     'sfcStatus': sfc_inst_info[0].status}

        resp_serializer = GetSfcRespSerializer(data=resp_data)
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)
            return Response(data={'error': resp_serializer.errors},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK, data=resp_serializer.data)

    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_202_ACCEPTED: DeleteSfcRespSerializer()
        }
    )
    def delete(self, request_paras, sfc_inst_id):
        resp = DeleteSfcs(sfc_inst_id).do()

        resp_serializer = DeleteSfcRespSerializer(data=resp)
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)
            return Response(data={"result": 1, "detail": resp_serializer.errors},
                            status=status.HTTP_202_ACCEPTED)

        return Response(data=resp, status=status.HTTP_202_ACCEPTED)
