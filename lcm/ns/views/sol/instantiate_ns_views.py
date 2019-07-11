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

from lcm.ns.biz.ns_instant import InstantNSService
from lcm.ns.serializers.sol.inst_ns_serializers import InstantNsReqSerializer
from lcm.pub.exceptions import BadRequestException
from lcm.ns.const import NS_OCC_BASE_URI
from lcm.ns.serializers.sol.pub_serializers import ProblemDetailsSerializer
from .common import view_safe_call_with_log

logger = logging.getLogger(__name__)


class InstantiateNsView(APIView):
    @swagger_auto_schema(
        request_body=InstantNsReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: "HTTP_202_ACCEPTED",
            status.HTTP_500_INTERNAL_SERVER_ERROR: ProblemDetailsSerializer()
        }
    )
    @view_safe_call_with_log(logger=logger)
    def post(self, request, ns_instance_id):
        logger.debug("Enter InstantiateNsView::post::ns_instance_id=%s", ns_instance_id)
        logger.debug("request.data=%s", request.data)

        req_serializer = InstantNsReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.debug("request.data is not valid,error: %s" % req_serializer.errors)
            raise BadRequestException(req_serializer.errors)

        InstantNsReq = request.data
        if "additionalParamsForVnf" in InstantNsReq:
            InstantNsReq['locationConstraints'] = []
            for additionalParamsForVnf in InstantNsReq["additionalParamsForVnf"]:
                vnf = {}
                vnf['vnfProfileId'] = additionalParamsForVnf['vnfProfileId']
                vnf['locationConstraints'] = {'vimId': additionalParamsForVnf['additionalParams']['vimId']}
                vnf['additionalParams'] = additionalParamsForVnf['additionalParams']
                InstantNsReq['locationConstraints'].append(vnf)

        ack = InstantNSService(ns_instance_id, request.data).do_biz()
        nsLcmOpOccId = ack.get('occ_id')
        if not nsLcmOpOccId:
            return Response(data=ack['data'], status=ack['status'])
        response = Response(data=ack['data'], status=status.HTTP_202_ACCEPTED)
        logger.debug("Location: %s" % ack['occ_id'])
        response["Location"] = NS_OCC_BASE_URI % nsLcmOpOccId
        logger.debug("Leave InstantiateNsView::post::ack=%s", ack)
        return response
