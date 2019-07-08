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


import json
import logging
import time
import traceback
import uuid

from drf_yasg.utils import swagger_auto_schema
from lcm.ns_sfcs.biz.create_flowcla import CreateFlowClassifier
from lcm.ns_sfcs.biz.create_port_chain import CreatePortChain
from lcm.ns_sfcs.biz.create_portpairgp import CreatePortPairGroup
from lcm.ns_sfcs.biz.create_sfc_worker import CreateSfcWorker
from lcm.ns_sfcs.serializers.serializers import CreateFlowClaSerializer
from lcm.ns_sfcs.serializers.serializers import CreatePortChainSerializer
from lcm.ns_sfcs.serializers.serializers import CreatePortPairGpSerializer
from lcm.ns_sfcs.serializers.serializers import CreateSfcInstReqSerializer, CreateSfcInstRespSerializer
from lcm.ns_sfcs.serializers.serializers import CreateSfcReqSerializer, CreateSfcRespSerializer
from lcm.ns_sfcs.biz.sfc_instance import SfcInstance
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns_sfcs.biz.utils import get_fp_id, ignorcase_get

logger = logging.getLogger(__name__)


class SfcInstanceView(APIView):
    @swagger_auto_schema(
        request_body=CreateSfcInstReqSerializer(),
        responses={
            status.HTTP_200_OK: CreateSfcInstRespSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request):
        try:
            req_serializer = CreateSfcInstReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise Exception(req_serializer.errors)

            data = {
                'nsinstid': request.data['nsInstanceId'],
                "ns_model_data": json.loads(request.data['context']),
                'fpindex': request.data['fpindex'],
                'fpinstid': str(uuid.uuid4()),
                'sdncontrollerid': request.data["sdnControllerId"]}
            rsp = SfcInstance(data).do_biz()

            resp_serializer = CreateSfcInstRespSerializer(data=rsp)
            if not resp_serializer.is_valid():
                raise Exception(resp_serializer.errors)

            return Response(data=rsp, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(data={'error': e.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PortPairGpView(APIView):
    @swagger_auto_schema(
        request_body=CreatePortPairGpSerializer(),
        responses={
            status.HTTP_200_OK: 'successful'
        }
    )
    def post(self, request):
        req_serializer = CreatePortPairGpSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.error(req_serializer.errors)

        data = {
            'fpinstid': request.data["fpinstid"],
            "ns_model_data": json.loads(request.data['context']),
            'nsinstid': request.data["nsinstanceid"]}
        CreatePortPairGroup(data).do_biz()
        return Response(status=status.HTTP_200_OK)


class FlowClaView(APIView):
    @swagger_auto_schema(
        request_body=CreateFlowClaSerializer(),
        responses={
            status.HTTP_200_OK: 'successful'
        }
    )
    def post(self, request):
        req_serializer = CreateFlowClaSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.error(req_serializer.errors)

        data = {
            'fpinstid': request.data["fpinstid"],
            "ns_model_data": json.loads(request.data['context'])}
        CreateFlowClassifier(data).do_biz()
        return Response(status=status.HTTP_200_OK)


class PortChainView(APIView):
    @swagger_auto_schema(
        request_body=CreatePortChainSerializer(),
        responses={
            status.HTTP_200_OK: 'successful'
        }
    )
    def post(self, request):
        req_serializer = CreatePortChainSerializer(data=request.data)
        if not req_serializer.is_valid():
            logger.error(req_serializer.errors)

        data = {
            'fpinstid': request.data["fpinstid"],
            "ns_model_data": json.loads(request.data['context'])}
        CreatePortChain(data).do_biz()
        return Response(status=status.HTTP_200_OK)


class SfcView(APIView):
    @swagger_auto_schema(
        request_body=CreateSfcReqSerializer(),
        responses={
            status.HTTP_200_OK: CreateSfcRespSerializer()
        }
    )
    def post(self, request):
        try:
            logger.info("Create Service Function Chain start")
            logger.info("service_function_chain_request: %s" % json.dumps(request.data))
            logger.info("service_function_chain_context  : %s" % json.dumps(request.data['context']))
            logger.info("service_function_chain_context  : %s" % request.data['context'])
            logger.info("service_function_chain_instanceid : %s" % ignorcase_get(request.data, 'nsInstanceId'))
            logger.info("service_function_chain_sdncontrollerid : %s" % ignorcase_get(request.data, 'sdnControllerId'))
            logger.info("service_function_chain_fpindex : %s" % ignorcase_get(request.data, 'fpindex'))
            ns_model_data = request.data['context']

            req_serializer = CreateSfcReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise Exception(req_serializer.errors)
        except Exception as e:
            logger.error("Exception occurs: %s", e.args[0])
            logger.error(traceback.format_exc())
        data = {
            'nsinstid': ignorcase_get(request.data, 'nsInstanceId'),
            "ns_model_data": ns_model_data,
            'fpindex': get_fp_id(ignorcase_get(request.data, 'fpindex'), ns_model_data),
            'fpinstid': str(uuid.uuid4()),
            'sdncontrollerid': ignorcase_get(request.data, 'sdnControllerId')
        }
        logger.info("Save FPInstModel start: ")
        SfcInstance(data).do_biz()
        logger.info("Save FPInstModel end: ")
        worker = CreateSfcWorker(data)
        job_id = worker.init_data()
        worker.start()
        logger.info("Service Function Chain Thread Sleep start : %s" % time.ctime())
        time.sleep(2)
        logger.info("Service Function Chain Thread Sleep end: %s" % time.ctime())
        logger.info("Create Service Function Chain end")

        resp_serializer = CreateSfcRespSerializer(data={"jobId": job_id,
                                                        "sfcInstId": data["fpinstid"]})
        if not resp_serializer.is_valid():
            logger.error(resp_serializer.errors)

        return Response(data={"jobId": job_id,
                              "sfcInstId": data["fpinstid"]},
                        status=status.HTTP_200_OK)
