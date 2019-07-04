# Copyright (c) 2019, CMCC Technologies Co., Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from drf_yasg.utils import swagger_auto_schema
from lcm.ns.serializers.sol.ns_lcm_op_occ import NSLCMOpOccSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns.biz.query_ns_lcm_op_occ import QueryNsLcmOpOcc
from lcm.ns.serializers.sol.ns_lcm_op_occ import NSLCMOpOccsSerializer
from lcm.ns.serializers.sol.pub_serializers import ProblemDetailsSerializer
from lcm.pub.exceptions import NSLCMException
from .common import view_safe_call_with_log

logger = logging.getLogger(__name__)
EXCLUDE_DEFAULT = [
    'operationParams',
    'error',
    'resourceChanges'
]
VALID_FILTERS = [
    "fields",
    "exclude_fields",
    "exclude_default",
    "id",
    "operationState",
    "stateEnteredTime",
    "startTime",
    "nsInstanceId",
    "operation"
]


def get_problem_details_serializer(status_code, error_message):
    problem_details = {
        "status": status_code,
        "detail": error_message
    }
    problem_details_serializer = ProblemDetailsSerializer(data=problem_details)
    problem_details_serializer.is_valid()
    return problem_details_serializer


class QueryMultiNsLcmOpOccs(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: NSLCMOpOccsSerializer(),
            status.HTTP_400_BAD_REQUEST: ProblemDetailsSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: ProblemDetailsSerializer()
        }
    )
    @view_safe_call_with_log(logger=logger)
    def get(self, request):
        logger.debug("QueryMultiNsLcmOpOccs--get::> %s" % request.query_params)

        if request.query_params and not set(request.query_params).issubset(set(VALID_FILTERS)):
            problem_details_serializer = get_problem_details_serializer(status.HTTP_400_BAD_REQUEST, "Not a valid filter")
            return Response(data=problem_details_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        resp_data = QueryNsLcmOpOcc(request.query_params).query_multi_ns_lcm_op_occ()
        if len(resp_data) == 0:
            return Response(data=[], status=status.HTTP_200_OK)

        ns_lcm_op_occs_serializer = NSLCMOpOccsSerializer(data=resp_data)
        if not ns_lcm_op_occs_serializer.is_valid():
            raise NSLCMException(ns_lcm_op_occs_serializer.errors)

        logger.debug("QueryMultiNsLcmOpOccs--get::> Remove default fields if exclude_default is specified")
        if 'exclude_default' in list(request.query_params.keys()):
            for field in EXCLUDE_DEFAULT:
                for lcm_op in ns_lcm_op_occs_serializer.data:
                    del lcm_op[field]
        return Response(data=ns_lcm_op_occs_serializer.data, status=status.HTTP_200_OK)


class QuerySingleNsLcmOpOcc(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: NSLCMOpOccSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: ProblemDetailsSerializer()
        }
    )
    @view_safe_call_with_log(logger=logger)
    def get(self, request, lcmopoccid):
        logger.debug("QuerySingleNsLcmOpOcc--get::> %s" % request.query_params)

        resp_data = QueryNsLcmOpOcc(request.query_params,
                                    lcm_op_occ_id=lcmopoccid).query_single_ns_lcm_op_occ()

        ns_lcm_op_occ_serializer = NSLCMOpOccSerializer(data=resp_data)
        if not ns_lcm_op_occ_serializer.is_valid():
            raise NSLCMException(ns_lcm_op_occ_serializer.errors)

        return Response(data=ns_lcm_op_occ_serializer.data, status=status.HTTP_200_OK)
