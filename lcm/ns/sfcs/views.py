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
import traceback
import uuid

import time
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lcm.ns.sfcs.create_flowcla import CreateFlowClassifier
from lcm.ns.sfcs.create_port_chain import CreatePortChain
from lcm.ns.sfcs.create_portpairgp import CreatePortPairGroup
from lcm.ns.sfcs.create_sfc_worker import CreateSfcWorker
from lcm.ns.sfcs.sfc_instance import SfcInstance
from lcm.ns.sfcs.utils import get_fp_id, ignorcase_get

logger = logging.getLogger(__name__)


class SfcInstanceView(APIView):
    def post(self, request):
        data = {
            'nsinstid': request.data['nsinstanceid'],
            "ns_model_data": json.loads(request.data['context']),
            'fpindex': request.data['fpindex'],
            'fpinstid': str(uuid.uuid4()),
            'sdncontrollerid': request.data["sdncontrollerid"]}
        rsp = SfcInstance(data).do_biz()
        return Response(data=rsp, status=status.HTTP_200_OK)


class PortPairGpView(APIView):
    def post(self, request):
        data = {
            'fpinstid': request.data["fpinstid"],
            "ns_model_data": json.loads(request.data['context']),
            'nsinstid': request.data["nsinstanceid"]}
        CreatePortPairGroup(data).do_biz()
        return Response(status=status.HTTP_200_OK)


class FlowClaView(APIView):
    def post(self, request):
        data = {
            'fpinstid': request.data["fpinstid"],
            "ns_model_data": json.loads(request.data['context'])}
        CreateFlowClassifier(data).do_biz()
        return Response(status=status.HTTP_200_OK)


class PortChainView(APIView):
    def post(self, request):
        data = {
            'fpinstid': request.data["fpinstid"],
            "ns_model_data": json.loads(request.data['context'])}
        CreatePortChain(data).do_biz()
        return Response(status=status.HTTP_200_OK)


class SfcView(APIView):
    def post(self, request):
        try:
            logger.info("Create Service Function Chain start")
            logger.info("service_function_chain_request: %s" % json.dumps(request.data))
            logger.info("service_function_chain_context  : %s" % json.dumps(request.data['context']))
            logger.info("service_function_chain_context  : %s" % request.data['context'])
            logger.info("service_function_chain_instanceid : %s" % ignorcase_get(request.data, 'nsinstanceid'))
            logger.info("service_function_chain_sdncontrollerid : %s" % ignorcase_get(request.data, 'sdncontrollerid'))
            logger.info("service_function_chain_fpindex : %s" % ignorcase_get(request.data, 'fpindex'))
            ns_model_data = request.data['context']
        except Exception as e:
            logger.error(traceback.format_exc())
        data = {
            'nsinstid': ignorcase_get(request.data, 'nsinstanceid'),
            "ns_model_data": ns_model_data,
            'fpindex': get_fp_id(ignorcase_get(request.data, 'fpindex'), ns_model_data),
            'fpinstid': str(uuid.uuid4()),
            'sdncontrollerid': ignorcase_get(request.data, 'sdncontrollerid')
        }
        logger.info("Save FPInstModel start: ")
        SfcInstance(data).do_biz()
        logger.info("Save FPInstModel end: ")
        worker = CreateSfcWorker(data)
        job_id = worker.init_data()
        worker.start()
        logger.info("Service Function Chain Thread Sleep start : %s" %time.ctime())
        time.sleep(2)
        logger.info("Service Function Chain Thread Sleep end: %s" % time.ctime())
        logger.info("Create Service Function Chain end")
        return Response(data={"jobId": job_id,
                              "sfcInstId": data["fpinstid"]},
                        status=status.HTTP_200_OK)
