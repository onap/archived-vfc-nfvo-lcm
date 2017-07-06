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

from lcm.ns.ns_create import CreateNSService
from lcm.ns.ns_get import GetNSInfoService
from lcm.ns.ns_instant import InstantNSService
from lcm.ns.ns_manual_scale import NSManualScaleService
from lcm.ns.ns_terminate import TerminateNsService, DeleteNsService
from lcm.pub.database.models import NSInstModel, ServiceBaseInfoModel
from lcm.pub.utils.jobutil import JobUtil, JOB_TYPE
from lcm.pub.utils.values import ignore_case_get
from lcm.pub.utils.restcall import req_by_msb
from lcm.pub.exceptions import NSLCMException

logger = logging.getLogger(__name__)


class CreateNSView(APIView):
    def get(self, request):
        logger.debug("CreateNSView::get")
        ret = GetNSInfoService().get_ns_info()
        logger.debug("CreateNSView::get::ret=%s", ret)
        return Response(data=ret, status=status.HTTP_200_OK)

    def post(self, request):
        logger.debug("Enter CreateNS: %s", request.data)
        nsd_id = ignore_case_get(request.data, 'nsdId')
        ns_name = ignore_case_get(request.data, 'nsName')
        description = ignore_case_get(request.data, 'description')
        try:
            ns_inst_id = CreateNSService(nsd_id, ns_name, description).do_biz()
        except Exception as e:
            logger.error("Exception in CreateNS: %s", e.message)
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.debug("CreateNSView::post::ret={'nsInstanceId':%s}", ns_inst_id)
        return Response(data={'nsInstanceId': ns_inst_id}, status=status.HTTP_201_CREATED)


class NSInstView(APIView):
    def post(self, request, ns_instance_id):
        ack = InstantNSService(ns_instance_id, request.data).do_biz()
        logger.debug("Leave NSInstView::post::ack=%s", ack)
        return Response(data=ack['data'], status=ack['status'])


class TerminateNSView(APIView):
    def post(self, request, ns_instance_id):
        logger.debug("Enter TerminateNSView::post %s", request.data)
        termination_type = ignore_case_get(request.data, 'terminationType')
        graceful_termination_timeout = ignore_case_get(request.data, 'gracefulTerminationTimeout')
        job_id = JobUtil.create_job("VNF", JOB_TYPE.TERMINATE_VNF, ns_instance_id)
        try:
            TerminateNsService(ns_instance_id, termination_type, graceful_termination_timeout, job_id).start()
        except Exception as e:
            logger.error("Exception in CreateNS: %s", e.message)
            return Response(data={'error': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        ret = {'jobId': job_id}
        logger.debug("Leave TerminateNSView::post ret=%s", ret)
        return Response(data=ret, status=status.HTTP_202_ACCEPTED)


class NSDetailView(APIView):
    def get(self, request, ns_instance_id):
        logger.debug("Enter NSDetailView::get ns(%s)", ns_instance_id)
        ret = GetNSInfoService(ns_instance_id).get_ns_info()
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

    def send_policy_request(self,ns_instance_id, nsd_id, file_url):
        input_data = {
            "nsid": ns_instance_id,
            "nsdid": nsd_id,
            "fileUri":file_url
        }
        req_param = json.JSONEncoder().encode(input_data)
        policy_engine_url = 'openoapi/polengine/v1/policyinfo'
        ret = req_by_msb(policy_engine_url, "POST", req_param)
        if ret[0] != 0:
            logger.error("Failed to send ns policy req")
            #raise NSLCMException('Failed to send ns policy req)')


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