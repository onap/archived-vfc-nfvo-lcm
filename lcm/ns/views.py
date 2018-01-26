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
import json
import logging
import os
import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from lcm.ns.ns_create import CreateNSService
from lcm.ns.ns_delete import DeleteNsService
from lcm.ns.ns_get import GetNSInfoService
from lcm.ns.ns_heal import NSHealService
from lcm.ns.ns_instant import InstantNSService
from lcm.ns.ns_manual_scale import NSManualScaleService
from lcm.ns.ns_terminate import TerminateNsService
from lcm.pub.database.models import NSInstModel, ServiceBaseInfoModel
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE
from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.utils.values import ignore_case_get
from lcm.ns.serializers import CreateNsReqSerializer, CreateNsRespSerializer
from lcm.ns.serializers import QueryNsRespSerializer
from lcm.ns.serializers import NsOperateJobSerializer
from lcm.ns.serializers import InstantNsReqSerializer
from lcm.ns.serializers import TerminateNsReqSerializer
from lcm.pub.exceptions import NSLCMException

logger = logging.getLogger(__name__)


class CreateNSView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            status.HTTP_200_OK: QueryNsRespSerializer(help_text="NS instances", many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def get(self, request):
        try:
            logger.debug("CreateNSView::get")
            filter = None
            csarId = ignore_case_get(request.META, 'csarId')
            if csarId:
                filter = {"csarId": csarId}

            ret = GetNSInfoService(filter).get_ns_info()
            logger.debug("CreateNSView::get::ret=%s", ret)
            resp_serializer = QueryNsRespSerializer(data=ret, many=True)
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)
            return Response(data=resp_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Exception in GetNS: %s", e.message)
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=CreateNsReqSerializer(),
        responses={
            status.HTTP_201_CREATED: CreateNsRespSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request):
        logger.debug("Enter CreateNS: %s", request.data)
        try:
            req_serializer = CreateNsReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NSLCMException(req_serializer.errors)

            if ignore_case_get(request.data, 'test') == "test":
                return Response(data={'nsInstanceId': "test"}, status=status.HTTP_201_CREATED)
            csar_id = ignore_case_get(request.data, 'csarId')
            ns_name = ignore_case_get(request.data, 'nsName')
            description = ignore_case_get(request.data, 'description')
            context = ignore_case_get(request.data, 'context')
            ns_inst_id = CreateNSService(csar_id, ns_name, description, context).do_biz()

            logger.debug("CreateNSView::post::ret={'nsInstanceId':%s}", ns_inst_id)
            resp_serializer = CreateNsRespSerializer(data={'nsInstanceId': ns_inst_id})
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)
            return Response(data=resp_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Exception in CreateNS: %s", e.message)
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        req_serializer = InstantNsReqSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response({'error': req_serializer.errors},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        ack = InstantNSService(ns_instance_id, request.data).do_biz()
        resp_serializer = NsOperateJobSerializer(data=ack['data'])
        if not resp_serializer.is_valid():
            return Response({'error': resp_serializer.errors},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.debug("Leave NSInstView::post::ack=%s", ack)
        return Response(data=resp_serializer.data, status=ack['status'])


class TerminateNSView(APIView):
    @swagger_auto_schema(
        request_body=TerminateNsReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: NsOperateJobSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request, ns_instance_id):
        try:
            logger.debug("Enter TerminateNSView::post %s", request.data)
            req_serializer = TerminateNsReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NSLCMException(req_serializer.errors)

            termination_type = ignore_case_get(request.data, 'terminationType')
            graceful_termination_timeout = ignore_case_get(request.data, 'gracefulTerminationTimeout')
            job_id = JobUtil.create_job("VNF", JOB_TYPE.TERMINATE_VNF, ns_instance_id)
            TerminateNsService(ns_instance_id, termination_type, graceful_termination_timeout, job_id).start()

            resp_serializer = NsOperateJobSerializer(data={'jobId': job_id})
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)
            logger.debug("Leave TerminateNSView::post ret=%s", resp_serializer.data)
            return Response(data=resp_serializer.data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error("Exception in CreateNS: %s", e.message)
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NSHealView(APIView):
    @swagger_auto_schema(
        request_body=HealNsReqSerializer(),
        responses={
            status.HTTP_202_ACCEPTED: NsOperateJobSerializer(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Inner error"
        }
    )
    def post(self, request, ns_instance_id):
        try:
            logger.debug("Enter HealNSView::post %s", request.data)
            logger.debug("Enter HealNSView:: %s", ns_instance_id)
            req_serializer = HealNsReqSerializer(data=request.data)
            if not req_serializer.is_valid():
                raise NSLCMException(req_serializer.errors)

            job_id = JobUtil.create_job("VNF", JOB_TYPE.HEAL_VNF, ns_instance_id)
            NSHealService(ns_instance_id, request.data, job_id).start()

            resp_serializer = NsOperateJobSerializer(data={'jobId': job_id})
            if not resp_serializer.is_valid():
                raise NSLCMException(resp_serializer.errors)

            logger.debug("Leave HealNSView::post ret=%s", resp_serializer.data)
            return Response(data=resp_serializer.data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error("Exception in HealNSView: %s", e.message)
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NSDetailView(APIView):
    def get(self, request, ns_instance_id):
        logger.debug("Enter NSDetailView::get ns(%s)", ns_instance_id)
        ns_filter = {"ns_inst_id": ns_instance_id}
        ret = GetNSInfoService(ns_filter).get_ns_info()
        if not ret:
            return Response(status=status.HTTP_404_NOT_FOUND)
        logger.debug("Leave NSDetailView::get::ret=%s", ret)
        return Response(data=ret, status=status.HTTP_200_OK)

    def delete(self, request, ns_instance_id):
        logger.debug("Enter NSDetailView::delete ns(%s)", ns_instance_id)
        DeleteNsService(ns_instance_id).do_biz()
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)


class SwaggerJsonView(APIView):
    def get(self, request):
        json_file = os.path.join(os.path.dirname(__file__), 'swagger.json')
        f = open(json_file)
        json_data = json.JSONDecoder().decode(f.read())
        f.close()
        return Response(json_data)


class NSInstPostDealView(APIView):
    def post(self, request, ns_instance_id):
        logger.debug("Enter NSInstPostDealView::post %s, %s", request.data, ns_instance_id)
        ns_post_status = ignore_case_get(request.data, 'status')
        ns_status = 'ACTIVE' if ns_post_status == 'true' else 'FAILED'
        ns_opr_status = 'success' if ns_post_status == 'true' else 'failed'
        try:
            NSInstModel.objects.filter(id=ns_instance_id).update(status=ns_status)
            ServiceBaseInfoModel.objects.filter(service_id=ns_instance_id).update(
                active_status=ns_status, status=ns_opr_status)
            nsd_info = NSInstModel.objects.filter(id=ns_instance_id)
            nsd_id = nsd_info[0].nsd_id
            nsd_model = json.loads(nsd_info[0].nsd_model)
            if "policies" in nsd_model and nsd_model["policies"]:
                policy = nsd_model["policies"][0]
                if "properties" in policy and policy["properties"]:
                    file_url = ignore_case_get(policy["properties"][0], "drl_file_url")
                else:
                    file_url = ""
                self.send_policy_request(ns_instance_id, nsd_id, file_url)
        except:
            logger.error(traceback.format_exc())
            return Response(data={'error': 'Failed to update status of NS(%s)' % ns_instance_id},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.debug("*****NS INST %s, %s******", ns_status, ns_opr_status)
        return Response(data={'success': 'Update status of NS(%s) to %s' % (ns_instance_id, ns_status)},
                        status=status.HTTP_202_ACCEPTED)

    def send_policy_request(self, ns_instance_id, nsd_id, file_url):
        input_data = {
            "nsid": ns_instance_id,
            "nsdid": nsd_id,
            "fileUri": file_url
        }
        req_param = json.JSONEncoder().encode(input_data)
        policy_engine_url = 'api/polengine/v1/policyinfo'
        ret = req_by_msb(policy_engine_url, "POST", req_param)
        if ret[0] != 0:
            logger.error("Failed to send ns policy req")


class NSManualScaleView(APIView):
    def post(self, request, ns_instance_id):
        logger.debug("Enter NSManualScaleView::post %s, %s", request.data, ns_instance_id)
        job_id = JobUtil.create_job("NS", JOB_TYPE.MANUAL_SCALE_VNF, ns_instance_id)
        try:
            NSManualScaleService(ns_instance_id, request.data, job_id).start()
        except Exception as e:
            logger.error(traceback.format_exc())
            JobUtil.add_job_status(job_id, 255, 'NS scale failed: %s' % e.message)
            return Response(data={'error': 'NS scale failed: %s' % ns_instance_id},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data={'jobId': job_id}, status=status.HTTP_202_ACCEPTED)
